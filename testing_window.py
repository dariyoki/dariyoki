import pygame

from src.animation import Animation
from src.sprite_sheet import get_images

pygame.init()
screen = pygame.display.set_mode((16 * 40, 9 * 40))
clock = pygame.time.Clock()


sheet = pygame.image.load("assets/sprites/player/dariyoki_jetpack.png").convert_alpha()
frames = get_images(sheet, rows=1, columns=4, size=128, bound=True)[1:]
animation_speed = 0.00005
jetpack_animation = Animation(frames, animation_speed)

pos = pygame.Vector2(50, 50)
bee_speed = 0.001
while True:

    dt = clock.get_time() * 120
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

    screen.fill((25, 25, 25))
    jetpack_animation.play(screen, pos, dt)

    pygame.display.flip()
    clock.tick()
