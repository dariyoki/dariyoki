import pygame
import random
import math
import uuid
from src.sprites import characters
from src.widgets import LoadingBar
from src.identification import enemy_ids


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

        # HP bar
        self.hp_bar_size = (60, 10)
        self.hp_bar = LoadingBar(
            value=self.hp,
            fg_color=(179, 2, 43),
            bg_color='black',
            rect=pygame.Rect((0, 0), self.hp_bar_size)
        )
        self.camera = [0, 0]

    def update(self, player_pos, info, dt):
        direction = ""
        dist = abs(self.x - player_pos[0])
        self.chasing = self.PLAYER_CHASE_RANGE > dist
        if self.chasing and dist > self.PLAYER_DIST:
            self.chasing = True
            if player_pos[0] < self.x:
                direction = "left"
            else:
                direction = "right"

        if not self.chasing:
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

        # # Handle damage
        # for shuriken in info["shurikens"]:
        #     if shuriken.rect.colliderect(pygame.Rect(
        #             self.rect.x - self.camera[0],
        #             self.rect.y - self.camera[1],
        #             *self.rect.size
        #     )):
        #         print('shuriken death')
        #         self.hp -= shuriken.damage
        #         info["shurikens"].remove(shuriken)

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

        self.x += dx
        self.y += dy

        # Handle idle distance
        if not self.chasing:
            self.idle_distance += abs(math.sqrt(dx ** 2 + dy ** 2))
            if self.idle_distance > 40:
                self.idle_movement_direction = random.choice(("right", "right", "left", "right", "jump"))
                self.idle_distance = 0

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))
        self.hp_bar.value = self.hp * (self.hp_bar_size[0] / self.max_hp)
        self.hp_bar.rect.center = (
            self.rect.midtop[0],
            self.rect.midtop[1] - 10
        )

    def draw(self, screen: pygame.Surface, camera):
        self.camera = camera
        screen.blit(self.image, (self.x - camera[0], self.y - camera[1]))
        self.hp_bar.draw(screen, camera, moving=True)
        denotion_pos = (
            self.hp_bar.rect.midtop[0] - camera[0],
            self.hp_bar.rect.y - camera[1] - self.hp_bar.rect.height * 2
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
