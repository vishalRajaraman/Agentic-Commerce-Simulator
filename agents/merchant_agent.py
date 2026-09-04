import os
import uuid
import json
from openai import AsyncOpenAI
from core.auth_layer import verify_ap2_handshake
from db import mongo_db

# Initialize AsyncOpenAI client with NVIDIA endpoint
client = AsyncOpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=os.getenv("NIM_API_KEY", "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"),
  max_retries=10,
  timeout=120.0
)

class MerchantAgent:
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        
        # We store conversational memory for active sessions
        # In a real app, this might be backed by Redis or MongoDB
        self.session_memory = {}

    async def _get_llm_response(self, session_id: str, system_prompt: str, user_message: str) -> tuple[str, str]:
        if session_id not in self.session_memory:
            self.session_memory[session_id] = [{"role": "system", "content": system_prompt}]
            
        self.session_memory[session_id].append({"role": "user", "content": user_message})
        
        try:
            completion = await client.chat.completions.create(
                model="nvidia/nemotron-3-ultra-550b-a55b", 
                messages=self.session_memory[session_id],
                temperature=0.6,
                top_p=0.7,
                max_tokens=4096,
                stream=False
            )
            response_text = completion.choices[0].message.content
            reasoning = getattr(completion.choices[0].message, 'reasoning_content', 'No reasoning provided.')
        except Exception as e:
            response_text = f'{{"status": "error", "message": "Failed to get response from NVIDIA API: {str(e)}" }}'
            reasoning = f"API error: {str(e)}"
        
        self.session_memory[session_id].append({"role": "assistant", "content": response_text})
        
        return response_text, reasoning

    async def negotiate(self, ap2_token: dict) -> dict:
        """
        Handle a complex negotiation offer from the Buyer Agent.
        Requires a signed and encrypted AP2 token payload.
        """
        try:
            # Load private key for this merchant
            private_key_path = f"merchant_keys/{self.merchant_id}_private.pem"
            if not os.path.exists(private_key_path):
                raise ValueError(f"Private key not found for {self.merchant_id}")
            with open(private_key_path, "r") as f:
                merchant_priv = f.read()
                
            # 1. Decrypt and Verify AP2 Handshake (PKI)
            payload = verify_ap2_handshake(merchant_priv, ap2_token)
            
            buyer_id = payload.get("customer_id", "unknown_buyer")
            proposed_terms = payload.get("proposed_terms")
            product = payload.get("product")
            session_id = payload.get("session_id", str(uuid.uuid4()))
            
            # 2. Fetch CRM Context
            crm_context = await mongo_db.get_merchant_crm(self.merchant_id, buyer_id)
            
            # 3. Construct System Prompt
            system_prompt = f"""You are a sharp, persuasive autonomous Merchant Agent for {self.merchant_id}.
You are negotiating a deal for the following product:
{json.dumps(product, indent=2)}

Buyer's CRM History: {crm_context}

YOUR PRIMARY GOAL: Maximise total revenue. Selling a bundle is ALWAYS better than a single-item discount.

=== NEGOTIATION PLAYBOOK (follow this strictly, round by round) ===

ROUND 1 - ANCHOR HIGH & PUSH THE BUNDLE:
Never immediately discount a single item. Open by enthusiastically pitching the bundle deal from bundle_rules as the best value. Explain the per-unit savings. Only mention the single-item base price as the fallback.

ROUND 2 - SWEETEN THE BUNDLE, HOLD THE LINE:
If the buyer rejects the bundle, do NOT drop the single-item price yet. Instead sweeten the bundle - throw in free shipping on the bundle, a related add-on product, or a small bundle % off. Make it feel irresistible. Express that you are going out of your way for them.

ROUND 3 - LOYALTY DISCOUNT ON SINGLE (last resort for returning customers):
Only if the buyer has explicitly refused the bundle TWICE, offer the loyalty discount (10-20% based on CRM) on the single item. Frame it as a special one-time gesture. Still remind them the bundle is better value per unit.

ROUND 4 - FINAL OFFER:
State clearly this is your absolute best and final price. Never go below (base_price * 0.80) for a single item.

=== RULES ===
- NEVER accept the buyer's first offer if it is below base_price.
- ALWAYS pitch the bundle at least once before conceding on single-item price.
- New customers: focus purely on bundle upsell. Do not offer loyalty discount.
- Returning customers: use loyalty only as a last resort after bundle attempts fail.
- Free shipping only per bundle_rules; never on a single item unless explicitly allowed.
- You may negotiate for UP TO 4 rounds. Do not end early unless the buyer accepts.
- Be warm, enthusiastic and sales-driven. Sound like a great salesperson, not a robot.

You MUST respond in JSON format with exactly three fields:
- "status": "accepted", "rejected", or "counter_offer"
- "final_terms": precise string with the ₹ amount and terms
- "message": a persuasive natural-language message (2-4 sentences)
"""
            
            # 4. Generate LLM Response
            user_message = f"Buyer proposes: {proposed_terms}"
            response_text, reasoning = await self._get_llm_response(session_id, system_prompt, user_message)
            
            # Parse the JSON response
            try:
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                response_json = json.loads(clean_text)
            except json.JSONDecodeError:
                response_json = {
                    "status": "counter_offer",
                    "final_terms": "pending",
                    "message": response_text
                }
            
            await mongo_db.save_audit_log(
                agent_type="merchant_agent",
                session_id=session_id,
                action="negotiation_response",
                reasoning=reasoning,
                payload=response_json
            )
            
            return response_json
            
        except Exception as e:
            error_json = {"status": "error", "message": f"Negotiation failed: {str(e)}"}
            if 'session_id' in locals():
                await mongo_db.save_audit_log(
                    agent_type="merchant_agent",
                    session_id=session_id,
                    action="negotiation_response",
                    reasoning=f"Error: {str(e)}",
                    payload=error_json
                )
            return error_json

    def generate_razorpay_link(self, final_terms: str) -> str:
        """
        Simulate generating a Razorpay payment link.
        """
        mock_payment_id = uuid.uuid4().hex[:8]
        return f"https://rzp.io/i/{mock_payment_id}?terms={final_terms.replace(' ', '_')}"

# Global registry of merchant agents
ACTIVE_MERCHANT_AGENTS = {}

def get_merchant_agent(merchant_id: str) -> MerchantAgent:
    if merchant_id not in ACTIVE_MERCHANT_AGENTS:
        ACTIVE_MERCHANT_AGENTS[merchant_id] = MerchantAgent(merchant_id)
    return ACTIVE_MERCHANT_AGENTS[merchant_id]
