from passlib.context import CryptContext

# Configure bcrypt as the password hashing algorithm
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plain-text password with its hashed version.
    Returns True if they match.
    """
    return pwd_context.verify(plain_password, hashed_password)