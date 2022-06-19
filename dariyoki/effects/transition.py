import pygame
from dariyoki.display import screen_width, screen_height


class FadeTransition:
    def __init__(self, fade_in: bool, fade_speed: float):
        self.fade_in = fade_in
        self.fade_speed = fade_speed
        self.image = pygame.Surface((screen_width, screen_height))

        self.event = False
        self.alpha = 255 if fade_in else 0
        self.image.set_alpha(self.alpha)

    def _handle_fade_in(self, dt: float):
        if self.alpha > 0:
            self.alpha -= self.fade_speed * dt
            self.event = False
        else:
            self.alpha = 0
            self.event = True

    def _handle_fade_out(self, dt: float):
        if self.alpha < 255:
            self.alpha += self.fade_speed * dt
            self.event = False
        else:
            self.event = True

    def update(self, dt: float) -> None:
        if self.fade_in:
            self._handle_fade_in(dt)
        else:
            self._handle_fade_out(dt)

        self.image.set_alpha(int(self.alpha))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (0, 0))

