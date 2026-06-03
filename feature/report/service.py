from feature.user.service import require_user
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.user import User


async def require_report_owner(
    current_user: User = Depends(require_user),
    report_user_id = UUID
):
    if current_user.user_id != report_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    return current_user