"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

from typing import Any, Dict, List, Tuple, Union

import pygame


def move_towards(self, target, speed: float):
    vec = (target - self).normalize() * speed
    self.x += vec.x
    self.y += vec.y


class Vec(pygame.math.Vector2):
    def move_towards(self, target, speed: float):
        vec = (target - self).normalize() * speed
        self.x += vec.x
        self.y += vec.y


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, Vec]
Size = Tuple[int, int]
RgbaOutput = Tuple[int, int, int, int]
ColorValue = Union[
    pygame.Color, int, str, Tuple[int, int, int], List[int], RgbaOutput
]
Events = List[pygame.event.Event]
EventInfo = Dict[str, Any]
WSurfInfo = List[Union[List[int], int]]
Assets = Dict[str, Union[pygame.Surface, Any]]
