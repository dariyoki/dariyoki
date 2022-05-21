import pygame

from src._globals import explosions
from src.effects.explosion import Explosion
from src.widgets import LoadingBar


class HealthPotion:
    def __init__(self, player_obj, border_image: pygame.Surface):
        self.health = 40
        self.player_obj = player_obj
        self.loading_bar = LoadingBar(
            value=0,
            fg_color="white",
            bg_color="black",
            rect=pygame.Rect(
                player_obj.rect.midtop[0], player_obj.rect.midtop[1] - 10, 50, 12
            ),
            border_image=border_image
        )

    def draw(self, screen: pygame.Surface, camera):
        self.loading_bar.draw(screen, camera, moving=True)

        if self.loading_bar.loaded:
            if self.player_obj.hp + self.health > self.player_obj.max_hp:
                self.player_obj.hp = self.player_obj.max_hp
            else:
                self.player_obj.hp += self.health
            explosions.append(
                Explosion(
                    400,
                    (4, 15),
                    [
                        self.player_obj.rect.center[0] - camera[0],
                        self.player_obj.rect.center[1] - camera[1],
                    ],
                    (2.5, 8.6),
                    "green",
                    size_reduction=0.6,
                )
            )


class ShieldPotion:
    def __init__(self, player_obj, border_image: pygame.Surface):
        self.shield = 50
        self.player_obj = player_obj
        self.loading_bar = LoadingBar(
            value=0,
            fg_color="white",
            bg_color="black",
            rect=pygame.Rect(
                player_obj.rect.midtop[0], player_obj.rect.midtop[1] - 10, 50, 12
            ),
            border_image=border_image
        )

    def draw(self, screen: pygame.Surface, camera):
        self.loading_bar.draw(screen, camera, moving=True)

        if self.loading_bar.loaded:
            if self.player_obj.shield + self.shield > self.player_obj.max_shield:
                self.player_obj.shield = self.player_obj.max_shield
            else:
                self.player_obj.shield += self.shield
            explosions.append(
                Explosion(
                    400,
                    (4, 15),
                    [
                        self.player_obj.rect.center[0] - camera[0],
                        self.player_obj.rect.center[1] - camera[1],
                    ],
                    (2.5, 8.6),
                    (0, 255, 255),
                    size_reduction=0.6,
                )
            )
