from typing import Set, Tuple
from typing_extensions import List
import numpy as np
import pygame

import test_algos.GA as GA

from common import DeliveryAgentInfo, create_agents, create_parcels
from node import Node, NodeOptions


class Renderer:
    def __init__(
        self,
        node: Node,
        offset: Tuple[float, float],
        zoom: float | None,
        node_radius: int,
        line_width: int,
    ):
        self.node = node
        self.offset = offset
        self.zoom = zoom
        self.node_radius = node_radius
        self.line_width = line_width

    def zoom_to_fit(self, display_region: Tuple[int, int]) -> float:
        width, height = display_region
        x_scale = width / (self.node.bbox[2] - self.node.bbox[0])  # type: ignore
        y_scale = height / (self.node.bbox[3] - self.node.bbox[1])  # type: ignore
        return min(x_scale, y_scale)

    def __draw_map(
        self,
        node: Node,
        offset: Tuple[int, int],
        zoom: float,
        visited: Set[Node],
    ):
        visited.add(node)
        for neighbour in node.neighbours:
            pygame.draw.aaline(
                self.surface,
                neighbour.color,
                (int(node.x * zoom + offset[0]), int(node.y * zoom + offset[1])),
                (
                    int(neighbour.x * zoom + offset[0]),
                    int(neighbour.y * zoom + offset[1]),
                ),
                max(self.line_width, int(zoom * self.line_width)),
            )
            if neighbour in visited:
                continue

            self.__draw_map(neighbour, offset, zoom, visited)
        pygame.draw.circle(
            self.surface,
            node.color,
            (int(node.x * zoom + offset[0]), int(node.y * zoom + offset[1])),
            max(self.node_radius, int(zoom * self.node_radius)),
        )

    def __draw_agents(
        self,
        offset: Tuple[int, int],
        zoom: float,
    ):
        pass

    def draw(self, display_region: Tuple[int, int]):
        zoom = self.zoom_to_fit(display_region) if self.zoom is None else self.zoom
        zoom *= 0.92 - (0.01 * self.node_radius)

        self.surface = pygame.Surface(display_region)
        self.surface.fill((255, 255, 255))
        self.__draw_map(
            self.node,
            (int(self.offset[0]), int(self.offset[1])),
            zoom,
            set(),
        )

        self.__draw_agents(
            (int(self.offset[0]), int(self.offset[1])),
            zoom,
        )


class App:
    def __init__(
        self,
        window_name: str = "node",
        window_size: Tuple[int, int] = (800, 800),
        fps: int = 60,
        scroll_speed: float = 1.1,
        node_radius: int = 3,
        line_width: int = 2,
    ):
        # Initializes the app with the given parameters
        self.window_name = window_name
        self.window_size = window_size
        self.fps = fps
        self.scroll_speed = scroll_speed

        # NOTE: Creates node
        root = Node(0, 0, (0, 0, 0), 0)
        no_of_nodes = root.create(NodeOptions())
        print(f" No of Nodes Created: {no_of_nodes}")

        parcels = create_parcels(no_of_nodes)
        agents = create_agents()

        routes = GA.model(root, parcels, agents, False)

        # NOTE: App Initialization
        self.renderer = Renderer(
            root,
            tuple(np.array(self.window_size) // 2),
            None,
            node_radius,
            line_width,
        )

        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.window_name)

        self.clock = pygame.time.Clock()

        self.running = True
        self.delta = 1 / self.fps

        self.initial_mouse_pos = np.zeros(2)
        self.initial_offset = (0, 0)
        self.is_dragging = False

    def run(self):
        while self.running:
            # Handles events
            for event in pygame.event.get():
                # Handles the quit event when the window is closed
                if event.type == pygame.QUIT:
                    self.running = False

                # Handles any event when a key is pressed
                if event.type == pygame.KEYDOWN:
                    # If the key pressed is ESC or Q, then the app will close
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        self.running = False
                        break

                    # If the key pressed is R, then the node will be reset to fit the window and
                    # offset will be set to the center
                    if event.key == pygame.K_r:
                        self.renderer.zoom = None
                        self.renderer.offset = tuple(np.array(self.window_size) // 2)

                # Handles the event when the window is resized
                if event.type == pygame.VIDEORESIZE:
                    self.window_size = event.size

                # Handles the event when the mouse wheel is scrolled
                if event.type == pygame.MOUSEWHEEL:
                    # If the zoom is not set, then it will be set to fit the window
                    if self.renderer.zoom is None:
                        self.renderer.zoom = self.renderer.zoom_to_fit(self.window_size)

                    # Stores the old zoom value to calculate offset
                    old_zoom = self.renderer.zoom

                    # Zoom in or out based on the scroll direction and the scroll speed
                    if event.y > 0:
                        self.renderer.zoom *= self.scroll_speed
                    elif event.y < 0:
                        self.renderer.zoom /= self.scroll_speed

                    # Clamp the zoom value to a certain range
                    zoom = self.renderer.zoom

                    # Calculates the offset based on the zoom value and the mouse position
                    mouse_pos = np.array(pygame.mouse.get_pos())
                    offset = np.array(self.renderer.offset)
                    self.renderer.offset = tuple(
                        mouse_pos - (mouse_pos - offset) * (zoom / old_zoom)
                    )
                # When the left mouse button is pressed, dragging starts
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.is_dragging:
                            # Stores the initial mouse position and the offset
                            self.initial_mouse_pos = np.array(pygame.mouse.get_pos())
                            self.initial_offset = self.renderer.offset
                            self.is_dragging = True

                # When the left mouse button is released, dragging stops
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False

            # Moves the node based on whether the ueser is currently dragging
            if self.is_dragging:
                self.mouse_pos = np.array(pygame.mouse.get_pos())
                self.renderer.offset = tuple(
                    self.initial_offset + self.mouse_pos - self.initial_mouse_pos
                )

            # Updates the node
            self.renderer.draw(self.window_size)

            # Draw the updated node
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.renderer.surface, (0, 0))
            pygame.display.flip()

            # Limits the frame rate to the specified fps
            self.clock.tick(self.fps)

        # Quits the pygame when the app is closed
        pygame.quit()


if __name__ == "__main__":
    app = App()
    app.run()
