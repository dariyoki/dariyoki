import time
from src.display import *
from src.world import World
from src.sprites import shield_potion_img
from src.player import Player
from src.enemy import Ninja
from src.items import Item


class Game:
    def __init__(self):
        self.run = True
        self.enemy_1 = Ninja(300, 200, None, "shadow", 2, 400, player_dist=200)
        self.item_1 = Item(shield_potion_img)
        self.world = World()
        self.camera = [-(screen_width // 2), -(screen_height // 2)]
        self.player = Player(50, 50, self.camera)

        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(100)

    def main_loop(self):
        start = time.perf_counter()
        while self.run:
            clock.tick()

            end = time.perf_counter()
            dt = end - start
            dt *= fps
            start = time.perf_counter()

            events = pygame.event.get()

            screen.fill(bg)
            self.world.draw(screen, self.camera)
            self.camera = self.player.camera

            # Line of lighting
            screen.blit(self.translucent_dark, (0, 0))

            # Glowing
            self.player.update(self.world.rects, events, dt)
            self.player.draw(screen)

            self.enemy_1.update(self.player.rect.center, self.world.rects, dt)
            self.enemy_1.draw(screen, self.camera)

            self.item_1.update([400, screen_height - (32*2) - 20], dt)
            self.item_1.draw(screen, self.camera)

            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
