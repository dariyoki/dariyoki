import pygame


def collide(self, info, event_info, dx, dy):
    dt = event_info["dt"]
    # Check collisions
    for pos in info["tiles"]:
        tile_type = info["tiles"][pos][0]
        stub = info["tiles"][pos][1]
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
        # Check for floor collision
        if "up" in tile_type:
            if stub.collidepoint(self.rect.midbottom) and self.rect.y < pos[1]:
                self.image = self.right_img if self.last_direction == "right" else self.left_img
                self.touched_ground = True
                self.angle = 0
                dy = stub.top - self.rect.bottom
                # self.velocity = 5
                break
    else:
        if not self.jumping:
            self.velocity += self.acceleration * dt
            dy += self.velocity * dt

    return dx, dy
