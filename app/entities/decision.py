from dataclasses import dataclass
from datetime import datetime


@dataclass
class Decision:
    id: str
    content: str
    description: str
    status: str
    date: datetime