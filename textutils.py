from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pygame


class Font:
    def __init__(self, id: str, pg: pygame.font.Font, size: int) -> None:
        self.id = id
        self.pg = pg
        self.size = size


type FontName = str | Path
"""Path to load font from file or string to use system font"""
type Color = tuple[int, int, int] | tuple[int, int, int, int]


font_cache: list[Font] = []


def _compute_font(id: str, name: FontName, size: int):
    for f in font_cache:
        if f.id == id and f.size == size:
            return f
    if isinstance(name, Path):
        return Font(id, pygame.font.Font(name, size), size)
    else:
        return Font(id, pygame.font.SysFont(name, size), size)

def render(text: str, size: int, font: FontName = "Arial", color: tuple = (255, 255, 255)) -> pygame.Surface:
    f = _compute_font(str(font), font, size)
    return f.pg.render(text, True, color)

def render_w_shadow(text: str, size: int, font: FontName = "Arial", 
                    color: tuple = (255, 255, 255), 
                    offset: int = 3, 
                    shadow_col: tuple = (0, 0, 0, 70)) -> pygame.Surface:
    shadow = render(text, size, font, shadow_col)
    fore = render(text, size, font, color)
    sx = max(shadow.get_size()[0], fore.get_size()[0])
    sy = max(shadow.get_size()[1], fore.get_size()[1])
    ret = pygame.Surface([sx, sy], pygame.SRCALPHA)
    ret.blit(shadow, [offset, offset])
    ret.blit(fore, [0, 0])
    return ret

@dataclass
class CachedSurface:
    getter: Callable[[], pygame.Surface]
    _value: pygame.Surface | None = None

    def get(self):
        if self._value is not None:
            return self._value
        self._value = v = self.getter()
        return v

    def invalidate(self):
        self._value = None
