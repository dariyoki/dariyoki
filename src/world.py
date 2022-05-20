import pygame
import pytmx

from src._types import Vec
from src.sprites import bush_img, bush_width, r_bush_img


class World:
    def __init__(self, tile_map: pytmx.TiledMap):
        self.tile_map = tile_map
        self.decorations = tuple(
            (
                (
                    pygame.transform.scale(obj.image, (obj.width, obj.height)),
                    (obj.x, obj.y),
                )
                for obj in tile_map.get_layer_by_name("decorations")
            )
        )

        self.x = 0
        self.parallax_tile_map = pytmx.load_pygame(
            "assets/data/level_data/level_0_test_parallax.tmx"
        )
        self.f = 25 / 32
        self.parallax_background = pygame.Surface((250 * 25, 100 * 25))
        self.parallax_background.set_colorkey(0)
        for x, y, image in self.parallax_tile_map.get_layer_by_name(
            "Parallax Layer 1"
        ).tiles():
            image.set_alpha(100)
            self.parallax_background.blit(
                image,
                (
                    (x * self.parallax_tile_map.tileheight),
                    (y * self.parallax_tile_map.tilewidth),
                ),
            )

        self.tiles_background = pygame.Surface((250 * 25, 100 * 25))
        self.tiles_background.set_colorkey(0)
        for x, y, image in self.tile_map.get_layer_by_name("Tile Layer 1").tiles():
            self.tiles_background.blit(
                image, ((x * self.tile_map.tileheight), (y * self.tile_map.tilewidth))
            )

        for obj in self.parallax_tile_map.get_layer_by_name("parallax decorations"):
            obj.image.set_alpha(100)
            self.parallax_background.blit(obj.image, (obj.x, obj.y))
        self.parallax_background = self.parallax_background.subsurface(
            self.parallax_background.get_bounding_rect()
        )

    def draw_grass(self, screen, camera: Vec):
        for x, y, image in self.tile_map.get_layer_by_name("grass").tiles():
            screen.blit(
                image,
                (
                    (x * self.tile_map.tileheight) - camera[0],
                    (y * self.tile_map.tilewidth) - camera[1] - (32 * 2),
                ),
            )

    def draw_dec(self, screen: pygame.Surface, camera: Vec):
        for image, pos in self.decorations:
            image.set_alpha(150)
            screen.blit(image, (pos[0] - camera[0], pos[1] - camera[1]))

    def draw_parallax(self, screen: pygame.Surface, camera: Vec):
        screen.blit(bush_img, (self.x - camera[0], 450))
        screen.blit(r_bush_img, (self.x - camera[0] + bush_width, 450))
        screen.blit(
            self.parallax_background,
            (100 - (camera[0] * self.f), 100 - (camera[1] * self.f)),
        )

    def draw(self, screen: pygame.Surface, camera: list[int, int]):
        screen.blit(self.tiles_background, (0 - camera[0], 0 - camera[1]))
