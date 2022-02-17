import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1100
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Sprite Sheet Preview')

'''Sprite Sheet'''
from src.sprites import flame_particles_images
sprite_sheet = flame_particles_images
attributes = {
    "size": 8,
    "sprite sheet": sprite_sheet,
    "rows": 2,
    "columns": 4
}

# Define colours
bg = (128, 128, 128)
white = (255, 255, 255)


def draw_grid(size, rows):
    for line in range(rows):
        pygame.draw.line(screen, white, (0, line * size), (screen.get_width(), line * size))
        pygame.draw.line(screen, white, (line * size, 0), (line * size, screen.get_height()))


def check_sprite_sheet(size: float, sprites: list[pygame.Surface], rows: int, columns: int, space: float = 20) -> None:
    size += space
    index = 0

    draw_grid(size, rows)
    for row in range(rows):
        for column in range(columns):
            screen.blit(sprites[index], (column * size, row * size))
            index += 1


# Set screen res
# width = int(attributes["size"] * attributes["columns"])
# height = int(attributes["size"] * attributes["rows"])
pygame.display.set_mode((64*5 + 20, 64*5 + 20))

run = True
while run:

    clock.tick(fps)

    # Draw background
    screen.fill(bg)
    check_sprite_sheet(*list(attributes.values()))

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
