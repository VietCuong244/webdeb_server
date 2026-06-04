from feature.user.service import require_user
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.novel import Novel
from models.user import User


async def require_user_on_novel(
    novel_id: UUID,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    novel = await db.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return [novel_id, current_user.user_id]