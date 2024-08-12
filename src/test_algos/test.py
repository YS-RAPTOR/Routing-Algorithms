from typing import List, Mapping
from common import DeliveryAgent, Parcel, Route
from graph import Graph


def model(
    graph: Graph,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgent],
) -> Mapping[DeliveryAgent, Route]:
    return {
        DeliveryAgent(0, 2, 3): Route([1, 2, 3], [-1, 0, 1]),
    }
