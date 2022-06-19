"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import random
from typing import Sequence

import pygame

from dariyoki.entities.enemy import Bee, Ninja
from dariyoki.entities.player import Player
from dariyoki.generics import EventInfo, Pos, Vec
from dariyoki.ui.widgets import LoadingBar
from dariyoki.utils import Glow, Time
from dariyoki.utils import camerify as c


class Spawner:
    def __init__(
        self,
        location,
        size,
        cool_down,
        number_of_enemies,
        enemy_size,
        hp,
        spawn_images: Sequence[pygame.Surface],
        border_image: pygame.Surface,
        characters,
        items,
        enemy_set: set,
    ) -> None:
        self.items = items
        self.border_image = border_image
        self.location = location
        self.size = size
        self.spawn_images = [
            pygame.transform.scale(img, size) for img in spawn_images
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
        self.time_passed = 0
        self.cool_down = cool_down
        self.number_of_enemies = number_of_enemies
        self.enemy_size = enemy_size
        self.hp = hp
        self.max_hp = hp
        self.camera = [0, 0]
        self.dt = 0
        self.characters = characters

        self.spawning_rects = []
        self.spawn_it = False
        self.last_len = 0
        self.once = True
        self.gain_damage = False
        self.interactable = False

        self.hp_bar_size = (160, 20)
        self.hp_bar = LoadingBar(
            value=self.hp,
            fg_color=(179, 2, 43),
            bg_color="black",
            rect=pygame.Rect((0, 0), self.hp_bar_size),
            border_image=border_image,
        )
        self.enemies = enemy_set

    def spawn(self, n):
        if len(self.spawning_rects) < n - 1:
            self.spawning_rects = [
                pygame.Rect(
                    self.location[0] + random.randrange(self.size[0]),
                    self.location[1],
                    300,
                    300,
                )
                for _ in range(n)
            ]

    def spawn_enemies(self, n):
        for _ in range(n):
            self.enemies.add(
                Ninja(
                    self.location[0] + random.randrange(self.size[0]),
                    self.location[1],
                    weapon=None,
                    clan="shadow",
                    speed=1.7,
                    characters=self.characters,
                    border_image=self.border_image,
                    items=self.items,
                )
            )

    def handle_shuriken_collision(self, shurikens):
        for shuriken in shurikens:
            if isinstance(
                shuriken.launcher, Player
            ) and shuriken.rect.colliderect(
                (c(self.init_rect.topleft, self.camera), self.size)
            ):
                self.hp -= shuriken.damage
                shurikens.remove(shuriken)
                self.damage_alpha = 100
                self.gain_damage = True
                break

    def update(self, event_info: EventInfo, shurikens, spawners):
        self.dt = event_info["dt"]
        self.handle_shuriken_collision(shurikens)

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
            self.image = pygame.transform.rotate(
                self.spawn_images[1], self.angle
            )
            self.time_passed = 0
            self.spawn(random.randrange(*self.number_of_enemies))
        else:
            self.image = pygame.transform.rotate(
                self.spawn_images[0], self.angle
            )

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
            self.rect.midtop[1] - 10,
        )

    def draw_spawn(self, screen, camera):
        for rect in self.spawning_rects:
            pygame.draw.rect(
                screen,
                "red",
                (rect.x - camera[0], rect.y - camera[1], *rect.size),
                width=3,
            )

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


class BeeSpawner:
    SIZE = (70, 70)
    HP = 50
    COOL_DOWN_RANGE = (3.4, 6.7)

    def __init__(
        self,
        location: Pos,
        bee_spawner_img: pygame.Surface,
        bee_img: pygame.Surface,
        border_image: pygame.Surface,
        player_instance,
    ) -> None:
        self.location = Vec(location)
        self.cool_down = random.uniform(*self.COOL_DOWN_RANGE)
        self.img = pygame.transform.scale(bee_spawner_img, self.SIZE)
        self.bee_img = bee_img
        self.rect = self.img.get_rect(center=location)
        self.player_instance = player_instance

        # Health Points (HP)
        self.hp = self.HP  # Mutable hp

        self.hp_bar_size = (80, 10)
        self.hp_bar = LoadingBar(
            value=self.HP,
            fg_color=(179, 2, 43),
            bg_color="black",
            rect=pygame.Rect((0, 0), self.hp_bar_size),
            border_image=border_image,
        )

        # Bee Generation
        self.bee_gen = Time(self.cool_down)
        self.is_alive = True

    def spawn_enemies(self, bees: set):
        bee = Bee(self.player_instance, Vec(self.rect.topleft), self.bee_img)
        bees.add(bee)
        self.bee_gen.time_to_pass = random.uniform(*self.COOL_DOWN_RANGE)

    def handle_projectile_collision(
        self, shurikens: set, sword_slashes: set
    ) -> None:
        for shuriken in set(shurikens):
            if shuriken.rect.colliderect(self.rect):
                self.is_alive = False
                shurikens.remove(shuriken)

        for sword_slash in set(sword_slashes):
            if sword_slash.rect.colliderect(self.rect):
                self.is_alive = False
                sword_slashes.remove(sword_slash)

    def update(self, shurikens: set, sword_slashes: set, bees: set) -> None:
        self.hp_bar.value = self.hp * (self.hp_bar_size[0] / self.HP)
        self.hp_bar.rect.center = (
            self.rect.midtop[0],
            self.rect.midtop[1] - 10,
        )

        if self.bee_gen.update():
            self.spawn_enemies(bees)
        self.handle_projectile_collision(shurikens, sword_slashes)

    def draw(self, screen: pygame.Surface, camera: Vec):
        screen.blit(self.img, self.rect.topleft - camera)
