"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import logging
import math

import pygame

logger = logging.getLogger()


class Projectile:
    def __init__(self, start, target, speed, size):
        self.x, self.y = start
        self.target_x, self.target_y = target
        self._speed = speed
        self.size = size

        self.rect = pygame.Rect((0, 0), self.size)

        # Getting the angle in radians
        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.degrees = math.degrees(self.angle)  # In degrees

        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

        self.distance = 0

    def set_target(self, target):
        self.target_x, self.target_y = target

        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.degrees = math.degrees(self.angle)

        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        self._speed = new_speed
        self.dx = math.cos(self.angle) * self._speed
        self.dy = math.sin(self.angle) * self._speed

    def move(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt

        # self.rect.x = int(self.x)
        # self.rect.y = int(self.y)
        self.rect.center = self.x, self.y

        self.distance += math.sqrt(
            ((self.dx * dt) ** 2) + ((self.dy * dt) ** 2)
        )
