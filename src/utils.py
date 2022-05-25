import math
import time
from typing import Sequence

import pygame


def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))

    return surf


def camerify(coord, camera):
    """
    Converts a coordinate to camera relative position

    :return: Converted coordinate
    """
    return coord[0] - camera[0], coord[1] - camera[1]


def rotate(extract, angle):
    dump = [pygame.transform.rotozoom(img, angle, 1) for img in extract]

    return dump


def resize(extract: Sequence[pygame.Surface], scale: float):
    width, height = extract[0].get_width() * scale, extract[0].get_height() * scale
    scaled = [pygame.transform.scale(img, (width, height)) for img in extract]

    return scaled


def turn_left(extract):
    left_images = [pygame.transform.flip(img, True, False) for img in extract]

    return left_images


def get_movement(angle: float, speed) -> tuple[int, int]:
    """

    :param angle: Angle in radians
    :param speed:
    :return: Required change in x and y to move towards angle
    """
    # Change in x and y
    dx = math.cos(angle) * speed
    dy = math.sin(angle) * speed

    return dx, dy


class Glow:
    def __init__(self, image: pygame.Surface, color, topleft):
        self.img_rect = image.get_bounding_rect()
        self.img_rect.topleft = topleft
        self.surf = circle_surf(self.img_rect.height, color)
        self.rect = self.surf.get_rect(center=self.img_rect.center)

    def change_pos(self, new_pos):
        self.rect = pygame.Rect(new_pos, self.rect.size)

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(
            self.surf,
            (
                self.rect.x - camera[0],
                self.rect.y - camera[1] + (self.img_rect.height // 2),
            ),
            special_flags=pygame.BLEND_RGB_ADD,
        )


class Time:
    """
    Class to check if time has passed.
    """

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def update(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            self.start = time.perf_counter()
            return True
        return False


class Expansion:
    """
    Number expansion and contraption
    """

    def __init__(self, number: float, lower_limit: float, upper_limit: float, speed: float):
        self.number = number
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.speed = speed

    def update(self, cond: bool, dt: float):
        if cond:
            if self.number < self.upper_limit:
                self.number += self.speed * dt
        else:
            if self.number > self.lower_limit:
                self.number -= self.speed * dt

