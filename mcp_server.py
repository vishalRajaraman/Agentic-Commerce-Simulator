from mcp.server.fastmcp import FastMCP
from typing import List, Dict
import database
import mongo_db
import vector_store
from auth_layer import sign_payload
from merchant_agent import get_merchant_agent
import asyncio

# Initialize FastMCP Server on port 8001 to avoid conflicting with FastAPI on 8000
mcp = FastMCP("AgenticCommerceTools", port=8001)

@mcp.tool()
def query_registry(user_query: str) -> List[Dict]:
    """
    Query the central registry using a semantic search of the user's intent.
    Returns a list of matching merchants (with merchant_id and endpoint_interact routes).
    """
    print(f"[MCP TOOL: query_registry] Semantically searching registry for '{user_query}'")
    return database.search_merchants_by_category(user_query)

@mcp.tool()
def search_merchant_catalog(merchant_id: str, query: str) -> List[Dict]:
    """
    Search a specific merchant's catalog for products matching the query.
    Returns the top matching items and their constraints (base_price, bundle_rules).
    """
    print(f"[MCP TOOL: search_merchant_catalog] Searching {merchant_id} for '{query}'")
    results = vector_store.search_merchant_catalog(merchant_id, query)
    return results

@mcp.tool()
async def fetch_customer_profile(customer_id: str) -> str:
    """
    Fetch the summarized customer profile (long-term memory) from MongoDB.
    """
    print(f"[MCP TOOL: fetch_customer_profile] Fetching profile for {customer_id}")
    profile = await mongo_db.get_customer_profile(customer_id)
    return profile if profile else "No existing profile for this customer."

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
        "session_id": session_id,
        "product": product_dict,
        "proposed_terms": proposed_terms
    }
    
    # Sign payload for AP2 Handshake
    ap2_token = sign_payload(agent_id=customer_id, payload=payload)
    
    # Send to merchant agent
    agent = get_merchant_agent(merchant_id)
    response = await agent.negotiate(ap2_token)
    
    return response

@mcp.tool()
async def finalize_deal_and_request_approval(customer_id: str, merchant_id: str, final_terms: str, item_description: str) -> str:
    """
    Finalizes the deal with the merchant, asks the merchant to generate a Razorpay link,
    and then sends that link to the user (via Twilio/UI) for final approval.
    """
    print(f"[MCP TOOL: finalize_deal] Finalizing deal with {merchant_id} on terms: {final_terms}")
    agent = get_merchant_agent(merchant_id)
    payment_link = agent.generate_razorpay_link(final_terms)
    
    msg = f"DEAL FINALIZED! {item_description} from {merchant_id}.\nTerms: {final_terms}\nPlease pay here: {payment_link}"
    print(f"\n--- MOCK TWILIO MESSAGE TO {customer_id} ---\n{msg}\n---------------------------------------\n")
    
    return f"Deal finalized. Payment link generated and sent to user: {payment_link}"

if __name__ == "__main__":
    # Run the server using HTTP SSE transport on port 8001
    mcp.run(transport="sse")
