"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import random
from enum import Enum

import pygame

from dariyoki.generics import Vec
from dariyoki.ui.widgets import LoadingBar
from dariyoki.utils import Glow, circle_surf


class HoverDirection(Enum):
    UP = "UP"
    DOWN = "DOWN"


class Item:
    def __init__(self, name: str, image: pygame.Surface, pos):
        self.init_pos = pos if isinstance(pos, Vec) else Vec(pos)
        self.pos = self.init_pos.copy()
        self.name = name
        self.image = image
        self.rect = self.image.get_bounding_rect()

        if name == "health potion":
            self.color = (20, 60, 20)
        elif name == "shield potion":
            self.color = (20, 40, 40)
        elif name == "jetpack":
            self.color = None
        else:
            self.color = (20, 20, 20)

        # Sliding
        self.slide_len = random.randrange(20, 80)
        self.slide_speed = random.randrange(2, 5)
        self.slide_dist = 0
        self.slide_dir = random.choice((1, -1))

        # Hover
        self.hover_movement = 0
        self.hover_speed = 1
        self.hover_direction = HoverDirection.UP
        self.i_radius = 0

    def update(self, dt):
        # if self.slide_speed > 0.3:
        #     self.slide_speed -= 1 * dt
        dx = self.slide_speed * self.slide_dir * dt
        self.init_pos[0] += dx
        self.slide_dist += abs(dx)
        if self.slide_dist > self.slide_len:
            self.slide_speed = 0

        self.pos = Vec(self.init_pos)
        if self.hover_direction == HoverDirection.UP:
            self.hover_movement -= self.hover_speed * dt
            self.i_radius -= (self.hover_speed * dt) / 4
            if self.hover_movement < 0:
                self.hover_direction = HoverDirection.DOWN
        elif self.hover_direction == HoverDirection.DOWN:
            self.hover_movement += self.hover_speed * dt
            self.i_radius += (self.hover_speed * dt) / 4
            if self.hover_movement > 20:
                self.hover_direction = HoverDirection.UP

        self.pos[1] += self.hover_movement
        self.rect = self.image.get_rect(topleft=(self.pos[0], self.pos[1]))

    def draw(self, screen, camera):
        screen.blit(self.image, self.pos - camera)
        if self.color is not None:
            screen.blit(
                circle_surf(
                    radius=self.rect.height + self.i_radius, color=self.color
                ),
                (self.pos[0] - 12 - camera[0], self.pos[1] - 11 - camera[1]),
                special_flags=pygame.BLEND_RGB_ADD,
            )


class Chest:
    def __init__(
        self, x, y, load_control, load_speed, chests, items: dict, border_image
    ):
        self.x, self.y = x, y
        self.closed_img = chests[0]
        self.open_img = chests[1]
        self.image = self.closed_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.glow = Glow(self.image, (40, 40, 20), (x, y))
        self.loading_bar = LoadingBar(
            value=0,
            fg_color="white",
            bg_color="black",
            rect=pygame.Rect((self.rect.center[0], y + 10), (150 / 2, 20 / 2)),
            border_image=border_image,
        )
        self.load_control = load_control
        self.load_speed = load_speed

        # Predetermined Items
        self.items = []
        n_items = random.randrange(2, 7)
        weights = {
            "health potion": 50,
            "shield potion": 60,
            "shuriken": 40,
            "sword": 20,
            "smoke bomb": 10,
            "scythe": 3,
        }

        for _ in range(n_items):
            name, *_ = random.choices(
                tuple(weights.keys()), k=1, weights=tuple(weights.values())
            )
            item = Item(name, items[name], [self.x, self.y])
            self.items.append(item)

    def update(self, keys, dt):
        if keys[self.load_control]:
            if not self.loading_bar.loaded:
                self.loading_bar.value += 1 * dt

    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - camera[0], self.y - camera[1]))
        if self.loading_bar.loaded:
            self.image = self.open_img
        else:
            self.glow.draw(screen, camera)
