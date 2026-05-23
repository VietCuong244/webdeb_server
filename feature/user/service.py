from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from feature.auth.schema import TokenData
from feature.auth.service import verify_access_token
from models.user import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token, credentials_exception)
    user_email: str = payload.get("user_email")
    if user_email is None:
        raise credentials_exception
    token_data = TokenData(user_email=user_email)
    
    user = (await db.execute(select(User).where(User.user_email == token_data.user_email))).scalar()
    if user is None:
        raise credentials_exception
    return user

async def require_user(current_user: User = Depends(get_current_user)):
    return current_user

async def require_unlocked_user(current_user: User = Depends(require_user)):
    if current_user.user_islocked == True:
        raise HTTPException(status_code=403, detail="Account is locked")
    return current_user

async def require_admin(current_user: User = Depends(require_unlocked_user)):
    if current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

