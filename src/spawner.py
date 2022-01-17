import pygame
from src.utils import Glow
from src.sprites import spawner_imgs


class Spawner:
    def __init__(self, location, size) -> None:
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

    def update(self, dt):
        # self.angle += 1 * dt
        # self.image = pygame.transform.rotozoom(self.spawn_images[0], int(self.angle), 1)
        # self.rect = self.image.get_rect(topleft=self.location)
        pass

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.image, (
            self.location[0] - camera[0],
            self.location[1] - camera[1]
        ))
        self.glow.draw(screen, camera)
