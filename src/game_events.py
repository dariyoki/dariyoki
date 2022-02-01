import pygame
from enum import Enum
from src.sprites import blue_ribbon
from src.globals import general_info


class Achievements(Enum):
    ...


class Achievement:
    def __init__(self):
        self.image = blue_ribbon.copy()


class GeneralInfo:
    def __init__(self, msg, color):
        self.msg = msg
        self.color = color
        self.font = pygame.font.SysFont("arialrounded", 18)
        self.text = self.font.render(msg, True, color)
        self.text_rect = self.text.get_rect(center=(1100//2, 270))
        self.pos = list(self.text_rect.topleft)
        self.alpha = 0
        self.size = 18
        self.fade_in = True

    def draw(self, screen, dt):
        if self.fade_in and self.alpha < 255:
            self.alpha += 7.6 * dt
        else:
            self.fade_in = False

        if not self.fade_in and self.alpha > 0:
            self.alpha -= 3.6 * dt
            if self.alpha < 0:
                general_info[0] = None

        if self.pos[1] > 150:
            self.pos[1] -= 5.3 * dt

        if self.size < 21:
            self.size += 0.9 * dt

        self.font = pygame.font.SysFont("arialrounded", int(self.size))
        self.text = self.font.render(self.msg, True, self.color)
        self.text.set_alpha(self.alpha)
        screen.blit(self.text, self.pos)


