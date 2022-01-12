import pygame
import os
from src.sprite_sheet import SpriteSheet
from src.utils import resize, turn_left

path = "assets/sprites/"
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
border_img = pygame.image.load(path + "border.png").convert_alpha()

# Items
health_potion_img = pygame.image.load(path + "items/health_potion.png").convert_alpha()
shield_potion_img = pygame.image.load(path + "items/shield_potion.png").convert_alpha()
shuriken_img = pygame.image.load(path + "items/shuriken.png").convert_alpha()
sb_img = pygame.image.load(path + "items/smoke_bomb.png").convert_alpha()
sword_img = pygame.image.load(path + "items/sword.png").convert_alpha()

item_size = (25, 25)
items = {
    "health potion": pygame.transform.scale(health_potion_img, item_size),
    "shield potion": pygame.transform.scale(shield_potion_img, item_size),
    "shuriken": pygame.transform.scale(shuriken_img, item_size),
    "smoke bomb": pygame.transform.scale(sb_img, item_size),
    "sword": pygame.transform.scale(sword_img, item_size)
}

background_img = pygame.image.load(path + "background.png").convert()

# Information cards
i_cards = {i_card[2:-5].replace('_', ' '): pygame.image.load(path + f"icards/{i_card}").convert() for i_card in
           os.listdir(path + "icards/")}
