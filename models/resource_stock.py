from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResourceStock:
    resource_id: int
    resource_type_id: int
    donor_ngo: int
    quantity: int
    status: str  # 'available','reserved','low','out_of_stock'
    last_verified_by: int
    last_updated: datetime
    location: str
    latitude: float
    longitude: float
