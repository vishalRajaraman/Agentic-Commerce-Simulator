import asyncio
import os
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from tools import (
    query_registry, 
    fetch_customer_profile, 
    update_customer_profile,
    send_initial_rfq_parallel,
    negotiate_with_merchant,
    finalize_deal_and_request_approval
)

from langchain_openai import ChatOpenAI

# Ensure NIM_API_KEY is available in .env
nim_api_key = os.getenv("NIM_API_KEY")

# We use the Nemotron 550b model for the Buyer Agent's Brain via the OpenAI compatible endpoint
llm = ChatOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nim_api_key,
    model="nvidia/nemotron-3-ultra-550b-a55b",
    temperature=0.7,
    max_tokens=1024,
    model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}}
)

tools = [
    query_registry, 
    fetch_customer_profile, 
    update_customer_profile,
    send_initial_rfq_parallel,
    negotiate_with_merchant,
    finalize_deal_and_request_approval
]

system_prompt = (
    "You are a powerful autonomous Buyer Agent. Your job is to find the best deal for the user by negotiating with multiple merchants.\n"
    "You have access to several tools. Follow these steps strictly:\n"
    "1. Use `fetch_customer_profile` to get any preferences for the user.\n"
    "2. Use `query_registry` to find relevant merchant IDs for the requested category.\n"
    "3. Use `send_initial_rfq_parallel` passing the list of merchant_ids to get their initial quotes.\n"
    "4. Based on the quotes, select the best merchant and use `negotiate_with_merchant` to counter-offer a lower price. You can try 1 or 2 rounds of negotiation.\n"
    "5. Once a merchant accepts a price, use `finalize_deal_and_request_approval` to lock it in and send the payment link to the user.\n"
    "If a merchant rejects, try another merchant or accept their counter offer.\n"
)

agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

async def process_user_intent(customer_id: str, intent: str):
    print(f"--- Buyer Agent Intake ---")
    print(f"Customer: {customer_id} | Intent: {intent}")
    
    response = await agent_executor.ainvoke({
        "messages": [("user", f"User ID: {customer_id}. User wants: {intent}")]
    })
    
    return response['messages'][-1].content

if __name__ == "__main__":
    asyncio.run(process_user_intent("user_123", "Buy me 2 pairs of black socks"))
