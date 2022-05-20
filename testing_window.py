import pygame
from src.animation import Animation
from src.sprite_sheet import get_images
from src.utils import turn_left

pygame.init()
screen = pygame.display.set_mode((16 * 40, 9 * 40))
clock = pygame.time.Clock()

sheet = pygame.image.load("assets/sprites/boss/bee_queen.png").convert_alpha()
frames = get_images(sheet, 1, 5, 64, fixer=16)
left_frames = turn_left(frames)
bee_animation_speed = 0.00005
bee_queen_idle_animation_right = Animation(frames, bee_animation_speed)
bee_queen_idle_animation_left = Animation(left_frames, bee_animation_speed)
bee_queen_idle_animation = bee_queen_idle_animation_right

pos = pygame.Vector2(50, 50)
bee_speed = 0.001
while True:

    dt = clock.get_time() * 120
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

    delta = pygame.Vector2(0, 0)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        delta.x += bee_speed * dt
    if keys[pygame.K_LEFT]:
        delta.x -= bee_speed * dt
    if keys[pygame.K_UP]:
        delta.y -= bee_speed * dt
    if keys[pygame.K_DOWN]:
        delta.y += bee_speed * dt

    if delta.x < 0:
        bee_queen_idle_animation = bee_queen_idle_animation_right
    elif delta.x > 0:
        bee_queen_idle_animation = bee_queen_idle_animation_left

    pos += delta
    screen.fill((25, 25, 25))
    bee_queen_idle_animation.play(screen, pos, dt)

    pygame.display.flip()
    clock.tick()


