import pygame
from src.sprite_sheet import SpriteSheet
from src.utils import resize, turn_left


path = "assets/sprites/"
ss = pygame.image.load(path + "player/characters.png").convert_alpha()
characters_ss = SpriteSheet(ss, 128, 128)
characters = characters_ss.get_images(4, 4, 32, 32, fixer=8)
characters = resize(characters, scale=2)

sword_attack_img = pygame.image.load(path + "player/sword attack.png").convert_alpha()
sword_attack_ss = SpriteSheet(sword_attack_img, 128, 32)
sword_attack = sword_attack_ss.get_images(1, 4, 32, 32, 16)
sword_attack = resize(sword_attack, scale=3)
lsword_attack = turn_left(sword_attack)

shield_potion_img = pygame.image.load(path + "items/shield_potion.png").convert_alpha()
shield_potion_img = pygame.transform.scale(shield_potion_img, (25, 25))

chest_img = pygame.image.load(path + "items/chest.png").convert_alpha()
chest_ss = SpriteSheet(chest_img, 64, 32)
chests = None

