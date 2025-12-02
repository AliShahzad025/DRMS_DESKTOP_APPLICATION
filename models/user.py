from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    user_id: int
    name: str
    email: str
    phone: str
    location: str
    latitude: float
    longitude: float
    language: str
    role: str  # 'Admin', 'NGO', 'Volunteer', 'Victim'
    password_hash: str
    created_at: datetime
    updated_at: datetime
