import pygame

pygame.init()
screen = pygame.display.set_mode((16 * 40, 9 * 40))
clock = pygame.time.Clock()


my_cursor_img = pygame.image.load("assets/sprites/cursor.png").convert_alpha()
pygame.mouse.set_cursor((0, 0), my_cursor_img)
while True:

    dt = clock.get_time() * 120
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

    screen.fill((25, 25, 25))

    pygame.display.flip()
    clock.tick()
