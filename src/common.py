from dataclasses import dataclass
from typing import List

# Type aliases for location. Location is the same as the id of a root node.
Location = int


@dataclass
class DeliveryAgent:
    # Id of the agent
    id: int
    # Maximum number of parcels the agent can carry
    max_capacity: int
    # Maximum distance the agent can travel
    max_dist: float

    def __hash__(self):
        return hash(self.id)


@dataclass
class Parcel:
    # Id of the parcel
    id: int
    # Location where the parcel will be delivered to
    location: Location


class Route:
    def __init__(self, locations: List[Location], drops: List[int]):
        if len(locations) != len(drops):
            raise ValueError("Length of locations and drops must be the same")

        # List of locations the agent will visit in the order as they appear in the list
        self.locations = locations
        # Each location either has the Id of the parcel to be dropped at that location or -1 if no parcel is to be dropped
        self.drops = drops

    def get_parcels(self) -> List[Parcel]:
        parcels = []
        for loc, drop in zip(self.locations, self.drops):
            if drop != -1:
                parcels.append(Parcel(drop, loc))
        return parcels
