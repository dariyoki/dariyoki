import pygame
from typing import List, Tuple, Union, Dict, Any

Pos = Union[Tuple[int, int], List[int], pygame.Vector2]
Size = Tuple[int, int]
RgbaOutput = Tuple[int, int, int, int]
ColorValue = Union[pygame.Color, int, str, Tuple[int, int, int], List[int], RgbaOutput]
Events = List[pygame.event.Event]
EventInfo = Dict[str, Any]
WSurfInfo = List[Union[List[int], int]]
Assets = Dict[str, Union[pygame.Surface, Any]]
