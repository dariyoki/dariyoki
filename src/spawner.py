import pygame
import random
from src.utils import Glow
from src.sprites import spawner_imgs
from src.enemy import Ninja


class Spawner:
    def __init__(self, location, size, cool_down, number_of_enemies) -> None:
        self.location = location
        self.size = size
        self.spawn_images = [
            pygame.transform.scale(spawner_imgs[0], size),
            pygame.transform.scale(spawner_imgs[1], size),
        ]
        self.image = self.spawn_images[0]
        self.rect = self.image.get_rect()
        self.angle = 0
        self.glow = Glow(self.image, (11, 3, 25), self.location)
        self.enemies = []
        self.time_passed = 0
        self.cool_down = cool_down
        self.number_of_enemies = number_of_enemies

    def spawn(self, n):
        self.enemies += [Ninja(
            self.location[0] + random.randrange(self.size[0]),
            self.location[1],
            weapon=None,
            clan="shadow",
            speed=1.7,
        ) for _ in range(n)]

    def update(self, raw_dt):
        self.time_passed += raw_dt
        if self.time_passed > self.cool_down:
            self.spawn(random.randrange(*self.number_of_enemies))
            self.time_passed = 0

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.image, (
            self.location[0] - camera[0],
            self.location[1] - camera[1]
        ))
        self.glow.draw(screen, camera)
