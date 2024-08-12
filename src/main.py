from dataclasses import dataclass
from typing import List, Mapping

type Location = int
type Route = List[Location]


@dataclass
class DeliveryAgent:
    id: int
    capacity: int
    max_dist: float


@dataclass
class Parcel:
    id: int
    location: Location


def model(
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgent],
) -> Mapping[DeliveryAgent, Route]:
    return {}
