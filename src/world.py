import pygame
from src.sprites import bee_tile_set_info


class World:
    def __init__(self, level_manager):
        self.level_manager = level_manager

    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        for img, rect in zip(self.level_manager.all_images, self.level_manager.all_rects):
            screen.blit(bee_tile_set_info[img], pygame.Rect(
                (rect.x - camera[0], rect.y - camera[1]),
                rect.size
            ))
        # for rect in self.level_manager.all_rects:
        #     pygame.draw.rect(screen, "black", pygame.Rect(rect.x-camera[0], rect.y-camera[1], *rect.size))
