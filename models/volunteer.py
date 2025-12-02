from dataclasses import dataclass
from datetime import datetime

@dataclass
class Volunteer:
    volunteer_id: int
    roles: str
    verified: bool
    status: str  # 'available','busy','inactive'
    last_active: datetime
