from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.Status import Status


@dataclass
class Decision:
    id: str
    content: str
    description: str
    status: Status
    date: datetime