from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserSignUp(BaseModel):
    username: str
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="Password must be between 8 and 128 characters, and include at least one letter and one number."
    )
    email: EmailStr

    # Viết hàm Validator riêng cho password bằng thư viện re của Python
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        # 1. Kiểm tra xem có chứa ít nhất 1 chữ cái không
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái.")
        
        # 2. Kiểm tra xem có chứa ít nhất 1 chữ số không
        if not re.search(r"\d", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ số.")
        
        # 3. Kiểm tra cấm dấu cách (space) nếu bạn muốn thắt chặt
        if " " in value:
            raise ValueError("Mật khẩu không được chứa khoảng trắng.")
            
        return value

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id : Optional[int] = None
    user_name: str | None = None
    user_email: str | None = None
    user_role: str | None = None
    