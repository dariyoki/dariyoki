"""
This file is a part of the 'dariyoki' source code.
The source code is distributed under the GPL V3 license.
"""

from typing import Union

from dariyoki.states.levels import Level, LevelSelector
from dariyoki.states.main_menu import MainMenu

GameStates = Union[Level, LevelSelector, MainMenu]
