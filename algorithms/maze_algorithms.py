from typing import List, Tuple, Set
import random
from abc import ABC, abstractmethod
import heapq

class MazeAlgorithm(ABC):
    @abstractmethod
    def generate(self, width: int, height: int) -> List[List[int]]:
        pass
    
    @abstractmethod
    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass

class DFSMazeGenerator(MazeAlgorithm):
    def generate(self, width: int, height: int) -> List[List[int]]:
        # Initialize maze with walls
        maze = [[1 for _ in range(width)] for _ in range(height)]
        
        def carve_path(x: int, y: int):
            maze[y][x] = 0  # Mark current cell as path
            
            # Define possible directions (right, down, left, up)
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < width and 0 <= new_y < height and 
                    maze[new_y][new_x] == 1):
                    # Carve through the wall between cells
                    maze[y + dy//2][x + dx//2] = 0
                    carve_path(new_x, new_y)
        
        # Start from a random point
        start_x = random.randrange(0, width, 2)
        start_y = random.randrange(0, height, 2)
        carve_path(start_x, start_y)
        
        return maze
    
    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and 
                    maze[new_y][new_x] == 0):
                    neighbors.append((new_x, new_y))
            return neighbors
        
        visited = set()
        path = []
        
        def dfs(x: int, y: int) -> bool:
            if (x, y) == end:
                path.append((x, y))
                return True
                
            visited.add((x, y))
            
            for next_x, next_y in get_neighbors(x, y):
                if (next_x, next_y) not in visited:
                    if dfs(next_x, next_y):
                        path.append((x, y))
                        return True
            
            return False
        
        # Return empty list if no path is found
        if not dfs(start[0], start[1]):
            return []
        
        return list(reversed(path))

class BFSMazeGenerator(MazeAlgorithm):
    def generate(self, width: int, height: int) -> List[List[int]]:
        from collections import deque
        
        maze = [[1 for _ in range(width)] for _ in range(height)]
        start = (1, 1)
        queue = deque([start])
        visited = {start}
        
        while queue:
            x, y = queue.popleft()
            maze[y][x] = 0
            
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < width and 0 <= new_y < height and 
                    (new_x, new_y) not in visited):
                    maze[y + dy//2][x + dx//2] = 0
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))
        
        return maze
    
    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == end:
                return path
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and 
                    maze[new_y][new_x] == 0 and (new_x, new_y) not in visited):
                    queue.append(((new_x, new_y), path + [(new_x, new_y)]))
                    visited.add((new_x, new_y))
        
        return []

class AStarMazeGenerator(MazeAlgorithm):
    def generate(self, width: int, height: int) -> List[List[int]]:
        maze = [[1 for _ in range(width)] for _ in range(height)]
        
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
            neighbors = []
            for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < width and 0 <= new_y < height:
                    neighbors.append((new_x, new_y))
            return neighbors
        
        start = (1, 1)
        end = (width - 2, height - 2)
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            maze[current[1]][current[0]] = 0
            
            if current == end:
                break
                
            for next_pos in get_neighbors(*current):
                tentative_g = g_score[current] + 1
                
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    came_from[next_pos] = current
                    g_score[next_pos] = tentative_g
                    f_score[next_pos] = tentative_g + heuristic(next_pos, end)
                    heapq.heappush(open_set, (f_score[next_pos], next_pos))
                    
                    # Carve path between cells
                    mid_x = (current[0] + next_pos[0]) // 2
                    mid_y = (current[1] + next_pos[1]) // 2
                    maze[mid_y][mid_x] = 0
        
        return maze

    def solve(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = [(0, start, [start])]
        closed_set = set()
        
        while open_set:
            f, current, path = heapq.heappop(open_set)
            
            if current == end:
                return path
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if (0 <= next_pos[0] < len(maze[0]) and 
                    0 <= next_pos[1] < len(maze) and 
                    maze[next_pos[1]][next_pos[0]] == 0 and 
                    next_pos not in closed_set):
                    g = len(path)
                    h = heuristic(next_pos, end)
                    f = g + h
                    heapq.heappush(open_set, (f, next_pos, path + [next_pos]))
        
        return []

class PrimMazeGenerator(MazeAlgorithm):
    def generate(self, width: int, height: int) -> List[List[int]]:
        maze = [[1 for _ in range(width)] for _ in range(height)]
        walls = []
        
        # Start with a random cell
        start_x = random.randrange(1, width - 1, 2)
        start_y = random.randrange(1, height - 1, 2)
        maze[start_y][start_x] = 0
        
        # Add surrounding walls to wall list
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_x, new_y = start_x + dx, start_y + dy
            if 0 <= new_x < width and 0 <= new_y < height:
                walls.append((new_x, new_y, start_x, start_y))
        
        # While there are walls in our list
        while walls:
            # Pick a random wall
            wall_x, wall_y, from_x, from_y = walls.pop(random.randrange(len(walls)))
            
            # Check if the cell on the opposite side of the wall is unvisited
            to_x = wall_x + (wall_x - from_x)
            to_y = wall_y + (wall_y - from_y)
            
            if (0 <= to_x < width and 0 <= to_y < height and 
                maze[to_y][to_x] == 1):  # If unvisited
                # Make the wall and cell a passage
                maze[wall_y][wall_x] = 0
                maze[to_y][to_x] = 0
                
                # Add neighboring walls
                for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                    new_x, new_y = to_x + dx, to_y + dy
                    if (0 <= new_x < width and 0 <= new_y < height and 
                        maze[new_y][new_x] == 1):
                        walls.append((new_x, new_y, to_x, to_y))
        
        return maze
