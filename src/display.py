import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 60

# screen_width = 960
# screen_height = 576
screen_width = 1100
screen_height = 650

screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption('Game')

camera = [-(screen_width // 2 - 60), -(screen_height // 2)]
player_start_pos = (50, 57)

