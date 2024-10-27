from abc import ABC, abstractmethod
import random
from algorithms.maze_algorithms import MazeAlgorithm
from typing import List, Tuple

class PrimMazeGenerator(MazeAlgorithm):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        
    def generate(self, width: int, height: int) -> List[List[int]]:
        # Start with a grid full of walls
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        
        start_x = random.randint(0, self.width - 1)
        start_y = random.randint(0, self.height - 1)
        self.maze[start_y][start_x] = 0
        
        # Initialize the frontier cells
        frontier = []
        self._add_frontier_cells(start_x, start_y, frontier)
        
        while frontier:
            # Pick a random frontier cell
            current = random.choice(frontier)
            frontier.remove(current)
            x, y = current
            
            # Connect it to a random visited neighbor
            neighbors = self._get_visited_neighbors(x, y)
            if neighbors:
                nx, ny = random.choice(neighbors)
                self.maze[y][x] = 0
                # Carve passage between cells
                self.maze[(y + ny) // 2][(x + nx) // 2] = 0
                
                # Add new frontier cells
                self._add_frontier_cells(x, y, frontier)
        
        return self.maze
    
    def _add_frontier_cells(self, x, y, frontier):
        """Add unvisited cells that are two steps away from current cell"""
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.width and 0 <= new_y < self.height and 
                self.maze[new_y][new_x] == 1 and 
                (new_x, new_y) not in frontier):
                frontier.append((new_x, new_y))
    
    def _get_visited_neighbors(self, x, y):
        """Get list of visited neighbors that are two cells away"""
        neighbors = []
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and 
                self.maze[ny][nx] == 0):
                neighbors.append((nx, ny))
        return neighbors

    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Solve the maze using a simple depth-first search
        Args:
            maze: The maze to solve
            start: Starting position (x, y)
            end: End position (x, y)
        Returns:
            List of positions representing the solution path
        """
        if not start or not end:
            return []
            
        visited = set()
        path = []
        
        def dfs(current):
            if current == end:
                return True
                
            x, y = current
            visited.add(current)
            
            # Try all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                next_pos = (next_x, next_y)
                
                if (0 <= next_x < len(maze[0]) and 
                    0 <= next_y < len(maze) and 
                    maze[next_y][next_x] == 0 and 
                    next_pos not in visited):
                    
                    path.append(next_pos)
                    if dfs(next_pos):
                        return True
                    path.pop()
                    
            return False
        
        path.append(start)
        dfs(start)
        return path
