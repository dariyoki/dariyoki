import pygame

from src.generics import Pos
from typing import Sequence


class Animation:
    def __init__(self, frames: Sequence[pygame.surface.Surface], speed: float):
        self.frames = frames
        self.speed = speed

        self.f_len = len(frames)
        self.index = 0
        self.animated_once = False

    def update(self, dt):
        self.index += self.speed * dt
        if self.index > self.f_len:
            self.index = 0
            self.animated_once = True

    def draw(self, screen: pygame.Surface, pos: Pos):
        screen.blit(self.frames[int(self.index)], pos)

    def play(self, screen, pos, dt):
        self.update(dt)
        self.draw(screen, pos)
