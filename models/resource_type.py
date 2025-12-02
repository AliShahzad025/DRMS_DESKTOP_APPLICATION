from dataclasses import dataclass

@dataclass
class ResourceType:
    resource_type_id: int
    name: str
    unit: str
    description: str

