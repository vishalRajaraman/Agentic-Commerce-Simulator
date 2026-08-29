import jwt
import os
import datetime

# Mock secret key for signing. In a real AP2 setup, agents would have their own key pairs.
AP2_SECRET_KEY = os.getenv("AP2_SECRET_KEY", "super_secret_ap2_key_for_agentic_commerce")

def sign_payload(agent_id: str, payload: dict) -> str:
    """
    Signs a payload (e.g. a negotiation offer) returning a JWT token to simulate an AP2 handshake.
    """
    data = {
        "agent_id": agent_id,
        "payload": payload,
        # using timezone-aware UTC datetime
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    }
    token = jwt.encode(data, AP2_SECRET_KEY, algorithm="HS256")
    return token

def verify_payload(token: str) -> dict:
    """
    Verifies the AP2 handshake JWT token.
    Returns the decoded payload if valid, raises an Exception otherwise.
    """
    try:
        decoded = jwt.decode(token, AP2_SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("AP2 Handshake Failed: Token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("AP2 Handshake Failed: Invalid token signature.")
