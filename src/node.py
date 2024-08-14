from typing import Set, Tuple, List
from typing_extensions import Self
from dataclasses import dataclass
import numpy as np


@dataclass
class NodeOptions:
    seed: int = 0
    # Root options
    root_splits: int = 20
    # Splitting options
    turn_around_chance: float = 0.5
    split_chance: float = 0.2
    max_split: int = 4
    min_split: int = 1
    # Branch options
    min_dist: int = 20
    max_dist: int = 200
    angle_range: int = 75
    # Depth options
    min_depth: int = 3
    max_depth: int = 6
    # Merge options
    merge_distance: int = 30
    # Return options
    return_angle_range: int = 60


class Node:
    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        id: int,
    ):
        self.x = x
        self.y = y
        self.id = id
        self.color = color
        self.neighbours = []
        self.bbox = None

    def create(self, opts: NodeOptions) -> int:
        np.random.seed(opts.seed)
        no_of_nodes = 0

        for i in range(opts.root_splits):
            # Choose a random distance
            distance = np.random.randint(opts.min_dist, opts.max_dist)
            # Equally distribute the branches around the root node
            dir = i * 360 / opts.root_splits

            # Calculate the new position
            x = self.x + distance * np.cos(np.radians(dir))
            y = self.y + distance * np.sin(np.radians(dir))

            # Generate a random color
            color = (
                np.random.randint(0, 255),
                np.random.randint(0, 255),
                np.random.randint(0, 255),
            )

            # Create a new node
            no_of_nodes += 1
            node = Node(x, y, color, no_of_nodes)
            # Add the new node to the neighbours of the root node and vice versa
            node.__add_neighbours(self)

            # Create a branch
            no_of_nodes = node.__create_branch(dir, opts, 0, no_of_nodes, self)

        # Calculate the bounding box for the graph
        self.bbox = self.__find_bbox(set())
        # Return the number of nodes created. +1 is added to include the root node
        return no_of_nodes + 1

    def __add_neighbours(self, node: Self):
        if node not in self.neighbours:
            self.neighbours.append(node)

        if self not in node.neighbours:
            node.neighbours.append(self)

    def __create_branch(
        self,
        dir: float,
        opts: NodeOptions,
        depth: int,
        no_of_nodes: int,
        root: Self,
    ) -> int:
        if depth >= opts.max_depth or np.random.rand() < opts.turn_around_chance:
            if depth >= opts.min_depth:
                # Return to the root node
                current = self

                # Check if the distance between the current node and the root node is greater than the maximum distance
                while (
                    np.sqrt((current.x - root.x) ** 2 + (current.y - root.y) ** 2)
                    > opts.max_dist
                ):
                    distance = np.random.randint(opts.min_dist, opts.max_dist)
                    # Calculate the direction to the root node
                    dir = np.rad2deg(
                        np.arctan2((root.y - current.y), (root.x - current.x))
                    )
                    # Add some randomness to the direction
                    dir += np.random.randint(
                        -opts.return_angle_range, opts.return_angle_range
                    )

                    # Calculate the new position
                    x = current.x + distance * np.cos(np.radians(dir))
                    y = current.y + distance * np.sin(np.radians(dir))

                    # Create a new node
                    no_of_nodes += 1
                    new = Node(x, y, current.color, no_of_nodes)

                    # Add the new node to the neighbours of the current node
                    new.__add_neighbours(current)
                    current = new

                # Since the current node is now within the maximum distance from the root node, connect it to the root node
                root.__add_neighbours(current)  # type: ignore
                return no_of_nodes

        # Check if the current node should split
        if np.random.rand() < opts.split_chance:
            # Choose a random number of splits
            no_of_splits = np.random.randint(opts.min_split, opts.max_split)
            for i in range(no_of_splits):
                # Choose a random distance and direction
                distance = np.random.randint(opts.min_dist, opts.max_dist)
                dir += np.random.randint(-opts.angle_range, opts.angle_range)

                # Calculate the new position
                x = self.x + distance * np.cos(np.radians(dir))
                y = self.y + distance * np.sin(np.radians(dir))

                # Generate a random color. One of the branches will have the same color as the current node
                color = (
                    self.color
                    if i == 0
                    else (
                        np.random.randint(0, 255),
                        np.random.randint(0, 255),
                        np.random.randint(0, 255),
                    )
                )

                # Create a new node
                no_of_nodes += 1
                node = Node(x, y, color, no_of_nodes)
                node.__add_neighbours(self)

                # Create a branch
                no_of_nodes = node.__create_branch(
                    dir, opts, depth + 1, no_of_nodes, root
                )
            return no_of_nodes

        else:
            # Choose a random distance and direction
            distance = np.random.randint(opts.min_dist, opts.max_dist)
            dir += np.random.randint(-opts.angle_range, opts.angle_range)

            # Calculate the new position
            x = self.x + distance * np.cos(np.radians(dir))
            y = self.y + distance * np.sin(np.radians(dir))

            # Create a new node
            no_of_nodes += 1
            node = Node(x, y, self.color, no_of_nodes)
            node.__add_neighbours(self)

            return node.__create_branch(dir, opts, depth + 1, no_of_nodes, root)

    def __find_bbox(
        self, visited: Set[Self], rect: List[float] = [0, 0, 0, 0]
    ) -> List[float]:
        visited.add(self)
        # Find the bounding box for the graph
        for neighbour in self.neighbours:
            if neighbour in visited:
                continue
            rect = neighbour.__find_bbox(visited, rect)

            if neighbour.x < rect[0]:
                rect[0] = neighbour.x
            if neighbour.x > rect[2]:
                rect[2] = neighbour.x
            if neighbour.y < rect[1]:
                rect[1] = neighbour.y
            if neighbour.y > rect[3]:
                rect[3] = neighbour.y
        return rect

    def get_all_nodes(self, visited: Set[Self]) -> Set[Self]:
        visited.add(self)
        for neighbour in self.neighbours:
            if neighbour in visited:
                continue
            neighbour.get_all_nodes(visited)
        return visited

    def find_immediate_from_id(self, id: int) -> Self | None:
        # Find the immediate child or parent node that has the given id
        for neighbour in self.neighbours:
            if neighbour.id == id:
                return neighbour
        return None
