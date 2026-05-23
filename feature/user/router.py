from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from feature.auth.service import hash_password
from feature.user.service import get_current_user
from models.user import User
from database import get_db
from feature.user.schema import UserUpdate

router_user = APIRouter(prefix="/user", tags=["user"])

# region check current user
@router_user.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {"user_name": current_user.user_name,
            "user_email": current_user.user_email,
            "user_id": current_user.user_id,
            "user_role": current_user.user_role}
    

@router_user.put("/me")
async def update_current_user(user_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    update_data = user_data.model_dump(exclude_unset=True)

    if "user_email" in update_data and update_data["user_email"] != current_user.user_email:
        existing_email = (
            await db.execute(select(User).where(User.user_email == update_data["user_email"]))
        ).scalar_one_or_none()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

    if "user_name" in update_data and update_data["user_name"] != current_user.user_name:
        existing_username = (
            await db.execute(select(User).where(User.user_name == update_data["user_name"]))
        ).scalar_one_or_none()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")

    for key, value in update_data.items():
        if key == "password":
            current_user.user_hashedpassword = hash_password(value)
            continue
        if hasattr(current_user, key):
            setattr(current_user, key, value)
    await db.commit()
    return {"message": "User updated successfully"}



# endregion
