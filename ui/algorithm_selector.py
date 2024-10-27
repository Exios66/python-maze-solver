import pygame
from ui.ui_component import UIComponent
from theme.theme_manager import ThemeManager
from algorithms.algorithm_types import AlgorithmType
import state

class AlgorithmSelector(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.open = False
        self.options = list(AlgorithmType)
        self.option_height = 30
        self.hovered = False
        self.dropdown_surface = None
        self.needs_update = True
        
    def draw(self, screen: pygame.Surface) -> None:
        theme = ThemeManager.get_theme(state.current_theme)
        
        # Draw main button
        pygame.draw.rect(screen, theme.colors["button"], self.rect, border_radius=8)
        pygame.draw.rect(screen, theme.colors["wall"], self.rect, 2, border_radius=8)
        
        # Draw current algorithm name
        font = pygame.font.Font(None, 24)
        text = state.algorithm.meta.display_name
        text_surface = font.render(text, True, theme.colors["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw dropdown if open
        if self.open:
            if self.needs_update:
                self._update_dropdown_surface(theme)
            
            dropdown_rect = pygame.Rect(
                self.rect.x,
                self.rect.bottom,
                self.rect.width,
                self.option_height * len(self.options)
            )
            screen.blit(self.dropdown_surface, dropdown_rect)
    
    def _update_dropdown_surface(self, theme):
        height = self.option_height * len(self.options)
        self.dropdown_surface = pygame.Surface((self.rect.width, height), pygame.SRCALPHA)
        
        for i, algo in enumerate(self.options):
            option_rect = pygame.Rect(0, i * self.option_height, self.rect.width, self.option_height)
            
            # Draw option background
            pygame.draw.rect(self.dropdown_surface, theme.colors["button"], option_rect)
            pygame.draw.rect(self.dropdown_surface, theme.colors["wall"], option_rect, 1)
            
            # Draw option text
            font = pygame.font.Font(None, 24)
            text = algo.meta.display_name
            text_surface = font.render(text, True, theme.colors["text"])
            text_rect = text_surface.get_rect(center=option_rect.center)
            self.dropdown_surface.blit(text_surface, text_rect)
        
        self.needs_update = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if main button clicked
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                self.needs_update = True
                return True
                
            # Check if option clicked
            elif self.open:
                dropdown_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom,
                    self.rect.width,
                    self.option_height * len(self.options)
                )
                
                if dropdown_rect.collidepoint(event.pos):
                    clicked_index = (event.pos[1] - self.rect.bottom) // self.option_height
                    if 0 <= clicked_index < len(self.options):
                        state.algorithm = self.options[clicked_index]
                        self.open = False
                        self.needs_update = True
                        return True
                else:
                    self.open = False
                    self.needs_update = True
                    
        return False
