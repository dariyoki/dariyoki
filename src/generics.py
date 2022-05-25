from typing import Any, Dict, List, Tuple, Union

import pygame


class Vec(pygame.math.Vector2):
    def move_towards(self, target, speed: float):
        self += (target - self).normalize() * speed


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, Vec]
Size = Tuple[int, int]
RgbaOutput = Tuple[int, int, int, int]
ColorValue = Union[pygame.Color, int, str, Tuple[int, int, int], List[int], RgbaOutput]
Events = List[pygame.event.Event]
EventInfo = Dict[str, Any]
WSurfInfo = List[Union[List[int], int]]
Assets = Dict[str, Union[pygame.Surface, Any]]
