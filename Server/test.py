from typing import Dict
import numpy as np
import importlib
import pkgutil

from common import DeliveryAgentInfo, Route, create_agents, create_parcels
from node import Node, NodeOptions
from Simulator import Simulator
import Algos


import cProfile
import pstats
import time

DEBUG = True
CHECK_PERFORMANCE = False


def print_info(agent: DeliveryAgentInfo, allocation, results):
    print(f" Agent {agent.id} is Valid - {results[0]}")
    print(f" Agent Capacity: {agent.max_capacity}")
    print(f" Agent Max Distance: {agent.max_dist}")
    if results[0]:
        print(f" Agent is Carrying Parcels: {results[1]}")
        print(f" Agent travel distance: {results[2]}")
    print(f" Agent Allocation: {allocation}")


def display_results(
    simulator: Simulator,
    routes: Dict[DeliveryAgentInfo, Route],
):
    print(" Individual Agent Results:")
    print("-" * 79)

    allocations = [{agent: route.get_allocation() for agent, route in routes.items()}]

    _, total_parcels, total_distance = simulator.simulate(allocations)[0]
    num_invalid_agents = 0

    agent_results = simulator.get_agent_results(0)
    agents = list(routes.keys())
    for results, agent in zip(agent_results[:-1], agents[:-1]):
        # Display agent information
        print_info(agent, routes[agent].get_allocation(), results)
        print()

    print_info(agents[-1], routes[agents[-1]].get_allocation(), agent_results[-1])

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
    simulator = Simulator(root, parcels)

    print("=" * 79)
    print(" Test Data:")
    print("-" * 79)
    print(f" Parcels: {len(parcels)}")
    print(f" Agents: {len(agents)}")
    print(f" Nodes: {no_of_nodes}")

    # Run all test algorithms in the folder test_algos
    for module_info in pkgutil.iter_modules(Algos.__path__):  # type: ignore
        submodule = importlib.import_module(f"test_algos.{module_info.name}")

        # Check if the module has a model function
        if not hasattr(submodule, "model"):
            print(f" Module {module_info.name} does not have a model function")
            continue

        # Run the model function
        if CHECK_PERFORMANCE:
            with cProfile.Profile() as pr:
                routes: Dict[DeliveryAgentInfo, Route] = submodule.model(
                    root, parcels, agents, DEBUG
                )
            stats = pstats.Stats(pr)
            stats.strip_dirs()
            import os

            os.makedirs("profiling", exist_ok=True)
            stats.dump_stats(f"profiling/{module_info.name}-{time.time()}.prof")
        else:
            routes: Dict[DeliveryAgentInfo, Route] = submodule.model(
                root, parcels, agents, DEBUG
            )

        # Display results
        print("=" * 79)
        print(f" Results for {module_info.name}:")
        print("-" * 79)
        display_results(simulator, routes)
        print()
