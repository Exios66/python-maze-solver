class MazeConfig:
    class Screen:
        MIN_WIDTH = 800
        MIN_HEIGHT = 600
        TITLE = "Maze Visualizer"

    class UI:
        CELL_SIZE_DESKTOP = 20
        CELL_SIZE_MOBILE = 30
        CONTROL_PANEL_HEIGHT = 120

    class Animation:
        FPS = 60
        MIN_SPEED = 1
        MAX_SPEED = 100
        DEFAULT_SPEED = 50

    class Colors:
        BACKGROUND = (0, 0, 0)
        WALL = (255, 255, 255)
        PATH = (255, 165, 0)
        VISITED = (100, 100, 100)
        START = (0, 255, 0)
        END = (255, 0, 0)
