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

from db import database
from db import mongo_db
from db.mongo_db import MongoDB
from core.models import X402Message, X402Metadata, RegistryResponsePayload, MerchantMatch, MerchantEndpoint
from agents.buyer_agent import process_user_intent
from twilio.rest import Client

app = FastAPI(title="Agentic Commerce Hub")

# Mount the static directory to serve the frontend UI
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    # Initialize SQLite (Registry) and Pinecone
    pass
    # Initialize MongoDB (Memory, Sessions, Transactions)
    MongoDB.connect()

@app.on_event("shutdown")
async def shutdown_event():
    MongoDB.disconnect()

# Twilio Client Initialization
twilio_client = None
try:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if account_sid and auth_token:
        twilio_client = Client(account_sid, auth_token)
except Exception as e:
    print(f"Twilio initialization failed: {e}")

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

async def execute_payment(latest_tx: dict) -> str:
    from db.mongo_db import get_razorpay_credentials, update_transaction_status
    import razorpay
    
    customer_id = latest_tx["customer_id"]
    rzp_customer_id, rzp_token_id = await get_razorpay_credentials(customer_id)
    
    if not rzp_token_id:
        return f"Wallet Not Setup! Please authorize your Agent Wallet."
        
    if rzp_token_id.startswith("mock_token_"):
        import uuid
        fake_id = "pay_" + uuid.uuid4().hex[:14]
        await update_transaction_status(latest_tx["_id"], "Paid")
        return f"Payment successful\nItem name: {latest_tx.get('item_description')}\nAmount: {latest_tx.get('amount_paise', 1000)/100}\nRazorpay receipt: {fake_id}"
        
    try:
        rzp_key = os.getenv("RAZORPAY_KEY_ID")
        rzp_secret = os.getenv("RAZORPAY_KEY_SECRET")
        client = razorpay.Client(auth=(rzp_key, rzp_secret))
        
        order = client.order.create({
            "amount": latest_tx.get("amount_paise", 1000),
            "currency": "INR",
            "customer_id": rzp_customer_id,
            "receipt": f"receipt_{str(latest_tx['_id'])}"
        })
        
        await update_transaction_status(latest_tx["_id"], "Paid")
        return f"Payment successful\nItem name: {latest_tx.get('item_description')}\nAmount: {latest_tx.get('amount_paise', 1000)/100}\nRazorpay receipt: {order['receipt']}"
    except Exception as e:
        await update_transaction_status(latest_tx["_id"], "Failed")
        return f"Payment failed: {str(e)}"

async def process_and_reply_twilio(customer_id: str, user_intent: str, phone_number: str = None):
    print(f"[Background Task] Starting process_and_reply_twilio for {customer_id}")
    reply, session_id = await process_user_intent(customer_id, user_intent)
    if reply:
        print(f"[Background Task] Sending reply: {reply}")
        send_twilio_message(phone_number or customer_id, reply)
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
    phone_number = From.replace("whatsapp:", "")
    # Map all WhatsApp users to our demo user so they have access to the configured Razorpay wallet
    customer_id = "vishal_123"
    user_intent = Body.strip()
    
    print(f"=== Received Twilio Webhook ===")
    print(f"From: {From} -> Phone: {phone_number} -> Customer ID: {customer_id}")
    print(f"Body: {user_intent}")
    
    # Check if the user is confirming a payment
    from db.mongo_db import get_customer_transactions, update_transaction_status
    

    transactions = await get_customer_transactions(customer_id)
    if transactions:
        latest_tx = transactions[0] # They are sorted by _id desc
        if latest_tx.get("status") == "Pending Payment" and user_intent.lower() in ["yes", "y", "ok", "sure", "pay", "approve"]:
            msg = await execute_payment(latest_tx)
            send_twilio_message(phone_number, msg)
            from fastapi.responses import Response
            return Response(content='<Response></Response>', media_type="application/xml")

    # Run the buyer agent processing and reply in the background
    background_tasks.add_task(process_and_reply_twilio, customer_id, user_intent, phone_number)
    
    # Twilio requires valid TwiML response. We return empty TwiML since the agent will reply via API later.
    from fastapi.responses import Response
    return Response(content='<Response></Response>', media_type="application/xml")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Endpoint for the web UI to interact with the agent.
    """
    # Check if the user is confirming a payment
    from db.mongo_db import get_customer_transactions, update_transaction_status
    transactions = await get_customer_transactions(req.customer_id)
    if transactions:
        latest_tx = transactions[0]
        if latest_tx.get("status") == "Pending Payment" and req.intent.lower() in ["yes", "y", "ok", "sure", "pay", "approve"]:
            msg = await execute_payment(latest_tx)
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

import razorpay
import uuid
import random
from datetime import datetime, timedelta

@app.post("/api/razorpay/create_setup_order")
async def create_setup_order(req: Request):
    data = await req.json()
    customer_id = data.get("customer_id", "vishal_123")
    
    rzp_key = os.getenv("RAZORPAY_KEY_ID")
    rzp_secret = os.getenv("RAZORPAY_KEY_SECRET")
    client = razorpay.Client(auth=(rzp_key, rzp_secret))
    
    uid = uuid.uuid4().hex[:6]
    phone = str(random.randint(1000000000, 9999999999))
    rzp_customer = client.customer.create({
        "name": f"Vishal {uid}",
        "email": f"vishal_{uid}@example.com",
        "contact": phone
    })
    
    order_data = {
        "amount": 100,
        "currency": "INR",
        "customer_id": rzp_customer["id"]
    }
    
    order = client.order.create(data=order_data)
    
    return {
        "order_id": order["id"],
        "razorpay_customer_id": rzp_customer["id"],
        "key": rzp_key
    }

@app.post("/api/razorpay/verify_setup")
async def verify_setup(req: Request):
    data = await req.json()
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")
    customer_id = data.get("customer_id", "vishal_123")
    rzp_customer_id = data.get("razorpay_customer_id")
    
    rzp_key = os.getenv("RAZORPAY_KEY_ID")
    rzp_secret = os.getenv("RAZORPAY_KEY_SECRET")
    client = razorpay.Client(auth=(rzp_key, rzp_secret))
    
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    payment = client.payment.fetch(razorpay_payment_id)
    token_id = payment.get("token_id")
    
    if not token_id:
        # Fallback for test mode to mock a token if standard order is used
        token_id = f"mock_token_{razorpay_payment_id}"
        
    if token_id:
        from db.mongo_db import save_razorpay_credentials
        await save_razorpay_credentials(customer_id, rzp_customer_id, token_id)
        return {"status": "success", "message": "Wallet authorized successfully!"}
    
    return {"status": "error", "message": "Token not generated."}
