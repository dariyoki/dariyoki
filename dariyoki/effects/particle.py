"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import math
import random

import pygame

from dariyoki.generics import Vec
from dariyoki.utils import circle_surf, get_movement


class Particle:
    def __init__(
        self,
        pos,
        color,
        size,
        speed,
        shape: str,
        size_reduction,
        glow: bool = False,
        angle=None,
    ):
        self.pos = pos
        self.color = color
        self.size = size
        self.speed = speed
        self.shape = shape
        self.vec = pygame.Vector2(self.pos)
        # self.vec.rotate(random.randrange(0, 360))
        if angle is None:
            self.angle = math.atan2(
                random.randrange(-300, 500) - random.randrange(-300, 500),
                random.randrange(-300, 500) - random.randrange(-300, 500),
            )
        else:
            self.angle = angle
        self.dx, self.dy = get_movement(self.angle, speed)

        self.rect = pygame.Rect(tuple(self.pos), (size, size))
        self.size_reduction = size_reduction
        self.glow = glow

    def draw(self, screen, dt, speed_reduce=0):
        if speed_reduce:
            self.dx, self.dy = get_movement(self.angle, speed_reduce)
        self.vec[0] += self.dx * dt
        self.vec[1] += self.dy * dt

        # if self.size < 6:
        #     self.vec[1] += 120 * dt

        self.size -= self.size_reduction * dt
        self.rect = pygame.Rect(self.vec, (self.size, self.size))

        if self.shape == "square":
            pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape == "circle":
            pygame.draw.circle(screen, self.color, self.rect.center, self.size)

        if self.glow and self.size > 0:
            surf = circle_surf(self.size * 2, (20, 20, 20))
            r = surf.get_rect(center=self.rect.center)
            screen.blit(surf, r, special_flags=pygame.BLEND_RGB_ADD)


class BezierParticle:
    def __init__(self, x, y, flame_particles) -> None:
        self.vec = Vec(x, y)
        self.image = random.choice(flame_particles)
        self.rect = self.image.get_rect()
        self.glow_color = 10
        self.glow_increment = random.uniform(0.1, 0.3)
        self.glow_radius = 10
        self.inc_up = True

        self.increment = random.uniform(0.2, 0.8)
        self.drop = random.uniform(-0.4, 0.4)

    def draw(self, screen: pygame.Surface, speed: float, dt: float) -> None:
        movement = self.increment * speed * dt
        self.vec.x += movement
        self.vec.y += movement
        self.vec.y += self.drop

        screen.blit(self.image, (self.vec.x, self.vec.y))
        self.rect.topleft = self.vec.x, self.vec.y

        # Handle color
        if self.inc_up:
            self.glow_color += self.glow_increment * dt
            self.glow_radius -= (self.glow_increment * dt) / 8
            if self.glow_color > 60:
                self.inc_up = False
        else:
            self.glow_color -= self.glow_increment * dt
            self.glow_radius += (self.glow_increment * dt) / 8
            if self.glow_color < 10:
                self.inc_up = True

        # Outer circle
        color = (self.glow_color, self.glow_color, self.glow_color)
        glow_surf = circle_surf(self.glow_radius, color)
        glow_rect = glow_surf.get_rect(center=self.rect.center)
        screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_RGB_ADD)


class TriangularParticle:
    ...


class CircleParticle:
    ...


class SoulParticle:
    def __init__(
        self,
        start_x,
        start_y,
        speed,
        mode,
        shape,
        size: list[int],
        colour: tuple[int, int, int],
        prange: tuple[float, float],
        acceleration=False,
        glow=True,
        size_reduction: float = 0.3,
    ):
        self.x = start_x
        self.y = start_y
        self.speed = speed
        self.mode = mode
        self.shape = shape
        self.size = size
        self.colour = colour
        self.increase = random.uniform(*prange)
        self.acceleration = acceleration
        self.glow = glow
        self.size_reduction = size_reduction

        self.dt = 0

    def update(self, dt):
        self.dt = dt

        # Reduce Particle Size
        self.size[0] -= self.size_reduction * self.dt
        self.size[1] -= self.size_reduction * self.dt

        if self.mode == "classic":
            self.classic()
        elif self.mode == "crazy":
            self.crazy()

    def classic(self):
        self.x += self.increase * self.dt
        self.y -= self.speed * self.dt

    def crazy(self):
        self.x += random.randrange(-3, 3) * self.speed
        self.y += random.randrange(-3, 3) * self.speed

    def draw(self, screen):
        rect = pygame.Rect((self.x, self.y), self.size)
        rect.center = (self.x, self.y)

        if self.shape == "rectangle":
            pygame.draw.rect(screen, self.colour, rect)
        elif self.shape == "circle":
            pygame.draw.circle(
                screen, self.colour, (self.x, self.y), tuple(self.size)[0]
            )

        if self.glow and self.shape != "rectangle":
            bloom_rect = pygame.Rect(
                self.x, self.y, self.size[0] * 2, self.size[1] * 2
            )
            bloom_rect.center = (self.x, self.y)
            try:
                bloom = circle_surf(tuple(self.size)[0] * 1.2, (150, 150, 150))
            except pygame.error:
                bloom = circle_surf(1, (150, 150, 150))
            bloom.set_alpha(150)
            screen.blit(bloom, bloom_rect)
