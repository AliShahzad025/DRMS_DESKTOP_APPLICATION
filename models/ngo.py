from dataclasses import dataclass

@dataclass
class NGO:
    ngo_id: int
    org_name: str
    verified: bool
    can_manage_resources: bool = False
    registration_doc: str
    region: str
    contact_person: str
