import pygame
from src.sprites import characters


class Ninja:
    def __init__(self, x, y, weapon, clan: str, speed, jump_height, player_dist):
        self.x, self.y = x, y
        self.weapon = weapon

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

        # Casket
        self.last_direction = "right"

        # Movement vars
        self.angle = 0
        
        # Statistics
        self.hp = 100
        self.shield = 100
        self.soul_energy = 100

        # Movement speeds
        self.speed = speed
        self.JUMP_HEIGHT = jump_height
        self.player_dist = player_dist
        self.velocity = 5
        self.acceleration = 2

        # Stacking values
        self.jump_stack = 0

    def update(self, player_pos, info, dt):
        direction = ""
        if abs(self.x - player_pos[0]) > self.player_dist:
            if player_pos[0] < self.x:
                direction = "left"
            else:
                direction = "right"

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

        self.rect = self.right_img.get_rect(topleft=(self.x, self.y))

    def draw(self, screen: pygame.Surface, camera):
        # pygame.draw.rect(screen, "red", self.rect, width=1)
        screen.blit(self.image, (self.x - camera[0], self.y - camera[1]))


