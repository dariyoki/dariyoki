import pygame
import pytmx
from src.sprites import bee_tile_set_info


class World:
    def __init__(self, tile_map: pytmx.TiledMap):
        self.tile_map = tile_map
        self.decorations = tuple((
            (pygame.transform.scale(obj.image, (obj.width, obj.height)), (obj.x, obj.y)) for obj
            in tile_map.get_layer_by_name("decorations")
        ))

    def draw_dec(self, screen: pygame.Surface, camera: list[int, int]):
        for image, pos in self.decorations:
            image.set_alpha(150)
            screen.blit(
                image,
                (
                    pos[0] - camera[0],
                    pos[1] - camera[1]
                )
            )


    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        for x, y, image in self.tile_map.get_layer_by_name("Tile Layer 1").tiles():
            screen.blit(image, (
                (x * self.tile_map.tileheight) - camera[0],
                (y * self.tile_map.tilewidth) - camera[1]
            )
                            )
