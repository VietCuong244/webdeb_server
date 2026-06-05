from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from feature.auth import service
from feature.user.service import require_admin
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .schema import UserSignUp
from feature.common.response import AuthRegisterResponse, TokenResponse, RootAdminResponse


router_auth = APIRouter(prefix="/auth", tags=["auth"])


# region User Registration
@router_auth.post("/rootadmin", response_model=RootAdminResponse)
async def create_root_admin(db: AsyncSession=Depends(get_db)):
    username = "admin"
    email = "admin@example.com"
    password = "admin123456"
    
    existing_admin = (await db.execute(select(User).where(User.user_email == email))).scalar_one_or_none()
    if existing_admin:
        return {
            "message": "Root admin user already exists!",
            "user_name": existing_admin.user_name,
            "user_email": existing_admin.user_email,
            "user_id": existing_admin.user_id,
        }

    new_admin = User(
        user_name=username,
        user_email=email,
        user_hashedpassword=service.hash_password(password),
        user_role="admin"
    )
    
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    
    return {
        "message": "Root admin user created successfully",
        "user_name": new_admin.user_name,
        "user_email": new_admin.user_email,
        "user_id": new_admin.user_id
    }


@router_auth.post("/newadmin", response_model=AuthRegisterResponse)
async def create_admin(admin_data: UserSignUp,current_user: User = Depends(require_admin), db: AsyncSession=Depends(get_db)):
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


@router_auth.post("/signup", response_model=AuthRegisterResponse)
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


@router_auth.post("/login", description="Using email and password to login", response_model=TokenResponse)
async def login(user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession=Depends(get_db)):
    # check user exist
    user = (await db.execute(select(User).where(User.user_email == user_data.username))).scalar()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not service.verify_password(user_data.password, user.user_hashedpassword):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if user.user_islocked:
        raise HTTPException(status_code=403, detail="Account is locked. Please contact support.")
    # create token
    access_token = service.create_access_token(data={"user_name":user.user_name,
                                                     "user_email":user.user_email,
                                                     "user_role":user.user_role})
    return {"access_token": access_token, "token_type": "bearer"}

# endregion 
