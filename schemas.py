from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str] = None

class ContactResponse(ContactBase):
    id: int
    owner_id: Optional[int] = None # Це поле ми додамо для зв'язку

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserResponse(UserBase):
    id: int
    is_verified: bool
    avatar: str | None = None

    class Config:
        from_attributes = True

class TokenModel(BaseModel):
    access_token: str
    token_type: str

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72) # Додайте max_length
    