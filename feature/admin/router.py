from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from feature.user.service import require_admin
from database import SessionLocal, get_db
from models.user import User
from feature.common.response import AdminGetAllUsersResponse, MessageResponse


router_admin = APIRouter(prefix="/admin", tags=["admin"])

@router_admin.put("/user/{user_id}/lock", response_model=MessageResponse)
async def lock_user(user_id: str, current_user = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user.user_role == "admin":
        raise HTTPException(status_code=400, detail="Cannot lock an admin user")
    await db.execute(text("UPDATE users SET user_is_locked = TRUE WHERE user_id = :user_id"), {"user_id": user_id})
    await db.commit()
    return {"message": "User locked successfully"}

@router_admin.put("/user/{user_id}/unlock", response_model=MessageResponse)
async def unlock_user(user_id: str, current_user = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user.user_role == "admin":
        raise HTTPException(status_code=400, detail="Cannot unlock an admin user")
    await db.execute(text("UPDATE users SET user_is_locked = FALSE WHERE user_id = :user_id"), {"user_id": user_id})
    await db.commit()
    return {"message": "User unlocked successfully"}

@router_admin.delete("/user/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: str, current_user = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user.user_role == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete an admin user")
    await db.execute(text("DELETE FROM users WHERE user_id = :user_id"), {"user_id": user_id})
    await db.commit()
    return {"message": "User deleted successfully"}

@router_admin.get("/users", response_model=AdminGetAllUsersResponse)
async def get_all_users(
    current_user = Depends(require_admin), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return {
        "users": users
    }