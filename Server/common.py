from dataclasses import dataclass
from typing import List

import numpy as np

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


def create_parcels(
    no_of_nodes: int,
    seed: int = 0,
    min_parcels: int = 20,
    max_parcels: int = 50,
):
    np.random.seed(seed)
    # Randomly generate number of parcels
    no_of_parcels = np.random.randint(min_parcels, max_parcels)

    # Randomly assign parcels to nodes
    return [Parcel(i, np.random.randint(1, no_of_nodes)) for i in range(no_of_parcels)]


def create_agents(
    seed: int = 0,
    min_agents: int = 3,
    max_agents: int = 5,
    min_capacity: int = 5,
    max_capacity: int = 10,
    min_dist: float = 500,
    max_dist: float = 5000,
):
    np.random.seed(seed)
    # Randomly generate number of agents
    no_agents = np.random.randint(min_agents, max_agents)

    # Randomly assign capacity and max distance to agents
    return [
        DeliveryAgentInfo(
            i,
            np.random.randint(min_capacity, max_capacity),
            np.random.uniform(min_dist, max_dist),
        )
        for i in range(no_agents)
    ]
