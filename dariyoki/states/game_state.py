"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import abc

import pygame


class GameState(abc.ABC):
    def __init__(self, state_name: str, screen: pygame.Surface):
        self.state_name = state_name
        self.screen = screen

        # Visuals
        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(120)
        self.transition_overlay_surface = pygame.Surface(screen.get_size())
        self.transition_overlay_surface.set_alpha(0)
        self.transition_overlay_surface_alpha = 0
        self.transitioning = False
        self.transition_fade_speed = 5.7

    def handle_fade_in(self, dt) -> bool:
        self.transition_overlay_surface_alpha += (
            self.transition_fade_speed * dt
        )
        if self.transition_overlay_surface_alpha > 255:
            self.transition_overlay_surface_alpha = 255
            return True

        return False

    def handle_fade_out(self, dt) -> bool:
        self.transition_overlay_surface_alpha -= (
            self.transition_fade_speed * dt
        )
        if self.transition_overlay_surface_alpha < 0:
            self.transition_overlay_surface_alpha = 0
            return True

        return False
