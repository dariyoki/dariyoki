"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import logging
from typing import Sequence

import pygame

from src.animation import Animation
from src.generics import EventInfo, Vec
from src.utils import Time, mod_alpha, resize, rotate
from src.weapons.projectiles import Projectile

logger = logging.getLogger()


class WindSlash(Projectile):
    def __init__(
        self,
        frames: Sequence[pygame.Surface],
        pos: tuple,
        mouse_pos: tuple,
        speed: float,
    ):
        frames = resize(frames, 3)
        super().__init__(
            start=pos,
            target=mouse_pos,
            speed=speed,
            size=frames[3].get_bounding_rect().size,
        )
        # self.frames = rotate(frames, self.degrees - 20 + 60)
        self.frames = frames
        self.animation = Animation(self.frames, 0.4)
        self.alpha = 255
        self.rotate_angle = 0

    def update(self, dt: float):
        super().move(dt)
        if self.speed > 10:
            self.speed -= 0.5

        if self.alpha > 100:
            self.alpha -= 5 * dt
        mod_alpha(self.animation.frames, self.alpha)
        #
        # self.rotate_angle += 1
        # self.animation.frames = rotate(self.animation.frames, self.rotate_angle)
        # if not self.animation.animated_once:
        self.animation.update(dt)

    def draw(self, screen: pygame.Surface, camera: Vec):
        self.animation.draw(screen, self.rect.topleft - camera)


class Sword:
    BASE_WIND_SPEED = 50.3
    BASE_WIND_DISTANCE = 1000
    BASE_DAMAGE = 120

    def __init__(
        self,
        level: int,
        soul_energy: int,
        slash_frames: Sequence[pygame.Surface],
    ):
        self.pos = Vec()
        self.level = level
        self.soul_energy = soul_energy
        self.slash_frames = slash_frames
        self.wind_slash_gen_time = Time(0.5)
        self.projectiles = set()
        self.wind_speed = (level / 2) * self.BASE_WIND_SPEED
        self.wind_distance = (level / 2) * self.BASE_WIND_DISTANCE
        self.damage = (level / 2) * self.BASE_DAMAGE

    def create_wind_slash(
        self, player_pos: tuple, mouse_pos: tuple, camera: Vec
    ):
        wind_slash = WindSlash(
            frames=self.slash_frames,
            pos=player_pos,
            mouse_pos=mouse_pos + camera,
            speed=self.wind_speed,
        )
        self.projectiles.add(wind_slash)

    def update(
        self, event_info: EventInfo, player_pos: tuple, camera: Vec
    ) -> None:
        for event in event_info["events"]:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and self.wind_slash_gen_time.update()
            ):
                self.create_wind_slash(player_pos, event.pos, camera)
