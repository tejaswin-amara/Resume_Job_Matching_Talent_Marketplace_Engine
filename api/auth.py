"""Authentication and Token Verification Dependency.

Provides centralized bearer token verification for protected endpoints.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify bearer token for protected endpoints.

    shortcut: Accepts any valid bearer token until production IdP (Firebase Admin SDK) is connected.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid auth credentials")
    return credentials.credentials
