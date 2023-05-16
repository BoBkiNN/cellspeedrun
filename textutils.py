import pygame
import utils

font_cache = []
shadowed_cache = {}

class Font:
    def __init__(self, name: str, pg: pygame.font.Font, size: int) -> None:
        self.name = name
        self.pg = pg
        self.size = size

class ShadowedText:
    def __init__(self, text: str, name: str, size: int, color: tuple, surface: pygame.Surface) -> None:
        self.text = text
        self.name = name
        self.size = size
        self.color = color
        self.surface = surface


def render(text: str, size: int, name: str = "Arial", color: tuple = (255, 255, 255), file: bool = False) -> pygame.Surface:
    font: Font = None
    for f in font_cache:
        f: Font
        if f.size == size and f.name == name:
            font = f
            break
    else:
        if file:
            font = Font(name, pygame.font.Font(name, size), size)
        else:
            font = Font(name, pygame.font.SysFont(name, size), size)
    return font.pg.render(text, True, color)

def render_w_shadow(text: str, size: int, name: str = "Arial", color: tuple = (255, 255, 255), file: bool = False, offset: int = 3, shadow_col: tuple = (0, 0, 0, 70)) -> pygame.Surface:
    try:
        st: ShadowedText = shadowed_cache[(text, size, color)]
        return st.surface
    except KeyError:
        pass
    shadow = render(text, size, name, shadow_col, file)
    fore = render(text, size, name, color, file)
    sx = max(shadow.get_size()[0], fore.get_size()[0])
    sy = max(shadow.get_size()[1], fore.get_size()[1])
    ret = pygame.Surface([sx, sy], pygame.SRCALPHA)
    ret.blit(shadow, [offset, offset])
    ret.blit(fore, [0, 0])
    st = ShadowedText(text, name, size, color, ret)
    shadowed_cache[(text, size, color)] = st
    return ret