import numpy as np
from typing import Tuple, List
from typing_extensions import Self
import tkinter as tk

SEED = 0

SPLIT_CHANCE = 0.25
END_CHANCE = 0.3

ROOT_SPLITS = 25
ROOT_ANGLE = 360

MAX_SPLIT = 3
MIN_SPLIT = 1

MIN_DIST = 10
MAX_DIST = 100

ANGLE_RANGE = 45


class Graph:
    def __init__(self, x: float, y: float, color: Tuple[float, float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.children = []

    def add_child(self, child: Self):
        self.children.append(child)

    def find_bbox(self, rect: List[float] = [0, 0, 0, 0]) -> List[float]:
        for child in self.children:
            rect = child.find_bbox(rect)

            if child.x < rect[0]:
                rect[0] = child.x
            if child.x > rect[2]:
                rect[2] = child.x
            if child.y < rect[1]:
                rect[1] = child.y
            if child.y > rect[3]:
                rect[3] = child.y
        return rect

    def display(self):
        disp = tk.Tk()
        disp.title("Path")

        bbox = self.find_bbox()
        canvas_width = (bbox[2] - bbox[0]) * 1.25
        canvas_height = (bbox[3] - bbox[1]) * 1.25

        canvas = tk.Canvas(disp, width=canvas_width, height=canvas_height)
        canvas.pack()

        # Draw root
        center = (
            canvas_width / 2,
            canvas_height / 2,
        )
        self.__display_recursive(canvas, center, center)
        self.__draw_node(canvas, center)

        disp.mainloop()

    def __color_str(self) -> str:
        return "#{0:02x}{1:02x}{2:02x}".format(
            int(self.color[0] * 255), int(self.color[1] * 255), int(self.color[2] * 255)
        )

    def __draw_node(self, canvas: tk.Canvas, loc: Tuple[float, float]):
        canvas.create_oval(
            loc[0] - 5,
            loc[1] - 5,
            loc[0] + 5,
            loc[1] + 5,
            fill=self.__color_str(),
        )

    def __display_recursive(
        self,
        canvas: tk.Canvas,
        prev_loc: Tuple[float, float],
        center: Tuple[float, float],
    ):
        loc = (center[0] + self.x, center[1] + self.y)
        canvas.create_line(prev_loc, loc, fill=self.__color_str())
        for child in self.children:
            child.__display_recursive(canvas, loc, center)
        self.__draw_node(canvas, loc)


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
    graph.display()
