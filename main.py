import asyncio
import logging
import time

from src.display import *
from src.sprites import load_assets
from src.states.levels import LevelSelector, Level
from src.states.main_menu import MainMenu
from src.states.generics import GameStates


logger = logging.getLogger("log")


class Game:
    TILE_SIZE = 32
    PARALLAX_TILE_SIZE = 16
    TOTAL_ROWS = 250
    TOTAL_COLS = 100

    def __init__(self):
        self.state = "main menu"
        self.last_state = self.state
        self.assets = load_assets(self.state)
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
            case "level":
                self.current_state = Level(0, screen, self.assets)
            case "main menu":
                self.current_state = MainMenu(screen, self.assets)
            case "level selector":
                self.current_state = LevelSelector(screen, self.assets)

    def selective_process(self, event_info):

        if self.state == "main menu":
            pygame.display.set_caption("Dariyoki | Main Menu")
            self.current_state.update(event_info)
            self.current_state.draw(event_info)
        elif self.state == "level":
            pygame.display.set_caption("Dariyoki | Level Test")
            self.current_state.update(event_info)
        elif self.state == "level selector":
            pygame.display.set_caption("Dariyoki | Level Selector")
            self.current_state.draw()

    async def main_loop(self):
        start = time.perf_counter()
        while self.run:
            clock.tick()
            self.last_state = self.state

            # Calc
            end = time.perf_counter()
            dt = end - start
            raw_dt = dt
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

            # Touchup
            self.current_state.transition_overlay_surface.set_alpha(
                self.current_state.transition_overlay_surface_alpha
            )
            screen.blit(self.current_state.transition_overlay_surface, (0, 0))

            screen.blit(
                self.font.render(f"{clock.get_fps():.2f}", True, (200, 174, 0)),
                (1000, 10),
            )
            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.flip()
            if self.current_state.next_state is not None:
                self.state = self.current_state.next_state
            if self.last_state != self.state:
                self.assets = load_assets(self.state)
                self.selective_load()
            await asyncio.sleep(0)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    asyncio.run(game.main_loop())
