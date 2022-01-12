import time
import json
from src.display import *
from src.sprites import background_img
from src.world import World
from src.player import Player
from src.enemy import Ninja
from src.items import Chest
from src.stats import Info


class Game:
    def __init__(self):
        # Controls
        with open('data/controls.json') as f:
            self.controls = json.load(f)

        self.run = True
        self.player = Player(*player_start_pos, camera, self.controls["controls"])
        self.enemy_1 = Ninja(player_start_pos[0] + 300, player_start_pos[1], None, "shadow", 2, 400, player_dist=200)
        chest = Chest(player_start_pos[0] + 500,
                      player_start_pos[1] - 10, pygame.K_f, 0.5)
        self.world = World()
        self.camera = camera

        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(100)

        self.item_info = Info(screen, eval("pygame." + self.controls["controls"]["info toggle"]))

        self.items = []
        self.chests = [chest]
        self.opened_chests = []

    def main_loop(self):
        start = time.perf_counter()
        while self.run:
            clock.tick()

            # Calc
            end = time.perf_counter()
            dt = end - start
            dt *= fps
            start = time.perf_counter()

            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Render
            screen.blit(background_img, (0, 0))
            self.world.draw(screen, self.camera)
            self.camera = self.player.camera

            # Opened chest becomes part of the background
            for opened_chest in self.opened_chests:
                opened_chest.draw(screen, self.camera)

            # Line of lighting
            screen.blit(self.translucent_dark, (0, 0))
            # Glowing

            # Chests
            for chest in self.chests:
                chest.draw(screen, self.camera)

                # Removing chest
                if chest.loading_bar.loaded:
                    self.items += chest.items
                    self.chests.remove(chest)
                    self.opened_chests.append(chest)

            info = {
                "tiles": self.world.rects,
                "items": self.items,
                "chests": self.chests,
                "item info": self.item_info
            }
            # Player and enemies
            self.player.update(info, events, keys, dt)
            self.player.draw(screen)

            self.enemy_1.update(self.player.rect.center, self.world.rects, dt)
            self.enemy_1.draw(screen, self.camera)

            for item in self.items:
                item.update(dt)
                item.draw(screen, self.camera)

            # self.item_1.update(dt)
            # self.item_1.draw(screen, self.camera)

            # Item information
            self.item_info.update(self.player.colliding_item, events, dt)
            self.item_info.draw(screen)

            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
