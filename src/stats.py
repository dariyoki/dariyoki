import pygame
import itertools
from src.sprites import (border_img,
                         selected_border_img,
                         i_cards,
                         sword_img,
                         shuriken_img,
                         health_potion_img,
                         shield_potion_img,
                         sb_img,
                         scythe_img,
                         bar_border_img)
from src.widgets import Label, LoadingBar


class ItemStats:
    def __init__(self, item):
        self.name = item.name
        self.hp = None
        self.shield = None
        self.damage = None
        self.other_benefits = None
        self.description = None
        match item.name:
            case "health potion":
                self.hp = 40
                self.description = f"""
                A health potion brewed in the Bee territory. 
                It gives you {self.hp} Health!
                """
            case "shield potion":
                self.shield = 50
                self.description = f"""
                A shield potion made from the nectar of the rich blue Gylops plants found 
                commonly in the Davis territory.
                It gives you {self.shield} shield!
                """
            case "shuriken":
                self.damage = 30
                self.description = f"""
                A basic but deadly shuriken forged in the depths of Valhalla.
                It causes {self.damage} damage!
                """
            case "sword":
                self.damage = 60
                self.description = f"""
                An almost fatal blow sword. But we weary as it can only be used in close 
                range! 
                It causes {self.damage} damage!
                """
            case "smoke bomb":
                self.shield = 10
                self.description = """
                A smoke bomb that ninjas use to disappear and then reappear in another place.
                """


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
        #
        # self.label = Label(
        #     position=self.pos,
        #     size=(140, 35),
        #     content="Click [ i ] to open/close",
        #     colour='black',
        #     border_colour='white',
        #     txt_colour='purple',
        # )

    def update(self, colliding_item, events, dt):
        if colliding_item is not None:
            self.item = colliding_item
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.open_control:
                    self.opening = not self.opening
                    self.o_lock = not self.o_lock

        if self.opening:
            if self.pos[0] < 30:
                self.pos[0] += 8 * dt

        else:
            if self.pos[0] > -self.width:
                self.pos[0] -= 8 * dt

        # self.label.change_pos((self.pos[0] + 77, self.pos[1]))
        self.rect = self.surf.get_rect(topleft=tuple(self.pos))

    def draw(self, screen):
        if self.item is not None:
            self.surf = i_cards[self.item.name]
            self.surf.set_alpha(self.ALPHA)
        screen.blit(self.surf, tuple(self.pos))

        # self.label.draw(screen)


class PlayerStatistics:
    def __init__(self, screen, player_obj):
        self.screen = screen
        self.player_obj = player_obj

        # Inventory back surface
        self.inventory_surf = pygame.Surface((screen.get_width(), 130))
        self.inventory_surf.set_alpha(170)

        start = (120, 40)
        width = player_obj.hp * 1.7
        height = 17
        self.hp_bar = LoadingBar(
                value=player_obj.hp,
                fg_color='green',
                bg_color='black',
                rect=pygame.Rect((start[0], 610 - height - 5), (width, height)),
                _border_img=bar_border_img
            )
        self.shield_bar = LoadingBar(
                value=player_obj.hp,
                fg_color=(0, 0, 255),
                bg_color='black',
                rect=pygame.Rect((start[0], 610), (width, height)),
                _border_img=bar_border_img
            )
        self.se_bar = LoadingBar(
                value=player_obj.hp,
                fg_color=(0, 255, 255),
                bg_color='black',
                rect=pygame.Rect((970, 40), (width, height)),
                _border_img=bar_border_img
            )

        bsize = (50, 50)
        self.bsize = bsize
        self.border_img = pygame.transform.scale(border_img, bsize)
        self.selected_border_img = pygame.transform.scale(selected_border_img, bsize)
        brect = self.border_img.get_rect()
        self.inventory_rects = [pygame.Rect(
                     ((brect.height + 5) * col + 300, (brect.width + 5) * 0 + 30),
                     brect.size
                 ) for col in range(8)]
        self.init_inventory_rects = list(self.inventory_rects)
        self.order = {
            "shuriken": pygame.transform.scale(shuriken_img, bsize),
            "sword": pygame.transform.scale(sword_img, bsize),
            "scythe": pygame.transform.scale(scythe_img, bsize),
            "health potion": pygame.transform.scale(health_potion_img, bsize),
            "shield potion": pygame.transform.scale(shield_potion_img, bsize),
            "smoke bomb": pygame.transform.scale(sb_img, bsize),
        }

        # Indices
        self.chosen_index = 1
        self.init_collide_index = 1
        self.init_collide = False
        self.last_index = None

        # Font
        self.font = pygame.font.SysFont("bahnschrift", 20)

    def update(self, mouse_pos, mouse_press, events):
        self.screen.blit(self.inventory_surf, (0, 0))
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

                    if event.type == pygame.MOUSEBUTTONUP and self.init_collide:
                        if hover_index != self.init_collide_index:
                            self.player_obj.inventory[self.init_collide_index], self.player_obj.inventory[hover_index] = self.player_obj.inventory[hover_index], self.player_obj.inventory[self.init_collide_index]

                        self.init_collide = False

                if self.last_index != hover_index:
                    copy_rects = []
                    for index, i_rect in enumerate(self.inventory_rects):
                        if index < hover_index:
                            i_rect = pygame.Rect(i_rect.x - 10, i_rect.y, *i_rect.size)
                        elif index > hover_index:
                            i_rect = pygame.Rect(i_rect.x + 10, i_rect.y, *i_rect.size)
                        else:
                            center = i_rect.center
                            i_rect = pygame.Rect(*i_rect.topleft, i_rect.width + 5, i_rect.height + 5)
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
        self.se_bar.draw(self.screen, [0, 0])

        for index, vals in enumerate(zip(self.player_obj.inventory, self.inventory_rects)):
            item_name, rect = vals
            if item_name is not None:
                quantity = self.player_obj.item_count[item_name]
                if quantity > 0:
                    self.screen.blit(self.order[item_name], rect)
                    if index == self.chosen_index:
                        self.player_obj.equipped = item_name
                    if quantity > 1:
                        if item_name in ("sword", "scythe"):
                            num_surf = self.font.render(str(quantity), True, "yellow")
                        else:
                            num_surf = self.font.render(str(quantity), True, "green")
                        self.screen.blit(num_surf, (rect.x + 5, rect.y + 20))
                elif index == self.chosen_index:
                    self.player_obj.equipped = None

            if index == self.chosen_index:
                # pygame.draw.rect(self.screen, 'yellow', rect, width=3)
                self.screen.blit(self.selected_border_img, rect)
            else:
                self.screen.blit(self.border_img, rect)
