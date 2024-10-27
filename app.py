import pygame
import random
import heapq
import sys
import json
import time
import threading
from collections import deque
from typing import List, Tuple, Dict, Optional, Set, Union, Any
from dataclasses import dataclass, field
from enum import Enum, auto, member
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import platform
import os
import math
from abc import ABC, abstractmethod
from theme.theme_manager import Theme, ThemeManager  # This replaces the previous import
from algorithms.maze_algorithms import DFSMazeGenerator, BFSMazeGenerator

# Enhanced logging configuration with better error handling and more features
def setup_logging():
    """
    Configure logging with multiple handlers and enhanced formatting.
    Includes both file and console logging with rotation policies.
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"maze_visualizer_{timestamp}.log"
        rotating_log_file = log_dir / "maze_visualizer_rotating.log"

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # File handler with daily rotation
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)

        # Rotating file handler (size-based)
        rotating_handler = RotatingFileHandler(
            filename=rotating_log_file,
            maxBytes=1024*1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        rotating_handler.setFormatter(detailed_formatter)
        rotating_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        # Remove any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add all handlers
        logger.addHandler(file_handler)
        logger.addHandler(rotating_handler)
        logger.addHandler(console_handler)

        logger.info("Logging system initialized successfully")
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        logging.error(f"Failed to initialize advanced logging: {str(e)}")

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Enhanced error handling decorator
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

# Initialize pygame with comprehensive error handling
@error_handler
def initialize_pygame():
    try:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
    except pygame.error as e:
        logger.critical(f"Failed to initialize pygame: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error during pygame initialization: {e}")
        sys.exit(1)

initialize_pygame()

# After pygame initialization and before Theme class

# 5. MazeConfig class
class MazeConfig:
    class Screen:
        MIN_WIDTH = 800
        MIN_HEIGHT = 600
        PADDING = 20
        
    class Maze:
        MIN_SIZE = 5
        MAX_SIZE = 150
        DEFAULT_WIDTH = 20
        DEFAULT_HEIGHT = 20
        
    class Animation:
        MIN_SPEED = 1
        MAX_SPEED = 1000
        DEFAULT_SPEED = 50
        FPS = 60
        
    class UI:
        CELL_SIZE_DESKTOP = 20
        CELL_SIZE_MOBILE = 30
        CONTROL_PANEL_HEIGHT = 200
        BUTTON_HEIGHT = 40
        SLIDER_HEIGHT = 20
        DROPDOWN_HEIGHT = 40
        
    class Files:
        SAVE_FOLDER = Path("saved_mazes")
        SCREENSHOT_FOLDER = Path("screenshots")
        CONFIG_FILE = Path("config.json")
        
    @classmethod
    def initialize(cls):
        for folder in [cls.Files.SAVE_FOLDER, cls.Files.SCREENSHOT_FOLDER]:
            folder.mkdir(exist_ok=True)

# 6. Theme/ThemeManager classes (already present, but needs to be after MazeConfig)

# 7. AlgorithmType class (needs to be before MazeState)
class AlgorithmType(Enum):
    @member
    class Meta:
        def __init__(self, display_name: str, complexity: str, description: str):
            self.display_name = display_name
            self.complexity = complexity
            self.description = description
    
    DFS = Meta("Depth-First Search", "O(V + E)", "Explores deeply before backtracking")
    BFS = Meta("Breadth-First Search", "O(V + E)", "Explores nearest neighbors first")
    ASTAR = Meta("A* Pathfinding", "O(E log V)", "Finds optimal path using heuristics")
    PRIM = Meta("Prim's Algorithm", "O(E log V)", "Creates minimum spanning tree")
    KRUSKAL = Meta("Kruskal's Algorithm", "O(E log V)", "Creates minimum spanning tree")
    WILSON = Meta("Wilson's Algorithm", "O(V^2)", "Creates unbiased mazes")
    ALDOUS_BRODER = Meta("Aldous-Broder", "O(V^3)", "Creates unbiased mazes")
    RECURSIVE_DIVISION = Meta("Recursive Division", "O(V log V)", "Divides space recursively")
    HUNT_AND_KILL = Meta("Hunt and Kill", "O(V^2)", "Similar to DFS with random walks")

# 8. MazeState class (already present, but needs to be after AlgorithmType)

# Enhanced state management
@dataclass
class MazeState:
    # Maze properties
    width: int = MazeConfig.Maze.DEFAULT_WIDTH
    height: int = MazeConfig.Maze.DEFAULT_HEIGHT
    speed: int = MazeConfig.Animation.DEFAULT_SPEED
    algorithm: AlgorithmType = AlgorithmType.DFS
    maze: List[List[int]] = field(default_factory=lambda: [[]])
    
    # Runtime state
    running: bool = False
    paused: bool = False
    solution_path: List[Tuple[int, int]] = field(default_factory=list)
    visited_cells: Set[Tuple[int, int]] = field(default_factory=set)
    start_pos: Tuple[int, int] = field(default=(1, 1))
    end_pos: Tuple[int, int] = field(default=(18, 18))
    
    # UI state
    current_theme: str = "dark"
    show_stats: bool = True
    show_grid: bool = True
    show_animation: bool = True
    dropdown_open: bool = False
    
    # Performance metrics
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "generation_time": 0.0,
        "solving_time": 0.0,
        "cells_visited": 0,
        "path_length": 0,
    })
    
    # Mobile-specific state
    touch_start: Optional[Tuple[int, int]] = None
    pinch_start_distance: Optional[float] = None
    
    def reset_stats(self):
        self.stats = {
            "generation_time": 0.0,
            "solving_time": 0.0,
            "cells_visited": 0,
            "path_length": 0,
        }

# Initialize game state
state = MazeState()
MazeConfig.initialize()

# UI Components
class UIComponent(ABC):
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        pass

class Button(UIComponent):
    def __init__(self, rect: pygame.Rect, text: str, action: callable):
        self.rect = rect
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        color = theme.colors["button_hover"] if self.hovered else theme.colors["button"]
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.action()
            return True
        return False

# Add these constants after MazeConfig class
class UIConstants:
    BUTTON_WIDTH = 160
    BUTTON_HEIGHT = 40
    BUTTON_PADDING = 10
    CONTROL_PANEL_HEIGHT = 120
    STATS_PANEL_WIDTH = 200
    FONT_SIZE = 24

# Add this class after UIComponent class
class ControlPanel(UIComponent):
    def __init__(self, screen_width: int, screen_height: int):
        self.rect = pygame.Rect(
            0,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT,
            screen_width,
            UIConstants.CONTROL_PANEL_HEIGHT
        )
        
        # Create buttons
        button_y = screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING
        button_x = UIConstants.BUTTON_PADDING
        
        self.buttons = [
            Button(
                pygame.Rect(button_x, button_y, UIConstants.BUTTON_WIDTH, UIConstants.BUTTON_HEIGHT),
                "Generate Maze",
                self.generate_maze
            ),
            Button(
                pygame.Rect(button_x + UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING, 
                          button_y, 
                          UIConstants.BUTTON_WIDTH, 
                          UIConstants.BUTTON_HEIGHT),
                "Solve Maze",
                self.solve_maze
            ),
            Button(
                pygame.Rect(button_x + (UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING) * 2,
                          button_y,
                          UIConstants.BUTTON_WIDTH,
                          UIConstants.BUTTON_HEIGHT),
                "Reset",
                self.reset_maze
            )
        ]

        self.algorithms = {
            AlgorithmType.DFS: DFSMazeGenerator(),
            AlgorithmType.BFS: BFSMazeGenerator(),
            # Add other algorithms as they're implemented
        }

    def draw(self, screen: pygame.Surface) -> None:
        # Draw panel background
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["background"],
            self.rect
        )
        
        # Draw border
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["wall"],
            self.rect,
            2  # border width
        )
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def generate_maze(self):
        if not state.running:
            state.running = True
            
            # Record start time
            start_time = time.time()
            
            # Generate maze using selected algorithm
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                state.maze = algorithm.generate(state.width, state.height)
                
                # Update stats
                state.stats["generation_time"] = time.time() - start_time
                logger.info(f"Generated maze using {state.algorithm.name}")
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def solve_maze(self):
        if state.running and not state.paused and hasattr(state, 'maze'):
            # Record start time
            start_time = time.time()
            
            # Solve maze using selected algorithm
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                state.solution_path = algorithm.solve(
                    state.maze,
                    state.start_pos,
                    state.end_pos
                )
                
                # Update stats
                state.stats["solving_time"] = time.time() - start_time
                state.stats["path_length"] = len(state.solution_path)
                logger.info(f"Solved maze using {state.algorithm.name}")
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def reset_maze(self):
        state.running = False
        state.paused = False
        state.solution_path = []
        state.visited_cells = set()
        state.reset_stats()
        logger.info("Maze reset")

# Performance Optimizations
class MazeRenderer:
    def __init__(self):
        self.cache = {}
        self.dirty = True
        self.cell_size = MazeConfig.UI.CELL_SIZE_DESKTOP
        self.screen = pygame.display.get_surface()
        self.control_panel = ControlPanel(
            self.screen.get_width(),
            self.screen.get_height()
        )
    
    def clear(self):
        """Clear the screen with background color"""
        self.screen.fill(ThemeManager.get_theme(state.current_theme).colors["background"])
    
    @error_handler
    def render(self, maze: List[List[int]], screen: pygame.Surface) -> None:
        """Render the maze grid"""
        if self.dirty:
            self._update_cache(maze)
        self._draw_from_cache(screen)
    
    def draw_cell(self, pos: Tuple[int, int], cell_type: str) -> None:
        """Draw a single cell with the specified type"""
        x, y = pos
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        color = ThemeManager.get_theme(state.current_theme).colors[cell_type]
        pygame.draw.rect(self.screen, color, rect)
    
    def draw_control_panel(self) -> None:
        """Draw the control panel UI"""
        self.control_panel.draw(self.screen)
    
    def draw_stats(self, stats: Dict[str, Any]) -> None:
        """Draw performance statistics"""
        font = pygame.font.Font(None, 24)
        y_offset = 10
        for key, value in stats.items():
            text = f"{key}: {value}"
            text_surface = font.render(
                text,
                True,
                ThemeManager.get_theme(state.current_theme).colors["text"]
            )
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def draw_grid_lines(self) -> None:
        """Draw grid lines"""
        for x in range(0, self.screen.get_width(), self.cell_size):
            pygame.draw.line(
                self.screen,
                ThemeManager.get_theme(state.current_theme).colors["wall"],
                (x, 0),
                (x, self.screen.get_height() - MazeConfig.UI.CONTROL_PANEL_HEIGHT)
            )
        for y in range(0, self.screen.get_height() - MazeConfig.UI.CONTROL_PANEL_HEIGHT, self.cell_size):
            pygame.draw.line(
                self.screen,
                ThemeManager.get_theme(state.current_theme).colors["wall"],
                (0, y),
                (self.screen.get_width(), y)
            )
    
    def _update_cache(self, maze: List[List[int]]) -> None:
        """Update the rendering cache"""
        self.cache = {}
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 1:  # Wall
                    self.cache[(x, y)] = ThemeManager.get_theme(state.current_theme).colors["wall"]
        self.dirty = False
    
    def _draw_from_cache(self, screen: pygame.Surface) -> None:
        """Draw the maze from cache"""
        for (x, y), color in self.cache.items():
            rect = pygame.Rect(
                x * self.cell_size,
                y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, color, rect)

# Touch Controls Handler
class TouchHandler:
    def __init__(self):
        self.touch_threshold = 10
        self.last_touch_time = 0
        
    @error_handler
    def handle_touch(self, event: pygame.event.Event, state: MazeState) -> None:
        if event.type == pygame.FINGERDOWN:
            state.touch_start = (event.x, event.y)
            self.last_touch_time = time.time()
        elif event.type == pygame.FINGERUP:
            self._handle_touch_end(event, state)
    
    def _handle_touch_end(self, event: pygame.event.Event, state: MazeState) -> None:
        if state.touch_start is None:
            return
        
        dx = event.x - state.touch_start[0]
        dy = event.y - state.touch_start[1]
        
        if abs(dx) > self.touch_threshold or abs(dy) > self.touch_threshold:
            self._handle_swipe(dx, dy, state)
        else:
            self._handle_tap(event, state)

# Algorithm Implementations
class MazeAlgorithm(ABC):
    @abstractmethod
    def generate(self, width: int, height: int) -> List[List[int]]:
        pass
    
    @abstractmethod
    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass

class DFSMazeGenerator(MazeAlgorithm):
    @error_handler
    def generate(self, width: int, height: int) -> List[List[int]]:
        # Implementation of DFS maze generation
        pass
    
    @error_handler
    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        # Implementation of DFS maze solving
        pass

# Enhanced state update function
@error_handler
def update_game_state():
    """Update the game state for each frame"""
    # Add your game state update logic here
    pass

# Move render_frame before game_loop and after MazeRenderer class
@error_handler
def render_frame(renderer: MazeRenderer):
    """Render a single frame of the game"""
    try:
        # Clear the screen
        renderer.clear()
        
        # Calculate maze area dimensions
        maze_height = renderer.screen.get_height() - UIConstants.CONTROL_PANEL_HEIGHT
        
        # Draw maze grid if it exists
        if hasattr(state, 'maze'):
            renderer.render(state.maze, renderer.screen)
        
        # Draw visited cells
        if state.show_animation:
            for cell in state.visited_cells:
                renderer.draw_cell(cell, "visited")
        
        # Draw solution path
        if state.solution_path:
            for cell in state.solution_path:
                renderer.draw_cell(cell, "path")
        
        # Draw start and end positions
        renderer.draw_cell(state.start_pos, "start")
        renderer.draw_cell(state.end_pos, "end")
        
        # Draw UI elements
        renderer.draw_control_panel()
        
        # Draw stats if enabled
        if state.show_stats:
            renderer.draw_stats({
                "Generation Time": f"{state.stats['generation_time']:.2f}s",
                "Solving Time": f"{state.stats['solving_time']:.2f}s",
                "Cells Visited": state.stats['cells_visited']
            })
        
        # Draw grid lines if enabled
        if state.show_grid:
            renderer.draw_grid_lines()
        
        # Update the display
        pygame.display.flip()
        
    except Exception as e:
        logger.error(f"Error in render_frame: {str(e)}")
        raise

# Then define game_loop after render_frame
@error_handler
def game_loop():
    renderer = MazeRenderer()
    touch_handler = TouchHandler()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle UI events
            renderer.control_panel.handle_event(event)
            touch_handler.handle_touch(event, state)
            
        if state.running and not state.paused:
            update_game_state()
            
        render_frame(renderer)
        clock.tick(MazeConfig.Animation.FPS)

# Move setup_display before the main block
def setup_display():
    """Initialize the pygame display with the configured dimensions"""
    try:
        screen = pygame.display.set_mode((
            MazeConfig.Screen.MIN_WIDTH,
            MazeConfig.Screen.MIN_HEIGHT
        ))
        pygame.display.set_caption("Maze Visualizer")
        return screen
    except pygame.error as e:
        logger.critical(f"Failed to setup display: {e}")
        sys.exit(1)

# Then the main block
if __name__ == "__main__":
    initialize_pygame()
    setup_display()  # Make sure display is set up before game loop
    game_loop()

class AlgorithmSelector(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.open = False
        self.options = list(AlgorithmType)
        self.option_height = 30
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        
        # Draw main button
        pygame.draw.rect(screen, theme.colors["button"], self.rect, border_radius=8)
        
        # Draw selected algorithm name
        font = pygame.font.Font(None, 24)
        text = state.algorithm.Meta.display_name
        text_surface = font.render(text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw dropdown if open
        if self.open:
            for i, algo in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.option_height,
                    self.rect.width,
                    self.option_height
                )
                pygame.draw.rect(screen, theme.colors["button"], option_rect)
                
                text = algo.Meta.display_name
                text_surface = font.render(text, True, theme.colors["text"])
                text_rect = text_surface.get_rect(center=option_rect.center)
                screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return True
            elif self.open:
                # Check if clicked on an option
                for i, algo in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * self.option_height,
                        self.rect.width,
                        self.option_height
                    )
                    if option_rect.collidepoint(event.pos):
                        state.algorithm = algo
                        self.open = False
                        return True
        return False

# Add these new UI components after existing UI classes

class Slider(UIComponent):
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float, 
                 current_val: float, label: str):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.dragging = False
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        
        # Draw slider track
        pygame.draw.rect(screen, theme.colors["button"], self.rect, border_radius=4)
        
        # Calculate handle position
        handle_x = self.rect.x + (self.rect.width * 
                                 (self.current_val - self.min_val) / 
                                 (self.max_val - self.min_val))
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y, 10, self.rect.height)
        pygame.draw.rect(screen, theme.colors["slider"], handle_rect, border_radius=5)
        
        # Draw label and value
        font = pygame.font.Font(None, 24)
        label_surface = font.render(
            f"{self.label}: {self.current_val:.1f}", 
            True, 
            theme.colors["text"]
        )
        screen.blit(label_surface, (self.rect.x, self.rect.y - 20))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            self.current_val = (self.min_val + 
                              (rel_x / self.rect.width) * 
                              (self.max_val - self.min_val))
            return True
        return False

class InfoPanel(UIComponent):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible = False
        self.current_info = ""
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        theme = ThemeManager.get_theme(state.current_theme)
        
        # Draw panel background
        pygame.draw.rect(screen, theme.colors["background"], self.rect)
        pygame.draw.rect(screen, theme.colors["wall"], self.rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, 24)
        lines = self.current_info.split('\n')
        y_offset = 10
        
        for line in lines:
            text_surface = font.render(line, True, theme.colors["text"])
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 25
    
    def show_algorithm_info(self, algorithm: AlgorithmType):
        self.current_info = (
            f"Algorithm: {algorithm.Meta.display_name}\n"
            f"Complexity: {algorithm.Meta.complexity}\n"
            f"Description: {algorithm.Meta.description}"
        )
        self.visible = True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.visible = False
                return True
        return False

# Update ControlPanel to include new UI elements
class ControlPanel(UIComponent):
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        # ... (existing initialization code) ...
        
        # Add speed slider
        self.speed_slider = Slider(
            pygame.Rect(
                UIConstants.BUTTON_PADDING,
                screen_height - UIConstants.CONTROL_PANEL_HEIGHT + 70,
                200,
                20
            ),
            MazeConfig.Animation.MIN_SPEED,
            MazeConfig.Animation.MAX_SPEED,
            state.speed,
            "Animation Speed"
        )
        
        # Add algorithm selector
        self.algorithm_selector = AlgorithmSelector(
            screen_width - 220,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING,
            200,
            UIConstants.BUTTON_HEIGHT
        )
        
        # Add info panel
        self.info_panel = InfoPanel(
            pygame.Rect(
                screen_width - 250,
                screen_height - 300,
                240,
                200
            )
        )
    
    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        self.speed_slider.draw(screen)
        self.algorithm_selector.draw(screen)
        self.info_panel.draw(screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        return (super().handle_event(event) or
                self.speed_slider.handle_event(event) or
                self.algorithm_selector.handle_event(event) or
                self.info_panel.handle_event(event))
