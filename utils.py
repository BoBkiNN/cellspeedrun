import random, colorsys, enum
from vector2 import Vector
import pygame

def random_col(max: int = 255) -> tuple:
    return (random.randint(0, max), random.randint(0, max), random.randint(0, max))

def random_chromatic(max: int = 40, min: int = 0) -> tuple:
    max_value = max/255
    min_value = min/255
    value = random.uniform(min_value, max_value)
    # Convert the HSV color to RGB
    r, g, b = colorsys.hsv_to_rgb(0, 0, value)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return (r, g, b)

def random_chromatic_alpha(alpha: int = 255, max: int = 40, min: int = 0) -> tuple:
    r, g, b = random_chromatic(max, min)
    return (r, g, b, alpha)

def random_exclude(min: int, max: int, exclude: int):
    n = random.randint(min, max)
    while n == exclude:
        n = random.randint(min, max)
    return n

def eq_vec(one: Vector, other: Vector):
        if one.x == other.x and one.y == other.y: return True
        else: return False

class AttachTo(enum.Enum):
     UP = -1
     MIDDLE = 0
     DOWN = 1

class UiElement:
     def __init__(self, surf: pygame.Surface, pos: list, offset: tuple = (0, 0)):
          self.surf = surf
          self.x = pos[0]
          self.y = pos[1]
          self.offset = offset
          self.size = list(surf.get_size())
          fs = list(self.size)
          fs[0] += offset[0]
          fs[1] += offset[1]
          self.full_size = fs

class UiRow:
    def __init__(self, surface: pygame.Surface) -> None:
          self.size = list(surface.get_size())
          self.elements: list[UiElement] = []
          self.surf = surface
        
    def get_last(self) -> UiElement:
        if len(self.elements) == 0:
            return None
        else:
            return self.elements[len(self.elements)-1]
    
    def concat_surf(self):
        sx = 0
        sy = 0
        for el in self.elements:
            sx = max(sx, el.x+el.full_size[0])
            sy = max(sy, el.y+el.full_size[1])
        last = self.get_last()
        if last != None:
            sx -= last.offset[0]
            sy -= last.offset[1]
        self.surf = pygame.Surface([sx, sy], pygame.SRCALPHA)
    
    def render(self) -> pygame.Surface:
        self.concat_surf()
        for el in self.elements:
            self.surf.blit(el.surf, [el.x, el.y])
        return self.surf
    
    def add(self, surf: pygame.Surface, attach: AttachTo = AttachTo.MIDDLE, offset: int = 0):
        last = self.get_last()
        sizes = surf.get_size()
        if last == None:
            pos = [0, 0]
            el = UiElement(surf, pos)
            if self.size[0] < el.size[0] or self.size[1] < el.size[1]:
                self.size[0] = el.size[0]
                self.size[1] = el.size[1]
                self.surf = pygame.Surface(list(self.size), pygame.SRCALPHA)
        else:
            if attach == AttachTo.UP:
                y = last.y
            elif attach == AttachTo.DOWN:
                y = last.y+last.size[1]-sizes[1]
            else:
                y = last.y+last.size[1]//2-sizes[1]//2
            if y < last.y:
                last.y = last.y+y
                y = y+y
            pos = [last.x+last.full_size[0]+offset, y]
            el = UiElement(surf, pos)
            if self.size[0] < el.size[0] or self.size[1] < el.size[1]:
                self.size[0] = el.size[0]
                self.size[1] = el.size[1]
                self.surf = pygame.Surface(list(self.size), pygame.SRCALPHA)
        self.elements.append(el)
        return self
