"""
SentinelX EDR - Security Middleware
====================================
API key validation and optional JWT authentication for the dashboard.

Modes:
    - No API_KEY set: All endpoints are open (development mode)
    - API_KEY set: Endpoints require X-API-Key header or Bearer token
    - JWT: Optional token-based auth for dashboard sessions
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings

logger = logging.getLogger(__name__)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ── Security Schemes ────────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> bool:
    """
    FastAPI dependency that validates API key or JWT token.
    
    If no API_KEY is configured in settings, all requests pass through
    (development/demo mode). In production, set API_KEY env var.

    Usage:
        @router.get("/secure", dependencies=[Depends(verify_api_key)])
        def secure_endpoint():
            ...
    """
    settings = get_settings()

    # If no API key is configured, allow all requests (dev mode)
    if not settings.API_KEY:
        return True

    # Check X-API-Key header
    if api_key and api_key == settings.API_KEY:
        return True

    # Check Bearer token (JWT)
    if credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            if payload.get("sub"):
                return True
        except JWTError:
            pass

    logger.warning("Unauthorized API access attempt")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key / token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a JWT access token.
    
    Args:
        subject: The token subject (e.g., username or user ID).
        expires_delta: Custom expiration time. Defaults to JWT_EXPIRATION_MINUTES.
    
    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": "sentinelx-edr",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    expires_delta = timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": "sentinelx-edr",
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_ws_token(token: str) -> Optional[str]:
    """
    Verify a JWT token for WebSocket connections.
    WebSockets can't use standard HTTP headers, so the token
    is passed as a query parameter.
    
    Args:
        token: JWT token string from query parameter.
    
    Returns:
        Subject (username/ID) if valid, None otherwise.
    """
    settings = get_settings()

    # If no API key configured, accept all connections
    if not settings.API_KEY:
        return "anonymous"

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload.get("sub")
    except JWTError:
        return None
