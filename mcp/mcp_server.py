from mcp.server.fastmcp import FastMCP
from typing import List, Dict
from db import database
from db import mongo_db
from db import vector_store
import asyncio
import os
import httpx
from dotenv import load_dotenv
load_dotenv()
from twilio.rest import Client

# Twilio Client Initialization
twilio_client = None
try:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if account_sid and auth_token:
        twilio_client = Client(account_sid, auth_token)
except Exception as e:
    print(f"Twilio initialization failed: {e}")

# Initialize FastMCP Server on port 8001 to avoid conflicting with FastAPI on 8000
mcp = FastMCP("AgenticCommerceTools", port=8001)

from core import crypto_utils
from core.auth_layer import create_ap2_handshake
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.path.exists("buyer_private.pem"):
    buyer_priv, buyer_pub = crypto_utils.generate_rsa_key_pair()
    with open("buyer_private.pem", "w") as f: f.write(buyer_priv)
    with open("buyer_public.pem", "w") as f: f.write(buyer_pub)
else:
    with open("buyer_private.pem", "r") as f: buyer_priv = f.read()
    with open("buyer_public.pem", "r") as f: buyer_pub = f.read()

@mcp.tool()
def query_registry(user_query: str) -> List[Dict]:
    """
    Query the central registry using a semantic search of the user's intent.
    Returns a list of matching merchants (with merchant_id and endpoint_interact routes).
    """
    print(f"[MCP TOOL: query_registry] Semantically searching registry for '{user_query}'")
    return database.search_merchants_by_category(user_query)

@mcp.tool()
def search_merchant_catalog(merchant_id: str, query: str) -> str:
    """
    Search a specific merchant's catalog for products matching the query.
    Returns the top matching items in a readable YAML format.
    """
    print(f"[MCP TOOL: search_merchant_catalog] Searching {merchant_id} for '{query}'")
    results = vector_store.search_merchant_catalog(merchant_id, query)
    
    import yaml
    
    yaml_data = {"products": []}
    for item in results:
        product = {
            "id": item.get("product_id", ""),
            "description": item.get("description", ""),
            "base_price": item.get("base_price", ""),
            "bundle_rules": item.get("bundle_rules", "")
        }
        yaml_data["products"].append(product)
        
    return yaml.dump(yaml_data, sort_keys=False)

@mcp.tool()
async def fetch_merchant_context(customer_id: str, merchant_id: str) -> str:
    """
    Fetch the summarized customer profile (long-term memory) for a specific merchant from MongoDB.
    """
    print(f"[MCP TOOL: fetch_merchant_context] Fetching profile for {customer_id} with merchant {merchant_id}")
    return await mongo_db.get_merchant_crm(merchant_id, customer_id)

@mcp.tool()
async def update_customer_profile(customer_id: str, merchant_id: str, new_summary: str) -> str:
    """
    Updates the customer's profile summary for a SPECIFIC merchant in MongoDB after a transaction completes.
    You MUST provide the merchant_id of the merchant you just transacted with.
    """
    print(f"[MCP TOOL: update_customer_profile] Updating profile for {customer_id} on {merchant_id}")
    await mongo_db.update_customer_profile(customer_id, merchant_id, new_summary)
    return "Profile updated successfully."

@mcp.tool()
async def negotiate_with_merchant(customer_id: str, merchant_id: str, session_id: str, product_dict: dict, proposed_terms: str) -> Dict:
    """
    Negotiate complex terms with a merchant.
    Signs the payload with an AP2 token and sends it to the Merchant Agent.
    """
    print(f"[MCP TOOL: negotiate_with_merchant] Negotiating with {merchant_id}: {proposed_terms}")
    
    # Construct the payload
    payload = {
        "customer_id": customer_id,
        "session_id": session_id,
        "product": product_dict,
        "proposed_terms": proposed_terms
    }
    
    # Fetch merchant public key for encryption
    merchant_pub = database.get_merchant_public_key(merchant_id)
    if not merchant_pub:
        return {"status": "error", "message": f"Merchant {merchant_id} public key not found in registry."}

    # Create PKI AP2 Handshake token
    ap2_token = create_ap2_handshake(buyer_priv, buyer_pub, merchant_pub, payload)
    
    # Send to merchant agent via network
    endpoint = database.get_merchant_endpoint(merchant_id)
    if not endpoint:
        return {"status": "error", "message": f"Merchant {merchant_id} endpoint not found."}
        
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(endpoint, json={"ap2_token": ap2_token})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[HTTP Error] Negotiating with {merchant_id}: {e}")
            return {"status": "error", "message": f"Failed to reach merchant server: {str(e)}"}

@mcp.tool()
def send_twilio_message(to_number: str, body: str) -> str:
    """
    Sends a WhatsApp message to the user via Twilio.
    """
    if not twilio_client:
        print(f"\n--- MOCK TWILIO MESSAGE TO {to_number} ---\n{body}\n---------------------------------------\n")
        return "Twilio not configured. Message mocked."
    
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
        
    try:
        message = twilio_client.messages.create(
            from_=from_number,
            body=body,
            to=to_number
        )
        print(f"[Twilio] Sent message SID {message.sid} to {to_number}")
        return f"Message sent successfully with SID {message.sid}"
    except Exception as e:
        print(f"[Twilio Error] {e}")
        return f"Failed to send message: {e}"

@mcp.tool()
async def finalize_deal_and_request_approval(customer_id: str, merchant_id: str, final_terms: str, item_description: str) -> str:
    """
    Finalizes the deal with the merchant, asks the merchant to generate a Razorpay link,
    and then sends that link to the user (via Twilio/UI) for final approval.
    """
    print(f"[MCP TOOL: finalize_deal] Finalizing deal with {merchant_id} on terms: {final_terms}")
    
    endpoint = database.get_merchant_endpoint(merchant_id)
    payment_link = f"https://rzp.io/mock?merchant={merchant_id}"
    
    if endpoint:
        generate_link_endpoint = endpoint.replace("/interact", "/generate_link")
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(generate_link_endpoint, json={"final_terms": final_terms})
                resp.raise_for_status()
                payment_link = resp.json().get("payment_link", payment_link)
            except Exception as e:
                print(f"[HTTP Error] Generating link for {merchant_id}: {e}")
    
    transaction_data = {
        "customer_id": customer_id,
        "merchant_id": merchant_id,
        "item_description": item_description,
        "final_terms": final_terms,
        "status": "Pending Payment"
    }
    await mongo_db.create_transaction(transaction_data)
    
    msg = (
        f"✅ *DEAL FINALIZED!*\n\n"
        f"🛒 *Item:* {item_description}\n"
        f"🏪 *Merchant:* {merchant_id}\n"
        f"📋 *Terms:* {final_terms}\n\n"
        f"💳 *Please pay here to confirm:* \n{payment_link}"
    )
    send_twilio_message(customer_id, msg)
    
    return f"Deal finalized. Payment link generated and sent to user: {payment_link}"

if __name__ == "__main__":
    # Run the server using HTTP SSE transport on port 8001
    mcp.run(transport="sse")
