import time
import pickle

import pygame

from src.display import *
from src.sprites import background_img, characters, bee_tile_set_info, chests
from src.world import World
from src.items import Chest
from src.level_manager import LevelManager
from src_le.option import ChooseOption
from src_le.s_data import SChest

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


def generate_possible_rects(rows, columns, rect_size, start) -> list[pygame.Rect]:
    possibilities = []
    for row in range(rows):
        for col in range(columns):
            r = pygame.Rect(
                ((col * rect_size) + start[0],
                 (row * rect_size) - start[1]),
                (rect_size, rect_size)
            )
            possibilities.append(r)

    return possibilities


def closest(lst, k):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - k))]


def save_data(data):
    with open("data/level_data/level_0", "wb") as f:
        pickle.dump(data, f)


def main():
    with open('data/level_data/level_0', 'rb') as f:
        level_manager = pickle.load(f)

    # level_manager = LevelManager()
    world = World(level_manager)
    possible_rects = generate_possible_rects(
        rows=120,
        columns=600,
        rect_size=32,
        start=(-1000, 500)
    )
    speed = 5
    current_tile_name = "upleft"
    opts = {
        0: "upleft",
        1: "up",
        2: "upright",
        3: "left",
        4: "center",
        5: "right",
        6: "downleft",
        7: "down",
        8: "downright",
        9: "chest",
        10: "clear"
    }
    r_surf = pygame.Surface((32, 32))
    r_surf.fill('red')
    opts_imgs = list(bee_tile_set_info.values()) + [chests[0], r_surf]
    options = ChooseOption(opts_imgs, screen)

    # Copy double data
    c_chests = []
    c_chest_poses = []

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
        if pygame.mouse.get_pressed()[0] and mouse_pos[1] > 100:
            asd = pygame.Rect((0, 0), (32, 32))
            asd.center = mouse_pos
            x = closest([r.x for r in possible_rects], asd.x + camera[0])
            y = closest([r.y for r in possible_rects], asd.y + camera[1])
            tile = pygame.Rect((x, y), (32, 32))

            if "clear" in current_tile_name:
                for pos in level_manager.all_rects:
                    stub = pygame.Rect(pos, (32, 32))
                    if stub.colliderect(tile):
                        del level_manager.all_rects[pos]
                        break

            elif (tile.x, tile.y) not in level_manager.all_rects:
                if "up" in current_tile_name:
                    level_manager.all_rects[(tile.x, tile.y)] = current_tile_name
                if "down" in current_tile_name:
                    level_manager.all_rects[(tile.x, tile.y)] = current_tile_name
                if "left" in current_tile_name:
                    level_manager.all_rects[(tile.x, tile.y)] = current_tile_name
                if "right" in current_tile_name:
                    level_manager.all_rects[(tile.x, tile.y)] = current_tile_name

                if "center" in current_tile_name:
                    level_manager.all_rects[(tile.x, tile.y)] = current_tile_name

                if "chest" in current_tile_name:
                    if (tile.x, tile.y) not in c_chest_poses:
                        level_manager.chests.append(SChest(tile.x, tile.y, pygame.K_f, 7))
                        c_chests.append(Chest(tile.x, tile.y, pygame.K_f, 7))
                        c_chest_poses.append((tile.x, tile.y))

        current_tile_name = opts[options.chosen_option]

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

        if keys[pygame.K_LCTRL]:
            controlling = True
        else:
            controlling = False

        camera[0] -= dx
        camera[1] += dy

        # Render
        screen.blit(background_img, (0, 0))
        world.draw(screen, camera)
        screen.blit(characters[0], (player_start_pos[0] - camera[0],
                                    player_start_pos[1] - camera[1]))

        for chest in c_chests:
            chest.draw(screen, camera)

        options.update(mouse_pos, dt)
        options.draw()

        # for rect in possible_rects:
        #     pygame.draw.rect(screen, "black", rect, width=1)

        # Event check
        for event in events:
            if event.type == pygame.QUIT:
                run = False

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_z:
            #         if controlling:
            #             level_manager.all_rects.pop()

        # Update display
        pygame.display.update()

    save_data(level_manager)


if __name__ == '__main__':
    main()

