import pygame
import random
import time
import sys
from src.effects.explosion import Explosion

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
fps = 60

explosions = []

cd = 0.3
time_passed = 0
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

    # time_passed += raw_dt
    # if time_passed > cd:
    #     explosions.append(Explosion(1000, (4, 15), [random.randrange(500), random.randrange(500)]))
    #     time_passed = 0
    # Event loop
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            explosions.append(Explosion(1000, (4, 15), list(mouse_pos), (40, 120), 'green'))

    # Rendering
    screen.fill(0)

    for explosion in explosions:
        explosion.draw(screen, raw_dt)
        if len(explosion.particles) == 0:
            explosions.remove(explosion)

    pygame.display.update()
