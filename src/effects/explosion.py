import pygame
import random
from src.effects.particle import Particle


class Explosion:
    def __init__(self, n_particles, n_size, pos, speed):
        self.n_particles = n_particles
        self.n_size = n_size

        self.particles = [Particle(
            pos=pos,
            color='white',
            size=random.randrange(*n_size),
            speed=random.uniform(*speed),
            shape="square"
        ) for _ in range(n_particles)]

    def draw(self, screen, dt):
        for particle in self.particles:
            particle.draw(screen, dt)

            if particle.size < 0:
                self.particles.remove(particle)
