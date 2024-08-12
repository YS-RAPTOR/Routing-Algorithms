from typing import Tuple
import numpy as np
import pygame

from graph import Graph, GraphOptions


class DrawGraph:
    def __init__(
        self,
        graph: Graph,
        offset: Tuple[float, float],
        zoom: float | None,
        node_radius: int,
        line_width: int,
    ):
        self.graph = graph
        self.offset = offset
        self.zoom = zoom
        self.node_radius = node_radius
        self.line_width = line_width

    def zoom_to_fit(self, display_region: Tuple[int, int]) -> float:
        width, height = display_region
        x_scale = width / (self.graph.bbox[2] - self.graph.bbox[0])  # type: ignore
        y_scale = height / (self.graph.bbox[3] - self.graph.bbox[1])  # type: ignore
        return min(x_scale, y_scale)

    def draw(
        self,
        graph: Graph,
        surface: pygame.Surface,
        offset: Tuple[int, int],
        zoom: float,
    ):
        for child in graph.children:
            pygame.draw.aaline(
                surface,
                child.color,
                (int(graph.x * zoom + offset[0]), int(graph.y * zoom + offset[1])),
                (int(child.x * zoom + offset[0]), int(child.y * zoom + offset[1])),
                max(self.line_width, int(zoom * self.line_width)),
            )
            self.draw(child, surface, offset, zoom)
            pygame.draw.circle(
                surface,
                child.color,
                (int(child.x * zoom + offset[0]), int(child.y * zoom + offset[1])),
                max(self.node_radius, int(zoom * self.node_radius)),
            )
        pygame.draw.circle(
            surface,
            graph.color,
            (int(graph.x * zoom + offset[0]), int(graph.y * zoom + offset[1])),
            max(self.node_radius, int(zoom * self.node_radius)),
        )

    def update(self, display_region: Tuple[int, int]):
        zoom = self.zoom_to_fit(display_region) if self.zoom is None else self.zoom
        zoom *= 0.92 - (0.01 * self.node_radius)
        self.surface = pygame.Surface(display_region)
        self.surface.fill((255, 255, 255))
        self.draw(
            self.graph,
            self.surface,
            (int(self.offset[0]), int(self.offset[1])),
            zoom,
        )


class App:
    def __init__(
        self,
        window_name: str = "Graph",
        window_size: Tuple[int, int] = (800, 800),
        fps: int = 60,
        scroll_speed: float = 1.1,
        node_radius: int = 5,
        line_width: int = 2,
    ):
        # Initializes the app with the given parameters
        self.window_name = window_name
        self.window_size = window_size
        self.fps = fps
        self.scroll_speed = scroll_speed

        # NOTE: Creates Graph
        graph = Graph(None, 0, 0, (0, 0, 0), 0)
        print(f"No of Nodes Created: {graph.create(GraphOptions())}")

        # NOTE: App Initialization
        self.draw_graph = DrawGraph(
            graph,
            tuple(np.array(self.window_size) // 2),
            None,
            node_radius,
            line_width,
        )
        self.draw_graph.update(self.window_size)

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

                    # If the key pressed is R, then the graph will be reset to fit the window and
                    # offset will be set to the center
                    if event.key == pygame.K_r:
                        self.draw_graph.zoom = None
                        self.draw_graph.offset = tuple(np.array(self.window_size) // 2)

                # Handles the event when the window is resized
                if event.type == pygame.VIDEORESIZE:
                    self.window_size = event.size

                # Handles the event when the mouse wheel is scrolled
                if event.type == pygame.MOUSEWHEEL:
                    # If the zoom is not set, then it will be set to fit the window
                    if self.draw_graph.zoom is None:
                        self.draw_graph.zoom = self.draw_graph.zoom_to_fit(
                            self.window_size
                        )

                    # Stores the old zoom value to calculate offset
                    old_zoom = self.draw_graph.zoom

                    # Zoom in or out based on the scroll direction and the scroll speed
                    if event.y > 0:
                        self.draw_graph.zoom *= self.scroll_speed
                    elif event.y < 0:
                        self.draw_graph.zoom /= self.scroll_speed

                    zoom = self.draw_graph.zoom

                    # Calculates the offset based on the zoom value and the mouse position
                    mouse_pos = np.array(pygame.mouse.get_pos())
                    offset = np.array(self.draw_graph.offset)
                    self.draw_graph.offset = tuple(
                        mouse_pos - (mouse_pos - offset) * (zoom / old_zoom)
                    )
                # When the left mouse button is pressed, dragging starts
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.is_dragging:
                            # Stores the initial mouse position and the offset
                            self.initial_mouse_pos = np.array(pygame.mouse.get_pos())
                            self.initial_offset = self.draw_graph.offset
                            self.is_dragging = True

                # When the left mouse button is released, dragging stops
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False

            # Moves the graph based on whether the ueser is currently dragging
            if self.is_dragging:
                self.mouse_pos = np.array(pygame.mouse.get_pos())
                self.draw_graph.offset = tuple(
                    self.initial_offset + self.mouse_pos - self.initial_mouse_pos
                )

            # Updates the graph
            self.draw_graph.update(self.window_size)

            # Draw the updated graph
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.draw_graph.surface, (0, 0))
            pygame.display.flip()

            # Limits the frame rate to the specified fps
            self.clock.tick(self.fps)

        # Quits the pygame when the app is closed
        pygame.quit()


if __name__ == "__main__":
    app = App()
    app.run()
