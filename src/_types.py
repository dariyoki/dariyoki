import math
from typing import Any, Dict, List, Tuple, Union

import pygame

Pos = Union[Tuple[int, int], List[int], pygame.Vector2]
Size = Tuple[int, int]
RgbaOutput = Tuple[int, int, int, int]
ColorValue = Union[pygame.Color, int, str, Tuple[int, int, int], List[int], RgbaOutput]
Events = List[pygame.event.Event]
EventInfo = Dict[str, Any]
WSurfInfo = List[Union[List[int], int]]
Assets = Dict[str, Union[pygame.Surface, Any]]


class Vec(pygame.math.Vector2):
    def move_towards(self, target, speed: float):
        # angle = self.angle_to(target)
        # self.x += math.cos(math.radians(angle)) * speed
        # self.y += math.sin(math.radians(angle)) * speed

        # return angle
        self += (target - self).normalize() * speed
