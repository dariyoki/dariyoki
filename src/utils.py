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


class Glow:
    def __init__(self, image: pygame.Surface, color, topleft):
        self.img_rect = image.get_rect(topleft=topleft)
        average = (self.img_rect.width + self.img_rect.height) // 2
        radius = average // 1.5
        self.surf = circle_surf(radius, color)
        self.rect = self.surf.get_rect(center=self.img_rect.center)

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.surf, pygame.Rect((self.rect.x - camera[0], self.rect.y - camera[1]),
                                           self.surf.get_size()),
                    special_flags=pygame.BLEND_RGB_ADD)


class LoadingBar:
    def __init__(self, value, fg_color, bg_color, rect: pygame.Rect):
        self.value = value
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rect = rect
        self.rect.center = self.rect.topleft
        self.val_rect = pygame.Rect(
            (rect.x + 2, rect.y + 2),
            (self.value, self.rect.height // 2)
        )
        self.loaded = False

    def draw(self, screen: pygame.Surface, camera):
        pygame.draw.rect(screen, self.bg_color, pygame.Rect((self.rect.x - camera[0], self.rect.y - camera[1]),
                                                            self.rect.size))

        self.loaded = self.value >= self.rect.width - 4

        pygame.draw.rect(screen, self.fg_color, pygame.Rect((self.val_rect.x - camera[0], self.val_rect.y - camera[1]),
                                                            (int(self.value), self.rect.height // 2)))


