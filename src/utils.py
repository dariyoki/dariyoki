import pygame
import math


def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))

    return surf


def rotate(extract, angle):
    dump = [pygame.transform.rotozoom(img, angle, 1) for img in extract]

    return dump


def resize(extract: list[pygame.Surface], scale: float):
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
    :return:
    """
    # Change in x and y
    dx = math.cos(angle) * speed
    dy = math.sin(angle) * speed

    return dx, dy


class Glow:
    def __init__(self, image: pygame.Surface, color, topleft):
        self.img_rect = image.get_rect(topleft=topleft)
        average = (self.img_rect.width + self.img_rect.height) // 2
        radius = average // 1.5
        self.surf = circle_surf(radius, color)
        self.rect = self.surf.get_rect(center=self.img_rect.center)

    def change_pos(self, new_pos):
        self.rect = pygame.Rect(new_pos, self.rect.size)

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.surf, pygame.Rect((self.rect.x - camera[0], self.rect.y - camera[1]),
                                           self.surf.get_size()),
                    special_flags=pygame.BLEND_RGB_ADD)



