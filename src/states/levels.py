import json
import random
from typing import Optional

import pygame
import pytmx

from src._globals import enemy_ids, explosions, general_info, shurikens, spawners
from src.generics import Vec
from src.display import camera, player_start_pos, screen_width, screen_height
from src.effects.exp_circle import ExpandingCircle, ExpandingCircles
from src.effects.explosion import Explosion
from src.entities.enemy import Bee, Ninja
from src.entities.player import Player
from src.items import Chest
from src.spawner import Spawner
from src.states.game_state import GameState
from src.ui.stats import Info, PlayerStatistics
from src.utils import Time, resize
from src.world import World


class LevelSelector(GameState):
    def __init__(self, screen: pygame.Surface, assets: dict):
        super().__init__("level selector", screen)
        self.assets = assets
        self.mod_assets()
        self.next_state = None

    def mod_assets(self):
        self.assets["level_map_cr"] = pygame.transform.scale(self.assets["level_map_cr"], (screen_width, screen_height))

    def draw(self):
        self.screen.blit(self.assets["level_map_cr"], (0, 0))


class Level(GameState):
    TILE_SIZE = 32

    def __init__(self, n: int, screen: pygame.Surface, assets: dict):
        super().__init__("level", screen)
        # Controls
        with open("assets/data/controls.json") as f:
            self.controls = json.load(f)

        self.next_state: Optional[str] = None
        self.tile_map = pytmx.TiledMap()
        self.all_rects = {}
        self.load_level(n)
        self.assets = assets
        self.assets["chest"] = resize(self.assets["chest"], 2.0)
        item_size = (25, 25)
        self._items = {
            "health potion": pygame.transform.scale(
                self.assets["health_potion"], item_size
            ),
            "shield potion": pygame.transform.scale(
                self.assets["shield_potion"], item_size
            ),
            "shuriken": pygame.transform.scale(self.assets["shuriken"], item_size),
            "smoke bomb": pygame.transform.scale(self.assets["smoke_bomb"], item_size),
            "sword": pygame.transform.scale(self.assets["sword"], item_size),
            "scythe": pygame.transform.scale(self.assets["scythe"], item_size),
        }
        self.player = Player(
            *player_start_pos,
            camera,
            self.controls["controls"],
            screen,
            assets=self.assets,
            items=self._items,
        )
        self.world = World(self.tile_map, self.assets["bush_parallax"])
        self.camera = camera
        # Levels
        self.item_info = Info(
            screen, eval("pygame." + self.controls["controls"]["info toggle"])
        )
        self.items = []
        self.opened_chests = []
        self.chests = [
            Chest(
                obj.x,
                obj.y - 32,
                pygame.K_f,
                7,
                border_image=self.assets["border"],
                chests=self.assets["chest"],
                items=self._items,
            )
            for obj in self.tile_map.get_layer_by_name("chests")
        ]
        global spawners
        spawners += [
            Spawner(
                [obj.x, obj.y],
                (obj.width, obj.height),
                7,
                (1, 4),
                self.player.rect.size,
                100,
                border_image=self.assets["border"],
                spawn_images=(
                    self.assets["spawner_shadow_ninja"],
                    self.assets["spawning_shadow_ninja"],
                ),
                characters=self.assets["characters"],
                items=self.items
            )
            for obj in self.tile_map.get_layer_by_name("spawners")
        ]
        # spawners = []

        self.enemies: list[Ninja] = []

        # Inventory
        self.statistics = PlayerStatistics(screen, self.player, self.assets)

        self.bees: list[Bee] = []
        self.bee_gen_time = Time(random.uniform(4, 6))

        self.i_cards = {
            "ak47": self.assets["i_ak47"],
            "glock": self.assets["i_glock"],
            "health potion": self.assets["i_health_potion"],
            "scythe": self.assets["i_scythe"],
            "shield potion": self.assets["i_shield_potion"],
            "shuriken": self.assets["i_shuriken"],
            "smoke bomb": self.assets["i_smoke_bomb"],
            "sword": self.assets["i_sword"],
        }

        self.t_time_passed = 0

        self.expanding_circles = ExpandingCircles(
            init_radius=5, max_radius=40, increment=3, colour=(255, 0, 0), width=10
        )
        self.screen_shake = 0
        self.screen_shake_val = 0

    def handle_screen_shake(self, dt):
        # Handle screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1.3 * dt

        render_offset = [0, 0]
        if self.screen_shake > 0:
            render_offset[0] = (
                random.randint(0, self.screen_shake_val * 2) - self.screen_shake_val
            )
            render_offset[1] = (
                random.randint(0, self.screen_shake_val * 2) - self.screen_shake_val
            )

        self.camera[0] += render_offset[0]
        self.camera[1] += render_offset[1]

    def load_level(self, n):
        # Level data
        self.tile_map = pytmx.load_pygame(f"assets/data/level_data/level_{n}_test.tmx")
        tile_map = self.tile_map
        for index, layer in enumerate(tile_map):
            if layer.name == "Tile Layer 1":
                for x, y, _ in layer.tiles():
                    tile_properties = tile_map.get_tile_properties(x, y, index)
                    tile_pos = (x * tile_map.tileheight, y * tile_map.tilewidth)
                    self.all_rects[tile_pos] = (
                        tile_properties["type"],
                        pygame.Rect(tile_pos, (self.TILE_SIZE, self.TILE_SIZE)),
                    )
                break

    def handle_shurikens(self, dt):
        # Shurikens
        for shuriken in shurikens:
            shuriken.move(dt)
            if shuriken.launcher == self.player:
                shuriken.draw(self.screen, [0, 0], dt)
            else:
                shuriken.draw(self.screen, self.camera, dt)

            broken = False
            if not isinstance(shuriken.launcher, Ninja):
                for enemy in self.enemies:
                    if shuriken.rect.colliderect(
                        (
                            enemy.rect.x - self.camera[0],
                            enemy.rect.y - self.camera[1],
                            *enemy.rect.size,
                        )
                    ):
                        enemy.hp -= shuriken.damage
                        shurikens.remove(shuriken)
                        explosions.append(
                            Explosion(
                                500,
                                (12, 25),
                                list(shuriken.rect.center),
                                (5, 12),
                                "white",
                            )
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

            if shuriken.launcher != self.player and shuriken.rect.colliderect(
                self.player.rect
            ):
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

    def update(self, event_info: dict) -> None:
        dt = event_info["dt"]
        mouse_pos = event_info["mouse pos"]
        events = event_info["events"]
        mouse_press = event_info["mouse press"]

        info = {
            "items": self.items,
            "item info": self.item_info,
            "tiles": self.all_rects,
            "chests": self.chests,
            "stats": self.statistics,
            "expanding circles": self.expanding_circles,
        }

        # Transitioning
        if self.transitioning:
            self.handle_fade_out(dt)

        # Render
        self.screen.blit(self.assets["background"], (0, 0))

        # Handle spawners
        for spawner in spawners:
            spawner.update(event_info)
            spawner.draw(self.screen, camera)
            for enemy in spawner.enemies:
                if enemy not in self.enemies and enemy.id in enemy_ids:
                    self.enemies.append(enemy)

                if enemy.id not in enemy_ids:
                    spawner.enemies.remove(enemy)

        self.world.draw_parallax(self.screen, camera)
        self.world.draw(self.screen, self.camera)
        self.world.draw_grass(self.screen, self.camera)
        self.camera = self.player.camera

        # Opened chest becomes part of the background
        for opened_chest in self.opened_chests:
            opened_chest.draw(self.screen, self.camera)

        # Line of lighting
        self.screen.blit(self.translucent_dark, (0, 0))

        # Decorations
        self.world.draw_dec(self.screen, self.camera)

        # Chests
        for chest in self.chests:
            chest.draw(self.screen, self.camera)

            # Removing chest
            if chest.loading_bar.loaded:
                self.items += chest.items
                self.chests.remove(chest)
                self.opened_chests.append(chest)

        # Player and enemies
        self.player.update(info, event_info)
        self.player.draw(self.screen)

        for spawner in spawners:
            spawner.draw_spawn(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.update(
                player_pos=self.player.rect.center, info=info, event_info=event_info
            )
            enemy.draw(self.screen, self.camera)
            if (
                enemy.hp <= 0
                or enemy.y > self.tile_map.height * self.tile_map.tileheight
            ):
                self.enemies.remove(enemy)
                enemy_ids.remove(enemy.id)

        if self.bee_gen_time.update():
            new_bee = Bee(
                self.player,
                Vec(random.randrange(0, 300), random.randrange(0, 300)),
                bee_img=self.assets["bee"],
            )
            self.bees.append(new_bee)

        for bee in self.bees:
            bee.update()
            bee.draw(self.screen, camera)

        # Items
        for item in self.items:
            item.update(dt)
            item.draw(self.screen, self.camera)

        # Shruikens
        self.handle_shurikens(dt)

        # Handle screen shake
        self.handle_screen_shake(dt)

        # Explosions
        for explosion in explosions:
            explosion.draw(self.screen, dt)

            if len(explosion.particles) == 0:
                explosions.remove(explosion)

        # General Info and Achievements
        if general_info[0] is not None:
            general_info[0].draw(self.screen, dt)

        # Inventory and statistics
        self.statistics.update(event_info)
        self.statistics.draw()

        # Item information
        self.item_info.update(self.player.colliding_item, events, dt)
        self.item_info.draw(self.screen, self.i_cards)

        # Click effect
        self.expanding_circles.update(events, mouse_pos)
        self.expanding_circles.draw(self.screen, dt)
        self.screen.blit(self.assets["game_border"], (0, 0))

