from dataclasses import dataclass
from datetime import datetime

@dataclass
class Notification:
    notification_id: int
    message: str
    channel: str  # 'in_app','email','sms'
    recipient_user_id: int
    recipient_role: str  # 'Admin','NGO','Volunteer','Victim'
    created_at: datetime
    delivered_at: datetime
    status: str  # 'pending','sent','delivered','read','failed'
    meta: dict
