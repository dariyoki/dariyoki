import random

import pygame

from src._types import EventInfo
from src.effects.particle import BezierParticle, SoulParticle


class MainMenuFlare:
    def __init__(self, flame_particles) -> None:
        self.flame_particles = flame_particles
        self.particles: list[BezierParticle] = []

        # Wind
        self.wind = 1
        self.wind_to_be = 1
        self.wind_tension = 0.3
        self.p1 = -3
        self.p2 = 3

        # Particle generation
        self.generation_rate = 30
        self.generation_speed = 2
        self.count = 0
        self.time_passed = 0
        self.time_to_pass = random.randrange(1, 3)

    def draw(self, screen: pygame.Surface, event_info: EventInfo) -> None:
        dt = event_info["dt"]
        raw_dt = event_info["raw dt"]
        self.count += self.generation_speed * dt
        if self.count > self.generation_rate:
            type_one = (random.randrange(0, 1100), 0)
            type_two = (0, random.randrange(0, 650))
            self.particles.append(
                BezierParticle(
                    *random.choice((type_one, type_two)), self.flame_particles
                )
            )
            self.count = 0

        self.time_passed += raw_dt
        if self.time_passed > self.time_to_pass:
            self.wind_to_be = random.uniform(self.p1, self.p2)
            if 1 > self.wind_to_be > 0:
                self.wind_to_be += 1.3
            elif -1 < self.wind_to_be < 0:
                self.wind_to_be -= 1.3
            else:
                self.wind_to_be = 1.5
            self.wind_tension = random.uniform(0.3, 0.9) if self.wind_to_be > 0 else 1.3

            self.time_passed = 0
            self.time_to_pass = random.randrange(1, 3)

        # Update wind
        if self.wind < self.wind_to_be:
            self.wind += self.wind_tension * dt
        elif self.wind > self.wind_to_be:
            self.wind -= self.wind_tension * dt

        # Cleanup wind
        if self.wind > self.p2:
            self.wind = self.p2

        if self.wind < self.p1:
            self.wind = self.p1

        # Draw particles
        for particle in self.particles:
            particle.draw(screen, self.wind, dt)

            if particle.vec.x > 1100 or particle.vec.y > 650:
                self.particles.remove(particle)


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
                    size_reduction=0.9,
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
                    size_reduction=0.5,
                )
            )
            self.count = 0
