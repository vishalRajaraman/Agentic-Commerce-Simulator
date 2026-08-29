import asyncio
import os
import sys
import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import AIMessage
import mongo_db

# Ensure NIM_API_KEY is available in .env
nim_api_key = os.getenv("NIM_API_KEY")

# We use the Nemotron model for the Buyer Agent's Brain via the OpenAI compatible endpoint
llm = ChatOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nim_api_key,
    model="nvidia/nemotron-3-ultra-550b-a55b",
    temperature=0.7,
    max_tokens=1024,
    model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}}
)

system_prompt = """
You are a powerful autonomous Buyer Agent. Your job is to find the absolute best deal for the user by negotiating aggressively with multiple merchants.
You have access to several MCP tools. Follow these steps strictly:
1. Use `fetch_customer_profile` to get any preferences for the user.
2. Use `query_registry` with the user's intent to query the central vector database and retrieve the interaction endpoints of relevant merchants.
3. Search the merchant catalogs using `search_merchant_catalog` for the merchants returned by the registry.
4. Based on the catalog constraints, select the best merchant and use `negotiate_with_merchant` to send a complex proposal. You must negotiate aggressively—try to get a lower price than the base price, or demand free shipping/bundle deals. You can try 1 or 2 rounds of negotiation if rejected.
5. Once a merchant accepts, use `finalize_deal_and_request_approval` to lock it in and send the payment link to the user.
6. Summarize the transaction and update the user's preferences for that specific merchant using `update_customer_profile` (you MUST provide the merchant_id) before finishing.

Always fight for the lowest possible price! However, to avoid endless haggling, if a merchant provides a final 'take-it-or-leave-it' counter-offer, you MUST accept it (if reasonable) or move on to another merchant immediately. Do not get stuck in a loop.
"""

async def process_user_intent(customer_id: str, intent: str, session_id: str = None):
    print(f"--- Buyer Agent Intake ---")
    print(f"Customer: {customer_id} | Intent: {intent}")
    
    # Configure MCP Client to connect to the HTTP SSE Server
    mcp_server_url = "http://localhost:8001/sse"
    
    try:
        async with sse_client(mcp_server_url, timeout=60) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection to the MCP Server
                await session.initialize()
                
                # Fetch the tools dynamically from the server
                tools = await load_mcp_tools(session)
                print(f"[MCP] Successfully loaded {len(tools)} tools from server via SSE.")
                
                # Create the agent with the dynamically loaded tools
                agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
                
                # Ensure MongoDB is connected for logging
                if mongo_db.MongoDB.db is None:
                    mongo_db.MongoDB.connect()
                
                # Run the agent
                session_id = session_id or os.urandom(8).hex()
                response = await agent_executor.ainvoke({
                    "messages": [("user", f"User ID: {customer_id}. User wants: {intent}. Negotiation Session ID: {session_id}")]
                })
                
                # Extract and log the Buyer Agent's reasoning from the AIMessages
                for msg in response.get("messages", []):
                    if isinstance(msg, AIMessage):
                        # Construct the reasoning text
                        reasoning_text = ""
                        if msg.content:
                            reasoning_text += str(msg.content)
                        if hasattr(msg, "additional_kwargs") and "reasoning_content" in msg.additional_kwargs:
                            reasoning_text += f"\n[Internal Reasoning]: {msg.additional_kwargs['reasoning_content']}"
                        
                        tool_calls = msg.tool_calls if hasattr(msg, "tool_calls") else []
                        
                        if reasoning_text or tool_calls:
                            await mongo_db.save_audit_log(
                                agent_type="buyer_agent",
                                session_id=session_id,
                                action="decision_step",
                                reasoning=reasoning_text.strip(),
                                payload={"tool_calls": tool_calls}
                            )
                
                return response['messages'][-1].content, session_id
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to process user intent via MCP HTTP Server: {e}")
        return f"System error occurred: {str(e)}", None

if __name__ == "__main__":
    asyncio.run(process_user_intent("user_123", "Buy me 2 pairs of black socks"))
