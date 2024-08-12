from typing import Tuple, List
from typing_extensions import Self
from dataclasses import dataclass
import numpy as np


@dataclass
class GraphOptions:
    seed: int = 1
    # Root options
    root_splits: int = 25
    root_angle: int = 360
    # Splitting options
    end_chance: float = 0.35
    split_chance: float = 0.6
    max_split: int = 3
    min_split: int = 1
    # Branch options
    min_dist: int = 10
    max_dist: int = 100
    angle_range: int = 45
    # Depth options
    min_depth: int = 3
    max_depth: int = 6


class Graph:
    def __init__(
        self,
        parent: Self | None,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        id: int,
    ):
        self.x = x
        self.y = y
        self.id = id
        self.color = color
        self.parent = parent
        self.children = []
        self.bbox = None

    def create(self, opts: GraphOptions) -> int:
        np.random.seed(opts.seed)
        no_of_nodes = 0
        for _ in range(opts.root_splits):
            angle = np.random.randint(0, opts.root_angle)
            distance = np.random.randint(opts.min_dist, opts.max_dist)

            x = self.x + np.cos(np.radians(angle)) * distance
            y = self.y + np.sin(np.radians(angle)) * distance

            color = (
                np.random.randint(0, 255),
                np.random.randint(0, 255),
                np.random.randint(0, 255),
            )

            no_of_nodes += 1
            branch = Graph(self, x, y, color, no_of_nodes)
            self.children.append(branch)
            no_of_nodes = branch.__create_branch(angle, opts, 1, no_of_nodes)

        self.bbox = self.__find_bbox()
        return no_of_nodes + 1

    def find_immediate_from_id(self, id: int) -> Self | None:
        if self.parent is not None and self.parent.id == id:
            return self.parent
        for child in self.children:
            if child.id == id:
                return child
        return None

    def __create_branch(
        self, dir: float, opts: GraphOptions, depth: int, no_of_nodes: int
    ) -> int:
        if np.random.rand() < opts.end_chance or depth >= opts.max_depth:
            if depth >= opts.min_depth:
                return no_of_nodes

        if np.random.rand() < opts.split_chance:
            splits = np.random.randint(opts.min_split, opts.max_split)
            for i in range(splits):
                angle = (
                    np.random.randint(-opts.angle_range, opts.angle_range) + dir
                ) % 360
                distance = np.random.randint(opts.min_dist, opts.max_dist)

                x = self.x + np.cos(np.radians(angle)) * distance
                y = self.y + np.sin(np.radians(angle)) * distance
                color = (
                    self.color
                    if i == 0
                    else (
                        np.random.randint(0, 255),
                        np.random.randint(0, 255),
                        np.random.randint(0, 255),
                    )
                )

                no_of_nodes += 1
                branch = Graph(self, x, y, color, no_of_nodes)
                self.children.append(branch)
                no_of_nodes = branch.__create_branch(
                    angle, opts, depth + 1, no_of_nodes
                )
            return no_of_nodes
        else:
            angle = (np.random.randint(-opts.angle_range, opts.angle_range) + dir) % 360
            distance = np.random.randint(opts.min_dist, opts.max_dist)

            x = self.x + np.cos(np.radians(angle)) * distance
            y = self.y + np.sin(np.radians(angle)) * distance
            color = self.color
            no_of_nodes += 1
            branch = Graph(self, x, y, color, no_of_nodes)
            self.children.append(branch)
            return branch.__create_branch(angle, opts, depth + 1, no_of_nodes)

    def __find_bbox(self, rect: List[float] = [0, 0, 0, 0]) -> List[float]:
        for child in self.children:
            rect = child.__find_bbox(rect)

            if child.x < rect[0]:
                rect[0] = child.x
            if child.x > rect[2]:
                rect[2] = child.x
            if child.y < rect[1]:
                rect[1] = child.y
            if child.y > rect[3]:
                rect[3] = child.y
        return rect
