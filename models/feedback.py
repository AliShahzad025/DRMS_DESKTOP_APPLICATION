from dataclasses import dataclass
from datetime import datetime

@dataclass
class Feedback:
    feedback_id: int
    request_id: int
    victim_id: int
    rating: int
    comments: str
    created_at: datetime
