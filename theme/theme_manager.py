from typing import Dict, Tuple

class Theme:
    def __init__(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        self.name = name
        self.colors = colors

class ThemeManager:
    themes: Dict[str, Theme] = {
        "dark": Theme("Dark", {
            "background": (0, 0, 0),
            "wall": (50, 50, 50),
            "path": (255, 165, 0),
            "visited": (144, 238, 144),
            "start": (50, 205, 50),
            "end": (220, 20, 60),
            "text": (255, 255, 255),
            "button": (0, 128, 128),
            "button_hover": (0, 153, 153),
            "slider": (0, 191, 255),
        }),
        "light": Theme("Light", {
            "background": (255, 255, 255),
            "wall": (100, 100, 100),
            "path": (255, 140, 0),
            "visited": (144, 238, 144),
            "start": (34, 139, 34),
            "end": (178, 34, 34),
            "text": (0, 0, 0),
            "button": (70, 130, 180),
            "button_hover": (100, 149, 237),
            "slider": (30, 144, 255),
        }),
        "contrast": Theme("High Contrast", {
            "background": (0, 0, 0),
            "wall": (255, 255, 255),
            "path": (255, 255, 0),
            "visited": (0, 255, 0),
            "start": (0, 255, 0),
            "end": (255, 0, 0),
            "text": (255, 255, 255),
            "button": (128, 128, 128),
            "button_hover": (192, 192, 192),
            "slider": (255, 255, 255),
        })
    }

    @classmethod
    def get_theme(cls, name: str) -> Theme:
        return cls.themes.get(name, cls.themes["dark"])
