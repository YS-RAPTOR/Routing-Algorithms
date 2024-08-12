from typing import Tuple, List
from dataclasses import dataclass

import numpy as np
import pygame


@dataclass
class Options:
    # NOTE: Generation options

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

    # NOTE: Display options

    window_name: str = "Graph"
    display_width: int = 1000
    display_height: int = 1000
    fps: int = 60

    # Graph Rendering options
    node_radius: int = 4
    line_width: int = 2

    # NOTE: User input options
    move_speed: int = 10
    scroll_speed: float = 1.1


class Graph:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], id: int = 0):
        self.x = x
        self.y = y
        self.id = id
        self.color = color
        self.children = []
        self.bbox = None

    def create(self, opts: Options):
        np.random.seed(opts.seed)
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

            branch = Graph(x, y, color)
            self.children.append(branch)
            branch.__create_branch(angle, opts, 1)

        self.bbox = self.__find_bbox()

    def __create_branch(self, dir: float, opts: Options, depth: int):
        if np.random.rand() < opts.end_chance or depth >= opts.max_depth:
            if depth >= opts.min_depth:
                return

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

                branch = Graph(x, y, color)
                self.children.append(branch)
                branch.__create_branch(angle, opts, depth + 1)
        else:
            angle = (np.random.randint(-opts.angle_range, opts.angle_range) + dir) % 360
            distance = np.random.randint(opts.min_dist, opts.max_dist)

            x = self.x + np.cos(np.radians(angle)) * distance
            y = self.y + np.sin(np.radians(angle)) * distance
            color = self.color
            branch = Graph(x, y, color)
            self.children.append(branch)
            branch.__create_branch(angle, opts, depth + 1)

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

    def draw(
        self,
        surface: pygame.Surface,
        offset: Tuple[int, int],
        zoom: float,
        opts: Options,
    ):
        for child in self.children:
            pygame.draw.aaline(
                surface,
                child.color,
                (int(self.x * zoom + offset[0]), int(self.y * zoom + offset[1])),
                (int(child.x * zoom + offset[0]), int(child.y * zoom + offset[1])),
                max(opts.line_width, int(zoom * opts.line_width)),
            )
            child.draw(surface, offset, zoom, opts)
            pygame.draw.circle(
                surface,
                child.color,
                (int(child.x * zoom + offset[0]), int(child.y * zoom + offset[1])),
                max(opts.node_radius, int(zoom * opts.node_radius)),
            )
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x * zoom + offset[0]), int(self.y * zoom + offset[1])),
            max(opts.node_radius, int(zoom * opts.node_radius)),
        )


class DrawGraph:
    def __init__(self, graph: Graph, offset: Tuple[float, float], zoom: float | None):
        self.graph = graph
        self.offset = offset
        self.zoom = zoom
        self.surface = pygame.Surface(
            (
                (self.graph.bbox[2] - self.graph.bbox[0]) * 1.25,  # type: ignore
                (self.graph.bbox[3] - self.graph.bbox[1]) * 1.25,  # type: ignore
            )
        )

    def zoom_to_fit(self, opts: Options) -> float:
        width = opts.display_width
        height = opts.display_height

        x_scale = width / (self.graph.bbox[2] - self.graph.bbox[0])  # type: ignore
        y_scale = height / (self.graph.bbox[3] - self.graph.bbox[1])  # type: ignore
        return min(x_scale, y_scale)

    def update(self, opts: Options):
        zoom = self.zoom_to_fit(opts) if self.zoom is None else self.zoom
        zoom *= 0.92 - (0.01 * opts.node_radius)
        self.surface = pygame.Surface((opts.display_width, opts.display_height))
        self.surface.fill((255, 255, 255))
        graph.draw(
            self.surface,
            (int(self.offset[0]), int(self.offset[1])),
            zoom,
            opts,
        )


if __name__ == "__main__":
    opts = Options()
    graph = Graph(0, 0, (0, 0, 0))
    graph.create(opts)

    draw_graph = DrawGraph(
        graph, (opts.display_width // 2, opts.display_height // 2), None
    )
    draw_graph.update(opts)

    pygame.init()
    screen = pygame.display.set_mode((opts.display_width, opts.display_height))
    pygame.display.set_caption(opts.window_name)
    pygame.key.set_repeat(1, 1)

    clock = pygame.time.Clock()

    running = True
    delta = 1 / opts.fps

    initial_mouse_pos = np.zeros(2)
    initial_offset = (0, 0)
    is_dragging = False

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                    break

            if event.type == pygame.VIDEORESIZE:
                opts.display_width = event.w
                opts.display_height = event.h

            if event.type == pygame.MOUSEWHEEL:
                if draw_graph.zoom is None:
                    draw_graph.zoom = draw_graph.zoom_to_fit(opts)

                old_zoom = draw_graph.zoom

                if event.y > 0:
                    draw_graph.zoom *= opts.scroll_speed
                elif event.y < 0:
                    draw_graph.zoom /= opts.scroll_speed

                mx, my = pygame.mouse.get_pos()
                draw_graph.offset = (
                    mx - (mx - draw_graph.offset[0]) * (draw_graph.zoom / old_zoom),  # type: ignore
                    my - (my - draw_graph.offset[1]) * (draw_graph.zoom / old_zoom),  # type: ignore
                )

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    draw_graph.zoom = None
                    draw_graph.offset = (
                        opts.display_width // 2,
                        opts.display_height // 2,
                    )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not is_dragging:
                        initial_mouse_pos = np.array(pygame.mouse.get_pos())
                        initial_mouse_pos -= np.array(
                            (opts.display_width, opts.display_height)
                        )
                        initial_mouse_pos = (initial_mouse_pos - 0.5) * 2
                        initial_offset = draw_graph.offset
                        is_dragging = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

        if is_dragging:
            mouse_pos = np.array(pygame.mouse.get_pos())
            mouse_pos -= np.array((opts.display_width, opts.display_height))
            mouse_pos = (mouse_pos - 0.5) * 2

            draw_graph.offset = (
                initial_offset[0] + mouse_pos[0] - initial_mouse_pos[0],
                initial_offset[1] + mouse_pos[1] - initial_mouse_pos[1],
            )

        draw_graph.update(opts)
        # Draw
        screen.fill((255, 255, 255))
        screen.blit(draw_graph.surface, (0, 0))
        pygame.display.flip()
        clock.tick(opts.fps)

    pygame.quit()
