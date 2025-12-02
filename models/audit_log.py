from dataclasses import dataclass
from datetime import datetime

@dataclass
class AuditLog:
    log_id: int
    actor_user_id: int
    action: str
    target_table: str
    target_id: str
    details: dict
    logged_at: datetime
