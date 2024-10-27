import pygame
from ui.ui_component import UIComponent
from theme.theme_manager import ThemeManager
import state

class Slider(UIComponent):
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float, initial_val: float, label: str):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_radius = 8
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        
        # Draw slider track
        pygame.draw.rect(screen, theme.colors["slider"], self.rect, border_radius=4)
        
        # Calculate handle position
        handle_x = self._value_to_pos()
        handle_pos = (handle_x, self.rect.centery)
        
        # Draw handle
        pygame.draw.circle(screen, theme.colors["button"], handle_pos, self.handle_radius)
        pygame.draw.circle(screen, theme.colors["wall"], handle_pos, self.handle_radius, 2)
        
        # Draw label
        font = pygame.font.Font(None, 24)
        label_text = f"{self.label}: {int(self.value)}"
        text_surface = font.render(label_text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(
            bottomleft=(self.rect.left, self.rect.top - 5)
        )
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(
                self._value_to_pos() - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
            
        return False
    
    def _value_to_pos(self) -> int:
        """Convert current value to pixel position"""
        value_range = self.max_val - self.min_val
        pos_range = self.rect.width
        normalized_value = (self.value - self.min_val) / value_range
        return int(self.rect.left + (normalized_value * pos_range))
    
    def _update_value(self, x_pos: int) -> None:
        """Update slider value based on mouse position"""
        pos_range = self.rect.width
        value_range = self.max_val - self.min_val
        normalized_pos = max(0, min(1, (x_pos - self.rect.left) / pos_range))
        self.value = self.min_val + (normalized_pos * value_range)
        state.speed = self.value  # Update game speed in state
