from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# A dummy password hash used to mitigate timing attacks
DUMMY_PASSWORD_HASH = pwd_context.hash("DUMMY_PASSWORD_AT_STARTUP_!@#")

def verify_plain_against_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a given password hash.

    This function compares the provided plain password with a stored bcrypt hash
    using Passlib's CryptContext. If the verification fails or if the given hash
    is invalid (e.g., when the user does not exist), it performs a dummy 
    verification using a predefined hash (DUMMY_PASSWORD_HASH) to normalize 
    response time. This helps mitigate timing attacks that could reveal 
    whether a username exists in the system.

    Args:
        plain_password (str): The user-provided plain-text password.
        hashed_password (str): The stored bcrypt hash to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
        
    except Exception:
        # Fallback verification to prevent timing leaks on invalid hashes
        try:
            pwd_context.verify(plain_password, DUMMY_PASSWORD_HASH)
        except Exception:
            pass
        return False