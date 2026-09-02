import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet

def generate_rsa_key_pair() -> tuple[str, str]:
    """Generates a 2048-bit RSA key pair and returns them as PEM strings."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def sign_data(private_key_pem: str, data: dict) -> str:
    """Signs a dictionary payload using the private key."""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )
    
    message = json.dumps(data, sort_keys=True).encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(public_key_pem: str, data: dict, signature_b64: str) -> bool:
    """Verifies the signature of a dictionary payload."""
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8')
    )
    
    message = json.dumps(data, sort_keys=True).encode('utf-8')
    signature = base64.b64decode(signature_b64.encode('utf-8'))
    
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def encrypt_data(public_key_pem: str, data: dict) -> dict:
    """
    Encrypts a payload using Hybrid Encryption:
    1. Generate an AES key (Fernet).
    2. Encrypt the data with the AES key.
    3. Encrypt the AES key with the RSA public key.
    Returns a dict with 'enc_key' and 'enc_data'.
    """
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8')
    )
    
    # 1. Symmetric encryption of data
    fernet_key = Fernet.generate_key()
    f = Fernet(fernet_key)
    message = json.dumps(data).encode('utf-8')
    enc_data = f.encrypt(message)
    
    # 2. Asymmetric encryption of the symmetric key
    enc_fernet_key = public_key.encrypt(
        fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return {
        "enc_key": base64.b64encode(enc_fernet_key).decode('utf-8'),
        "enc_data": enc_data.decode('utf-8') # Fernet outputs URL-safe base64 string
    }

def decrypt_data(private_key_pem: str, encrypted_payload: dict) -> dict:
    """
    Decrypts a Hybrid Encrypted payload.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )
    
    enc_fernet_key = base64.b64decode(encrypted_payload['enc_key'].encode('utf-8'))
    enc_data = encrypted_payload['enc_data'].encode('utf-8')
    
    # 1. Asymmetric decryption of the symmetric key
    fernet_key = private_key.decrypt(
        enc_fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 2. Symmetric decryption of data
    f = Fernet(fernet_key)
    dec_message = f.decrypt(enc_data)
    
    return json.loads(dec_message.decode('utf-8'))
