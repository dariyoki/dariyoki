import pygame
from src.sprites import bee_tile_set_info


class World:
    def __init__(self, level_manager):
        self.level_manager = level_manager

    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        for pos in self.level_manager.all_rects:
            screen.blit(
                bee_tile_set_info[self.level_manager.all_rects[pos]],
                (
                    pos[0] - camera[0],
                    pos[1] - camera[1]
                )
            )

