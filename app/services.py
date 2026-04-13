import os
import base64
from cryptography.fernet import Fernet


def _get_fernet():
    """Get or generate Fernet instance from environment key."""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Generate and warn (dev only)
        key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = key
        print(f"[WARNING] No ENCRYPTION_KEY set. Generated temporary key: {key}")
        print("[WARNING] Set ENCRYPTION_KEY env var for persistent encryption!")
    
    # Ensure key is valid base64 Fernet key
    try:
        if isinstance(key, str):
            key = key.encode()
        return Fernet(key)
    except Exception:
        # Key might not be valid Fernet format, generate one
        new_key = Fernet.generate_key()
        os.environ['ENCRYPTION_KEY'] = new_key.decode()
        print(f"[WARNING] Invalid ENCRYPTION_KEY. Generated new key.")
        return Fernet(new_key)


def encrypt_note(plaintext: str) -> str:
    """Encrypt a note's content and return base64 string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_note(ciphertext: str) -> str:
    """Decrypt a note's content and return plaintext."""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return '[Decryption failed – key mismatch or corrupted data]'


def generate_encryption_key() -> str:
    """Utility: generate a fresh Fernet key (use once for setup)."""
    return Fernet.generate_key().decode()
