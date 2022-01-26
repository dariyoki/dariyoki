import pygame
import os
from src.sprite_sheet import SpriteSheet
from src.utils import resize, turn_left

path = "assets/sprites/"
# Cursor
cursor_img = pygame.image.load(path + "cursor.png").convert_alpha()
cursor_img = resize([cursor_img], 0.5)[0]

ss = pygame.image.load(path + "player/characters.png").convert_alpha()
characters_ss = SpriteSheet(ss)
characters = characters_ss.get_images(4, 4, 32, 32, fixer=8)
characters = resize(characters, scale=2)

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

background_img = pygame.image.load(path + "background.png").convert()
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

# Bar boder
bar_border_img = pygame.image.load(path + "borders/bar_border.png").convert_alpha()
