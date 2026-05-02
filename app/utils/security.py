import hashlib
import secrets

def generate_salt() -> bytes:
    return secrets.token_bytes(64)

def get_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000, dklen=64).hex()

def generate_session_token() -> str:
    return secrets.token_hex(16)