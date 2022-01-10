import time
import random
from src.display import *
from src.sprites import items
from src.world import World
from src.player import Player
from src.enemy import Ninja
from src.items import Item, Chest


class Game:
    def __init__(self):
        self.run = True
        self.enemy_1 = Ninja(300, 200, None, "shadow", 2, 400, player_dist=200)
        chest = Chest(400, screen_height - (32*3), pygame.K_f, 0.5)
        # self.item_1 = Item('shield potion', items['shield potion'], [400, screen_height - (32*2) - 20])
        self.world = World()
        self.camera = [-(screen_width // 2), -(screen_height // 2)]
        self.player = Player(50, 50, self.camera)

        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(100)

        self.items = []
        self.chests = [chest]
        self.opened_chests = []

    def main_loop(self):
        x_freq = random.randrange(10)
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
            screen.fill(bg)
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
                "chests": self.chests
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

            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
