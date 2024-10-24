from collections import deque
from typing import Dict, List, Tuple
from common import DeliveryAgentInfo, Id, Parcel
from node import Node

SPEED = 1

"""

NOTE: DO NOT USE THIS FUNCTION
import Simulator from Simulator
Much Faster and Efficient

```python
from Simulator import Simulator
```


"""


# Returns the route between two nodes
# The route is list of nodes starting from the end node to the start node
# The end node is given as an Id
# TODO: A* algorithm can be implemented for a more efficient route finding
def get_route(start: Node, end: Id):
    # Create a queue for BFS and enqueue the starting node
    queue = deque([start])
    # Keep track of visited nodes and predecessors
    visited = {start.id}
    predecessor: Dict[int, Id | None] = {start.id: None}

    # BFS loop
    while queue:
        current = queue.popleft()

        # If the goal is reached, reconstruct and return the path
        if current.id == end:
            path = []
            curr = current.id
            while curr is not None:
                path.append(curr)
                curr = predecessor[curr]
            return path, current

        # Explore neighbors
        for neighbor in current.neighbours:
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                predecessor[neighbor.id] = current.id
                queue.append(neighbor)

    raise ValueError("No path found")


class Agent:
    def __init__(
        self,
        info: DeliveryAgentInfo,
        parcels_allocated: List[Id],
        all_parcels: List[Parcel],
        agent_starting_location: Node,
    ):
        self.info = info
        self.dist_travelled: float = 0
        self.progress: float = 0
        self.is_valid: bool = True

        # First element of parcels_allocated is the agent's starting location
        # Agents starting location should always be -1
        if parcels_allocated[0] != -1:
            self.is_valid = False
            return

        # Check if the same parcel is allocated to the agent multiple times
        for i, parcel_id in enumerate(parcels_allocated):
            # Except the -1 placeholder, which is used to indicate the warehouse
            if parcel_id == -1:
                continue

            for j, other_parcel in enumerate(parcels_allocated):
                # Ignore the same parcel being compared
                if i == j:
                    continue

                # If the same parcel is allocated to the agent multiple times
                if parcel_id == other_parcel:
                    self.is_valid = False
                    return

        num_parcels = 0

        parcels_to_deliver: List[Id] = []
        removed_parcels: List[Parcel] = []
        parcel_map = {parcel.id: parcel for parcel in all_parcels}

        for parcel_id in parcels_allocated:
            if parcel_id == -1:
                num_parcels = 0
                # The warehouse is the starting location
                parcels_to_deliver.append(0)
                continue

            num_parcels += 1
            # Check if the parcel allocation exceeds the agent's capacity
            if num_parcels > info.max_capacity:
                # Therefore the agent is invalid
                self.is_valid = False
                # Add the removed parcels back to the list of all parcels
                for parcel in removed_parcels:
                    all_parcels.append(parcel)
                return

            if parcel_id in parcel_map:
                parcels_to_deliver.append(parcel_map[parcel_id].location)
            else:
                # Parcel not found in the list of all parcels.
                # That means the parcel was allocated to another agent
                # Therefore the agent is invalid
                self.is_valid = False

                # Add the removed parcels back to the list of all parcels
                for parcel in removed_parcels:
                    all_parcels.append(parcel)
                return

            # Remove the parcel from the list of all parcels
            all_parcels.remove(parcel_map[parcel_id])
            removed_parcels.append(parcel_map[parcel_id])

        # To make the algorithm more efficient. Popping from the end is faster
        parcels_to_deliver.reverse()
        # Remove the warehouse
        parcels_to_deliver.pop()
        self.locations_to_visit = parcels_to_deliver
        self.parcels_delivered = 0

        # Check if the agent has at least one
        self.current_location = agent_starting_location

        self.running = True
        # Route is a list of node ids starting from the end node to the start node
        self.calculate_route()

        if self.running:
            # Account for [-1, -1, 0] case
            while len(self.route) == 0:
                if not self.calculate_route():
                    self.is_valid = False
                    return
            # Sets the current target to the correct node id to visit according to the route
            self.current_target: Id = self.route.pop()
            # Calculate the distance between the current location and the current target
            self.target_location: Node = self.current_location.find_immediate_from_id(
                self.current_target
            )  # type: ignore
            self.distance_to_target = self.current_location.simple_distance(
                self.target_location
            )

    def calculate_route(self) -> bool:
        # If there are no more parcels to deliver, the agent is done
        if len(self.locations_to_visit) == 0:
            self.running = False
            return False

        # The current parcel to deliver is the last element in the locations_to_visit list
        self.current_parcel_to_deliver = self.locations_to_visit.pop()

        # Get the route from the current location to the current parcel to deliver
        self.route = get_route(self.current_location, self.current_parcel_to_deliver)[0]

        # If the route does not start from the current location, the route is invalid
        if self.route[-1] != self.current_location.id:
            raise ValueError("Route does not start from the current location")

        # Remove the current location from the route
        self.current_target: Id = self.route.pop()
        return True

    def step(self) -> bool:
        # If the agent is invalid, the agent cannot move
        # If the agent is not running, the agent cannot move
        if not self.is_valid or not self.running:
            return False

        # If the agent has travelled the maximum distance, the agent cannot move
        # Make sure the agent does not travel more than the maximum distance
        if self.dist_travelled >= self.info.max_dist:
            self.dist_travelled = self.info.max_dist
            return False

        # If the agent has reached the current target
        if self.progress >= self.distance_to_target:
            # Update the current location and the progress
            self.current_location = self.target_location
            self.progress -= self.distance_to_target  # type: ignore

            while len(self.route) == 0:
                # As longs as the agent is not in the warehouse add one to the parcels delivered
                if self.current_location.id != 0:
                    self.parcels_delivered += 1
                # Calculate the next route
                if not self.calculate_route():
                    # If there are no more parcels to deliver, the agent is done
                    return False

            # Set the current target to the correct node id to visit according to the route
            self.current_target: Id = self.route.pop()
            # Calculate the distance between the current location and the current target
            self.target_location: Node = self.current_location.find_immediate_from_id(
                self.current_target
            )  # type: ignore
            self.distance_to_target = self.current_location.simple_distance(
                self.target_location
            )
        # Add the distance travelled and the progress according to the speed
        self.progress += SPEED
        self.dist_travelled += SPEED

        return True


class Simulator:
    def __init__(
        self,
        agent_allocation: Dict[DeliveryAgentInfo, List[Id]],
        parcels: List[Parcel],
        start: Node,
    ):
        # Create agents with the given agent allocation
        all_parcels = parcels.copy()
        self.agents = [
            Agent(info, agent_allocation[info], all_parcels, start)
            for info in agent_allocation
        ]

    def simulate(self) -> Tuple[int, float, int]:
        # Run the simulation until all agents have finished
        running = [agent.is_valid for agent in self.agents]
        while any(running):
            running = [agent.step() for agent in self.agents]

        total_distance = 0
        total_parcels = 0
        num_invalid_agents = 0

        # Calculate the total distance travelled and the total parcels delivered
        for agent in self.agents:
            if agent.is_valid:
                total_distance += agent.dist_travelled
                total_parcels += agent.parcels_delivered
            else:
                # If the agent is invalid, increment the number of invalid
                num_invalid_agents += 1

        return total_parcels, total_distance, num_invalid_agents
