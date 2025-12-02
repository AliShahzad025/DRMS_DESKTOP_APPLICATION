from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    task_id: int
    title: str
    description: str
    task_type: str  # 'delivery','rescue','medical','assessment','other'
    status: str  # 'unassigned','assigned','in_progress','completed','cancelled'
    assigned_volunteer_id: int
    created_by: int
    related_request_id: int
    created_at: datetime
    updated_at: datetime
