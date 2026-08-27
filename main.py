from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

import database
from models import X402Message, X402Metadata, RegistryResponsePayload, MerchantMatch, MerchantEndpoint

app = FastAPI(title="Central Discovery Registry")

@app.on_event("startup")
def startup_event():
    # Initialize the database and seed it on startup
    database.init_db()

@app.post("/api/registry/search", response_model=X402Message)
async def registry_search(request_payload: X402Message):
    # The incoming request should have intent="registry_search" and payload={"query": "..."}
    # Safely extract the query string
    payload_data = request_payload.payload
    query = ""
    if isinstance(payload_data, dict):
        query = payload_data.get("query", "")
    
    # Search DB for merchants matching the category query
    matches = database.search_merchants_by_category(query)
    
    # Format Response to match the x402 protocol specification
    merchant_matches = []
    for m in matches:
        merchant_matches.append(
            MerchantMatch(
                merchant_id=m["merchant_id"],
                category_match=m["category"],
                endpoints=MerchantEndpoint(interact=m["endpoint_interact"])
            )
        )
    
    payload = RegistryResponsePayload(
        matches_found=len(merchant_matches),
        merchants=merchant_matches
    )
    
    response = X402Message(
        metadata=X402Metadata(
            session_id=request_payload.metadata.session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature="signed_by_registry_001",
            sender_type="registry"
        ),
        intent="registry_response",
        payload=payload
    )
    
    return response
