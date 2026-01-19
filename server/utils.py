import secrets
import string

def generate_key(length=24):
    """Generates a secure random license key."""
    chars = string.ascii_uppercase + string.digits
    # Format: XXXXX-XXXXX-XXXXX-XXXXX
    # 4 blocks of 5 chars = 20 chars
    
    key = '-'.join(''.join(secrets.choice(chars) for _ in range(5)) for _ in range(4))
    return key
