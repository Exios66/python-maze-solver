import pygame
from ui.ui_component import UIComponent
from theme.theme_manager import ThemeManager
import state

class Button(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        color = theme.colors["button_hover"] if self.hovered else theme.colors["button"]
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Draw button border
        pygame.draw.rect(screen, theme.colors["wall"], self.rect, 2, border_radius=8)
        
        # Draw button text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False
