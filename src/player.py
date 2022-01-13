import pygame
import json
import math
import random
from src.utils import circle_surf, rotate
from src.sprites import characters, sword_attack, lsword_attack
from src.animation import Animation


class Player:
    JUMP_HEIGHT = 200
    DASH_LENGTH = 150

    def __init__(self, x, y, camera, controls):
        # Constructor objects
        self.x, self.y = x, y
        self.right_img = characters[0]
        self.left_img = pygame.transform.flip(self.right_img, True, False)
        self.image = self.right_img
        self.rect = self.image.get_rect()

        # Controls
        self.controls = controls

        self.right_control = eval("pygame." + controls["right"])
        self.left_control = eval("pygame." + controls["left"])
        self.jump_control = eval("pygame." + controls["jump"])
        self.attack_control = eval("pygame." + controls["attack"])
        self.dash_control = eval("pygame." + controls["dash"])

        # Inventory
        self.inventory = {
            "weapons": {
                "shuriken": 0,
                "sword": 0
            },
            "items": {
                "health potion": 0,
                "shield potion": 0,
                "smoke bomb": 0
            },
            "soul boosted": {
                "soul shuriken": 0,
                "soul bomb": 0,
                "soul sword": 0,
            }
        }

        # Animations
        self.sword_attack_animation = Animation(sword_attack, speed=0.4)
        self.lsword_attack_animation = Animation(lsword_attack, speed=0.4)

        # Flags
        self.jumping = False
        self.touched_ground = False
        self.attacking = False
        self.dashing = False
        self.standing_near_chest = False
        self.colliding_item = None
        self.once = True

        # Casket
        self.last_direction = "right"
        self.dash_images = []
        self.rs = []
        self.chest_index = -1
        self.info = {}

        # Statistics
        self.hp = 100
        self.last_hp = self.hp
        self.sheild = 0 
        self.soul_energy = 100
        self.current_damage = 0

        # Movement vars
        self.angle = 0
        self.camera = camera

        # Movement speeds
        self.speed = 5
        self.velocity = 3
        self.acceleration = 2
        self.dash_mult = 15

        # Stacking values
        self.jump_stack = 0
        self.dash_stack = 0

        # dt
        self.dt = 0
        self.dx, self.dy = 0, 0

    def update(self, info, events, keys, dt):
        self.dt = dt
        self.info = info
        self.last_hp = self.hp

        # Default iteration values
        dx, dy = 0, 0

        if keys[self.right_control]:
            dx += self.speed * dt
            self.last_direction = "right"

            self.image = self.right_img
        if keys[self.left_control]:
            dx -= self.speed * dt
            self.last_direction = "left"

            self.image = self.left_img

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.jump_control and self.touched_ground:
                    self.jumping = True
                    self.jump_stack = 0

                if event.key == self.attack_control:
                    r_angle = random.randrange(-50, 20)
                    if self.last_direction == "right":
                        self.sword_attack_animation.frames = rotate(sword_attack, r_angle)
                    elif self.last_direction == "left":
                        self.lsword_attack_animation.frames = rotate(lsword_attack, r_angle)
                    self.attacking = True

                if event.key == self.dash_control:
                    self.dashing = True
                    self.dash_stack = 0

                if event.key == pygame.K_e:
                    self.hp -= 5
                    info["stats"].hp_bar.value = self.hp

        # Check collisions
        for pos in info["tiles"]:
            stub = pygame.Rect(pos, (32, 32))

            # Check for floor collision
            if "up" in info["tiles"][pos]:
                if stub.collidepoint(self.rect.midbottom) and self.rect.y < pos[1]:
                    self.image = self.right_img if self.last_direction == "right" else self.left_img
                    self.touched_ground = True
                    self.angle = 0
                    dy = stub.top - self.rect.bottom
                    # self.velocity = 5
                    break

            # Check for right collision
            if "right" in info["tiles"][pos]:
                if stub.collidepoint(self.rect.midright) and dx > 0:
                    dx = 0

            # Check for left collision
            if "left" in info["tiles"][pos]:
                if stub.collidepoint(self.rect.midleft) and dx < 0:
                    dx = 0

            # Check for roof collsion
            if "down" in info["tiles"][pos]:
                if dy != 0 and stub.collidepoint(self.rect.midtop):
                    # dy = 0
                    self.jumping = False
        else:
            if not self.jumping:
                self.velocity += self.acceleration * dt
                dy += self.velocity * dt

        # Gravity control
        if self.jumping:
            self.angle += 200 * dt

            self.image = pygame.transform.rotozoom(self.right_img, int(self.angle), 1)
            self.velocity -= self.acceleration * dt
            dy -= self.velocity * dt
            self.jump_stack += abs(dy)

            if dy == abs(dy):
                dy = -dy

            if self.jump_stack > self.JUMP_HEIGHT:
                self.jumping = False
                self.jump_stack = 0
                self.velocity = 5

            self.touched_ground = False

        # Dashing
        if self.dashing:
            dx *= self.dash_mult * dt
            dy *= self.dash_mult * dt

            self.dash_stack += math.sqrt(dx**2 + dy**2)

            if self.dash_stack >= self.DASH_LENGTH:
                self.dashing = False
                self.dash_stack = 0

            d_img = self.image.copy()
            d_img.set_alpha(150)
            self.dash_images.append([d_img, (self.x, self.y), 150])

        # Handle chests
        if self.once:
            self.rs = [r.rect for r in info["chests"]]
            self.once = False
        if (index := self.rect.collidelist(self.rs)) != -1:
            self.chest_index = index
            self.standing_near_chest = True
        else:
            if len(info["chests"]) != 0:
                info["chests"][self.chest_index].loading_bar.value = 0
                self.standing_near_chest = False

        # Update loading bar
        if self.standing_near_chest and len(info["chests"]) != 0:
            info["chests"][self.chest_index].update(keys, dt)

        # Handle items
        for item in info["items"]:
            if self.rect.colliderect(item.rect):
                self.colliding_item = item
                if not info["item info"].o_lock:
                    info["item info"].opening = True

        # Update player coord
        self.x += dx
        self.y += dy

        # Update Camera coord
        self.dx, self.dy = dx, dy
        # self.camera[0] += dx
        # self.camera[1] += dy
        # self.camera[0] = (self.x - self.camera[0]) * 0.6
        # self.camera[1] = (self.y - self.camera[1]) * 0.6

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))

    def draw(self, screen: pygame.Surface):
        # Draw dash shadows
        for dasher in self.dash_images:
            dasher[2] -= 2 * self.dt
            if dasher[2] <= 0:
                self.dash_images.remove(dasher)
            dasher[0].set_alpha(int(dasher[2]))
            screen.blit(dasher[0], (dasher[1][0] - self.camera[0], dasher[1][1] - self.camera[1]))

        # Draw player
        screen.blit(self.image, (self.x - self.camera[0], self.y - self.camera[1]))
        # Draw glowing effect
        screen.blit(circle_surf(radius=self.right_img.get_height(), color=(20, 20, 20)),
                    (self.x - self.right_img.get_width() - 5 - self.camera[0],
                     self.y - (self.right_img.get_height() // 2) - self.camera[1]),
                    special_flags=pygame.BLEND_RGB_ADD)
        if self.attacking:
            if self.last_direction == "right":
                self.sword_attack_animation.play(screen,
                                                 (self.x + 10 - self.camera[0], self.y - self.camera[1]), self.dt)
                if self.sword_attack_animation.index == 0:
                    self.attacking = False
            elif self.last_direction == "left":
                self.lsword_attack_animation.play(screen, (self.x - 10 - self.image.get_width() - self.camera[0],
                                                           self.y - self.camera[1]), self.dt)
                if self.lsword_attack_animation.index == 0:
                    self.attacking = False

        # Draw loading bar
        if self.standing_near_chest and len(self.info["chests"]) != 0:
            self.info["chests"][self.chest_index].loading_bar.draw(screen, self.camera)

        self.current_damage = self.last_hp - self.hp

        # Update camera pos
        self.camera[0] += (self.x - self.camera[0] - (screen.get_width() // 2)) * 0.2
        self.camera[1] += (self.y - self.camera[1] - (screen.get_height() // 2)) * 0.2
