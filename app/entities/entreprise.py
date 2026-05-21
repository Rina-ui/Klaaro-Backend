from dataclasses import dataclass
from datetime import datetime


@dataclass
class Entreprise:
    id: str
    name: str
    email: str
    number: int
    location: str
    creation_date: datetime
