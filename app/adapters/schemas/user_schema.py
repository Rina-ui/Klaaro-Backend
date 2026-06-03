from pydantic import BaseModel, ConfigDict

from app.entities.enum.account_type import AccountType
from app.entities.enum.role import Role


class UserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str
    profession: str
    role: Role
    account_type: AccountType

class UserResponse(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: str
    profession: str
    role: Role
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