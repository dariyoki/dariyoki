import math
from typing import Optional

import pygame

from src._globals import general_info, shurikens
from src._types import Vec
from src.animation import Animation
from src.audio import dash_sfx, pickup_item_sfx
from src.consumables import HealthPotion, ShieldPotion
from src.effects.particle_effects import PlayerAura
from src.entities.traits import collide, jump
from src.ui.game_events import GeneralInfo
from src.utils import camerify as c
from src.utils import circle_surf, turn_left
from src.weapons.shurikens import Shuriken


class Player:
    JUMP_HEIGHT = 210
    DASH_LENGTH = 150
    INVENTORY_SLOTS = 8

    def __init__(
        self, x, y, camera, controls, screen: pygame.Surface, assets: dict, items: dict
    ):
        # Constructor objects
        self.x, self.y = x, y
        self.vec = Vec(self.x, self.y)
        self.right_img = assets["dari"][0]
        self.left_img = pygame.transform.flip(self.right_img, True, False)
        self.image = self.right_img
        self.rect = self.image.get_rect()
        self.screen = screen

        # Controls
        self.controls = controls
        self.right_control = getattr(pygame, controls["right"])
        self.left_control = getattr(pygame, controls["left"])
        self.jump_control = [getattr(pygame, control) for control in controls["jump"]]
        self.dash_control = getattr(pygame, controls["dash"])
        self.pickup_control = getattr(pygame, controls["pickup item"])

        # Inventory
        self.item_count = {
            "health potion": 0,
            "shield potion": 0,
            "smoke bomb": 0,
            "shuriken": 0,
            "sword": 0,
            "scythe": 0,
            "soul shuriken": 0,
            "soul bomb": 0,
            "soul sword": 0,
        }
        self.inventory: list[Optional[str]] = [
            None for _ in range(self.INVENTORY_SLOTS)
        ]
        self.item_pickup_circle_radius = self.rect.height
        self.item_pickup_circle_width = 5
        self.item_pickup_start = False

        # Animations
        sword_attack = assets["sword attack"]
        lsword_attack = turn_left(sword_attack)
        self.sword_attack_animation = Animation(sword_attack, speed=0.4)
        self.lsword_attack_animation = Animation(lsword_attack, speed=0.4)
        self.shield_breaking_animation = Animation(assets["shield_bubble"], speed=0.2)
        self.aura = PlayerAura((0, 0, 0), 2)

        # Flags
        self.jumping = False
        self.touched_ground = False
        self.attacking = False
        self.dashing = False
        self.standing_near_chest = False
        self.colliding_item = None
        self.once = True
        self.shield_break = False
        self.dash_once = True

        # Surfs
        self.glow_surf = circle_surf(40, (20, 20, 40))
        self.glow_surf_alpha = 255

        # Casket
        self.last_direction = "right"
        self.dash_images = []
        self.rs = []
        self.chest_index = -1
        self.info = {}
        self.items = items
        self.equip_items = items.copy()
        self.equip_items["sword"] = pygame.transform.rotate(
            pygame.transform.scale2x(self.equip_items["sword"]), -45
        )
        self.equip_items["scythe"] = pygame.transform.rotate(
            pygame.transform.scale2x(self.equip_items["scythe"]), -45
        )
        self.player_shield_img = assets["shield_bubble"][0]

        # Consumables
        self.health_potion = HealthPotion(self, assets["border"])
        self.shield_potion = ShieldPotion(self, assets["border"])

        # Statistics
        self.max_hp, self.max_soul_energy, self.max_shield = 100, 100, 100
        self.hp = 100
        self.last_hp = self.hp
        self.shield = 0
        self.soul_energy = 100
        self.current_damage = 0
        self.equipped = None
        self.costs = {
            "dash": 15,
        }

        # Weapon data
        self.cooldowns = {"shuriken": 0.3, "glock": 0.6}
        self.attack_cd = 0

        # Movement vars
        self.angle = 0
        self.camera = camera

        # Movement speeds
        self.speed = 5
        self.velocity = 2
        self.acceleration = 1.3
        self.dash_mult = 15

        # Stacking values
        self.jump_stack = 0
        self.dash_stack = 0
        self.item_collide_stack = 0

        # dt
        self.dt = 0
        self.dx, self.dy = 0, 0

    def handle_shurikens(self, target):
        shurikens.append(
            Shuriken(
                start=(
                    self.rect.center[0] - self.camera[0],
                    self.rect.center[1] - self.camera[1],
                ),
                target=target,
                speed=12,
                launcher=self,
                items=self.items,
            )
        )
        if self.item_count["shuriken"] > 0:
            self.item_count["shuriken"] -= 1
        else:
            self.equipped = None

    def handle_health_potion(self):
        self.health_potion.loading_bar.rect = pygame.Rect(
            pygame.Rect(self.rect.midtop[0], self.rect.midtop[1] - 10, 50, 12)
        )
        self.health_potion.loading_bar.value += 0.9 * self.dt
        self.health_potion.draw(self.screen, self.camera)
        if self.health_potion.loading_bar.loaded:
            if self.item_count["health potion"] > 0:
                self.item_count["health potion"] -= 1
                self.health_potion = HealthPotion(self)
            else:
                self.equipped = None

    def handle_shield_potion(self):
        self.shield_potion.loading_bar.rect = pygame.Rect(
            pygame.Rect(self.rect.midtop[0], self.rect.midtop[1] - 10, 50, 12)
        )
        self.shield_potion.loading_bar.value += 0.5 * self.dt
        self.shield_potion.draw(self.screen, self.camera)
        if self.shield_potion.loading_bar.loaded:
            self.glow_surf_alpha = 255
            if self.item_count["shield potion"] > 0:
                self.item_count["shield potion"] -= 1
                self.shield_potion = ShieldPotion(self)
            else:
                self.equipped = None

    def handle_item_pickup(self, info, raw_dt):
        # Handle items
        stub_rx = [item.rect for item in info["items"]]
        if (index := self.rect.collidelist(stub_rx)) != -1:
            self.item_collide_stack += raw_dt
            self.colliding_item = info["items"][index]
            if not info["item info"].o_lock and self.item_collide_stack > 1.5:
                info["item info"].opening = True
        else:
            self.item_collide_stack = 0
            self.colliding_item = None
            if not info["item info"].o_lock:
                info["item info"].opening = False

        # Drawing item pickup circle
        if self.item_pickup_start:
            pygame.draw.circle(
                self.screen,
                "white",
                (
                    self.rect.center[0] - self.camera[0],
                    self.rect.center[1] - self.camera[1],
                ),
                radius=self.item_pickup_circle_radius,
                width=int(self.item_pickup_circle_width),
            )
            self.item_pickup_circle_radius -= 3 * self.dt
            self.item_pickup_circle_width -= 0.3 * self.dt
            if self.item_pickup_circle_radius < 1:
                self.item_pickup_start = False
                self.item_pickup_circle_radius = self.rect.height
                self.item_pickup_circle_width = 5

        # Update `item_count` and `inventory` sync
        for item, quantity in self.item_count.items():
            if quantity == 0 and item in self.inventory:
                self.inventory[self.inventory.index(item)] = None

    def update(self, info: dict, event_info: dict) -> None:
        dt = event_info["dt"]
        self.dt = event_info["dt"]
        self.info = info
        self.last_hp = self.hp
        info["stats"].hp_bar.value = self.hp * 1.7
        info["stats"].shield_bar.value = self.shield * 1.7
        info["stats"].se_bar.value = self.soul_energy * 1.7

        # Default iteration values
        dx, dy = 0, 0

        if event_info["keys"][self.right_control]:
            dx += self.speed * dt
            self.last_direction = "right"

            self.image = self.right_img
        if event_info["keys"][self.left_control]:
            dx -= self.speed * dt
            self.last_direction = "left"

            self.image = self.left_img

        if (
            event_info["mouse press"][0]
            and self.equipped is not None
            and event_info["mouse pos"][1] > 130
        ):
            self.attack_cd += event_info["raw dt"]
            if self.equipped in self.cooldowns:
                if self.attack_cd >= self.cooldowns[self.equipped]:
                    if self.equipped == "shuriken":
                        self.handle_shurikens(event_info["mouse pos"])
                        self.attack_cd = 0

            if self.equipped == "health potion":
                self.handle_health_potion()

            if self.equipped == "shield potion":
                self.handle_shield_potion()

        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key in self.jump_control and self.touched_ground:
                    self.jumping = True
                    self.jump_stack = 0

                if event.key == self.dash_control:
                    if self.soul_energy > self.costs["dash"]:
                        self.dashing = True
                        self.dash_stack = 0
                        self.soul_energy -= self.costs["dash"]
                    else:
                        general_info[0] = GeneralInfo("Not enough soul energy!", "red")

                if event.key == self.pickup_control:
                    if self.colliding_item is not None:
                        name = self.colliding_item.name
                        match name:
                            case "shuriken":
                                quantity = 10
                            case _:
                                quantity = 1

                        if self.inventory.count(None) < 1:
                            general_info[0] = GeneralInfo(
                                f"Out of inventory slots! (MAX:8)", "red"
                            )
                        else:
                            info["items"].remove(self.colliding_item)
                            self.item_count[name] += quantity
                            general_info[0] = GeneralInfo(
                                f"+{quantity} {name} picked up!", "white"
                            )
                            pickup_item_sfx.play()
                            if name not in self.inventory:
                                for index, item in enumerate(self.inventory):
                                    if item is None:
                                        self.inventory[index] = name
                                        self.item_pickup_start = True
                                        break

        # Dashing
        if not self.dashing:
            self.dash_once = True

        if self.dashing:
            if self.dash_once:
                dash_sfx.play()
                self.dash_once = False
            dx *= self.dash_mult * dt
            dy *= self.dash_mult * dt

            self.dash_stack += math.sqrt(dx**2 + dy**2)

            if self.dash_stack >= self.DASH_LENGTH:
                self.dashing = False
                self.dash_stack = 0

            d_img = self.image.copy()
            d_img.set_alpha(150)
            self.dash_images.append([d_img, (self.x, self.y), 150])

        dx, dy = collide(self, info, event_info, dx, dy)
        dy = jump(self, dt, dy)

        # Handle chests
        self.rs = [r.rect for r in info["chests"]]
        if (index := self.rect.collidelist(self.rs)) != -1:
            self.chest_index = index
            self.standing_near_chest = True
        else:
            self.chest_index = -1
            if len(info["chests"]) != 0:
                info["chests"][self.chest_index].loading_bar.value = 0
                self.standing_near_chest = False

        # Handle item pickup
        self.handle_item_pickup(info, event_info["raw dt"])

        # Update loading bar
        if self.standing_near_chest and len(info["chests"]) != 0:
            info["chests"][self.chest_index].update(event_info["keys"], dt)

        # Update player coord
        self.x += dx
        self.y += dy
        self.vec += (dx, dy)

        # Update Camera coord
        self.dx, self.dy = dx, dy

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))

    def draw(self, screen: pygame.Surface):
        # pygame.draw.rect(screen, "red", (
        #     self.rect.x - self.camera[0],
        #     self.rect.y - self.camera[1],
        #     *self.rect.size
        # ), width=3)
        # Draw dash shadows
        for dasher in self.dash_images:
            dasher[2] -= 2 * self.dt
            if dasher[2] <= 0:
                self.dash_images.remove(dasher)
            dasher[0].set_alpha(int(dasher[2]))
            screen.blit(dasher[0], c(dasher[1], self.camera))

        # Draw player aura
        player_shield_rect = self.player_shield_img.get_rect(center=self.rect.center)
        shield_pos = c(player_shield_rect.topleft, self.camera)
        if self.shield < 1 or self.glow_surf_alpha <= 0:
            self.aura.update(
                self.rect.center[0] - self.camera[0],
                self.rect.center[1] - self.camera[1],
                screen,
                self.dt,
            )

        # Draw player
        screen.blit(self.image, self.vec - self.camera)

        # Draw player weapon
        if self.equipped is not None:
            stub = self.equip_items[self.equipped].get_rect(center=self.rect.center)
            if self.last_direction == "right":
                screen.blit(
                    self.equip_items[self.equipped],
                    (stub.x + 20 - self.camera[0], stub.y - self.camera[1]),
                )
            elif self.last_direction == "left":
                img = pygame.transform.flip(
                    self.equip_items[self.equipped], True, False
                )
                screen.blit(
                    img, (stub.x - 20 - self.camera[0], stub.y - self.camera[1])
                )

        # Draw loading bar
        if self.standing_near_chest and len(self.info["chests"]) != 0:
            self.info["chests"][self.chest_index].loading_bar.draw(screen, self.camera)

        self.current_damage = self.last_hp - self.hp

        # Draw shield
        if self.shield > 1:
            self.shield_break = True

            if self.glow_surf_alpha > 0:
                self.glow_surf_alpha -= 2.3 * self.dt
                self.player_shield_img.set_alpha(self.glow_surf_alpha)
                self.glow_surf.set_alpha(self.glow_surf_alpha)
                screen.blit(self.player_shield_img, shield_pos)
                screen.blit(
                    self.glow_surf, shield_pos, special_flags=pygame.BLEND_RGB_ADD
                )
        elif self.shield_break:
            if (
                self.shield_breaking_animation.index
                > self.shield_breaking_animation.f_len - 1
            ):
                self.shield_break = False
                self.info["expanding circles"].add(
                    pos=c(player_shield_rect.center, self.camera), color=(0, 20, 200)
                )
            else:
                self.shield_breaking_animation.play(screen, shield_pos, self.dt)

        # Update camera pos
        self.camera[0] += (self.x - self.camera[0] - (screen.get_width() // 2)) * 0.03
        self.camera[1] += (self.y - self.camera[1] - (screen.get_height() // 2)) * 0.03