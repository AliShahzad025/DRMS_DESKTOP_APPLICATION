from dataclasses import dataclass

@dataclass
class UrgencyWeight:
    urgency_level: str  # 'low','medium','high','critical'
    weight: int

