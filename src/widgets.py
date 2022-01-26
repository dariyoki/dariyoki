import pygame
from src.generic_types import Pos, Size, ColorValue
from src.sprites import border_img


class LoadingBar:
    def __init__(self, value, fg_color, bg_color, rect: pygame.Rect, max_value=100, _border_img=None):
        self.value = value
        self.sfg_color = fg_color
        self.sbg_color = bg_color
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rect = rect
        self.rect.center = self.rect.topleft
        self.val_rect = pygame.Rect(
            rect.topleft,
            (self.value, self.rect.height)
        )
        self.loaded = False
        if _border_img is not None:
            self.border_img = _border_img
        else:
            self.border_img = border_img

        self.border_img = pygame.transform.scale(self.border_img, rect.size)
        self.max_value = max_value

    def draw(self, screen: pygame.Surface, camera, moving: bool = False):
        if moving:
            self.val_rect = pygame.Rect(
                self.rect.topleft,
                (self.value, self.rect.height)
            )
        pygame.draw.rect(screen, self.bg_color, pygame.Rect((self.rect.x - camera[0], self.rect.y - camera[1]),
                                                            self.rect.size))

        self.loaded = self.value >= self.rect.width

        pygame.draw.rect(screen, self.fg_color, pygame.Rect((self.val_rect.x - camera[0], self.val_rect.y - camera[1]),
                                                            (int(self.value), self.rect.height)))

        screen.blit(self.border_img, (self.rect.x - camera[0], self.rect.y - camera[1]))


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
