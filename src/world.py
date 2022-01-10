import pygame
import pickle


class World:
    def __init__(self):
        with open("data/level_data/level_0", "rb") as f:
            self.rects = pickle.load(f)

    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        for rect in self.rects:
            pygame.draw.rect(screen, "black", pygame.Rect(rect.x-camera[0], rect.y-camera[1], *rect.size))
