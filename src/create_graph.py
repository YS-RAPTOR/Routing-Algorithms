import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from typing_extensions import Self

SEED = 0

SPLIT_CHANCE = 0.25
END_CHANCE = 0.3

ROOT_SPLITS = 10
ROOT_ANGLE = 360

MAX_SPLIT = 3
MIN_SPLIT = 1

MIN_DIST = 1
MAX_DIST = 10

ANGLE_RANGE = 45


class Graph:
    def __init__(self, x: float, y: float, color: Tuple[float, float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.children = []

    def add_child(self, child: Self):
        self.children.append(child)


def create_branch(parent: Graph, dir: float, depth: int = 0):
    if np.random.rand() < END_CHANCE:
        return

    if np.random.rand() < SPLIT_CHANCE:
        splits = np.random.randint(MIN_SPLIT, MAX_SPLIT)
        for i in range(splits):
            angle = (np.random.randint(-ANGLE_RANGE, ANGLE_RANGE) + dir) % 360
            distance = np.random.randint(MIN_DIST, MAX_DIST)

            x = parent.x + np.cos(np.radians(angle)) * distance
            y = parent.y + np.sin(np.radians(angle)) * distance
            color = (
                parent.color
                if i == 0
                else (
                    np.random.rand(),
                    np.random.rand(),
                    np.random.rand(),
                )
            )

            branch = Graph(x, y, color)
            parent.add_child(branch)
            create_branch(branch, angle, depth + 1)
    else:
        angle = (np.random.randint(-ANGLE_RANGE, ANGLE_RANGE) + dir) % 360
        distance = np.random.randint(MIN_DIST, MAX_DIST)

        x = parent.x + np.cos(np.radians(angle)) * distance
        y = parent.y + np.sin(np.radians(angle)) * distance
        color = parent.color
        branch = Graph(x, y, color)
        parent.add_child(branch)
        create_branch(branch, angle, depth + 1)


def create_graph() -> Graph:
    root = Graph(0, 0, (0, 0, 0))
    np.random.seed(SEED)
    for _ in range(ROOT_SPLITS):
        angle = np.random.randint(0, ROOT_ANGLE)
        distance = np.random.randint(MIN_DIST, MAX_DIST)

        x = root.x + np.cos(np.radians(angle)) * distance
        y = root.y + np.sin(np.radians(angle)) * distance

        color = (
            np.random.rand(),
            np.random.rand(),
            np.random.rand(),
        )

        branch = Graph(x, y, color)
        root.add_child(branch)
        create_branch(branch, angle)

    return root


if __name__ == "__main__":
    graph = create_graph()
