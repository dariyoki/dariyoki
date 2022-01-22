import pygame
import random
from src.utils import Glow
from src.sprites import spawner_imgs


class Spawner:
    def __init__(self, location, size, cool_down, number_of_enemies, enemy, enemy_size) -> None:
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
        self.enemies: list[enemy] = []
        self.time_passed = 0
        self.cool_down = cool_down
        self.number_of_enemies = number_of_enemies
        self.enemy = enemy
        self.enemy_size = enemy_size

        self.spawning_rects = []
        self.spawn_it = False
        self.last_len = 0
        self.once = True

    def spawn(self, n):
        if len(self.spawning_rects) < n - 1:
            self.spawning_rects = [pygame.Rect(
                self.location[0] + random.randrange(self.size[0]),
                self.location[1],
                300,
                300
            ) for _ in range(n)]

    def spawn_enemies(self, n):
        self.enemies += [self.enemy(
            self.location[0] + random.randrange(self.size[0]),
            self.location[1],
            weapon=None,
            clan="shadow",
            speed=1.7,
        ) for _ in range(n)]

    def update(self, raw_dt, dt):
        self.time_passed += raw_dt
        if self.time_passed > self.cool_down:
            print('hasp1')
            self.spawn_it = True
            self.once = True
            self.time_passed = 0

        if self.spawn_it:
            self.image = self.spawn_images[1]
            self.time_passed = 0
            self.spawn(random.randrange(*self.number_of_enemies))
        else:
            self.image = self.spawn_images[0]

        for rect in self.spawning_rects:
            v = 0
            if rect.width > self.enemy_size[0]:
                rect.width -= 0.4 * dt
            else:
                v += 1

            if rect.height > self.enemy_size[1]:
                rect.height -= 0.4 * dt
            else:
                v += 1

            if v == 2:
                self.spawn_it = False
                self.last_len = len(self.spawning_rects)
                self.spawning_rects = []
                break

        if not self.spawn_it and self.last_len > 0:
            if self.once:
                self.spawn_enemies(self.last_len)
                self.once = False

    def draw_spawn(self, screen, camera):
        for rect in self.spawning_rects:
            pygame.draw.rect(screen, 'red', (
                rect.x - camera[0],
                rect.y - camera[1],
                *rect.size
            ), width=3)

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.image, (
            self.location[0] - camera[0],
            self.location[1] - camera[1]
        ))
        self.glow.draw(screen, camera)
