import pygame
import time
import sys

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
fps = 60

from src.sprites import bee_boss_frames, bee_tile_set_img
from src.animation import Animation
from src.utils import resize

pygame.image.save(resize([bee_tile_set_img], scale=25/32)[0], "assets/sprites/tilesets/parallax_bee_tile_set.png")

bee_boss_walk = Animation(bee_boss_frames, speed=0.09)
pos = [50, 50]
start = time.perf_counter()
while True:
    clock.tick()
    end = time.perf_counter()
    raw_dt = end - start
    dt = raw_dt * fps
    start = time.perf_counter()

    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()
    mouse_press = pygame.mouse.get_pressed()
    pos[0] += dt

    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()

    # Rendering
    screen.fill('grey')
    bee_boss_walk.play(screen, pos, dt)

    pygame.display.update()
