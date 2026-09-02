import asyncio
import os
import json
from auth_layer import sign_payload
from mongo_db import MongoDB
import mongo_db
import vector_store

async def run_tests():
    print("--- Starting Backend Tests ---")
    
    # 1. Connect MongoDB
    MongoDB.connect()
    
    # 2. Test Customer Profile
    print("\n[TEST] update_customer_profile")
    await mongo_db.update_customer_profile("user_ui_test", "Likes fast shipping and bulk discounts")
    profile = await mongo_db.get_customer_profile("user_ui_test")
    print(f"Profile fetched: {profile}")
    
    # 3. Test Pinecone Catalog Search
    print("\n[TEST] search_merchant_catalog")
    results = vector_store.search_merchant_catalog("merchant_004_clothing", "black socks")
    print(f"Catalog search results: {json.dumps(results, indent=2)}")
    
    # 4. Test Merchant Agent Negotiation (AP2 Layer)
    print("\n[TEST] merchant_agent.negotiate")
    from merchant_agent import get_merchant_agent
    
    agent = get_merchant_agent("merchant_004_clothing")
    
    payload = {
        "session_id": "test_session_123",
        "product": {
            "product_id": "prod_001_socks",
            "merchant_id": "merchant_004_clothing",
            "description": "High-quality black cotton socks",
            "base_price": 20.0,
            "bundle_rules": "Buy 2 for $35"
        },
        "proposed_terms": "I want to buy 2 pairs for $35 total, according to your bundle rules."
    }
    
    ap2_token = sign_payload("user_ui_test", payload)
    
    response = await agent.negotiate(ap2_token)
    print(f"Merchant Agent Response: {json.dumps(response, indent=2)}")
    
    MongoDB.disconnect()

if __name__ == "__main__":
    asyncio.run(run_tests())
