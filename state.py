class MazeState:
    def __init__(self):
        self.running = False
        self.paused = False
        self.maze = None
        self.solution_path = []
        self.visited_cells = set()
        self.stats = {"generation_time": 0, "solving_time": 0, "cells_visited": 0}
        # Add other state variables as needed

state = MazeState()
