import pygame
from abc import ABC, abstractmethod

class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the component on the screen"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events
        
        Returns:
            bool: True if the event was handled, False otherwise
        """
        pass
