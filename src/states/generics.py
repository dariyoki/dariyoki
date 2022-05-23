from typing import Union

from src.states.levels import Level, LevelSelector
from src.states.main_menu import MainMenu

GameStates = Union[Level, LevelSelector, MainMenu]

