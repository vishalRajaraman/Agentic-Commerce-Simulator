from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from merchant_agent import get_merchant_agent
from typing import Dict, Any

app = FastAPI(title="Merchant Network Server")

class AP2Payload(BaseModel):
    ap2_token: str

class LinkPayload(BaseModel):
    final_terms: str

@app.post("/api/merchant/{merchant_id}/interact")
async def interact_with_merchant(merchant_id: str, payload: AP2Payload):
    print(f"[Merchant Server] Incoming AP2 negotiation for {merchant_id}")
    agent = get_merchant_agent(merchant_id)
    response = await agent.negotiate(payload.ap2_token)
    return response

@app.post("/api/merchant/{merchant_id}/generate_link")
async def generate_payment_link(merchant_id: str, payload: LinkPayload):
    print(f"[Merchant Server] Generating payment link for {merchant_id}")
    agent = get_merchant_agent(merchant_id)
    link = agent.generate_razorpay_link(payload.final_terms)
    return {"payment_link": link}

if __name__ == "__main__":
    # Run the distributed merchant servers on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002)
