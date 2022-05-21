import uuid

import pygame

from src.angular_movement import Projectile
from src.effects.particle_effects import ShurikenContrail
from src.utils import circle_surf


class Shuriken(Projectile):
    def __init__(self, start, target, speed, launcher, items, item_size):
        super().__init__(start, target, speed, item_size)
        self.shuriken_img = items["shuriken"]
        self.image = self.shuriken_img.copy()
        self.damage = 30
        self.id = uuid.uuid1()
        self.launcher = launcher
        self.angle = 0
        self.contrail = ShurikenContrail()
        self.glow_radius = self.image.get_width() // 2

    def draw(self, screen, camera, dt):
        self.angle += 5 * dt
        # pygame.draw.rect(screen, 'red', pygame.Rect(
        #     self.rect.x - camera[0],
        #     self.rect.y - camera[1],
        #     *self.rect.size
        # ), width=1)

        self.image = pygame.transform.rotozoom(self.shuriken_img, int(self.angle), 1)
        self.contrail.update(
            self.rect.center[0] - camera[0], self.rect.center[1] - camera[1], screen, dt
        )
        screen.blit(self.image, (self.rect.x - camera[0], self.rect.y - camera[1]))

        surf = circle_surf(self.glow_radius, (31, 32, 34))
        rect = surf.get_rect(center=self.rect.center)
        screen.blit(
            surf,
            (rect.x - camera[0], rect.y - camera[1]),
            special_flags=pygame.BLEND_RGB_ADD,
        )
