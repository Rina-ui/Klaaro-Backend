from dataclasses import dataclass
from datetime import datetime

@dataclass
class Rapport:
    id: str
    type: str
    content: str
    periode: str
    date_generation: datetime
    user_id: str