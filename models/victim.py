from dataclasses import dataclass

@dataclass
class Victim:
    victim_id: int
    verified_contact: bool
    vulnerability_notes: str
