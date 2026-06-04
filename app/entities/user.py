from dataclasses import dataclass
from typing import Optional

from app.entities.enum.account_type import AccountType
from app.entities.enum.role import Role


@dataclass
class User:
    id: str
    lastname: str
    firstname: str
    email: str
    password: str
    profession: str
    role: Role
    account_type: AccountType
    entreprise_id: Optional[str] = None