from typing import List, Mapping
import numpy as np
import importlib
import pkgutil

from common import DeliveryAgent, Parcel, Route
from graph import Graph, GraphOptions
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
    min_agents: int = 1,
    max_agents: int = 3,
    min_capacity: int = 5,
    max_capacity: int = 10,
    min_dist: float = 10,
    max_dist: float = 20,
):
    # Randomly generate number of agents
    no_agents = np.random.randint(min_agents, max_agents)

    # Randomly assign capacity and max distance to agents
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
    # Keep track of total distance and parcels
    total_distance = 0
    total_parcels = 0

    print("Individual Agent Results:")
    for agent, route in routes.items():
        # Display agent information
        print(f"Agent {agent.id}:")
        print(f"Agent Capacity: {agent.max_capacity}")
        print(f"Agent Max Distance: {agent.max_dist}")

        parcels = route.get_parcels()
        # Check if agent has exceeded capacity
        if len(parcels) > agent.max_capacity:
            raise Exception("Agent has exceeded capacity")

        # Display parcels carried by agent
        print(f"Agent is Carrying Parcels: {parcels}")
        distance = 0

        # Check if the route is valid
        if route.locations[0] != 0:
            raise Exception(f"Route for agent {agent.id} does not start at warehouse")
        if route.locations[-1] != 0:
            raise Exception(f"Route for agent {agent.id} does not end at warehouse")

        current_node: Graph = graph
        for loc, drop in zip(route.locations[1::], route.drops[1::]):
            # Checks if the route is valid
            travelling_to_node = current_node.find_immediate_from_id(loc)
            if travelling_to_node is None:
                raise Exception(f"Invalid route for agent {agent.id}")

            # Calculate distance travelled between nodes
            distance += np.sqrt(
                (current_node.x - travelling_to_node.x) ** 2
                + (current_node.y - travelling_to_node.y) ** 2
            )

            # Check if there is a drop
            if drop != -1:
                # Check if the drop is valid
                if Parcel(drop, travelling_to_node.id) not in parcels:
                    raise Exception(f"Agent {agent.id} has invalid drop")

                # Increment parcels delivered
                total_parcels += 1

            # Move to next node
            current_node = travelling_to_node

        # Calculate distance travelled by agent
        print(f"Agent travel distance: {distance}")
        total_distance += distance

    # Display total distance and parcels
    print()
    print(f"Total Parcels Delivered: {total_parcels}")
    print(f"Total Distance Travelled: {total_distance}")


if __name__ == "__main__":
    # Create graph
    graph = Graph(None, 0, 0, (0, 0, 0), 0)
    no_of_nodes = graph.create(GraphOptions())

    # Create parcels and agents
    np.random.seed(0)
    parcels = create_parcels(no_of_nodes)
    agents = create_agents()

    # Run all test algorithms in the folder test_algos
    for module_info in pkgutil.iter_modules(test_algos.__path__):  # type: ignore
        submodule = importlib.import_module(f"test_algos.{module_info.name}")

        # Check if the module has a model function
        if not hasattr(submodule, "model"):
            print(f"Module {module_info.name} does not have a model function")
            continue

        # Run the model function
        routes: Mapping[DeliveryAgent, Route] = submodule.model(graph, parcels, agents)

        # Display results
        print(f"Results for {module_info.name}:")
        display_results(graph, routes, parcels)
        print()
