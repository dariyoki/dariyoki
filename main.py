import random
import time
import json

import pygame.font
import pytmx
from src.display import *
from src.sprites import (cursor_img,
                         background_img,
                         menu_background_img,
                         moon,
                         game_border_img,
                         player_size)
from src.world import World
from src.player import Player
from src.enemy import Ninja
from src.stats import Info, PlayerStatistics
from src._globals import enemy_ids, shurikens, explosions, general_info, spawners
from src.effects.exp_circle import ExpandingCircles, ExpandingCircle
from src.effects.explosion import Explosion
from src.items import Chest
from src.spawner import Spawner
from src.widgets import MenuButton
from src.effects.particle_effects import MainMenuFlare
from src._types import EventInfo, Vec


class Game:
    TILE_SIZE = 32
    PARALLAX_TILE_SIZE = 16
    TOTAL_ROWS = 250
    TOTAL_COLS = 100
    CHUNK_SIZE = 5

    CHUNKS_INFO = tuple(((x * 32, y * 32)
                         for x, y in zip(range(0, TOTAL_ROWS, CHUNK_SIZE), range(0, TOTAL_COLS, CHUNK_SIZE))))

    def __init__(self):
        # Controls
        with open('assets/data/controls.json') as f:
            self.controls = json.load(f)

        pygame.mouse.set_cursor((0, 0), cursor_img)
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

        # Level data
        self.tile_map = pytmx.TiledMap()
        self.current_chunk_index = 0
        self.current_chunk = (0, 0)
        self.all_chunks = {}
        self.all_rects = {}
        self.load_level(0)
        # print(self.all_chunks)
        # self.all_rects = self.all_chunks[self.current_chunk]
        # print(self.all_rects)

        self.run = True
        self.player = Player(*player_start_pos, camera,
                             self.controls["controls"], screen)
        self.world = World(self.tile_map)
        self.camera = camera
        self.t_time_passed = 0
        self.font = pygame.font.Font("assets/fonts/Roboto-Light.ttf", 16)

        # Visuals
        self.translucent_dark = pygame.Surface(screen.get_size())
        self.translucent_dark.set_alpha(125)
        self.transition_overlay_surface = pygame.Surface(screen.get_size())
        self.transition_overlay_surface.set_alpha(0)
        self.transition_overlay_surface_alpha = 0
        self.transitioning = False
        self.transition_fade_speed = 5.7

        self.expanding_circles = ExpandingCircles(
            init_radius=5, max_radius=40, increment=3, colour=(255, 0, 0), width=10
        )
        self.screen_shake = 0
        self.screen_shake_val = 0

        # Levels
        self.item_info = Info(screen, eval(
            "pygame." + self.controls["controls"]["info toggle"]))
        self.opened_chests = []
        self.chests = [Chest(obj.x, obj.y - (32 * 2), pygame.K_f, 7)
                       for obj in self.tile_map.get_layer_by_name("chests")]
        global spawners
        spawners += [Spawner([obj.x, obj.y], (obj.width, obj.height), 7, (1, 4), Ninja, player_size, 100) for obj
                     in self.tile_map.get_layer_by_name("spawners")]
        # spawners = []

        self.items = []
        self.enemies: list[Ninja] = []

        # Inventory
        self.statistics = PlayerStatistics(
            screen,
            self.player
        )

        self.state = "main menu"

        # User interface
        self.menu_button_names = [
            "Start", "Reset", "Exit", "Contents", "Credits"]
        start = (screen.get_rect().center[0] - (170 / 2), 300)
        padding = 10
        self.menu_buttons = [
            MenuButton(
                (
                    start[0],
                    start[1] + ((30 + padding) * index)
                ),
                title=name
            ) for index, name in enumerate(self.menu_button_names)
        ]
        self.main_menu_flare = MainMenuFlare()
        self.moon_bob = [20, 30]
        self.bob_coord = (20, 40)
        self.moon_bob_forward = True

    def load_level(self, n):
        # Level data
        self.tile_map = pytmx.load_pygame(
            f'assets/data/level_data/level_{n}_test.tmx')
        tile_map = self.tile_map
        for index, layer in enumerate(tile_map):
            if layer.name == 'Tile Layer 1':
                for x, y, _ in layer.tiles():
                    tile_properties = tile_map.get_tile_properties(x, y, index)
                    tile_pos = (x * tile_map.tileheight, y * tile_map.tilewidth)
                    self.all_rects[tile_pos] = (tile_properties["type"],
                                                pygame.Rect(tile_pos,
                                                            (self.TILE_SIZE, self.TILE_SIZE))
                                                )
                    # previous_chunk = (0, 0)
                    # for chunk in self.CHUNKS_INFO:
                    #     self.all_chunks[chunk] = {}
                    #     if previous_chunk[0] > tile_pos[0] and previous_chunk[1] > tile_pos[1] and \
                    #             tile_pos[0] < chunk[0] and tile_pos[1] < chunk[1]:
                    #         self.all_chunks[chunk][tile_pos] = tile_properties["type"]
                    #     previous_chunk = chunk
                break

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
                            Explosion(500, (12, 25), list(
                                shuriken.rect.center), (5, 12), 'white')
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
            render_offset[0] = random.randint(
                0, self.screen_shake_val * 2) - self.screen_shake_val
            render_offset[1] = random.randint(
                0, self.screen_shake_val * 2) - self.screen_shake_val

        self.camera[0] += render_offset[0]
        self.camera[1] += render_offset[1]

    def handle_rust_binding(self, raw_dt):
        self.t_time_passed += raw_dt
        if self.t_time_passed > 1:
            f = open("read_data/player_inv.json", "w")
            json.dump(self.player.item_count, f, indent=2)
            self.t_time_passed = 0

    def handle_fade_in(self, dt) -> bool:
        self.transition_overlay_surface_alpha += self.transition_fade_speed * dt
        if self.transition_overlay_surface_alpha > 255:
            self.transition_overlay_surface_alpha = 255
            return True

        return False

    def handle_fade_out(self, dt) -> bool:
        self.transition_overlay_surface_alpha -= self.transition_fade_speed * dt
        if self.transition_overlay_surface_alpha < 0:
            self.transition_overlay_surface_alpha = 0
            return True

        return False

    def main_menu(self, event_info: EventInfo) -> None:
        screen.blit(menu_background_img, (0, 0))
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

        screen.blit(moon, self.moon_bob)
        self.main_menu_flare.draw(screen, event_info)
        for menu_btn in self.menu_buttons:
            menu_btn.update(event_info)
            menu_btn.draw(screen)

            if menu_btn.title == "Start" and menu_btn.clicked:
                self.transitioning = True

        if self.transitioning:
            if self.handle_fade_in(event_info["dt"]):
                self.state = "level test"

    def level_test(self, event_info: dict, info: dict) -> None:
        dt = event_info["dt"]
        mouse_pos = event_info["mouse pos"]
        events = event_info["events"]
        mouse_press = event_info["mouse press"]

        # previous_chunk = (0, 0)
        # for i, chunk in enumerate(self.CHUNKS_INFO):
        #     if self.player.x > previous_chunk[0] and self.player.y > previous_chunk[1] \
        #             and self.player.x < chunk[0] and self.player.y < chunk[1]:
        #         self.current_chunk = chunk
        #         self.current_chunk_index = i
        #         print(self.all_rects)
        #
        # self.all_rects = self.all_chunks[self.current_chunk]

        # Transitioning
        if self.transitioning:
            self.handle_fade_out(dt)

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

        self.world.draw_parallax(screen, camera)
        self.world.draw(screen, self.camera)
        self.world.draw_grass(screen, self.camera)
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
        self.statistics.update(event_info)
        self.statistics.draw()

        # Item information
        self.item_info.update(self.player.colliding_item, events, dt)
        self.item_info.draw(screen)

        # Click effect
        self.expanding_circles.update(events, mouse_pos)
        self.expanding_circles.draw(screen, dt)

        # self.handle_rust_binding(raw_dt)

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
            screen.fill(0)

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

            if self.state == "main menu":
                pygame.display.set_caption('Dariyoki | Main Menu')
                self.main_menu(event_info)
            elif self.state == "level test":
                pygame.display.set_caption('Dariyoki | Level Test')
                self.level_test(event_info, info)

            # Touchup
            self.transition_overlay_surface.set_alpha(
                self.transition_overlay_surface_alpha)
            screen.blit(self.transition_overlay_surface, (0, 0))
            screen.blit(game_border_img, (0, 0))
            # screen.blit(cursor_img, mouse_pos)

            screen.blit(self.font.render(f"{clock.get_fps():.2f}", True, (200, 174, 0)), (1000, 10))
            # Event handler
            for event in events:
                if event.type == pygame.QUIT:
                    self.run = False

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main_loop()
