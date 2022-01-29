import pygame
import time
import sys

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
fps = 60


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

    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()

    # Rendering
    screen.fill(0)
    pygame.display.update()
