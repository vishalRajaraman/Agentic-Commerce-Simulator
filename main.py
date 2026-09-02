from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timezone

from typing import Optional

from dotenv import load_dotenv
load_dotenv()

class ChatRequest(BaseModel):
    customer_id: str
    intent: str
    session_id: Optional[str] = None
import os

import database
import mongo_db
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

async def process_and_reply_twilio(customer_id: str, user_intent: str):
    print(f"[Background Task] Starting process_and_reply_twilio for {customer_id}")
    from mcp_server import send_twilio_message
    reply, session_id = await process_user_intent(customer_id, user_intent)
    if reply:
        print(f"[Background Task] Sending reply: {reply}")
        send_twilio_message(customer_id, reply)
    else:
        print("[Background Task] No reply generated.")

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
    user_intent = Body.strip()
    
    print(f"=== Received Twilio Webhook ===")
    print(f"From: {From} -> Customer ID: {customer_id}")
    print(f"Body: {user_intent}")
    
    # Check if the user is confirming a payment
    from mongo_db import get_customer_transactions, update_transaction_status
    from mcp_server import send_twilio_message
    
    transactions = await get_customer_transactions(customer_id)
    if transactions:
        latest_tx = transactions[0] # They are sorted by _id desc
        if latest_tx.get("status") == "Pending Payment" and user_intent.lower() in ["yes", "y", "ok", "sure", "pay"]:
            # Mock payment processing
            await update_transaction_status(latest_tx["_id"], "Paid")
            msg = f"Payment Successful for {latest_tx.get('item_description', 'your order')}! Your transaction ID is {latest_tx['_id']}. The merchant will ship it shortly."
            send_twilio_message(customer_id, msg)
            from fastapi.responses import Response
            return Response(content='<Response></Response>', media_type="application/xml")

    # Run the buyer agent processing and reply in the background
    background_tasks.add_task(process_and_reply_twilio, customer_id, user_intent)
    
    # Twilio requires valid TwiML response. We return empty TwiML since the agent will reply via API later.
    from fastapi.responses import Response
    return Response(content='<Response></Response>', media_type="application/xml")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Endpoint for the web UI to interact with the agent.
    """
    # Check if the user is confirming a payment
    from mongo_db import get_customer_transactions, update_transaction_status
    transactions = await get_customer_transactions(req.customer_id)
    if transactions:
        latest_tx = transactions[0]
        if latest_tx.get("status") == "Pending Payment" and req.intent.lower() in ["yes", "y", "ok", "sure", "pay"]:
            await update_transaction_status(latest_tx["_id"], "Paid")
            msg = f"Payment Successful for {latest_tx.get('item_description', 'your order')}! Your transaction ID is {latest_tx['_id']}. The merchant will ship it shortly."
            return {"reply": msg, "session_id": req.session_id}

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

@app.get("/api/orders/{customer_id}")
async def get_orders(customer_id: str):
    """
    Fetch all persistent transactions for a user.
    """
    if MongoDB.db is None:
        MongoDB.connect()
    orders = await mongo_db.get_customer_transactions(customer_id)
    return {"orders": orders}
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
