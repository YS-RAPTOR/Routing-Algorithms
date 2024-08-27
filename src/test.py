from typing import List, Mapping
import numpy as np
import importlib
import pkgutil

from common import DeliveryAgentInfo, Parcel, Route
from node import Node, NodeOptions
from simulate import Agent, Simulator
import test_algos


def create_parcels(
    no_of_nodes: int,
    min_parcels: int = 20,
    max_parcels: int = 50,
):
    # Randomly generate number of parcels
    no_of_parcels = np.random.randint(min_parcels, max_parcels)

    # Randomly assign parcels to nodes
    return [Parcel(i, np.random.randint(1, no_of_nodes)) for i in range(no_of_parcels)]


def create_agents(
    min_agents: int = 3,
    max_agents: int = 5,
    min_capacity: int = 5,
    max_capacity: int = 10,
    min_dist: float = 5000,
    max_dist: float = 20000,
):
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


def print_info(agent: Agent):
    print(f" Agent {agent.info.id} is Valid - {agent.is_valid}")
    print(f" Agent Capacity: {agent.info.max_capacity}")
    print(f" Agent Max Distance: {agent.info.max_dist}")
    if agent.is_valid:
        print(f" Agent is Carrying Parcels: {agent.parcels_delivered}")
        print(f" Agent travel distance: {agent.dist_travelled}")


def display_results(
    node: Node, routes: Mapping[DeliveryAgentInfo, Route], parcels: List[Parcel]
):
    print(" Individual Agent Results:")
    print("-" * 79)

    allocations = {agent: route.get_allocation() for agent, route in routes.items()}
    simulator = Simulator(allocations, parcels, node)
    total_parcels, total_distance, num_invalid_agents = simulator.simulate()

    for agent in simulator.agents[:-1]:
        # Display agent information
        print_info(agent)
        print()
    print_info(simulator.agents[-1])

    # Display total distance and parcels
    print("-" * 79)
    print(" Total Results:")
    print("-" * 79)
    print(f" Total Parcels Delivered: {total_parcels}")
    print(f" Total Distance Travelled: {total_distance}")
    print(f" Number of Invalid Agents: {num_invalid_agents}")


if __name__ == "__main__":
    # Create graph
    root = Node(0, 0, (0, 0, 0), 0)
    no_of_nodes = root.create(NodeOptions())

    # Create parcels and agents
    np.random.seed(0)
    parcels = create_parcels(no_of_nodes)
    agents = create_agents()

    print("=" * 79)
    print(" Test Data:")
    print("-" * 79)
    print(f" Parcels: {len(parcels)}")
    print(f" Agents: {len(agents)}")


    # Run all test algorithms in the folder test_algos
    for module_info in pkgutil.iter_modules(test_algos.__path__):  # type: ignore
        submodule = importlib.import_module(f"test_algos.{module_info.name}")

        # Check if the module has a model function
        if not hasattr(submodule, "model"):
            print(f" Module {module_info.name} does not have a model function")
            continue

        # Run the model function
        routes: Mapping[DeliveryAgentInfo, Route] = submodule.model(
            root, parcels, agents
        )

        # Display results
        print("=" * 79)
        print(f" Results for {module_info.name}:")
        print("-" * 79)
        display_results(root, routes, parcels)
        print()
