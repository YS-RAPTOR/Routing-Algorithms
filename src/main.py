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


def display_results(graph: Graph, routes: Mapping[DeliveryAgent, Route]):
    pass


if __name__ == "__main__":
    graph = Graph(0, 0, (0, 0, 0), 0)
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
        display_results(graph, routes)
        print()
