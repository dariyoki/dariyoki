import math
import random
import uuid

import pygame

from src._globals import enemy_ids, shurikens
from src.sprites import characters, bee_img
from src.traits import collide, jump
from src.weapons.shurikens import Shuriken
from src.widgets import LoadingBar
from src._types import Vec


class Ninja:
    JUMP_HEIGHT = 200
    PLAYER_CHASE_RANGE = 400

    def __init__(self, x, y, weapon, clan: str, speed):
        self.x, self.y = x, y
        self.PLAYER_DIST = random.randrange(100, 200)
        self.weapon = weapon
        self.id = uuid.uuid1()
        enemy_ids.append(self.id)
        self.denotion_font = pygame.font.SysFont("arialrounded", 24)
        self.question_mark = self.denotion_font.render("?", True, "red")
        self.exclamation_mark = self.denotion_font.render("!", True, "red")

        match clan:
            case "shadow":
                self.right_img = characters[8]

        self.left_img = pygame.transform.flip(self.right_img, True, False)
        self.image = self.right_img
        self.rect = self.image.get_rect()

        # Flags
        self.jumping = False
        self.touched_ground = False
        self.once = True
        self.chasing = False

        # Casket
        self.last_direction = "right"
        self.idle_movement_direction = "right"
        self.shuriken_cd = 1

        # Movement vars
        self.angle = 0
        self.idle_distance = 0

        # Statistics
        self.hp = 100
        self.max_hp = 100

        # Movement speeds
        self.speed = speed
        self.velocity = 5
        self.acceleration = 2

        # Stacking values
        self.jump_stack = 0
        self.shuriken_stack = 0

        # HP bar
        self.hp_bar_size = (60, 10)
        self.hp_bar = LoadingBar(
            value=self.hp,
            fg_color=(179, 2, 43),
            bg_color="black",
            rect=pygame.Rect((0, 0), self.hp_bar_size),
        )
        self.camera = [0, 0]

    def handle_shurikens(self, target):
        shurikens.append(
            Shuriken(start=self.rect.center, target=target, speed=6, launcher=self)
        )

        # # Clean up
        # for shuriken in self.shurikens:
        #     if shuriken not in shuriken_ids:
        #         self.shurikens.remove(shuriken)

    def update(self, player_pos, info, event_info):
        dt = event_info["dt"]
        direction = ""
        dist = abs(self.x - player_pos[0])
        self.chasing = self.PLAYER_CHASE_RANGE > dist
        if self.chasing and dist > self.PLAYER_DIST:
            self.chasing = True
            if player_pos[0] < self.x:
                direction = "left"
            else:
                direction = "right"

        if self.chasing:
            self.shuriken_stack += event_info["raw dt"]
            if self.shuriken_stack > self.shuriken_cd:
                self.handle_shurikens(player_pos)
                self.shuriken_stack = 0
        else:
            direction = self.idle_movement_direction
            if direction == "jump" and self.touched_ground:
                self.jumping = True

        # Default iteration values
        dx, dy = 0, 0

        if direction == "right":
            dx += self.speed * dt
            self.last_direction = "right"

            self.image = self.right_img
        if direction == "left":
            dx -= self.speed * dt
            self.last_direction = "left"

            self.image = self.left_img

        dx, dy = collide(self, info, event_info, dx, dy)

        dy = jump(self, dt, dy)

        self.x += dx
        self.y += dy

        # Handle idle distance
        if not self.chasing:
            self.idle_distance += abs(math.sqrt(dx**2 + dy**2))
            if self.idle_distance > 40:
                self.idle_movement_direction = random.choice(
                    ("right", "left", "right", "left", "jump")
                )
                self.idle_distance = 0

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))
        self.hp_bar.value = self.hp * (self.hp_bar_size[0] / self.max_hp)
        self.hp_bar.rect.center = (self.rect.midtop[0], self.rect.midtop[1] - 10)

    def draw(self, screen: pygame.Surface, camera):
        self.camera = camera
        screen.blit(self.image, (self.x - camera[0], self.y - camera[1]))
        self.hp_bar.draw(screen, camera, moving=True)
        denotion_pos = (
            self.hp_bar.rect.midtop[0] - camera[0],
            self.hp_bar.rect.y - camera[1] - self.hp_bar.rect.height * 2,
        )
        if self.chasing:
            screen.blit(self.exclamation_mark, denotion_pos)
        else:
            screen.blit(self.question_mark, denotion_pos)

        # pygame.draw.rect(screen, "red", (
        #     self.rect.x - camera[0],
        #     self.rect.y - camera[1],
        #     *self.rect.size
        # ), width=3)


class Bee:
    SPEED = 1.2

    def __init__(self, player_instance, vec: Vec):
        self.player_instance = player_instance
        self.vec = vec
        self.image = bee_img.copy()

    def update(self):
        self.vec.move_towards(self.player_instance.vec, self.SPEED)
        angle = self.vec.angle_to(self.player_instance.vec)
        self.image = pygame.transform.rotate(bee_img, angle)



    def draw(self, screen: pygame.Surface, camera: Vec):
        screen.blit(self.image, self.vec - camera)

