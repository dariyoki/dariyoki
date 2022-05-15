import pygame
import os
import json
from pathlib import Path
from src.sprite_sheet import SpriteSheet
from src.utils import resize, turn_left
from src._types import Assets
from src._globals import METADATA, PARENTS

path = "assets/sprites/"


def load_assets(state: str, assets: dict, path: Path = Path()) -> Assets:
    """
    Load assets dynamically from given path.

    Parameters:
        state: Game state to see if sprite is to be loaded.
        assets: Dictionary to modify in place.
        path: Path to load assets from.
    """

    for parent in PARENTS:
        for file in path.rglob("*"):
            img_data = METADATA[parent][file.name]["data"]
            if state not in img_data["state"]:
                if file.name in assets[parent]:
                    del assets[file.name]
                continue

            if img_data["sprite sheet"] is not None:
                assets[file.name] = SpriteSheet(*img_data["sprite sheet"].values())
                continue

            assets[file.name] = pygame.image.load(file.absolute().name)
            assets[file.name].convert_alpha() if img_data["convert alpha"] else assets[file.name].convert()

    return assets


# Background art
background_img = pygame.image.load(path + "backgrounds/background.png").convert()
menu_background_img = pygame.transform.scale(pygame.image.load(path + "backgrounds/red_ski_looks_good.jpeg"),
                                             (1100, 650))
moon = pygame.image.load(path + "backgrounds/moon.png").convert_alpha()

# Cursor
cursor_img = pygame.image.load(path + "cursor.png").convert_alpha()
cursor_img = resize([cursor_img], 0.5)[0]

ss = pygame.image.load(path + "player/characters.png").convert_alpha()
characters_ss = SpriteSheet(ss)
characters = characters_ss.get_images(4, 4, 32, 32, fixer=8)
characters = resize(characters, scale=2)
player_size = characters[0].get_size()

sword_attack_img = pygame.image.load(path + "player/sword attack.png").convert_alpha()
sword_attack_ss = SpriteSheet(sword_attack_img)
sword_attack = sword_attack_ss.get_images(1, 4, 32, 32, 16)
sword_attack = resize(sword_attack, scale=3)
lsword_attack = turn_left(sword_attack)

chest_img = pygame.image.load(path + "items/chest.png").convert_alpha()
chest_ss = SpriteSheet(chest_img)
chests = chest_ss.get_images(1, 2, 32, 32, fixer=8, bound=False)
chests = resize(chests, scale=2)

# Border art
border_img = pygame.image.load(path + "borders/border.png").convert_alpha()
selected_border_img = pygame.image.load(path + "borders/selected_border.png").convert_alpha()

# Items
health_potion_img = pygame.image.load(path + "items/health_potion.png").convert_alpha()
shield_potion_img = pygame.image.load(path + "items/shield_potion.png").convert_alpha()
shuriken_img = pygame.image.load(path + "items/shuriken.png").convert_alpha()
sb_img = pygame.image.load(path + "items/smoke_bomb.png").convert_alpha()
sword_img = pygame.image.load(path + "items/sword.png").convert_alpha()
scythe_img = pygame.image.load(path + "items/scythe.png").convert_alpha()

item_size = (25, 25)
items = {
    "health potion": pygame.transform.scale(health_potion_img, item_size),
    "shield potion": pygame.transform.scale(shield_potion_img, item_size),
    "shuriken": pygame.transform.scale(shuriken_img, item_size),
    "smoke bomb": pygame.transform.scale(sb_img, item_size),
    "sword": pygame.transform.scale(sword_img, item_size),
    "scythe": pygame.transform.scale(scythe_img, item_size)
}

game_border_img = pygame.image.load(path + "borders/game_border.png").convert_alpha()

# Information cards
i_cards = {i_card[2:-5].replace('_', ' '): pygame.image.load(path + f"icards/{i_card}").convert() for i_card in
           os.listdir(path + "icards/")}


# Tile sets
bee_tile_set_img = pygame.image.load(path + "tilesets/bee_tileset.png").convert_alpha()
bee_tile_set_ss = SpriteSheet(bee_tile_set_img)
bee_tile_set = bee_tile_set_ss.get_images(3, 3, 32, 32, fixer=10.7)
bee_tile_set_info = {
    "upleft": (upleft := pygame.transform.flip(bee_tile_set[2], True, False)),
    "up": bee_tile_set[1],
    "upright": bee_tile_set[2],
    "left": pygame.transform.flip(bee_tile_set[5], True, False),
    "center": bee_tile_set[4],
    "right": bee_tile_set[5],
    "downleft": pygame.transform.flip(upleft, False, True),
    "down": pygame.transform.flip(bee_tile_set[1], False, True),
    "downright": pygame.transform.flip(bee_tile_set[2], False, True)
}

# Spawners
spawner_imgs = [
    pygame.image.load(path + "spawners/spawner_shadow_ninja.png").convert_alpha(),
    pygame.image.load(path + "spawners/spawning_shadow_ninja.png").convert_alpha()
]

# The Blue Ribbon
blue_ribbon = pygame.image.load(path + "blue_ribbon.png").convert_alpha()

# Bar border
bar_border_img = pygame.image.load(path + "borders/bar_border.png").convert_alpha()

# Shield
shield_ss_img = pygame.image.load(path + "player/shield_bubble.png").convert_alpha()
shield_ss = SpriteSheet(shield_ss_img)
shield_frames = shield_ss.get_images(rows=1,
                                     columns=4,
                                     width=32,
                                     height=32,
                                     fixer=16)
shield_frames = resize(shield_frames, scale=3)
player_shield_img = shield_frames[0]

# Bee boss
bee_boss_ss_img = pygame.image.load(path + "boss/boss_walking.png").convert_alpha()
bee_boss_ss = SpriteSheet(bee_boss_ss_img)
bee_boss_frames = bee_boss_ss.get_images(1, 4, 64, 64, fixer=1)
bee_boss_frames = resize(bee_boss_frames, scale=2)

# Flame particles
flame_particles_ss_img = pygame.image.load(path + "decoration/flame_particles.png").convert_alpha()
flame_particles_ss = SpriteSheet(flame_particles_ss_img)
flame_particles_images = flame_particles_ss.get_images(
    rows=2,
    columns=4,
    width=8,
    height=8,
    fixer=0.3
)

# Bush Parallax
bush_img = pygame.image.load(path + "decoration/bush_parallax.png").convert_alpha()
r_bush_img = pygame.transform.flip(bush_img, True, False)
bush_width = bush_img.get_width()
