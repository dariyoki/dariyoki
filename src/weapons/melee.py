import pygame

from src.generics import Vec, EventInfo
from src.utils import Time


class Sword:
    def __init__(self, level: int, soul_energy: int):
        self.pos = Vec()
        self.level = level
        self.soul_energy = soul_energy
        self.wind_slash_gen_time = Time(0.5)

    def create_wind_slash(self):
        pass

    def update(self, event_info: EventInfo) -> None:
        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN and self.wind_slash_gen_time.update():
                self.create_wind_slash()
