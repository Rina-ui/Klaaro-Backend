from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from app.entities.enum.account_type import AccountType

class UserRequest(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    profession: str
    account_type: AccountType
    role: str = "user"

class UserResponse(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: str
    profession: str
    role: Optional[str] = "user"
    account_type: AccountType

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)