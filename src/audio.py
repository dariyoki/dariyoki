import pygame

pygame.mixer.init()

path = 'assets/audio/'
pygame.mixer.music.load(path + "harmony_in_chaos2.mp3")
pygame.mixer.music.play(-1)
dash_sfx = pygame.mixer.Sound(path + 'dash.wav')
dash_sfx.set_volume(0.1)

pickup_item_sfx = pygame.mixer.Sound(path + 'pickup_item.wav')
pickup_item_sfx.set_volume(0.1)

hover_sfx = pygame.mixer.Sound(path + 'hover.wav')
hover_sfx.set_volume(0.1)
