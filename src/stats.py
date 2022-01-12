import pygame
from src.sprites import border_img, i_cards
from src.widgets import Label


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
        # if self.item_stats is not None:
        #     text = self.font.render(self.item_stats.name, True, "yellow")
        #     f_rect = text.get_rect(center=(
        #         self.rect.midtop[0],
        #         self.rect.midtop[1] + 100
        #     ))
        #
        #     img_rect = self.item.image.get_rect(center=(
        #         self.rect.midtop[0],
        #         self.rect.midtop[1] + 50
        #     ))
        #
        #     screen.blit(self.item.image, img_rect)
        #     screen.blit(self.image_border, img_rect)
        #     screen.blit(
        #         self.font.render(self.item_stats.name, True, "white"),
        #         f_rect
        #     )
        # screen.blit(self.surf, tuple(self.pos))
