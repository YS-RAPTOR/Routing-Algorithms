from typing import List, Mapping
from common import DeliveryAgent, Parcel, Route
from graph import Graph


def model(
    graph: Graph,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgent],
) -> Mapping[DeliveryAgent, Route]:
    return {}
