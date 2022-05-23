import pygame

from src.generics import EventInfo, Vec
from src.effects.particle_effects import MainMenuFlare
from src.states.game_state import GameState
from src.ui.widgets import MenuButton


class MainMenu(GameState):
    def __init__(self, screen: pygame.Surface, assets: dict):
        super().__init__("main menu", screen)
        self.assets = assets
        self.next_state = None

        # User interface
        self.menu_button_names = ["Start", "Reset", "Exit", "Contents", "Credits"]
        start = (screen.get_rect().center[0] - (170 / 2), 300)
        padding = 10
        self.menu_buttons = [
            MenuButton((start[0], start[1] + ((30 + padding) * index)), title=name)
            for index, name in enumerate(self.menu_button_names)
        ]
        self.main_menu_flare = MainMenuFlare(self.assets["flame_particles"])
        self.moon_bob = [20, 30]
        self.bob_coord = (20, 40)
        self.moon_bob_forward = True

    def update(self, event_info: EventInfo):
        moon_motion = 0.4 * event_info["dt"]
        if self.moon_bob_forward:
            if self.moon_bob[0] < self.bob_coord[1]:
                self.moon_bob[0] += moon_motion
                self.moon_bob[1] += moon_motion
            else:
                self.moon_bob_forward = False
        else:
            if self.moon_bob[0] > self.bob_coord[0]:
                self.moon_bob[0] -= moon_motion
                self.moon_bob[1] -= moon_motion
            else:
                self.moon_bob_forward = True

        for menu_btn in self.menu_buttons:
            menu_btn.update(event_info)

            if menu_btn.title == "Start" and menu_btn.clicked:
                self.transitioning = True

        if self.transitioning:
            if self.handle_fade_in(event_info["dt"]):
                self.next_state = "level selector"

    def draw(self, event_info: EventInfo):
        self.screen.blit(self.assets["red_ski_looks_good"], (0, 0))
        self.main_menu_flare.draw(self.screen, event_info)

        for menu_btn in self.menu_buttons:
            menu_btn.draw(self.screen)
        self.screen.blit(self.assets["game_border"], (0, 0))
