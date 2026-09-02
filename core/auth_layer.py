from core import crypto_utils

def create_ap2_handshake(buyer_private_key: str, buyer_public_key: str, merchant_public_key: str, payload: dict) -> dict:
    """
    Creates a secure AP2 Handshake token.
    1. Signs the payload with the buyer's private key.
    2. Bundles the payload, signature, and buyer's public key.
    3. Encrypts the entire bundle with the merchant's public key.
    """
    # 1. Sign
    signature = crypto_utils.sign_data(buyer_private_key, payload)
    
    # 2. Bundle
    bundle = {
        "payload": payload,
        "signature": signature,
        "buyer_public_key": buyer_public_key
    }
    
    # 3. Encrypt
    encrypted_token = crypto_utils.encrypt_data(merchant_public_key, bundle)
    
    return encrypted_token

def verify_ap2_handshake(merchant_private_key: str, encrypted_token: dict) -> dict:
    """
    Verifies a secure AP2 Handshake token.
    1. Decrypts the token with the merchant's private key.
    2. Extracts the buyer's public key, signature, and payload.
    3. Verifies the signature.
    Returns the payload if valid, raises ValueError otherwise.
    """
    # 1. Decrypt
    try:
        bundle = crypto_utils.decrypt_data(merchant_private_key, encrypted_token)
    except Exception as e:
        raise ValueError(f"AP2 Handshake Failed: Decryption error - {e}")
        
    payload = bundle.get("payload")
    signature = bundle.get("signature")
    buyer_public_key = bundle.get("buyer_public_key")
    
    if not payload or not signature or not buyer_public_key:
        raise ValueError("AP2 Handshake Failed: Malformed bundle.")
        
    # 2. Verify
    is_valid = crypto_utils.verify_signature(buyer_public_key, payload, signature)
    if not is_valid:
        raise ValueError("AP2 Handshake Failed: Invalid signature (Identity mismatch).")
        
    return payload
