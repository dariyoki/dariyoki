import logging
import json
from pathlib import Path

import pygame

from src.sprite_sheet import get_images

logger = logging.getLogger("log")


def load_assets(state: str) -> dict:
    assets = {}
    path = Path("assets/sprites/")
    for metadata_f in path.rglob("*.json"):
        metadata = json.loads(metadata_f.read_text())
        for file, data in metadata.items():
            if state not in data["states"]:
                continue

            complete_path = metadata_f.parent / file
            logger.info(f"Loaded {complete_path}")
            if data["convert_alpha"]:
                image = pygame.image.load(complete_path).convert_alpha()
            else:
                image = pygame.image.load(complete_path).convert()

            if data["sprite_sheet"] is None:
                asset = image
            else:
                asset = get_images(image, *data["sprite_sheet"].values())

            file_extension = file[file.find(".") :]
            assets[file.replace(file_extension, "")] = asset

    return assets

