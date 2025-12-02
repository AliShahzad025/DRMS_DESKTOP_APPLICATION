from dataclasses import dataclass
from datetime import datetime

@dataclass
class Report:
    report_id: int
    report_type: str
    parameters: dict
    generated_by: int
    generated_at: datetime
    file_path: str
