import random
import time
import json
import pytmx
from src.display import *
from src.sprites import cursor_img, background_img, game_border_img, player_size
from src.world import World
from src.player import Player
from src.enemy import Ninja
from src.stats import Info, PlayerStatistics
from src.globals import enemy_ids, shurikens, explosions, general_info, spawners
from src.effects.exp_circle import ExpandingCircles, ExpandingCircle
from src.effects.explosion import Explosion
from src.items import Chest
from src.spawner import Spawner


class Game:
    def __init__(self):
        # Controls
        with open('assets/data/controls.json') as f:
            self.controls = json.load(f)

        # Level data
        self.tile_map = pytmx.load_pygame('assets/data/level_data/level_0_test.tmx')
        tile_map = self.tile_map
        self.all_rects = {}
        for index, layer in enumerate(tile_map):
            if layer.name == 'Tile Layer 1':
                for x, y, _ in layer.tiles():
                    tile_properties = tile_map.get_tile_properties(x, y, index)
                    self.all_rects[(x * tile_map.tileheight, y * tile_map.tilewidth)] = tile_properties['type']

        self.run = True
        self.player = Player(*player_start_pos, camera, self.controls["controls"], screen)
        self.world = World(tile_map)
        self.camera = camera

        # Visuals
        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(125)
        self.expanding_circles = ExpandingCircles(
            init_radius=5, max_radius=40, increment=3, colour=(255, 0, 0), width=10
        )
        self.screen_shake = 0
        self.screen_shake_val = 0

        # Levels
        self.item_info = Info(screen, eval("pygame." + self.controls["controls"]["info toggle"]))
        self.opened_chests = []
        self.chests = [Chest(obj.x, obj.y - (32 * 2), pygame.K_f, 7) for obj in tile_map.get_layer_by_name("chests")]
        global spawners
        spawners += [Spawner([obj.x, obj.y], (obj.width, obj.height), 7, (1, 4), Ninja, player_size, 100) for obj
                         in tile_map.get_layer_by_name("spawners")]
        # spawners = []

        self.items = []
        self.enemies: list[Ninja] = []

        # Inventory
        self.statistics = PlayerStatistics(
            screen,
            self.player
        )

    def load_level(self, n):
        # Level data
        tile_map = pytmx.load_pygame(f'assets/data/level_data/level_{n}.tmx')
        self.all_rects = {}
        for index, layer in enumerate(tile_map):
            for x, y, _ in layer.tiles():
                tile_properties = tile_map.get_tile_properties(x, y, index)
                self.all_rects[(x * tile_map.tileheight, y * tile_map.tilewidth)] = tile_properties['type']

    def handle_shurikens(self, dt):
        # Shurikens
        for shuriken in shurikens:
            shuriken.move(dt)
            if shuriken.launcher == self.player:
                shuriken.draw(screen, [0, 0], dt)
            else:
                shuriken.draw(screen, self.camera, dt)

            broken = False
            if not isinstance(shuriken.launcher, Ninja):
                for enemy in self.enemies:
                    if shuriken.rect.colliderect((
                            enemy.rect.x - self.camera[0],
                            enemy.rect.y - self.camera[1],
                            *enemy.rect.size
                    )):
                        enemy.hp -= shuriken.damage
                        shurikens.remove(shuriken)
                        explosions.append(
                            Explosion(500, (12, 25), list(shuriken.rect.center), (5, 12), 'white')
                        )
                        self.expanding_circles.circles.append(
                            ExpandingCircle(
                                shuriken.rect.center,
                                self.expanding_circles.init_radius,
                                self.expanding_circles.max_radius,
                                self.expanding_circles.increment,
                                (255, 255, 255),
                                width=self.expanding_circles.width,
                            )
                        )
                        self.screen_shake = 20
                        self.screen_shake_val = 2

                        broken = True
                        break

                if broken:
                    continue

            if shuriken.launcher != self.player and shuriken.rect.colliderect(self.player.rect):
                if self.player.shield > 0:
                    self.player.shield -= shuriken.damage
                else:
                    self.player.hp -= shuriken.damage
                shurikens.remove(shuriken)
                self.screen_shake = 30
                self.screen_shake_val = 4
                continue

            # Remove shuriken if it goes outside of boundary
            if shuriken.distance > 800:
                shurikens.remove(shuriken)

    def handle_screen_shake(self, dt):
        # Handle screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1.3 * dt

        render_offset = [0, 0]
        if self.screen_shake > 0:
            render_offset[0] = random.randint(0, self.screen_shake_val * 2) - self.screen_shake_val
            render_offset[1] = random.randint(0, self.screen_shake_val * 2) - self.screen_shake_val

        self.camera[0] += render_offset[0]
        self.camera[1] += render_offset[1]

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

            info = {
                "items": self.items,
                "item info": self.item_info,
                "tiles": self.all_rects,
                "chests": self.chests,
                "stats": self.statistics,
                "expanding circles": self.expanding_circles
            }

            event_info = {
                "events": events,
                "keys": keys,
                "mouse pos": mouse_pos,
                "mouse press": mouse_press,
                "dt": dt,
                "raw dt": raw_dt
            }

            # Render
            screen.blit(background_img, (0, 0))

            # Handle spawners
            for spawner in spawners:
                spawner.update(event_info)
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
            
            # Decorations
            self.world.draw_dec(screen, self.camera)

            # Chests
            for chest in self.chests:
                chest.draw(screen, self.camera)

                # Removing chest
                if chest.loading_bar.loaded:
                    self.items += chest.items
                    self.chests.remove(chest)
                    self.opened_chests.append(chest)

            # Player and enemies
            self.player.update(info, event_info)
            self.player.draw(screen)

            for spawner in spawners:
                spawner.draw_spawn(screen, self.camera)

            for enemy in self.enemies:
                enemy.update(
                    player_pos=self.player.rect.center,
                    info=info,
                    event_info=event_info
                )
                enemy.draw(screen, self.camera)
                if enemy.hp <= 0 or enemy.y > self.tile_map.height * self.tile_map.tileheight:
                    self.enemies.remove(enemy)
                    enemy_ids.remove(enemy.id)

            # Items
            for item in self.items:
                item.update(dt)
                item.draw(screen, self.camera)

            # Shruikens
            self.handle_shurikens(dt)

            # Handle screen shake
            self.handle_screen_shake(dt)

            # Explosions
            for explosion in explosions:
                explosion.draw(screen, dt)

                if len(explosion.particles) == 0:
                    explosions.remove(explosion)

            # General Info and Achievements
            if general_info[0] is not None:
                general_info[0].draw(screen, dt)

            # Inventory and statistics
            self.statistics.update(mouse_pos, mouse_press, events)
            self.statistics.draw()

            # Item information
            self.item_info.update(self.player.colliding_item, events, dt)
            self.item_info.draw(screen)

            # Click effect
            self.expanding_circles.update(events, mouse_pos)
            self.expanding_circles.draw(screen, dt)

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
