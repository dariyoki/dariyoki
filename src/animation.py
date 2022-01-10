import pygame


class Animation:
    def __init__(self, frames: list[pygame.surface], speed: float):
        self.frames = frames
        self.speed = speed

        self.f_len = len(frames)
        self.index = 0

    def update(self, dt):
        self.index += self.speed * dt
        if self.index > self.f_len:
            self.index = 0

    def draw(self, screen: pygame.Surface, pos: tuple[int, int]):
        screen.blit(self.frames[int(self.index)], pos)

    def play(self, screen, pos, dt):
        self.update(dt)
        self.draw(screen, pos)



