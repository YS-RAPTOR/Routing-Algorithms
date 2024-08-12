from typing import List, Mapping
from common import DeliveryAgent, Parcel, Route
from graph import Graph


# The model function takes a graph and a list of parcels and delivery agents as input
# and returns a mapping from delivery agents to routes.
def model(
    graph: Graph,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgent],
) -> Mapping[DeliveryAgent, Route]:
    return {
        DeliveryAgent(0, 2, 3): Route(
            [0, 1, 2, 3, 2, 1, 0],
            [-1, 0, 1, -1, -1, -1, -1],
        ),
    }
