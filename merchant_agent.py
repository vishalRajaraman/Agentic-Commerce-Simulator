import os
import uuid
import json
from openai import OpenAI
from auth_layer import verify_payload
import mongo_db

# Initialize OpenAI client with NVIDIA endpoint
client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=os.getenv("NIM_API_KEY", "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")
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
        
        # The user requested openai/gpt-oss-120b but Nvidia might map it to their specific model strings
        # We will use the standard endpoint call
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", # wait, nvidia doesn't have this exact name, but user provided it in the snippet
            messages=self.session_memory[session_id],
            temperature=0.7,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        
        response_text = completion.choices[0].message.content
        reasoning = getattr(completion.choices[0].message, "reasoning_content", "No reasoning provided.")
        
        self.session_memory[session_id].append({"role": "assistant", "content": response_text})
        
        return response_text, reasoning

    async def negotiate(self, ap2_token: str) -> dict:
        """
        Handle a complex negotiation offer from the Buyer Agent.
        Requires a signed AP2 token payload.
        """
        try:
            # 1. Verify AP2 Handshake
            decoded = verify_payload(ap2_token)
            buyer_id = decoded["agent_id"]
            payload = decoded["payload"]
            proposed_terms = payload.get("proposed_terms")
            product = payload.get("product")
            session_id = payload.get("session_id", str(uuid.uuid4()))
            
            # 2. Fetch CRM Context
            crm_context = await mongo_db.get_merchant_crm(self.merchant_id, buyer_id)
            
            # 3. Construct System Prompt
            system_prompt = f"""You are an autonomous Merchant Agent for {self.merchant_id}.
You are negotiating a deal for the following product:
{json.dumps(product, indent=2)}

Buyer's CRM History: {crm_context}

Your Goal: Maximize profit for the merchant. You MUST adhere to the product's base_price and bundle_rules. 
If the buyer asks for a lower price, try to keep the price as high as possible. You can counter-offer, but do not go below (base_price * 0.8).
If the buyer asks for free shipping, only grant it if it matches the bundle_rules.

CRITICAL RULE: To prevent endless haggling, you must either accept the buyer's terms or provide your absolute final 'take-it-or-leave-it' offer by your 2nd counter-offer. Do not let the negotiation stagnate!

You MUST respond in JSON format with exactly three fields:
- "status": "accepted", "rejected", or "counter_offer"
- "final_terms": a string summarizing the agreed or countered terms
- "message": a natural language message to the buyer
"""
            
            # 4. Generate LLM Response
            user_message = f"Buyer proposes: {proposed_terms}"
            response_text, reasoning = await self._get_llm_response(session_id, system_prompt, user_message)
            
            # Parse the JSON response
            try:
                # simple cleanup in case LLM wraps in markdown
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                response_json = json.loads(clean_text)
            except json.JSONDecodeError:
                response_json = {
                    "status": "counter_offer",
                    "final_terms": "pending",
                    "message": response_text
                }
            
            # 5. Audit Logging
            await mongo_db.save_audit_log(
                agent_type="merchant_agent",
                session_id=session_id,
                action="negotiation_response",
                reasoning=reasoning,
                payload=response_json
            )
            
            return response_json
            
        except Exception as e:
            return {"status": "error", "message": f"Negotiation failed: {str(e)}"}

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
