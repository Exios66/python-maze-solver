class UIComponent:
    """Base class for UI components"""
    def draw(self, screen):
        pass

    def handle_event(self, event):
        return False
