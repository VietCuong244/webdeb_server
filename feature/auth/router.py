from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from feature.auth import service
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .schema import UserSignUp
from feature.auth.service import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# region User Registration
@router.post("/newadmin")
async def create_admin(admin_data: UserSignUp, db: AsyncSession=Depends(get_db)):
    # check existing mail n user
    existing_email = (await db.execute(select(User).where(User.user_email == admin_data.email))).scalar()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    existing_username = (await db.execute(select(User).where(User.user_name == admin_data.username))).scalar()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # import to db
    hashed_password = service.hash_password(admin_data.password)
    new_admin = User(
        user_name=admin_data.username,
        user_email=admin_data.email,
        user_hashedpassword=hashed_password,
        user_role="admin"
    )
    db.add(new_admin)
    await db.commit()
    return {"message": "Admin user created successfully",
            "user_name": new_admin.user_name,
            "user_email": new_admin.user_email,
            "user_id": new_admin.user_id,
            "user_role": new_admin.user_role}


@router.post("/signup")
async def signup(user_data: UserSignUp, db: AsyncSession=Depends(get_db)):
    
    # check existing mail n user
    existing_email = (await db.execute(select(User).where(User.user_email == user_data.email))).scalar()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    existing_username = (await db.execute(select(User).where(User.user_name == user_data.username))).scalar()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # import to db
    hashed_password = service.hash_password(user_data.password)
    new_user = User(
        user_name=user_data.username,
        user_email=user_data.email,
        user_hashedpassword=hashed_password
    )
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully",
            "user_name": new_user.user_name,
            "user_email": new_user.user_email,
            "user_id": new_user.user_id}

# endregion

# region User Login


@router.post("/login", description="Using email and password to login")
async def login(user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession=Depends(get_db)):
    
    {
    "username": "user_email",
    "password": "user_password"
    }
    # check user exist
    user = (await db.execute(select(User).where(User.user_email == user_data.username))).scalar()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not service.verify_password(user_data.password, user.user_hashedpassword):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    # create token
    access_token = service.create_access_token(data={"user_name":user.user_name,
                                                     "user_email":user.user_email,
                                                     "user_role":user.user_role})
    return {"access_token": access_token, "token_type": "bearer"}
# endregion

# region check current user
@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {"user_name": current_user.user_name,
            "user_email": current_user.user_email,
            "user_id": current_user.user_id,
            "user_role": current_user.user_role}
# endregion