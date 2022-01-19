import pygame
import math


class Angle:
    def __init__(self, start, target, speed, size):
        self.x, self.y = start
        self.target_x, self.target_y = target
        self.speed = speed
        self.size = size

        self.rect = pygame.Rect((0, 0), self.size)

        # Getting the angle in radians
        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.degrees = self.angle * 57.2958  # In degrees

        # Change in x and y
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

        # if self.target_x < self.x:
        #
        #     print('event hp')
        #     self.dx = -self.dx
        # if self.target_y < self.y:
        #     self.dy = -self.dy

        # Calculating how much the object has moved
        self.distance = 0

    def set_target(self, target):
        self.target_x, self.target_y = target

        # Getting the angle in radians
        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.degrees = self.angle * 57.2958

        # Change in x and y
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def move(self, dt):
        # Update player pos by dx and dy
        self.x += self.dx * dt
        self.y += self.dy * dt

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Increasing amount moved
        self.distance += math.sqrt(((self.dx * dt) ** 2) + ((self.dy * dt) ** 2))

