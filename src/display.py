import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 960
screen_height = 576


screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption('Game')

bg = (128, 128, 128)
