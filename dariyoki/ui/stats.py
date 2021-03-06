"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import pygame

from dariyoki.generics import EventInfo
from dariyoki.ui.widgets import EnergyBar, LoadingBar


class Info:
    ALPHA = 150

    def __init__(self, screen: pygame.Surface, open_control: int):
        self.screen = screen
        padx, pady = 30, 15
        self.height = screen.get_height() - pady
        self.open_control = open_control
        self.width = 300

        self.surf = pygame.Surface((self.width, self.height - pady))
        self.surf.set_alpha(self.ALPHA)
        self.rect = self.surf.get_rect()

        self.pos = [-self.width, pady]

        # Flags
        self.opening = False
        self.o_lock = False
        self.item_stats = None
        self.item = None

    def update(self, colliding_item, events, dt):
        if colliding_item is not None:
            self.item = colliding_item
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.open_control:
                    self.opening = not self.opening
                    self.o_lock = True

        if self.opening:
            if self.pos[0] < 30:
                self.pos[0] += 8 * dt

        else:
            if self.pos[0] > -self.width:
                self.pos[0] -= 8 * dt

        self.rect = self.surf.get_rect(topleft=tuple(self.pos))

    def draw(self, screen, i_cards: dict):
        if self.item is not None:
            try:
                self.surf = i_cards[self.item.name]
            except KeyError:
                return
            self.surf.set_alpha(self.ALPHA)
        screen.blit(self.surf, tuple(self.pos))


class PlayerStatistics:
    def __init__(self, screen, player_obj, assets: dict):
        self.screen = screen
        self.player_obj = player_obj

        # Inventory back surface
        # self.inventory_surf = pygame.Surface((screen.get_width(), 130))
        # self.inventory_surf.set_alpha(170)

        start = (120, 78)
        width = player_obj.hp * 1.7
        height = 17
        self.hp_bar = LoadingBar(
            value=player_obj.hp,
            fg_color="green",
            bg_color="black",
            rect=pygame.Rect((start[0], start[1] - height - 20), (width, height)),
            border_image=assets["bar_border"],
        )
        self.shield_bar = LoadingBar(
            value=player_obj.hp,
            fg_color=(0, 0, 255),
            bg_color="black",
            rect=pygame.Rect((start[0], start[1]), (width, height)),
            border_image=assets["bar_border"],
        )
        self.se_bar = EnergyBar(player_obj, assets["bar_border"])

        bsize = (55, 55)
        self.bsize = bsize
        self.border_img = pygame.transform.scale(assets["border"], bsize)
        self.selected_border_img = pygame.transform.scale(
            assets["selected_border"], bsize
        )
        brect = self.border_img.get_rect()
        self.inventory_rects = [
            pygame.Rect(
                ((brect.height + 5) * col + 300, (brect.width + 5) * 0 + 500),
                brect.size,
            )
            for col in range(8)
        ]
        self.init_inventory_rects = list(self.inventory_rects)
        self.order = {
            "shuriken": pygame.transform.scale(assets["shuriken"], bsize),
            "sword": pygame.transform.scale(assets["sword"], bsize),
            "scythe": pygame.transform.scale(assets["scythe"], bsize),
            "health potion": pygame.transform.scale(
                assets["health_potion"], bsize
            ),
            "shield potion": pygame.transform.scale(
                assets["shield_potion"], bsize
            ),
            "smoke bomb": pygame.transform.scale(assets["smoke_bomb"], bsize),
            "jetpack": pygame.transform.scale(assets["jetpack"], bsize),
        }

        # Indices
        self.chosen_index = 0
        self.init_collide_index = 0
        self.init_collide = False
        self.last_index = None

        # Font
        self.font = pygame.font.SysFont("bahnschrift", 20)

    def update(self, event_info: EventInfo):
        mouse_pos = event_info["mouse pos"]
        mouse_press = event_info["mouse press"]
        events = event_info["events"]

        self.se_bar.update(event_info)
        # self.screen.blit(self.inventory_surf, (0, 0))
        if mouse_press[0] and self.init_collide:
            name = self.player_obj.inventory[self.init_collide_index]
            if name is not None:
                surf = self.order[name].copy()
                surf.set_alpha(200)
                self.screen.blit(surf, mouse_pos)

        for hover_index, rect in enumerate(self.inventory_rects):
            if rect.collidepoint(mouse_pos):
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.chosen_index = hover_index
                        self.init_collide_index = hover_index
                        self.init_collide = True

                    if (
                        event.type == pygame.MOUSEBUTTONUP
                        and self.init_collide
                    ):
                        if hover_index != self.init_collide_index:
                            (
                                self.player_obj.inventory[
                                    self.init_collide_index
                                ],
                                self.player_obj.inventory[hover_index],
                            ) = (
                                self.player_obj.inventory[hover_index],
                                self.player_obj.inventory[
                                    self.init_collide_index
                                ],
                            )

                        self.init_collide = False

                if self.last_index != hover_index:
                    copy_rects = []
                    for index, i_rect in enumerate(self.inventory_rects):
                        if index < hover_index:
                            i_rect = pygame.Rect(
                                i_rect.x - 10, i_rect.y, *i_rect.size
                            )
                        elif index > hover_index:
                            i_rect = pygame.Rect(
                                i_rect.x + 10, i_rect.y, *i_rect.size
                            )
                        else:
                            center = i_rect.center
                            i_rect = pygame.Rect(
                                *i_rect.topleft,
                                i_rect.width + 5,
                                i_rect.height + 5
                            )
                            i_rect.center = center
                        copy_rects.append(i_rect)

                    self.inventory_rects = copy_rects

                self.last_index = hover_index
                break
        else:
            self.inventory_rects = self.init_inventory_rects

    def draw(self):
        self.hp_bar.draw(self.screen, [0, 0])
        self.shield_bar.draw(self.screen, [0, 0])
        self.se_bar.draw(self.screen, [0, 0], moving=True)

        for index, vals in enumerate(
            zip(self.player_obj.inventory, self.inventory_rects)
        ):
            item_name, rect = vals
            if item_name is not None:
                quantity = self.player_obj.item_count[item_name]
                if quantity > 0:
                    self.screen.blit(self.order[item_name], rect)
                    if index == self.chosen_index:
                        self.player_obj.equipped = item_name
                    if quantity > 1:
                        if item_name in ("sword", "scythe"):
                            num_surf = self.font.render(
                                str(quantity), True, "yellow"
                            )
                        else:
                            num_surf = self.font.render(
                                str(quantity), True, "green"
                            )
                        self.screen.blit(num_surf, (rect.x + 5, rect.y + 20))
                elif index == self.chosen_index:
                    self.player_obj.equipped = None

            if index == self.chosen_index:
                # pygame.draw.rect(self.screen, 'yellow', rect, width=3)
                self.screen.blit(self.selected_border_img, rect)
            else:
                self.screen.blit(self.border_img, rect)
