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

    def __init__(self, x, y, camera):
        # Constructor objects
        self.x, self.y = x, y
        self.right_img = characters[0]
        self.left_img = pygame.transform.flip(self.right_img, True, False)
        self.image = characters[0]
        self.rect = self.image.get_rect()

        # Controls
        with open("data/controls.json") as f:
            self.controls = json.load(f)

        (
            self.right_control,
            self.left_control,
            self.jump_control,
            self.attack_control,
            self.dash_control
        ) = [eval("pygame." + control) for control in self.controls["controls"].values()]

        # Inventory
        self.inventory = {
            "weapons": {
                "shuriken": 0,
                "sword": 0
            },
            "items": {
                "health potion": 0,
                "shield potion": 0,

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

        # Casket
        self.last_direction = "right"
        self.dash_images = []

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

    def update(self, tiles: list[pygame.Rect], events, dt):
        self.dt = dt

        # Default iteration values
        dx, dy = 0, 0

        keys = pygame.key.get_pressed()
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

        # Check side collisions
        for tile in tiles:
            if tile.collidepoint(self.rect.midright) and dx > 0:
                dx = 0

            if tile.collidepoint(self.rect.midleft) and dx < 0:
                dx = 0

        # Gravity control
        for tile in tiles:
            if tile.collidepoint(self.rect.midbottom) and self.rect.y < tile.y:
                self.image = self.right_img if self.last_direction == "right" else self.left_img
                self.touched_ground = True
                self.angle = 0
                dy = tile.top - self.rect.bottom
                # self.velocity = 5
                break
        else:
            if not self.jumping:
                self.velocity += self.acceleration * dt
                dy += self.velocity * dt

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

        # Update player coord
        self.x += dx
        self.y += dy

        # Update Camera coord
        self.camera[0] += dx
        self.camera[1] += dy

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))

    def draw(self, screen: pygame.Surface):
        # Draw dash shadows
        for dasher in self.dash_images:
            dasher[2] -= 1 * self.dt
            if dasher[2] <= 0:
                self.dash_images = []
                break
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


