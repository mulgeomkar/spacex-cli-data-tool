from dataclasses import dataclass
from typing import Optional

@dataclass
class Launch:
    id: str
    flight_number: int
    name: str
    date_utc: str
    success: Optional[bool]
    details: Optional[str]
    rocket: str
    launchpad: str

    @classmethod
    def from_api_data(cls, data: dict):
        return cls(
            id=data['id'],
            flight_number=data['flight_number'],
            name=data['name'],
            date_utc=data['date_utc'],
            success=data.get('success'),
            details=data.get('details'),
            rocket=data['rocket']['name'] if isinstance(data['rocket'], dict) and 'name' in data['rocket'] else data['rocket'],
            launchpad=data['launchpad']['name'] if isinstance(data['launchpad'], dict) and 'name' in data['launchpad'] else data['launchpad'],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "flight_number": self.flight_number,
            "name": self.name,
            "date_utc": self.date_utc,
            "success": self.success,
            "details": self.details,
            "rocket": self.rocket,
            "launchpad": self.launchpad,
        }
