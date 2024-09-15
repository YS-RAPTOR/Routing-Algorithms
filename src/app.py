from dataclasses import dataclass
from enum import Enum
from typing_extensions import Tuple
import numpy as np
import pygame


class TextOrientation(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class Button:
    def __init__(
        self,
        size: Tuple[int, int],
        text: str,
        font_size: int,
        text_orientation: TextOrientation,
        foreground_color: Tuple[int, int, int],
        background_color: Tuple[int, int, int],
        hover_color: Tuple[int, int, int],
    ) -> None:
        self.size = size
        self.text = text
        self.font_size = font_size
        self.text_orientation = text_orientation
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.hover_color = hover_color

        self.bg = self.background_color


class TextField:
    pass


# TODO: Parcel Options Sidebar
# Change Parcel Information (Id cannot be changed, Location picked from map. Id always starting from zero to num_of_agents)
# Reroll Parcel Information
# Add and Remove Parcels
# On Hover Highlight location
class ParcelManager:
    pass


# TODO: Agent Options Sidebar
# Change Agent Information (Id cannot be changed, others can. Id always starting from zero to num_of_agents)
# Reroll Agent Information
# Add and Remove Agents
class AgentManager:
    pass


# TODO: Map Options Sidebar
# Change Map Settings and Recreate Map. Map Recreation always rerolls invalid parcels
# TODO: Render Map
class MapManager:
    def __init__(
        self,
        min_node_radius: int,
        min_line_width: int,
    ):
        self.min_node_radius = min_node_radius
        self.min_line_width = min_line_width
        self.sidebar_active = False

    def update(self):
        pass

    def render(self):
        pass

    def activate_sidebar(self):
        self.sidebar_active = True


# TODO:
# Render Parcels in Warehouse in the sidebar (On hover highlight agent/warehouse. Removed when delivered)
# Stop button at bottom of sidebar
# Render All Agents and the parcels carried by them
class SimulationManager:
    pass


# TODO: Main Sidebar
# Map button
# Parcels button
# Agents Button
# Run Button
class App:
    @dataclass
    class MouseInfo:
        mouse_pos: np.ndarray = np.zeros(2)
        initial_mouse_pos: np.ndarray = np.zeros(2)
        offset_from_initial: np.ndarray = np.zeros(2)
        is_dragging: bool = False

    def __init__(
        self,
        window_name: str = "node",
        window_size: Tuple[int, int] = (800, 800),
        target_fps: int = 60,
        scroll_speed: float = 1.1,
        min_node_radius: int = 3,
        min_line_width: int = 2,
        sidebar_width: int = 200,
    ):
        # Initializes the app with the given parameters
        self.running = True
        self.scroll_speed = scroll_speed
        self.target_fps = target_fps
        self.delta_time = 1 / target_fps

        # Initialize Managers
        self.mouse_info = self.MouseInfo()
        self.map_manager = MapManager(min_node_radius, min_line_width)

        # Initialize surfaces
        self.sidebar = pygame.Surface((sidebar_width, window_size[1]))
        self.canvas = pygame.Surface((window_size[0] - sidebar_width, window_size[1]))

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption(window_name)
        self.clock = pygame.time.Clock()

    def __update(self):
        # TODO: Capture input
        # TODO: Zoom in/out
        # TODO: Capture Button Clicks and Keyboard Input
        # TODO: Move Agents
        self.sidebar.fill((255, 0, 255))
        self.canvas.fill((255, 0, 0))

    def __render(self):
        # TODO: Render Map
        # TODO: Render Agents
        # TODO: Render Options

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.canvas, (0, 0))
        self.screen.blit(self.sidebar, (self.canvas.get_width(), 0))

    def run(self):
        while self.running:
            self.__update()
            self.__render()
            pygame.display.flip()
            self.clock.tick(self.target_fps)


if __name__ == "__main__":
    App().run()
