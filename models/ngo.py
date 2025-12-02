from dataclasses import dataclass

@dataclass
class NGO:
    ngo_id: int
    org_name: str
    verified: bool
    registration_doc: str
    region: str
    contact_person: str
