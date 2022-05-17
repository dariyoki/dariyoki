import asyncio

import pygame

WIDTH, HEIGHT = 500, 400
FPS = 60


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    from src.sprites import cursor_img
    pygame.mouse.set_cursor((0, 0), cursor_img)
    # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

    running = True
    while running:
        clock.tick(FPS)
        screen.fill("black")

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        await asyncio.sleep(0)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
