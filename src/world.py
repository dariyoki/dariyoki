import pygame
from src.sprites import bee_tile_set_info


class World:
    def __init__(self, tile_map):
        self.tile_map = tile_map

    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        for layer in self.tile_map:
            for x, y, image in layer.tiles():
                screen.blit(image, (
                                    (x * self.tile_map.tileheight) - camera[0],
                                    (y * self.tile_map.tilewidth) - camera[1]
                                    )
                            )

