from typing import List, Mapping
import numpy as np
import importlib
import pkgutil

from common import DeliveryAgent, Parcel, Route
from graph import Graph, GraphOptions
import test_algos


def create_parcels(
    no_of_nodes: int,
    seed: int = 0,
    min_parcels: int = 20,
    max_parcels: int = 50,
):
    np.random.seed(seed)
    no_of_parcels = np.random.randint(min_parcels, max_parcels)
    return [Parcel(i, np.random.randint(1, no_of_nodes)) for i in range(no_of_parcels)]


def create_agents(
    seed: int = 0,
    min_agents: int = 1,
    max_agents: int = 3,
    min_capacity: int = 5,
    max_capacity: int = 10,
    min_dist: float = 10,
    max_dist: float = 20,
):
    np.random.seed(seed)
    no_agents = np.random.randint(min_agents, max_agents)
    return [
        DeliveryAgent(
            i,
            np.random.randint(min_capacity, max_capacity),
            np.random.uniform(min_dist, max_dist),
        )
        for i in range(no_agents)
    ]


def display_results(
    graph: Graph, routes: Mapping[DeliveryAgent, Route], parcels: List[Parcel]
):
    total_distance = 0
    total_parcels = 0

    print("Individual Agent Results:")
    for agent, route in routes.items():
        # Check basic constraints
        print(f"Agent {agent.id}:")
        print(f"Agent Capacity: {agent.max_capacity}")
        print(f"Agent Max Distance: {agent.max_dist}")

        parcels = route.get_parcels()
        if len(parcels) > agent.max_capacity:
            raise Exception("Agent has exceeded capacity")
        print(f"Agent is Carrying Parcels: {parcels}")
        distance = 0

        current_node: Graph = graph
        for loc, drop in zip(route.locations, route.drops):
            travelling_to_node = current_node.find_immediate_from_id(loc)
            if travelling_to_node is None:
                raise Exception(f"Invalid route for agent {agent.id}")
            distance += np.sqrt(
                (current_node.x - travelling_to_node.x) ** 2
                + (current_node.y - travelling_to_node.y) ** 2
            )
            if drop != -1:
                if Parcel(drop, travelling_to_node.id) not in parcels:
                    raise Exception(f"Agent {agent.id} has invalid drop")
                total_parcels += 1
            current_node = travelling_to_node

        print(f"Agent travel distance: {distance}")
        total_distance += distance

    print()
    print(f"Total Parcels Delivered: {total_parcels}")
    print(f"Total Distance Travelled: {total_distance}")


if __name__ == "__main__":
    graph = Graph(None, 0, 0, (0, 0, 0), 0)
    no_of_nodes = graph.create(GraphOptions())
    parcels = create_parcels(no_of_nodes)
    agents = create_agents()

    for module_info in pkgutil.iter_modules(test_algos.__path__):  # type: ignore
        submodule = importlib.import_module(f"test_algos.{module_info.name}")
        if not hasattr(submodule, "model"):
            print(f"Module {module_info.name} does not have a model function")
            continue

        routes: Mapping[DeliveryAgent, Route] = submodule.model(graph, parcels, agents)
        print(f"Results for {module_info.name}:")
        display_results(graph, routes, parcels)
        print()
