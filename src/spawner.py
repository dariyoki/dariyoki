import pygame
import random
from src.utils import Glow, camerify as c
from src.sprites import spawner_imgs
from src._globals import shurikens, spawners
from src.player import Player
from src.widgets import LoadingBar


class Spawner:
    def __init__(self, location, size, cool_down, number_of_enemies, enemy, enemy_size, hp) -> None:
        self.location = location
        self.size = size
        self.spawn_images = [
            pygame.transform.scale(spawner_imgs[0], size),
            pygame.transform.scale(spawner_imgs[1], size),
        ]
        self.init_spawn_images = list(self.spawn_images)
        self.image = self.spawn_images[0]
        self.damage_surf = pygame.Surface(size)
        self.damage_surf.fill("red")
        self.damage_alpha = 100
        self.damage_surf.set_alpha(self.damage_alpha)
        self.init_rect = pygame.Rect(tuple(self.location), self.size)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.glow = Glow(self.image, (11, 3, 25), self.location)
        self.enemies: list[enemy] = []
        self.time_passed = 0
        self.cool_down = cool_down
        self.number_of_enemies = number_of_enemies
        self.enemy = enemy
        self.enemy_size = enemy_size
        self.hp = hp
        self.max_hp = hp
        self.camera = [0, 0]
        self.dt = 0

        self.spawning_rects = []
        self.spawn_it = False
        self.last_len = 0
        self.once = True
        self.gain_damage = False

        self.hp_bar_size = (160, 20)
        self.hp_bar = LoadingBar(
            value=self.hp,
            fg_color=(179, 2, 43),
            bg_color='black',
            rect=pygame.Rect((0, 0), self.hp_bar_size)
        )

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

    def handle_shuriken_collision(self):
        for shuriken in shurikens:
            if isinstance(shuriken.launcher, Player) and shuriken.rect.colliderect((
                c(self.init_rect.topleft, self.camera),
                self.size
            )):
                self.hp -= shuriken.damage
                shurikens.remove(shuriken)
                self.damage_alpha = 100
                self.gain_damage = True
                break

    def update(self, event_info):
        self.dt = event_info["dt"]
        self.handle_shuriken_collision()

        if self.hp <= 0:
            spawners.remove(self)

        self.angle += 0.7 * event_info["dt"]

        self.time_passed += event_info["raw dt"]
        if self.time_passed > self.cool_down:
            self.spawn_it = True
            self.once = True
            self.time_passed = 0

        if len(self.enemies) > 10:
            self.time_passed = 0

        if self.spawn_it:
            self.image = pygame.transform.rotate(self.spawn_images[1], self.angle)
            self.time_passed = 0
            self.spawn(random.randrange(*self.number_of_enemies))
        else:
            self.image = pygame.transform.rotate(self.spawn_images[0], self.angle)

        self.rect = self.image.get_rect(center=self.init_rect.center)

        for rect in self.spawning_rects:
            v = 0
            if rect.width > self.enemy_size[0]:
                rect.width -= 0.4 * event_info["dt"]
            else:
                v += 1

            if rect.height > self.enemy_size[1]:
                rect.height -= 0.4 * event_info["dt"]
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

        self.rect = self.image.get_rect(topleft=self.rect.topleft)
        self.hp_bar.value = self.hp * (self.hp_bar_size[0] / self.max_hp)
        self.hp_bar.rect.center = (
            self.rect.midtop[0],
            self.rect.midtop[1] - 10
        )

    def draw_spawn(self, screen, camera):
        for rect in self.spawning_rects:
            pygame.draw.rect(screen, 'red', (
                rect.x - camera[0],
                rect.y - camera[1],
                *rect.size
            ), width=3)

    def draw(self, screen: pygame.Surface, camera):
        self.camera = camera
        pos = c(self.rect.topleft, camera)
        self.spawn_images = [
            self.init_spawn_images[0].copy(),
            self.init_spawn_images[1].copy(),
        ]
        if self.gain_damage:
            for surf in self.spawn_images:
                surf.blit(self.damage_surf, (0, 0))

            self.damage_surf.set_alpha(int(self.damage_alpha))
            self.damage_alpha -= 10.5 * self.dt
            if self.damage_alpha < 0:
                self.gain_damage = False

        screen.blit(self.image, pos)
        self.glow.draw(screen, camera)
        self.hp_bar.draw(screen, camera, moving=True)
