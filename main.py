import time
import json
import pickle
from src.display import *
from src.sprites import cursor_img, background_img, game_border_img
from src.world import World
from src.player import Player
from src.enemy import Ninja
from src.items import Chest
from src.spawner import Spawner
from src.stats import Info, PlayerStatistics
from src.identification import enemy_ids


class Game:
    def __init__(self):
        # Controls
        with open('data/controls.json') as f:
            self.controls = json.load(f)

        # Level data
        with open('data/level_data/level_0', 'rb') as f:
            self.level_manager = pickle.load(f)

        self.run = True
        self.player = Player(*player_start_pos, camera, self.controls["controls"])
        # self.enemy_1 = Ninja(player_start_pos[0] + 300, player_start_pos[1], None, "shadow", 2, 400, player_dist=200)
        self.world = World(self.level_manager)
        self.camera = camera

        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(100)

        self.item_info = Info(screen, eval("pygame." + self.controls["controls"]["info toggle"]))
        self.level_manager.item_info = self.item_info

        self.opened_chests = []
        # Handling serialized mini objects to full fledged game objects
        self.chests = [Chest(s.x, s.y, s.load_control, s.load_speed) for s in self.level_manager.chests]
        self.spawners = [Spawner(*args) for args in self.level_manager.spawners]
        self.items = []
        self.enemies: list[Ninja] = []

        # World objects
        self.shurikens = []

        # Inventory 
        self.statistics = PlayerStatistics(
            screen,
            self.player
        )

    def main_loop(self):
        start = time.perf_counter()
        while self.run:
            clock.tick()

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

            # Render
            screen.blit(background_img, (0, 0))

            for spawner in self.spawners:
                spawner.update(raw_dt)
                spawner.draw(screen, camera)
                for enemy in spawner.enemies:
                    if enemy not in self.enemies and enemy.id in enemy_ids:
                        self.enemies.append(enemy)

                    if enemy.id not in enemy_ids:
                        spawner.enemies.remove(enemy)

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
                "items": self.items,
                "item info": self.item_info,
                "tiles": self.level_manager.all_rects,
                "chests": self.chests,
                "stats": self.statistics,
                "shurikens": self.shurikens
            }

            event_info = {
                "events": events,
                "keys": keys,
                "mouse pos": mouse_pos,
                "mouse press": mouse_press,
                "dt": dt,
                "raw dt": raw_dt
            }
            # Player and enemies
            self.player.update(info, event_info)
            self.player.draw(screen)

            for shuriken in self.player.shurikens:
                if shuriken not in self.shurikens:
                    self.shurikens.append(shuriken)

            for enemy in self.enemies:
                enemy.update(
                    player_pos=self.player.rect.center,
                    info=info,
                    dt=dt
                )
                enemy.draw(screen, self.camera)
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    enemy_ids.remove(enemy.id)

            # Items
            for item in self.items:
                item.update(dt)
                item.draw(screen, self.camera)

            # Shurikens
            for shuriken in self.shurikens:
                shuriken.move(dt)
                shuriken.draw(screen)

                for enemy in self.enemies:
                    if shuriken.rect.colliderect(
                        pygame.Rect(enemy.x - self.camera[0], enemy.y - self.camera[1], *enemy.rect.size)
                    ):
                        enemy.hp -= shuriken.damage
                        self.shurikens.remove(shuriken)
                        self.player.shurikens.remove(shuriken)
                        break

            # Inventory and statistics
            self.statistics.update(mouse_pos, mouse_press)
            self.statistics.draw()

            # Item information
            self.item_info.update(self.player.colliding_item, events, dt)
            self.item_info.draw(screen)

            screen.blit(game_border_img, (0, 0))
            screen.blit(cursor_img, mouse_pos)

            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
