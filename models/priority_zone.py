from dataclasses import dataclass

@dataclass
class PriorityZone:
    zone_id: int
    name: str
    description: str
    center_lat: float
    center_long: float
    radius_km: float
    priority_level: str  # 'low', 'medium', 'high'
