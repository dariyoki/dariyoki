import pygame
from src.sprites import (border_img,
                         i_cards,
                         sword_img,
                         shuriken_img,
                         health_potion_img,
                         shield_potion_img,
                         sb_img,
                         scythe_img)
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
    def __init__(self, screen: pygame.Surface, open_control: int):
        self.screen = screen
        padx, pady = 30, 15
        self.height = screen.get_height() - pady
        self.open_control = open_control
        self.width = 300

        self.surf = pygame.Surface((self.width, self.height - pady))
        self.image = pygame.transform.scale(border_img, (self.width, self.height - pady))
        self.surf.blit(self.image, (0, 0))
        self.surf.set_alpha(150)
        self.rect = self.surf.get_rect()

        self.pos = [-self.width, pady]

        # Flags
        self.opening = False
        self.o_lock = False
        self.item_stats = None
        self.item = None

        self.label = Label(
            position=self.pos,
            size=(140, 35),
            content="Click [ i ] to open/close",
            colour='black',
            border_colour='white',
            txt_colour='purple',
        )

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

        self.label.change_pos((self.pos[0] + 77, self.pos[1]))
        self.rect = self.surf.get_rect(topleft=tuple(self.pos))

    def draw(self, screen):
        if self.item is not None:
            self.surf = i_cards[self.item.name]
            self.surf.set_alpha(150)
            self.surf.blit(self.image, (0, 0))
        screen.blit(self.surf, tuple(self.pos))

        self.label.draw(screen)


class PlayerStatistics:
    def __init__(self, screen, player_obj):
        self.screen = screen
        self.player_obj = player_obj

        # Inventory back surface
        self.inventory_surf = pygame.Surface((screen.get_width(), 130))
        self.inventory_surf.set_alpha(170)

        start = (120, 30)
        width = player_obj.hp * 1.5
        self.hp_bar = LoadingBar(
                value=player_obj.hp,
                fg_color='green',
                bg_color='black',
                rect=pygame.Rect(start, (width, 20))
            )
        self.shield_bar = LoadingBar(
                value=player_obj.hp,
                fg_color=(0, 0, 255),
                bg_color='black',
                rect=pygame.Rect((start[0], start[1] + 20 + 5), (width, 20))
            )
        self.se_bar = LoadingBar(
                value=player_obj.hp,
                fg_color=(0, 255, 255),
                bg_color='black',
                rect=pygame.Rect((start[0], start[1] + (20 * 2) + (5 * 2)), (width, 20))
            )

        brect = border_img.get_rect()
        self.inventory_rects = []
        for row in range(len(player_obj.inventory.keys())):
            for col in range(10):
                self.inventory_rects.append(
                    pygame.Rect(
                        (brect.height * col + 370, brect.width * row + 10),
                        brect.size
                    )
                )

        self.order = {
            "J1": ("shuriken", shuriken_img),
            "J2": ("sword", sword_img),
            "J3": None,
            "J4": None,
            "J5": None,
            "J6": None,
            "J7": None,
            "J8": None,
            "J9": None,
            "J10": ("scythe", scythe_img),
            "K1": ("health potion", pygame.transform.scale(health_potion_img, (32, 32))),
            "K2": ("shield potion", pygame.transform.scale(shield_potion_img, (32, 32))),
            "K3": None,
            "K4": None,
            "K5": None,
            "K6": ("smoke bomb", sb_img),
            "K7": None,
            "K8": None,
            "K9": None,
            "K10": None,
            "L1": None,
            "L2": None,
            "L3": None,
            "L4": None,
            "L5": None,
            "L6": None,
            "L7": None,
            "L8": None,
            "L9": None,
            "L10": None,
        }

        self.chosen_index = 1

        # Font
        self.font = pygame.font.SysFont("bahnschrift", 25)

    def update(self, mouse_pos, mouse_press):
        if mouse_press[0]:
            for rect in self.inventory_rects:
                if rect.collidepoint(mouse_pos):
                    self.chosen_index = self.inventory_rects.index(rect)

    def draw(self):
        self.screen.blit(self.inventory_surf, (0, 0))
        self.hp_bar.draw(self.screen, [0, 0])
        self.shield_bar.draw(self.screen, [0, 0])
        self.se_bar.draw(self.screen, [0, 0])

        for index, vals in enumerate(zip(self.order, self.inventory_rects)):
            pos_key, rect = vals
            if self.order[pos_key] is not None:
                quantity = 0
                if "J" in pos_key:
                    quantity = self.player_obj.inventory["weapons"][self.order[pos_key][0]]
                elif "K" in pos_key:
                    quantity = self.player_obj.inventory["items"][self.order[pos_key][0]]
                elif "L" in pos_key:
                    quantity = self.player_obj.inventory["soul boosted"][self.order[pos_key][0]]

                if quantity > 0:
                    self.screen.blit(self.order[pos_key][1], rect)
                    if index == self.chosen_index:
                        self.player_obj.equipped = self.order[pos_key][0]
                    if quantity > 1:
                        num_surf = self.font.render(str(quantity), True, "green")
                        self.screen.blit(num_surf, rect)

            if index == self.chosen_index:
                pygame.draw.rect(self.screen, 'yellow', rect, width=3)
            else:
                self.screen.blit(border_img, rect)

