"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

import pygame

from dariyoki.generics import Vec


def collide(self, info, event_info, dx, dy, vec: Vec):
    dt = event_info["dt"]
    # Check collisions
    for pos in info["tiles"]:
        tile_type = info["tiles"][pos][0]
        stub = info["tiles"][pos][1]

        if vec.distance_to(stub.center) > 300:
            # logger.info("this should not be happening though")
            continue
        # Check for right collision
        if "right" in tile_type and self.last_direction == "left":
            if stub.colliderect(self.rect):
                dx = 0

        # Check for left collision
        if "left" in tile_type and self.last_direction == "right":
            if stub.colliderect(self.rect):
                dx = 0

        # Check for roof collision
        if "down" in tile_type:
            if stub.colliderect(self.rect):
                self.jumping = False

    for pos in info["tiles"]:
        tile_type = info["tiles"][pos][0]
        stub = info["tiles"][pos][1]

        if vec.distance_to(stub.center) > 300:
            continue
        # Check for floor collision
        if "up" in tile_type:
            if stub.collidepoint(self.rect.midbottom) and self.rect.y < pos[1]:
                self.image = (
                    self.right_img
                    if self.last_direction == "right"
                    else self.left_img
                )
                self.touched_ground = True
                self.angle = 0
                dy = stub.top - self.rect.bottom
                # self.velocity = 5
                break
    else:
        if not self.jumping:
            if self.velocity < 30:
                self.velocity += self.acceleration * dt
            dy += self.velocity * dt

    return dx, dy


def jump(self, dt, dy):
    # Gravity control
    if self.jumping:
        self.angle += 200 * dt

        self.image = pygame.transform.rotozoom(
            self.right_img, int(self.angle), 1
        )
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

    return dy
