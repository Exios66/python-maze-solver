from typing import List, Set, Tuple, Dict, Any
from algorithms.algorithm_types import AlgorithmType

class MazeState:
    def __init__(self):
        # Maze state
        self.maze: List[List[int]] = []
        self.width: int = 0
        self.height: int = 0
        self.start_pos: Tuple[int, int] = (1, 1)
        self.end_pos: Tuple[int, int] = (0, 0)
        
        # Algorithm state
        self.algorithm: AlgorithmType = AlgorithmType.DFS
        self.running: bool = False
        self.paused: bool = False
        self.show_animation: bool = True
        self.show_grid: bool = True
        
        # Animation state
        self.speed: float = 50.0
        self.visited_cells: Set[Tuple[int, int]] = set()
        self.solution_path: List[Tuple[int, int]] = []
        
        # UI state
        self.current_theme: str = "dark"
        self.stats: Dict[str, Any] = {
            "generation_time": 0.0,
            "solving_time": 0.0,
            "cells_visited": 0,
            "path_length": 0
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = {
            "generation_time": 0.0,
            "solving_time": 0.0,
            "cells_visited": 0,
            "path_length": 0
        }

# Create global state instance
state = MazeState()
