from dataclasses import dataclass
from datetime import datetime

@dataclass
class SOSRequest:
    request_id: int
    victim_id: int
    location: str
    latitude: float
    longitude: float
    type_of_need: str
    description: str
    urgency_level: str  # 'low','medium','high','critical'
    status: str
    priority_score: int
    created_at: datetime
    updated_at: datetime
    assigned_volunteer_id: int
    assigned_ngo: int
