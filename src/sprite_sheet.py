import pygame
from typing import List


class SpriteSheet:
    def __init__(self, image: pygame.Surface, width: float, height: float, bg: tuple[int, int, int] = (0, 0, 0)):
        self.bg = bg
        self.sheet = image

        # Width of each sprite NOT sprite sheet
        self.width, self.height = 0, 0

    def get_images(self, rows: int, columns: int, width: float, height: float, fixer: float = 1):
        self.width = width
        self.height = height

        images = []

        for i in range(rows):
            for e in range(columns):
                # Mod image
                image = self.sheet.subsurface(pygame.Rect((e * width), ((i * fixer) * columns), width, height))
                r = image.get_bounding_rect()
                image = image.subsurface(r)

                images.append(image)

        return images

