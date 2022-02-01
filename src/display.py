import pygame

pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
fps = 60

# screen_width = 960
# screen_height = 576
screen_width = 1100
screen_height = 650

compiling = False


# call any time before set_mode
def _dismiss_splash_screen():
    try:
        import pyi_splash  # special pyinstaller thing - import will not resolve in dev
        pyi_splash.close()
    except Exception:
        pass  # this is expected to throw an exception in non-splash launch contexts.


if compiling:
    _dismiss_splash_screen()

screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("dariyoki")
logo = pygame.image.load("assets/sprites/logo.ico").convert_alpha()
pygame.display.set_icon(logo)

# camera = [-(screen_width // 2 - 60), -(screen_height // 2)]
camera = [100, 100]
player_start_pos = (32*4, -200)

pygame.mouse.set_visible(False)

# Game boundary
start_x = -1000
end_x = -1000 + (32 * 600)
start_y = 500
end_y = 500 - (32 * 120)


