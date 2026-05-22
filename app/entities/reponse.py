from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reponse:
    id: str
    type: str
    content: str
    received_at: datetime
    received_by: str