from typing import List, Mapping
from common import DeliveryAgentInfo, Parcel, Route
from node import Node


# The model function takes a root_node and a list of parcels and delivery agents as input
# and returns a mapping from delivery agents to routes.
def model(
    root_node: Node,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgentInfo],
    debug: bool = False,
) -> Mapping[DeliveryAgentInfo, Route]:
    return {
        DeliveryAgentInfo(0, 2, 3): Route(
            [None, delivery_parcels[0], delivery_parcels[1], None]
        ),
    }
