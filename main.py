from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timezone

from typing import Optional

class ChatRequest(BaseModel):
    customer_id: str
    intent: str
    session_id: Optional[str] = None
import os

import database
from mongo_db import MongoDB
from models import X402Message, X402Metadata, RegistryResponsePayload, MerchantMatch, MerchantEndpoint
from buyer_agent import process_user_intent
from twilio.rest import Client

app = FastAPI(title="Agentic Commerce Hub")

# Mount the static directory to serve the frontend UI
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    # Initialize SQLite (Registry) and Pinecone
    database.init_db()
    # Initialize MongoDB (Memory, Sessions, Transactions)
    MongoDB.connect()

@app.on_event("shutdown")
async def shutdown_event():
    MongoDB.disconnect()

@app.post("/twilio/whatsapp")
async def twilio_whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Webhook to receive messages from Twilio WhatsApp.
    We process the intent in the background so Twilio doesn't time out.
    """
    customer_id = From.replace("whatsapp:", "")
    user_intent = Body
    
    # Run the buyer agent processing in the background
    background_tasks.add_task(process_user_intent, customer_id, user_intent)
    
    # Twilio requires valid TwiML response. We return empty TwiML since the agent will reply via API later.
    from fastapi.responses import Response
    return Response(content='<Response></Response>', media_type="application/xml")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Endpoint for the web UI to interact with the agent.
    """
    reply, session_id = await process_user_intent(req.customer_id, req.intent, req.session_id)
    return {"reply": reply, "session_id": session_id}

@app.get("/api/logs/{session_id}")
async def get_logs(session_id: str):
    """
    Fetch all audit logs for a given session from MongoDB.
    """
    if MongoDB.db is None:
        MongoDB.connect()
    
    logs_cursor = MongoDB.db.audit_logs.find({"session_id": session_id}).sort("timestamp", 1)
    
    formatted_logs = []
    async for log in logs_cursor:
        log["_id"] = str(log["_id"])
        if "timestamp" in log and log["timestamp"]:
            log["timestamp"] = log["timestamp"].isoformat()
        formatted_logs.append(log)
            
    return {"logs": formatted_logs}


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
