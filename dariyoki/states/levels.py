"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import functools
import json
import logging
import operator
import random
from typing import Optional

import pygame
import pytmx
import abc

from dariyoki.common import general_info
from dariyoki.display import camera, player_start_pos, screen_height, screen_width
from dariyoki.effects.exp_circle import ExpandingCircle, ExpandingCircles
from dariyoki.effects.explosion import Explosion
from dariyoki.effects.particle_effects import LevelMapFlare
from dariyoki.effects.transition import FadeTransition
from dariyoki.entities.enemy import Bee, Ninja
from dariyoki.entities.player import Player
from dariyoki.generics import EventInfo, Vec, Assets
from dariyoki.items import Chest, Item
from dariyoki.spawner import BeeSpawner, Spawner
from dariyoki.states.enums import States
from dariyoki.states.game_state import GameState
from dariyoki.ui.stats import Info, PlayerStatistics
from dariyoki.ui.widgets import FloatyText, LevelIcon
from dariyoki.utils import Time, resize
from dariyoki.weapons.shurikens import Shuriken
from dariyoki.world import World

logger = logging.getLogger()


class LevelSelector(GameState):
    def __init__(self, screen: pygame.Surface, assets: dict):
        super().__init__("level selector", screen)
        self.assets = assets
        self.mod_assets()
        self.next_state: Optional[States] = None
        self.current_territory = "Bee Territory"
        self.floaty_title_text = FloatyText(
            self.current_territory,
            screen.get_rect().midtop + Vec(0, 50),
            40,
            "yellow",
        )
        self.level_icon = pygame.Surface((85, 85))
        self.level_icon.fill("blue")
        self.level_icons = {
            "Bee Territory": tuple(
                (LevelIcon(n, self.assets["level_icon"]) for n in range(1, 6))
            ),
            "Electri City": tuple(
                (LevelIcon(n, self.assets["level_icon"]) for n in range(6, 11))
            ),
        }
        self.level_map_flare = LevelMapFlare()
        self.dt = 0

    def mod_assets(self):
        self.assets["bee_territory_level_map"] = pygame.transform.scale(
            self.assets["bee_territory_level_map"],
            (screen_width, screen_height),
        )

    def update(self, event_info: EventInfo):
        self.dt = event_info["dt"]
        self.floaty_title_text.update(event_info["dt"])
        for level_icon in self.level_icons[self.current_territory]:
            level_icon.update(event_info)
            if level_icon.is_clicked:
                self.next_state = States.LEVEL
                path = "assets/audio/"
                pygame.mixer.music.load(path + "two_worlds.mp3")
                pygame.mixer.music.play(-1, fade_ms=5000)

        self.level_map_flare.update()

    def draw(self):
        self.screen.blit(self.assets["bee_territory_level_map"], -camera)
        self.screen.blit(self.translucent_dark, (0, 0))
        self.floaty_title_text.draw(self.screen, camera)
        self.level_map_flare.draw(self.screen, self.dt)

        for level_icon in self.level_icons[self.current_territory]:
            level_icon.draw(self.screen, camera)

        self.screen.blit(self.assets["game_border"], (0, 0))


class EventStage(GameState):
    def __init__(self, screen: pygame.Surface, assets: Assets):
        super().__init__("level", screen)
        # Controls
        self.assets: Assets = assets
        with open("assets/data/controls.json") as f:
            self.controls = json.load(f)
        self.event_info = {}
        self.info = {}

    def update(self, event_info: EventInfo):
        self.event_info = event_info


class RenderBackgroundStage(EventStage):
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.assets["background"], (0, 0))


class MapInitStage(RenderBackgroundStage):
    TILE_SIZE = 32

    def __init__(self, n: int, screen: pygame.Surface, assets: Assets):
        super().__init__(screen, assets)
        self.tile_map = pytmx.TiledMap()
        self.load_level(n)
        try:
            self.items = [
                Item(
                    "jetpack", self.assets["jetpack"], Vec(obj.x, obj.y - 100)
                )
                for obj in self.tile_map.get_layer_by_name("items")
            ]
        except ValueError:
            self.items = []

        self.all_rects = {}
        item_size = (25, 25)
        self._items = {
            "health potion": pygame.transform.scale(
                self.assets["health_potion"], item_size
            ),
            "shield potion": pygame.transform.scale(
                self.assets["shield_potion"], item_size
            ),
            "shuriken": pygame.transform.scale(
                self.assets["shuriken"], item_size
            ),
            "smoke bomb": pygame.transform.scale(
                self.assets["smoke_bomb"], item_size
            ),
            "sword": pygame.transform.scale(self.assets["sword"], item_size),
            "scythe": pygame.transform.scale(self.assets["scythe"], item_size),
        }

    def load_level(self, n):
        # Level data
        self.tile_map = pytmx.load_pygame(
            f"assets/data/level_data/level_{n}_test.tmx"
        )
        tile_map = self.tile_map
        for index, layer in enumerate(tile_map):
            if layer.name == "tile layer 1":
                for x, y, _ in layer.tiles():
                    tile_properties = tile_map.get_tile_properties(x, y, index)
                    if tile_properties["type"] == "center":
                        continue

                    tile_pos = (
                        x * tile_map.tileheight,
                        y * tile_map.tilewidth,
                    )
                    self.all_rects[tile_pos] = (
                        tile_properties["type"],
                        pygame.Rect(
                            tile_pos, (self.TILE_SIZE, self.TILE_SIZE)
                        ),
                    )
                break


class EntityInitStage(MapInitStage):
    def __init__(self, screen: pygame.Surface, assets: Assets):
        super().__init__(0, screen, assets)
        self.shurikens = set()
        self.bees = set()

        self.player = Player(50, 50, camera, self.controls, self.screen, assets, self._items)


class SpawnerStage(EntityInitStage):
    def __init__(self, screen: pygame.Surface, assets: Assets) -> None:
        super().__init__(screen, assets)
        self.spawners = []
        # self.spawners = [
        #     Spawner(
        #         [obj.x, obj.y],
        #         (obj.width, obj.height),
        #         7,
        #         (1, 4),
        #         self.player.rect.size,
        #         100,
        #         border_image=self.assets["border"],
        #         spawn_images=(
        #             self.assets["spawner_shadow_ninja"],
        #             self.assets["spawning_shadow_ninja"],
        #         ),
        #         characters=self.assets["characters"],
        #         items=self._items,
        #         enemy_set=self.enemies,
        #     )
        #     for obj in self.tile_map.get_layer_by_name("spawners")
        # ]

    def update(self, event_info: EventInfo):
        super(SpawnerStage, self).update(event_info)
        # Handle spawners
        for spawner in self.spawners:
            if self.player.vec.distance_to(spawner.rect.center) > 1100:
                spawner.interactable = False
                continue
            else:
                spawner.interactable = True

            spawner.update(event_info, self.shurikens, self.spawners)

    def draw(self, screen: pygame.Surface) -> None:
        super(SpawnerStage, self).draw(screen)
        for spawner in self.spawners:
            if spawner.interactable:
                spawner.draw(screen, camera)


class TransitionStage(EntityInitStage):
    FADE_SPEED = 5.3

    def __init__(self, screen: pygame.Surface, assets: Assets):
        super().__init__(screen, assets)
        self.transition = FadeTransition(True, self.FADE_SPEED)
        self.next_state: Optional[States] = None

    def update(self, event_info: EventInfo):
        super().update(event_info)
        self.transition.update(event_info["dt"])
        if not self.player.alive:
            self.transition.fade_in = False
            if self.transition.event:
                self.next_state = States.MAIN_MENU

    def draw(self, screen: pygame.Surface) -> None:
        self.transition.draw(screen)


class Level(GameState):
    TILE_SIZE = 32

    def __init__(self, n: int, screen: pygame.Surface, assets: dict):
        super().__init__("level", screen)

        # Entities
        self.enemies: set[Ninja] = set()
        self.shurikens: set[Shuriken] = set()
        self.bees: set[Bee] = set()
        self.explosions: list[Explosion] = []

        # Controls
        with open("assets/data/controls.json") as f:
            self.controls = json.load(f)

        self.next_state: Optional[States] = None
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
            "shuriken": pygame.transform.scale(
                self.assets["shuriken"], item_size
            ),
            "smoke bomb": pygame.transform.scale(
                self.assets["smoke_bomb"], item_size
            ),
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
        # Levels
        self.item_info = Info(
            screen, eval("pygame." + self.controls["controls"]["info toggle"])
        )

        try:
            self.items = [
                Item(
                    "jetpack", self.assets["jetpack"], Vec(obj.x, obj.y - 100)
                )
                for obj in self.tile_map.get_layer_by_name("items")
            ]
        except ValueError:
            self.items = []
        self.opened_chests = []
        self.chests = [
            Chest(
                obj.x,
                obj.y - 40,
                pygame.K_f,
                7,
                border_image=self.assets["border"],
                chests=self.assets["chest"],
                items=self._items,
            )
            for obj in self.tile_map.get_layer_by_name("chests")
        ]

        self.spawners = []
        self.bee_spawners = set()
        for obj in self.tile_map.get_layer_by_name("spawners"):
            if obj.name == "bee spawner":
                self.bee_spawners.add(
                    BeeSpawner(
                        Vec(obj.x, obj.y),
                        self.assets["stone_bush_hive"][8],
                        self.assets["bee"],
                        self.assets["border"],
                        self.player,
                    )
                )

        # self.spawners = [
        #     Spawner(
        #         [obj.x, obj.y],
        #         (obj.width, obj.height),
        #         7,
        #         (1, 4),
        #         self.player.rect.size,
        #         100,
        #         border_image=self.assets["border"],
        #         spawn_images=(
        #             self.assets["spawner_shadow_ninja"],
        #             self.assets["spawning_shadow_ninja"],
        #         ),
        #         characters=self.assets["characters"],
        #         items=self._items,
        #         enemy_set=self.enemies,
        #     )
        #     for obj in self.tile_map.get_layer_by_name("spawners")
        # ]

        # Inventory
        self.statistics = PlayerStatistics(screen, self.player, self.assets)

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
            init_radius=5,
            max_radius=40,
            increment=3,
            colour=(255, 0, 0),
            width=10,
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
                random.randint(0, self.screen_shake_val * 2)
                - self.screen_shake_val
            )
            render_offset[1] = (
                random.randint(0, self.screen_shake_val * 2)
                - self.screen_shake_val
            )

        camera[0] += render_offset[0]
        camera[1] += render_offset[1]

    def load_level(self, n):
        # Level data
        self.tile_map = pytmx.load_pygame(
            f"assets/data/level_data/level_{n}_test.tmx"
        )
        tile_map = self.tile_map
        for index, layer in enumerate(tile_map):
            if layer.name == "tile layer 1":
                for x, y, _ in layer.tiles():
                    tile_properties = tile_map.get_tile_properties(x, y, index)
                    if tile_properties["type"] == "center":
                        continue

                    tile_pos = (
                        x * tile_map.tileheight,
                        y * tile_map.tilewidth,
                    )
                    self.all_rects[tile_pos] = (
                        tile_properties["type"],
                        pygame.Rect(
                            tile_pos, (self.TILE_SIZE, self.TILE_SIZE)
                        ),
                    )
                break

    def handle_wind_slash(self):
        for slash in set(self.player.sword.projectiles):
            for enemy in self.enemies:
                if slash.rect.colliderect(enemy.rect):
                    enemy.hp -= self.player.sword.damage
                    try:
                        self.player.sword.projectiles.remove(slash)
                    except KeyError:
                        pass
                    self.explosions.append(
                        Explosion(
                            500,
                            (12, 25),
                            list(slash.rect.center),
                            (5, 12),
                            "white",
                        )
                    )
                    self.expanding_circles.circles.append(
                        ExpandingCircle(
                            slash.rect.center,
                            self.expanding_circles.init_radius,
                            self.expanding_circles.max_radius,
                            self.expanding_circles.increment,
                            (255, 255, 255),
                            width=self.expanding_circles.width,
                        )
                    )
                    self.screen_shake = 20
                    self.screen_shake_val = 2

    def handle_shurikens(self, dt):
        # self.shurikens
        for shuriken in set(self.shurikens):
            shuriken.move(dt)
            if shuriken.launcher == self.player:
                shuriken.draw(self.screen, [0, 0], dt)
            else:
                shuriken.draw(self.screen, camera, dt)

            broken = False
            if not isinstance(shuriken.launcher, Ninja):
                for enemy in functools.reduce(
                    operator.or_, [self.enemies, self.bees]
                ):
                    if shuriken.collides(enemy.rect, camera):
                        enemy.hp -= shuriken.damage
                        self.shurikens.alive = False
                        self.explosions.append(
                            Explosion(
                                500,
                                (12, 25),
                                list(shuriken.rect.center),
                                (5, 12),
                                "white",
                            )
                        )
                        self.expanding_circles.add(shuriken.rect.center, "white")
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
                    (
                        self.screen_shake,
                        self.screen_shake_val,
                    ) = self.player.take_damage(
                        damage=shuriken.damage, shield=True
                    )
                else:
                    (
                        self.screen_shake,
                        self.screen_shake_val,
                    ) = self.player.take_damage(damage=shuriken.damage)

                self.shurikens.remove(shuriken)
                continue

            # Remove shuriken if it goes outside of boundary
            if shuriken.distance > 800:
                self.shurikens.remove(shuriken)

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
        for spawner in self.spawners:
            if self.player.vec.distance_to(spawner.rect.center) > 1100:
                continue

            spawner.update(event_info, self.shurikens, self.spawners)
            spawner.draw(self.screen, camera)

        self.world.draw_parallax(self.screen, camera)
        self.world.draw(self.screen, camera)
        self.world.draw_grass(self.screen, camera)

        # Opened chest becomes part of the background
        for opened_chest in self.opened_chests:
            opened_chest.draw(self.screen, camera)

        # Line of lighting
        self.screen.blit(self.translucent_dark, (0, 0))

        # Decorations
        self.world.draw_dec(self.screen, camera)

        # Chests
        for chest in self.chests:
            chest.draw(self.screen, camera)

            # Removing chest
            if chest.loading_bar.loaded:
                self.items += chest.items
                self.chests.remove(chest)
                self.opened_chests.append(chest)

        # Player and enemies
        self.player.update(info, event_info, self.shurikens, self.explosions)
        self.player.draw(self.screen)

        for spawner in self.spawners:
            spawner.draw_spawn(self.screen, camera)

        for enemy in set(self.enemies):
            if self.player.vec.distance_to(enemy.vec) > 1200:
                continue
            enemy.update(
                player_pos=self.player.rect.center,
                info=info,
                event_info=event_info,
                shurikens=self.shurikens,
            )
            enemy.draw(self.screen, camera)
            if enemy.hp <= 0 or enemy.y > self.TILE_SIZE * 100:
                self.enemies.remove(enemy)

        # Bee spawner
        for spawner in set(self.bee_spawners):
            if (
                self.player.vec.distance_squared_to(spawner.rect.topleft)
                > 1100**2
            ):
                continue

            spawner.update(
                shurikens=self.shurikens,
                sword_slashes=self.player.sword.projectiles,
                bees=self.bees,
            )
            spawner.draw(self.screen, camera)

            if not spawner.is_alive:
                self.bee_spawners.remove(spawner)
                logger.critical(len(self.bee_spawners))

        for bee in set(self.bees):
            bee.update(event_info["dt"])
            bee.draw(self.screen, camera)

            if bee.rect.colliderect(self.player.rect):
                bee.hp = 0
                (
                    self.screen_shake,
                    self.screen_shake_val,
                ) = self.player.take_damage(bee.damage, shield=True)

            if bee.hp <= 0:
                self.explosions.append(
                    Explosion(
                        n_particles=350,
                        n_size=(7, 19),
                        pos=list(bee.rect.center - camera),
                        speed=(3, 14),
                        color="yellow",
                        size_reduction=1.5,
                        # glow=False
                    )
                )
                self.bees.remove(bee)

        # Items
        for item in self.items:
            item.update(dt)
            item.draw(self.screen, camera)

        # Projectiles
        self.handle_shurikens(dt)
        if self.player.equipped == "sword":
            self.player.sword.update(
                event_info, (self.player.x, self.player.y), camera
            )

        for wind_slash in set(self.player.sword.projectiles):
            wind_slash.update(event_info["dt"])
            wind_slash.draw(self.screen, camera)
            for bee in set(self.bees):
                if wind_slash.rect.colliderect(bee.rect):
                    bee.hp -= self.player.sword.damage
                    self.player.sword.projectiles.remove(wind_slash)
                    break

            if wind_slash.distance > self.player.sword.wind_distance:
                self.player.sword.projectiles.remove(wind_slash)

        self.handle_wind_slash()
        # Handle screen shake
        self.handle_screen_shake(dt)

        # Explosions
        for explosion in self.explosions:
            explosion.draw(self.screen, dt)

            if len(explosion.particles) == 0:
                self.explosions.remove(explosion)

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
