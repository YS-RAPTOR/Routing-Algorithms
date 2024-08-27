from dataclasses import dataclass
from typing import List

# Type aliases for location. Location is the same as the id of a root node.
Location = int
Id = int


@dataclass
class DeliveryAgentInfo:
    # Id of the agent
    id: Id
    # Maximum number of parcels the agent can carry
    max_capacity: int
    # Maximum distance the agent can travel
    max_dist: float

    def __hash__(self):
        return hash(self.id)


@dataclass
class Parcel:
    # Id of the parcel
    id: Id
    # Location where the parcel will be delivered to
    location: Location


@dataclass
class Route:
    route: List[Parcel | None]

    def get_allocation(self) -> List[Id]:
        return [-1 if parcel is None else parcel.id for parcel in self.route]
