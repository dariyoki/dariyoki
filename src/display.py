import json
import logging
import os

import pygame

from src._globals import LOGGING_CONFIG_PATH
from src.generics import Vec

pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
fps = 60

# screen_width = 960
# screen_height = 576
screen_width = 1100
screen_height = 650

compiling = True

# call any time before set_mode
try:
    import pyi_splash  # special pyinstaller thing - import will not resolve in dev

    pyi_splash.close()
except ImportError:
    compiling = (
        False  # this is expected to throw an exception in non-splash launch contexts.
    )

screen: pygame.Surface = pygame.display.set_mode(
    (screen_width, screen_height), pygame.SCALED | pygame.RESIZABLE
)
pygame.display.set_caption("src")
logo = pygame.image.load("assets/sprites/logo.ico").convert_alpha()
pygame.display.set_icon(logo)

# camera = [-(screen_width // 2 - 60), -(screen_height // 2)]
camera = Vec(100, 100)
player_start_pos = (950, -200)

# Game boundary
start_x = -1000
end_x = -1000 + (32 * 600)
start_y = 500
end_y = 500 - (32 * 120)

logging.basicConfig()
logger = logging.getLogger()

if os.path.exists(LOGGING_CONFIG_PATH):
    with open(LOGGING_CONFIG_PATH) as f:
        log_config = json.load(f)
else:
    log_config = {
        "AVAILABLE_OPTIONS": [
            "CRITICAL",
            "ERROR",
            "WARNING",
            "DEBUG",
            "INFO",
            "NOTSET",
        ],
        "LOGGING_LEVEL": "DEBUG",
    }
    with open(LOGGING_CONFIG_PATH, "w") as f:
        json.dump(log_config, fp=f, indent=2)

if compiling:
    logger.setLevel("CRITICAL")
else:
    logger.setLevel(log_config["LOGGING_LEVEL"])

logger.info("Display initialized")
