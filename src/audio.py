import pygame

pygame.mixer.init()

path = 'assets/audio/'
dash_sfx = pygame.mixer.Sound(path + 'dash.wav')
dash_sfx.set_volume(0.3)

pickup_item_sfx = pygame.mixer.Sound(path + 'pickup_item.wav')
pickup_item_sfx.set_volume(0.2)
