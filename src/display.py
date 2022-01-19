import pygame

pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
fps = 60

# screen_width = 960
# screen_height = 576
screen_width = 1100
screen_height = 650

screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("dariyoki")
logo = pygame.image.load("assets/sprites/logo.png").convert_alpha()
pygame.display.set_icon(logo)

# camera = [-(screen_width // 2 - 60), -(screen_height // 2)]
camera = [0, 0]
player_start_pos = (50, 57)

pygame.mouse.set_visible(False)


