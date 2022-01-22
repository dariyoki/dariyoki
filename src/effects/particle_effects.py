"""
Cursor for pygame applications
Flexible and can be used in other projects
"""

import pygame
import random
from src.effects.particle import SoulParticle


class PlayerAura:
    def __init__(self, colour: tuple[int, int, int] | str, generation_rate: int):
        self.particles: list[SoulParticle] = []
        self.colour = colour
        self.generation_rate = generation_rate
        self.dt = 0
        self.count = 0

    def update(self, mx, my, screen, dt):
        self.dt = dt
        self.create_new_particle(mx, my)

        for particle in self.particles:
            if particle.size[0] <= 0.4:
                self.particles.remove(particle)
            particle.update(dt)
            particle.draw(screen)

    def create_new_particle(self, mx, my):
        self.count += self.dt
        if self.count >= self.generation_rate:
            size = random.randrange(11, 15)
            self.particles.append(
                SoulParticle(
                    mx,
                    my,
                    6,
                    "classic",
                    "circle",
                    [size, size],
                    self.colour,
                    (-2.5, 2.5),
                    size_reduction=0.9
                )
            )
            self.count = 0


class ShurikenContrail:
    def __init__(self):
        self.particles: list[SoulParticle] = []
        self.colour = (255, 255, 255)
        self.generation_rate = 2
        self.dt = 0
        self.count = 0

    def update(self, mx, my, screen, dt):
        self.dt = dt
        self.create_new_particle(mx, my)

        for particle in self.particles:
            if particle.size[0] <= 0.4:
                self.particles.remove(particle)
            particle.update(dt)
            particle.draw(screen)

    def create_new_particle(self, mx, my):
        self.count += self.dt
        if self.count >= self.generation_rate:
            size = random.randrange(7, 12)
            self.particles.append(
                SoulParticle(
                    mx,
                    my,
                    1.7,
                    "classic",
                    "rectangle",
                    [size, size],
                    self.colour,
                    (-1.3, 1.3),
                    size_reduction=0.5
                )
            )
            self.count = 0


