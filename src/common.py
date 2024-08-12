from dataclasses import dataclass
from typing import List

Location = int
Id = int


@dataclass
class DeliveryAgent:
    id: Id
    max_capacity: int
    max_dist: float

    def __hash__(self):
        return hash(self.id)


@dataclass
class Parcel:
    id: Id
    location: Location


@dataclass
class Route:
    locations: List[Location]
    drops: List[Id]

    def get_parcels(self) -> List[Parcel]:
        parcels = []
        for loc, drop in zip(self.locations, self.drops):
            if drop != -1:
                parcels.append(Parcel(drop, loc))
        return parcels
