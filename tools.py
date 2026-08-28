from langchain.tools import tool
import database
import mongo_db
from typing import List, Dict

@tool
def query_registry(category: str) -> List[Dict]:
    """
    Query the Central Discovery Registry to find merchants selling a specific product category.
    Returns a list of merchant dictionaries including merchant_id and endpoint_interact.
    """
    print(f"[TOOL: query_registry] Searching for {category}")
    merchants = database.search_merchants_by_category(category)
    return merchants

@tool
async def fetch_customer_profile(customer_id: str) -> str:
    """
    Fetch the summarized customer profile (long-term memory) from MongoDB.
    Returns a string containing the profile/preferences.
    """
    print(f"[TOOL: fetch_customer_profile] Fetching profile for {customer_id}")
    profile = await mongo_db.get_customer_profile(customer_id)
    return profile if profile else "No existing profile for this customer."

@tool
async def update_customer_profile(customer_id: str, new_summary: str) -> str:
    """
    Updates the customer's profile summary in MongoDB after a transaction completes.
    """
    print(f"[TOOL: update_customer_profile] Updating profile for {customer_id}")
    await mongo_db.update_customer_profile(customer_id, new_summary)
    return "Profile updated successfully."

@tool
async def send_initial_rfq_parallel(merchant_ids: List[str], item_description: str) -> Dict:
    """
    Simulates sending an initial RFQ (Request for Quote) to multiple merchants in parallel.
    Returns a dictionary of their initial quotes.
    """
    from merchant_agent import get_merchant_agent
    import asyncio
    
    print(f"[TOOL: send_initial_rfq_parallel] Requesting quotes for '{item_description}' from {merchant_ids}")
    
    async def get_quote(mid):
        # In a real system, this would be an HTTP/MCP call to the Merchant Agent
        agent = get_merchant_agent(mid)
        # Simulating network delay
        await asyncio.sleep(0.5)
        return mid, agent.process_rfq(item_description)

    results = await asyncio.gather(*(get_quote(mid) for mid in merchant_ids))
    return dict(results)

@tool
async def negotiate_with_merchant(merchant_id: str, proposed_price: float) -> Dict:
    """
    Counter-offer a specific price to a merchant.
    Returns their response (accepted, rejected, or counter_offer) and final price.
    """
    from merchant_agent import get_merchant_agent
    
    print(f"[TOOL: negotiate_with_merchant] Offering ${proposed_price} to {merchant_id}")
    agent = get_merchant_agent(merchant_id)
    return agent.negotiate(proposed_price)

@tool
async def finalize_deal_and_request_approval(customer_id: str, merchant_id: str, final_price: float, item_description: str) -> str:
    """
    Finalizes the deal with the merchant, asks the merchant to generate a Razorpay link,
    and then sends that link to the user (via Twilio/UI) for final approval.
    """
    from merchant_agent import get_merchant_agent
    
    print(f"[TOOL: finalize_deal] Finalizing deal with {merchant_id} for ${final_price}")
    agent = get_merchant_agent(merchant_id)
    payment_link = agent.generate_razorpay_link(final_price)
    
    # In a full Twilio setup, we would trigger the Twilio API here.
    # For now, we mock the notification.
    msg = f"DEAL FINALIZED! {item_description} for ${final_price} from {merchant_id}. Please pay here: {payment_link}"
    print(f"\n--- MOCK TWILIO MESSAGE TO {customer_id} ---\n{msg}\n---------------------------------------\n")
    
    return f"Deal finalized. Payment link generated and sent to user: {payment_link}"

