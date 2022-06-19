"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import json
import logging
import time

import pygame

from dariyoki.display import clock, fps, screen
from dariyoki.sprites import load_assets
from dariyoki.states.enums import States
from dariyoki.states.generics import GameStates, Level, LevelSelector, MainMenu

logger = logging.getLogger()


class Game:
    def __init__(self):
        self.state: States = States.MAIN_MENU
        self.assets = load_assets(self.state.value, screen)
        self.current_state: GameStates = MainMenu(screen, self.assets)
        # Controls
        with open("assets/data/controls.json") as f:
            self.controls = json.load(f)

        pygame.mouse.set_cursor((0, 0), self.assets["cursor"])

        self.run = True
        self.font = pygame.font.Font("assets/fonts/Roboto-Light.ttf", 16)
        logger.info("Game Initialized")

    def selective_load(self):
        match self.state:
            case States.MAIN_MENU:
                self.current_state = MainMenu(screen, self.assets)
            case States.LEVEL:
                self.current_state = Level(0, screen, self.assets)
            case States.LEVEL_SELECTOR:
                self.current_state = LevelSelector(screen, self.assets)

    def selective_process(self, event_info):
        if self.state == States.MAIN_MENU:
            pygame.display.set_caption("Dariyoki | Main Menu")
            self.current_state.update(event_info)
            self.current_state.draw(event_info)
        elif self.state == States.LEVEL:
            pygame.display.set_caption("Dariyoki | Level Test")
            self.current_state.update(event_info)
        elif self.state == States.LEVEL_SELECTOR:
            pygame.display.set_caption("Dariyoki | Level Selector")
            self.current_state.update(event_info)
            self.current_state.draw()

    def main_loop(self):
        start = time.perf_counter()
        while self.run:
            clock.tick()

            # Calc
            end = time.perf_counter()
            raw_dt = min(end - start, 0.7)
            dt = raw_dt
            dt *= fps
            start = time.perf_counter()

            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_press = pygame.mouse.get_pressed()
            screen.fill(0)

            event_info = {
                "events": events,
                "keys": keys,
                "mouse pos": mouse_pos,
                "mouse press": mouse_press,
                "dt": dt,
                "raw dt": raw_dt,
            }

            self.selective_process(event_info)

            # Touch up
            self.current_state.transition_overlay_surface.set_alpha(
                self.current_state.transition_overlay_surface_alpha
            )
            screen.blit(self.current_state.transition_overlay_surface, (0, 0))

            screen.blit(
                self.font.render(
                    f"{clock.get_fps():.2f}", True, (200, 174, 0)
                ),
                (1000, 10),
            )
            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            if self.current_state.next_state is not None:
                self.state = self.current_state.next_state
                self.assets = load_assets(self.state.value, screen)
                self.selective_load()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
