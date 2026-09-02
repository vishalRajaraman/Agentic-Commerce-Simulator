from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RegistrySearchRequest(BaseModel):
    query: str

class MerchantEndpoint(BaseModel):
    interact: str

class MerchantMatch(BaseModel):
    merchant_id: str
    category_match: str
    endpoints: MerchantEndpoint

class RegistryResponsePayload(BaseModel):
    matches_found: int
    merchants: List[MerchantMatch]

class X402Metadata(BaseModel):
    session_id: str
    timestamp: str
    signature: str
    sender_type: str

class X402Message(BaseModel):
    protocol: str = "x402"
    version: str = "1.0"
    metadata: X402Metadata
    intent: str
    payload: Any
