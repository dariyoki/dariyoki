"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import math

import pygame

from dariyoki.animation import Animation
from dariyoki.generics import EventInfo, Vec
from dariyoki.utils import turn_left


class Jetpack:
    SPEED = 5.3
    ANIMATION_SPEED = 0.4
    TIME_LIMIT = 10
    TOTAL_TIMER_RECT_WIDTH = 100
    FONT = pygame.font.Font(None, 50)

    def __init__(self, player_instance, pos: Vec):
        self.player_instance = player_instance
        self.smooth_diagonal = math.sqrt(2) / 2
        self.vec = pos.copy()
        frames = player_instance.assets["dari_jetpack"][1:]
        self.animation = Animation(frames, self.ANIMATION_SPEED)
        self.left_animation = Animation(
            turn_left(frames), self.ANIMATION_SPEED
        )
        self.facing_right: bool = True
        self.countdown = self.TIME_LIMIT
        self.width_mult = self.TOTAL_TIMER_RECT_WIDTH / self.TIME_LIMIT
        self.timer_fore_rect = pygame.Rect(
            50, 200, self.TOTAL_TIMER_RECT_WIDTH, 40
        )
        self.timer_back_rect = self.timer_fore_rect.copy()

    def update(self, event_info: EventInfo) -> None:
        dx, dy = 0, 0
        if event_info["keys"][pygame.K_w]:
            dy -= self.SPEED * event_info["dt"]
        if event_info["keys"][pygame.K_s]:
            dy += self.SPEED * event_info["dt"]
        if event_info["keys"][pygame.K_d]:
            dx += self.SPEED * event_info["dt"]
        if event_info["keys"][pygame.K_a]:
            dx -= self.SPEED * event_info["dt"]

        if dx < 0:
            self.facing_right = False
        elif dx > 0:
            self.facing_right = True

        if dx and dy:
            dx *= self.smooth_diagonal
            dy *= self.smooth_diagonal

        self.vec += (dx, dy)
        self.player_instance.update_coord(dx, dy)

        if self.facing_right:
            self.animation.update(event_info["dt"])
        else:
            self.left_animation.update(event_info["dt"])

        # Timer
        self.countdown -= event_info["raw dt"]
        self.timer_fore_rect.width = self.countdown * self.width_mult

    def draw(self, screen: pygame.Surface, camera: Vec) -> None:
        if self.facing_right:
            self.animation.draw(screen, self.vec - camera)
        else:
            self.left_animation.draw(screen, self.vec - camera)

        pygame.draw.rect(screen, "black", self.timer_back_rect)
        pygame.draw.rect(screen, "white", self.timer_fore_rect)
        if self.countdown < 10:
            color = "green"
        if self.countdown < 5:
            color = "yellow"
        if self.countdown < 3:
            color = "red"
        count_down_surf = self.FONT.render(
            f"{self.countdown:.2f}", True, color
        )
        screen.blit(
            count_down_surf,
            (
                self.timer_fore_rect.x,
                self.timer_fore_rect.y + count_down_surf.get_height(),
            ),
        )
