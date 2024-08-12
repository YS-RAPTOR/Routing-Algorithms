from dataclasses import dataclass
from typing import List

Location = int


class Route:
    def __init__(self, parcels: List[int], distance: float):
        self.parcels = parcels
        self.distance = distance


@dataclass
class DeliveryAgent:
    id: int
    capacity: int
    max_dist: float


@dataclass
class Parcel:
    id: int
    location: Location
