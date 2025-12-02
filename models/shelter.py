from dataclasses import dataclass

@dataclass
class Shelter:
    shelter_id: int
    name: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int
    contact: str

