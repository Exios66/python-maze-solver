# At the top of the file, update imports
from datetime import datetime  # Change time to datetime
import sys
import logging as logger  # Change venv import to proper logging
from typing import Any, Dict, List, Tuple  # Fix Tuple import
import pygame

from algorithms.maze_algorithms import (
    DFSMazeGenerator,
    BFSMazeGenerator,
    AStarMazeGenerator,
    PrimMazeGenerator
)
from algorithms.algorithm_types import AlgorithmType  # Make sure this file exists
import state
from theme.theme_manager import ThemeManager
from ui.ui_component import UIComponent
from ui.ui_constants import UIConstants
from config.maze_config import MazeConfig
from state import MazeState
from ui.button import Button
from ui.slider import Slider

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

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
        self.maze_height = self.screen.get_height() - UIConstants.CONTROL_PANEL_HEIGHT
        self.maze_width = self.screen.get_width()
    
    def clear(self):
        self.screen.fill(ThemeManager.get_theme(state.current_theme).colors["background"])
    
    def render(self, maze: List[List[int]], screen: pygame.Surface) -> None:
        if self.dirty:
            self._update_cache(maze)
        self._draw_from_cache(screen)
        self.control_panel.draw(screen)
    
    def draw_cell(self, pos: Tuple[int, int], cell_type: str) -> None:
        x, y = pos
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        color = ThemeManager.get_theme(state.current_theme).colors[cell_type]
        pygame.draw.rect(self.screen, color, rect)
    
    def draw_stats(self, stats: Dict[str, Any]) -> None:
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
        self.cache = {}
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 1:  # Wall
                    self.cache[(x, y)] = ThemeManager.get_theme(state.current_theme).colors["wall"]
        self.dirty = False
    
    def _draw_from_cache(self, screen: pygame.Surface) -> None:
        for (x, y), color in self.cache.items():
            rect = pygame.Rect(
                x * self.cell_size,
                y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, color, rect)

@error_handler
def render_frame(renderer: MazeRenderer):
    try:
        # Clear the screen
        renderer.clear()
        
        # Draw the maze if it exists
        if state.maze and len(state.maze) > 0:
            # Draw maze background
            pygame.draw.rect(
                renderer.screen,
                ThemeManager.get_theme(state.current_theme).colors["background"],
                pygame.Rect(0, 0, renderer.maze_width, renderer.maze_height)
            )
            
            # Draw maze walls
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
            
            # Draw grid if enabled
            if state.show_grid:
                renderer.draw_grid_lines()
        
        # Draw UI elements
        renderer.control_panel.draw(renderer.screen)
        
        # Update display
        pygame.display.flip()
        
    except Exception as e:
        logger.error(f"Error rendering frame: {e}")
        raise

# Previous content remains the same until ControlPanel class

class ControlPanel(UIComponent):
    def __init__(self, screen_width: int, screen_height: int):
        self.rect = pygame.Rect(
            0,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT,
            screen_width,
            UIConstants.CONTROL_PANEL_HEIGHT
        )
        
        button_y = screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING
        
        self.buttons = [
            Button(
                UIConstants.BUTTON_PADDING,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Generate Maze",
                self.generate_maze
            ),
            Button(
                UIConstants.BUTTON_PADDING + UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Solve Maze",
                self.solve_maze
            ),
            Button(
                UIConstants.BUTTON_PADDING + (UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING) * 2,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Reset",
                self.reset_maze
            )
        ]

        self.algorithms = {
            AlgorithmType.DFS: DFSMazeGenerator(),
            AlgorithmType.BFS: BFSMazeGenerator(),
            AlgorithmType.ASTAR: AStarMazeGenerator(),
            AlgorithmType.PRIM: PrimMazeGenerator()
        }

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
        
        self.algorithm_selector = AlgorithmSelector(
            screen_width - 220,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING,
            200,
            UIConstants.BUTTON_HEIGHT
        )
        
        self.info_panel = InfoPanel(
            pygame.Rect(
                screen_width - 250,
                screen_height - 300,
                240,
                200
            )
        )
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["background"],
            self.rect
        )
        
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["wall"],
            self.rect,
            2
        )
        
        for button in self.buttons:
            button.draw(screen)
            
        self.speed_slider.draw(screen)
        self.algorithm_selector.draw(screen)
        self.info_panel.draw(screen)
        
        if self.algorithm_selector.hovered:
            self.info_panel.show_algorithm_info(state.algorithm)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        if (self.speed_slider.handle_event(event) or
            self.algorithm_selector.handle_event(event) or
            self.info_panel.handle_event(event)):
            return True
            
        return False

    def generate_maze(self):
        if not state.running:
            state.running = True
            state.solution_path = []
            state.visited_cells = set()
            
            start_time = time.time()
            
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                # Generate the maze and store it in the state
                state.maze = algorithm.generate(state.width, state.height)
                state.stats["generation_time"] = time.time() - start_time
                state.stats["cells_visited"] = 0
                logger.info(f"Generated maze using {state.algorithm.name}")
                
                # Force renderer to update cache
                self.parent_renderer.dirty = True
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def solve_maze(self):
        if state.running and not state.paused and hasattr(state, 'maze'):
            start_time = time.time()
            
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                solution = algorithm.solve(
                    state.maze,
                    state.start_pos,
                    state.end_pos
                )
                
                state.solution_path = solution if solution is not None else []
                state.stats["solving_time"] = time.time() - start_time
                state.stats["path_length"] = len(state.solution_path)
                state.stats["cells_visited"] = len(state.visited_cells)
                
                if state.solution_path:
                    logger.info(f"Solved maze using {state.algorithm.name}")
                else:
                    logger.warning(f"No solution found using {state.algorithm.name}")
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def reset_maze(self):
        state.running = False
        state.paused = False
        state.solution_path = []
        state.visited_cells = set()
        state.reset_stats()
        logger.info("Maze reset")

    def toggle_theme(self):
        current_theme = state.current_theme
        themes = ["light", "dark", "high_contrast"]
        current_index = themes.index(current_theme)
        next_index = (current_index + 1) % len(themes)
        state.current_theme = themes[next_index]
        logger.info(f"Theme changed to {state.current_theme}")
        return True

class AlgorithmSelector(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.open = False
        self.options = list(AlgorithmType)
        self.option_height = 30
        self.hovered = False
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        pygame.draw.rect(screen, theme.colors["button"], self.rect, border_radius=8)
        font = pygame.font.Font(None, 24)
        text = state.algorithm.meta.display_name
        text_surface = font.render(text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        if self.open:
            for i, algo in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.option_height,
                    self.rect.width,
                    self.option_height
                )
                pygame.draw.rect(screen, theme.colors["button"], option_rect)
                text = algo.meta.display_name
                text_surface = font.render(text, True, theme.colors["text"])
                text_rect = text_surface.get_rect(center=option_rect.center)
                screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return True
            elif self.open:
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

class InfoPanel(UIComponent):
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible = False
        self.current_info = ""
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        theme = ThemeManager.get_theme(state.current_theme)
        pygame.draw.rect(screen, theme.colors["background"], self.rect)
        pygame.draw.rect(screen, theme.colors["wall"], self.rect, 2)
        
        font = pygame.font.Font(None, 24)
        lines = self.current_info.split('\n')
        y_offset = 10
        
        for line in lines:
            text_surface = font.render(line, True, theme.colors["text"])
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 25
    
    def show_algorithm_info(self, algorithm: AlgorithmType):
        self.current_info = (
            f"Algorithm: {algorithm.meta.display_name}\n"
            f"Complexity: {algorithm.meta.complexity}\n"
            f"Description: {algorithm.meta.description}"
        )
        self.visible = True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.visible = False
                return True
        return False

class ControlPanel(UIComponent):
    def __init__(self, screen_width: int, screen_height: int):
        self.rect = pygame.Rect(
            0,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT,
            screen_width,
            UIConstants.CONTROL_PANEL_HEIGHT
        )
        
        button_y = screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING
        
        self.buttons = [
            Button(
                UIConstants.BUTTON_PADDING,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Generate Maze",
                self.generate_maze
            ),
            Button(
                UIConstants.BUTTON_PADDING + UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Solve Maze",
                self.solve_maze
            ),
            Button(
                UIConstants.BUTTON_PADDING + (UIConstants.BUTTON_WIDTH + UIConstants.BUTTON_PADDING) * 2,
                button_y,
                UIConstants.BUTTON_WIDTH,
                UIConstants.BUTTON_HEIGHT,
                "Reset",
                self.reset_maze
            )
        ]

        self.algorithms = {
            AlgorithmType.DFS: DFSMazeGenerator(),
            AlgorithmType.BFS: BFSMazeGenerator(),
            AlgorithmType.ASTAR: AStarMazeGenerator(),
            AlgorithmType.PRIM: PrimMazeGenerator()
        }

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
        
        self.algorithm_selector = AlgorithmSelector(
            screen_width - 220,
            screen_height - UIConstants.CONTROL_PANEL_HEIGHT + UIConstants.BUTTON_PADDING,
            200,
            UIConstants.BUTTON_HEIGHT
        )
        
        self.info_panel = InfoPanel(
            pygame.Rect(
                screen_width - 250,
                screen_height - 300,
                240,
                200
            )
        )
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["background"],
            self.rect
        )
        
        pygame.draw.rect(
            screen,
            ThemeManager.get_theme(state.current_theme).colors["wall"],
            self.rect,
            2
        )
        
        for button in self.buttons:
            button.draw(screen)
            
        self.speed_slider.draw(screen)
        self.algorithm_selector.draw(screen)
        self.info_panel.draw(screen)
        
        if self.algorithm_selector.hovered:
            self.info_panel.show_algorithm_info(state.algorithm)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        if (self.speed_slider.handle_event(event) or
            self.algorithm_selector.handle_event(event) or
            self.info_panel.handle_event(event)):
            return True
            
        return False

    def generate_maze(self):
        if not state.running:
            state.running = True
            state.solution_path = []
            state.visited_cells = set()
            
            start_time = time.time()
            
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                # Generate the maze and store it in the state
                state.maze = algorithm.generate(state.width, state.height)
                state.stats["generation_time"] = time.time() - start_time
                state.stats["cells_visited"] = 0
                logger.info(f"Generated maze using {state.algorithm.name}")
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def solve_maze(self):
        if state.running and not state.paused and hasattr(state, 'maze'):
            start_time = time.time()
            
            algorithm = self.algorithms.get(state.algorithm)
            if algorithm:
                solution = algorithm.solve(
                    state.maze,
                    state.start_pos,
                    state.end_pos
                )
                
                state.solution_path = solution if solution is not None else []
                state.stats["solving_time"] = time.time() - start_time
                state.stats["path_length"] = len(state.solution_path)
                state.stats["cells_visited"] = len(state.visited_cells)
                
                if state.solution_path:
                    logger.info(f"Solved maze using {state.algorithm.name}")
                else:
                    logger.warning(f"No solution found using {state.algorithm.name}")
            else:
                logger.error(f"Algorithm {state.algorithm.name} not implemented")

    def reset_maze(self):
        state.running = False
        state.paused = False
        state.solution_path = []
        state.visited_cells = set()
        state.reset_stats()
        logger.info("Maze reset")

    def toggle_theme(self):
        current_theme = state.current_theme
        themes = ["light", "dark", "high_contrast"]
        current_index = themes.index(current_theme)
        next_index = (current_index + 1) % len(themes)
        state.current_theme = themes[next_index]
        logger.info(f"Theme changed to {state.current_theme}")

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
        self.maze_height = self.screen.get_height() - UIConstants.CONTROL_PANEL_HEIGHT
        self.maze_width = self.screen.get_width()
    
    def clear(self):
        self.screen.fill(ThemeManager.get_theme(state.current_theme).colors["background"])
    
    def render(self, maze: List[List[int]], screen: pygame.Surface) -> None:
        if self.dirty:
            self._update_cache(maze)
        self._draw_from_cache(screen)
        self.control_panel.draw(screen)
    
    def draw_cell(self, pos: Tuple[int, int], cell_type: str) -> None:
        x, y = pos
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        color = ThemeManager.get_theme(state.current_theme).colors[cell_type]
        pygame.draw.rect(self.screen, color, rect)
    
    def draw_stats(self, stats: Dict[str, Any]) -> None:
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
        self.cache = {}
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if cell == 1:  # Wall
                    self.cache[(x, y)] = ThemeManager.get_theme(state.current_theme).colors["wall"]
        self.dirty = False
    
    def _draw_from_cache(self, screen: pygame.Surface) -> None:
        for (x, y), color in self.cache.items():
            rect = pygame.Rect(
                x * self.cell_size,
                y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, color, rect)

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
    
    def _handle_swipe(self, dx: float, dy: float, state: MazeState) -> None:
        pass  # Implement swipe handling logic
    
    def _handle_tap(self, event: pygame.event.Event, state: MazeState) -> None:
        pass  # Implement tap handling logic

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

@error_handler
def update_game_state():
    pass  # Add game state update logic here

@error_handler
def render_frame(renderer: MazeRenderer):
    try:
        renderer.clear()
        
        if hasattr(state, 'maze'):
            renderer.render(state.maze, renderer.screen)
        
        if state.show_animation:
            for cell in state.visited_cells:
                renderer.draw_cell(cell, "visited")
        
        if state.solution_path:
            for cell in state.solution_path:
                renderer.draw_cell(cell, "path")
        
        renderer.draw_cell(state.start_pos, "start")
        renderer.draw_cell(state.end_pos, "end")
        
        if state.show_stats:
            renderer.draw_stats({
                "Generation Time": f"{state.stats['generation_time']:.2f}s",
                "Solving Time": f"{state.stats['solving_time']:.2f}s",
                "Cells Visited": state.stats['cells_visited']
            })
        
        if state.show_grid:
            renderer.draw_grid_lines()
        
        pygame.display.flip()
        
    except Exception as e:
        logger.error(f"Error in render_frame: {str(e)}")
        raise

def setup_display():
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
            
            renderer.control_panel.handle_event(event)
            touch_handler.handle_touch(event, state)
            
        if state.running and not state.paused:
            update_game_state()
            
        render_frame(renderer)
        clock.tick(MazeConfig.Animation.FPS)

if __name__ == "__main__":
    def initialize_pygame():
        pygame.init()
        pygame.font.init()
        logger.info("Pygame initialized")
    
    initialize_pygame()
    setup_display()
    game_loop()

