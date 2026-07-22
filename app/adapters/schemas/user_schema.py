from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from app.entities.enum.account_type import AccountType

class UserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str = Field(..., min_length=8, description="Le mot de passe doit contenir au moins 8 caractères")
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
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)

class UpdateAlertePreferencesRequest(BaseModel):
    alerte_frequence: str
    alerte_colonne_cible: str