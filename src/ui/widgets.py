import random
from typing import Any

import pygame

from src.generics import ColorValue, Pos, Size, WSurfInfo
from src.audio import hover_sfx


class LoadingBar:
    def __init__(
        self,
        value,
        fg_color,
        bg_color,
        rect: pygame.Rect,
        border_image: pygame.Surface,
        max_value=100,
    ):
        self.value = value
        self.sfg_color = fg_color
        self.sbg_color = bg_color
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rect = rect
        self.rect.center = self.rect.topleft
        self.val_rect = pygame.Rect(rect.topleft, (self.value, self.rect.height))
        self.background_surf = pygame.Surface(self.rect.size)
        self.loaded = False
        self.border_img = pygame.transform.scale(border_image, rect.size)
        self.max_value = max_value

    def draw(self, screen: pygame.Surface, camera, moving: bool = False):
        if moving:
            self.val_rect = pygame.Rect(
                self.rect.topleft, (self.value, self.rect.height)
            )
        screen.blit(
            self.background_surf, (self.rect.x - camera[0], self.rect.y - camera[1])
        )

        self.loaded = self.value >= self.rect.width

        pygame.draw.rect(
            screen,
            self.fg_color,
            pygame.Rect(
                (self.val_rect.x - camera[0], self.val_rect.y - camera[1]),
                (int(self.value), self.rect.height),
            ),
        )

        screen.blit(self.border_img, (self.rect.x - camera[0], self.rect.y - camera[1]))


class EnergyBar(LoadingBar):
    GEN_COOLDOWN = 0.3

    def __init__(self, player_obj, bar_border_img: pygame.Surface):
        width = player_obj.hp * 1.7
        height = 17
        super().__init__(
            value=player_obj.hp,
            fg_color=(0, 255, 255),
            bg_color="black",
            rect=pygame.Rect((970, 40), (width, height)),
            border_image=bar_border_img,
        )
        self.w_surfs: list[WSurfInfo] = []
        self.time_passed = 0
        self.b_surf = pygame.Surface((10, 3))
        self.b_surf.fill("white")

    def update(self, event_info):
        self.time_passed += event_info["raw dt"]
        if self.time_passed > self.GEN_COOLDOWN:
            if self.val_rect.width > 20:
                self.w_surfs.append(
                    [
                        [
                            self.val_rect.midright[0] - 10,
                            random.randrange(
                                self.val_rect.topright[1] + 2,
                                self.val_rect.bottomright[1] - 2,
                            ),
                        ],
                        255,
                    ]
                )

        for w_surf in self.w_surfs:
            w_surf[0][0] -= 5.3 * event_info["dt"]
            if self.val_rect.width > 0:
                w_surf[1] -= (
                    10.3 * event_info["dt"] * (self.rect.width / self.val_rect.width)
                )
            else:
                w_surf[1] -= 10.3 * event_info["dt"]

            if w_surf[1] < 0:
                self.w_surfs.remove(w_surf)

    def draw(self, screen: pygame.Surface, camera, moving: bool = False):
        super().draw(screen, camera, moving)
        for w_surf in self.w_surfs:
            _temp_surf = self.b_surf.copy()
            _temp_surf.set_alpha(w_surf[1])
            screen.blit(_temp_surf, w_surf[0])


class MenuButton:
    """
    Nice looking minimalistic button for the main menu.
    """

    def __init__(self, pos: Pos, title: str) -> None:
        self.pos = pos
        self.size = (170, 30)
        self.title = title
        self.clicked = False
        self.hover = False
        self.font = pygame.font.Font("assets/fonts/Roboto/Roboto-Regular.ttf", 17)
        self.rect = pygame.Rect(self.pos, self.size)
        self.text_surf = self.font.render(title, True, "white")
        self.text_surf_rect = self.text_surf.get_rect(center=self.pos)
        self.text_surf_rect.center = self.rect.center
        self.hover_surf = pygame.Surface(self.size)
        self.hover_surf.fill((0, 75, 189))
        self.hover_surf.set_alpha(230)
        self.hover_surf_alpha = 0
        self.once = True

    def update(self, event_info: dict[str, Any]):
        self.hover = self.rect.collidepoint(event_info["mouse pos"])
        if self.hover and self.hover_surf_alpha < 230:
            self.hover_surf_alpha += 7.4 * event_info["dt"]

        if not self.hover and self.hover_surf_alpha > 0:
            self.hover_surf_alpha -= 7.4 * event_info["dt"]

        # Cleanup
        if self.hover_surf_alpha > 230:
            self.hover_surf_alpha = 230
        if self.hover_surf_alpha < 0:
            self.hover_surf_alpha = 0

        for event in event_info["events"]:
            if self.hover and event.type == pygame.MOUSEBUTTONDOWN:
                self.clicked = True

    def draw(self, screen: pygame.Surface):
        # Hover surface
        screen.blit(self.hover_surf, self.rect)
        self.hover_surf.set_alpha(self.hover_surf_alpha)

        # Hover SFX
        if self.hover and self.once:
            hover_sfx.play()
            self.once = False

        if not self.hover:
            self.once = True

        # Border
        pygame.draw.rect(screen, "white", self.rect, width=3)

        # Actual text
        screen.blit(self.text_surf, self.text_surf_rect)


class Label:
    """
    Label widget used to display information about other widgets
    """

    def __init__(
        self,
        position: Pos,
        size: Size,
        content: str,
        colour: ColorValue = None,
        border_colour: ColorValue = None,
        txt_colour: ColorValue = (255, 255, 255),
        shape: str = "rectangle",
    ):
        """
        Initialize the Label Widget.

        :param position: Top-left position of the label
        :param size: Size of the label (width, height)
        :param content:
        :param colour:
        :param border_colour:
        :param txt_colour:
        :param shape:
        """
        self.position = position
        self.size = size
        self.rect = pygame.Rect(self.position, self.size)
        self.surface = pygame.Surface(self.size)
        # self.surface.set_colorkey((0, 0, 0))
        self.content = content

        self.colour = colour or None
        self.border_colour = border_colour or None
        self.txt_colour = txt_colour
        self.shape = shape
        self.t = pygame.font.SysFont("bahnschrift", size=self.rect.width // 14).render(
            content, True, self.txt_colour
        )

    def change_txt(self, txt):
        """
        Changes the label content

        :param txt: Text to be changed into
        :return:
        """
        self.t = pygame.font.SysFont("arial", size=self.rect.size[0] // 8).render(
            txt, True, self.txt_colour
        )

    def change_pos(self, pos):
        """
        Changes the position of the label

        :param pos:
        :return:
        """

        self.position = pos
        self.rect = pygame.Rect(pos, self.size)

    def draw(self, screen: pygame.Surface):
        """
        Draws the label

        :param screen: Screen to blit on
        :return:
        """
        if self.colour:
            if self.shape == "rectangle":
                pygame.draw.rect(
                    self.surface,
                    self.colour,
                    self.surface.get_rect(),
                    border_radius=1,
                    width=5,
                )
        if self.border_colour:
            pygame.draw.rect(
                self.surface,
                self.border_colour,
                self.surface.get_rect(),
                border_radius=4,
                width=1,
            )

        screen.blit(self.surface, self.rect)
        screen.blit(self.t, self.t.get_rect(center=self.rect.center))
