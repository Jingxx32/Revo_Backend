from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
import hashlib
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import select

from app.core.config import settings
from app.db.database import get_session
from app.db.models import User


# Use settings from config.py for consistent configuration
SECRET_KEY: str = settings.JWT_SECRET_KEY
ALGORITHM: str = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Use direct bcrypt library instead of passlib to avoid initialization issues
# We'll handle SHA-256 pre-hashing manually to avoid 72-byte limit
def _prepare_password_for_bcrypt(password: str) -> bytes:
    """
    Prepare password for bcrypt hashing.
    Always use SHA-256 pre-hashing to avoid bcrypt's 72-byte limit.
    Returns bytes for bcrypt library.
    """
    password_bytes = password.encode('utf-8')
    # Always hash with SHA-256 first to avoid 72-byte limit
    # SHA-256 produces 32 bytes (256 bits), well under the 72-byte limit
    sha256_hash = hashlib.sha256(password_bytes).digest()  # Use digest() not hexdigest() for bytes
    return sha256_hash


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with SHA-256 pre-hashing.
    
    All passwords are first hashed with SHA-256, then the SHA-256 hash is bcrypted.
    This completely avoids the 72-byte limit of bcrypt while maintaining security.
    
    Args:
        password: Plain text password (must be a string, not bytes)
        
    Returns:
        Hashed password string (prefixed with "sha256:" to indicate SHA-256 was used)
        
    Raises:
        ValueError: If password is None or empty
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    try:
        # Prepare password with SHA-256 pre-hashing (always, to avoid any length issues)
        prepared_password_bytes = _prepare_password_for_bcrypt(password)
        
        # Generate salt and hash using bcrypt
        # bcrypt.gensalt() generates a random salt
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(prepared_password_bytes, salt)
        
        # Convert to string and add marker
        hashed_str = hashed_bytes.decode('utf-8')
        return "sha256:" + hashed_str
    except Exception as e:
        # Catch any unexpected errors and provide a clear message
        error_msg = str(e)
        import traceback
        print(f"Password hashing error: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Password hashing failed: {error_msg}") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Supports our custom format with SHA-256 pre-hashing (starts with "sha256:").
    Also supports legacy bcrypt format (starts with "$2a$", "$2b$", etc.) for backward compatibility.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    
    # Ensure password is a string
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    
    try:
        # Check for our custom SHA-256 marker
        if hashed_password.startswith("sha256:"):
            # Remove marker
            actual_hash = hashed_password[7:]  # Remove "sha256:" prefix
            
            # Prepare password with SHA-256 pre-hashing (same as in hash_password)
            prepared_password_bytes = _prepare_password_for_bcrypt(plain_password)
            
            # Verify using bcrypt
            actual_hash_bytes = actual_hash.encode('utf-8')
            return bcrypt.checkpw(prepared_password_bytes, actual_hash_bytes)
        else:
            # Legacy format: try direct bcrypt verification
            # This provides backward compatibility for old passwords
            try:
                password_bytes = plain_password.encode('utf-8')
                hashed_bytes = hashed_password.encode('utf-8')
                return bcrypt.checkpw(password_bytes, hashed_bytes)
            except Exception:
                # If direct verification fails, also try with SHA-256 pre-hashing
                # (in case it's a new password stored without the marker)
                prepared_password_bytes = _prepare_password_for_bcrypt(plain_password)
                hashed_bytes = hashed_password.encode('utf-8')
                return bcrypt.checkpw(prepared_password_bytes, hashed_bytes)
    except Exception:
        # If verification fails for any reason, return False
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Use datetime.now(timezone.utc) instead of deprecated datetime.utcnow()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session=Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Prefer email; fallback to id if present
        email: Optional[str] = payload.get("email") or payload.get("sub")
        user_id: Optional[int] = payload.get("id")
        if not email and not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if email:
        stmt = select(User).where(User.email == email)
    else:
        stmt = select(User).where(User.id == user_id)

    user = session.exec(stmt).first()
    if not user:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user has admin privileges.
    
    Currently treats users with role 'admin' as administrators.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user

