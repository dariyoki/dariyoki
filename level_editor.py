import time
import pygame
import pickle
from src.display import *
from src.world import World

pygame.display.set_caption("Level Editor")


def generate_border(dimensions, rect_size) -> list[pygame.Rect]:
    rows = dimensions[1] // rect_size
    cols = dimensions[0] // rect_size

    border = []
    for row in range(rows):
        for col in range(cols):
            if row != rows - 1:
                continue
            r = pygame.Rect((col * rect_size, row * rect_size), (rect_size, rect_size))
            border.append(r)

    return border


def generate_possible_rects(dimensions, rect_size) -> list[pygame.Rect]:
    rows = dimensions[1] // rect_size
    cols = dimensions[0] // rect_size

    border = []
    for row in range(rows):
        for col in range(cols):
            r = pygame.Rect((col * rect_size, row * rect_size), (rect_size, rect_size))
            border.append(r)

    return border


def closest(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


def save_data(data):
    with open("data/level_data/level_0", "wb") as f:
        pickle.dump(data, f)


def main():
    save_data(generate_border((screen_width, screen_height), 32))
    world = World()
    possible_rects = generate_possible_rects((screen_width, screen_height), 32)
    camera = [0, 0]
    speed = 5

    run = True
    start = time.perf_counter()
    while run:
        # Calc
        end = time.perf_counter()
        dt = end - start
        dt *= fps
        start = time.perf_counter()
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        # Update
        if pygame.mouse.get_pressed()[0]:
            x = closest([r.x for r in possible_rects], mouse_pos[0])
            y = closest([r.y for r in possible_rects], mouse_pos[1])
            tile = pygame.Rect((x + camera[0], y + camera[1]), (32, 32))
            if tile not in world.rects:
                world.rects.append(tile)

        dx, dy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            dx -= speed * dt
        if keys[pygame.K_a]:
            dx += speed * dt
        if keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_s]:
            dy += speed * dt

        camera[0] -= dx
        camera[1] += dy

        # Render
        screen.fill(bg)
        world.draw(screen, camera)

        # for rect in possible_rects:
        #     pygame.draw.rect(screen, "black", rect, width=1)

        # Event check
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        # Update display
        pygame.display.update()

    save_data(world.rects)


if __name__ == '__main__':
    main()

