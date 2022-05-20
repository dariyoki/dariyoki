from typing import Optional

import pygame

from src._types import ColorValue
from src.animation import Animation


class SpriteSheet:
    def __init__(
        self,
        image: pygame.Surface,
        # rows: int,
        # columns: int,
        # width: float,
        # height: float,
        # fixer: float = 1,
        # bound=True,
        # animation_speed: Optional[int] = None
    ):
        self.sheet = image

        # Width of each sprite NOT sprite sheet
        self.width, self.height = 0, 0

        self.rows = []
        # self.all_images = self.get_images(rows, columns, width, height, fixer, bound)
        #
        # self.animations = tuple(
        #     (
        #         Animation(
        #             frames,
        #             animation_speed
        #         )
        #         for frames in self.rows
        #     )
        # )

    def get_images(
        self,
        rows: int,
        columns: int,
        width: float,
        height: float,
        fixer: float = 1,
        bound=True,
    ):
        self.width = width
        self.height = height

        images = []

        for i in range(rows):
            # _rows = []
            for e in range(columns):
                # Mod image
                image = self.sheet.subsurface(
                    pygame.Rect((e * width), ((i * fixer) * columns), width, height)
                )
                if bound:
                    r = image.get_bounding_rect()
                    image = image.subsurface(r)

                images.append(image)
            #     _rows.append(image)
            # self.rows.append(_rows)

        return images


def get_images(
    sheet: pygame.surface.Surface,
    rows: int,
    columns: int,
    size: float,
    bound=True,
):

    images = []

    for row in range(rows):
        for col in range(columns):
            # Mod image
            image = sheet.subsurface(
                pygame.Rect((col * size), ((row * size)), size, size)
            )
            if bound:
                r = image.get_bounding_rect()
                image = image.subsurface(r)

            images.append(image)

    return images


