import pygame
from src.sprites import items, item_size
from src.angular_movement import Angle


# TODO: Work on shurikens
class Shuriken(Angle):
    def __init__(self, start, target, speed):
        super().__init__(start, target, speed, item_size)
        self.shuriken_img = items["shuriken"]
        self.image = self.shuriken_img.copy()
        self.damage = 30

    def draw(self, screen):
        # pygame.draw.rect(screen, 'red', self.rect, width=1)
        screen.blit(self.image, self.rect)


