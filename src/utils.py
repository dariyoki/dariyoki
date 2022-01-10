import pygame


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

