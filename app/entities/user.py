from dataclasses import dataclass

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