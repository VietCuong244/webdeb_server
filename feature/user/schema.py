from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    user_name: str
    user_email: EmailStr
    password: str

class UserUpdate(UserBase):
    user_name: Optional[str] = None
    user_email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserAvatar(BaseModel):
    user_name: str
    user_avatar: Optional[str] = None