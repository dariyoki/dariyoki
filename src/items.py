import pygame
from enum import Enum
from src.utils import circle_surf


class HoverDirection(Enum):
    UP = "UP",
    DOWN = "DOWN"


class Item:
    def __init__(self, image: pygame.Surface):
        self.image = image
        self.rect = self.image.get_bounding_rect()
        self.pos = (0, 0)

        # Hover
        self.hover_movement = 0
        self.hover_speed = 1
        self.hover_direction = HoverDirection.UP.name
        self.i_radius = 0

    def update(self, pos, dt):
        self.pos = pos

        if self.hover_direction == "UP":
            self.hover_movement -= self.hover_speed * dt
            self.i_radius -= (self.hover_speed * dt) / 4
            if self.hover_movement < 0:
                self.hover_direction = HoverDirection.DOWN.name
        elif self.hover_direction == "DOWN":
            self.hover_movement += self.hover_speed * dt
            self.i_radius += (self.hover_speed * dt) / 4
            if self.hover_movement > 20:
                self.hover_direction = HoverDirection.UP.name

        self.pos[1] += self.hover_movement
        self.rect = self.image.get_rect(topleft=tuple(self.pos))

    def draw(self, screen, camera):
        screen.blit(self.image, (self.pos[0] - camera[0], self.pos[1] - camera[1]))
        screen.blit(circle_surf(radius=self.rect.height + self.i_radius, color=(20, 40, 40)),
                    (self.pos[0] - 12 - camera[0],
                     self.pos[1] - 11 - camera[1]),
                    special_flags=pygame.BLEND_RGB_ADD)



