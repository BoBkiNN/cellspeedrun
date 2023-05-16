import pygame
import os
from math import floor

assets_folder = os.getcwd()+os.sep+"assets"

image_cache = {}

def nearest_neighbor(surface: pygame.Surface, new_size: tuple) -> pygame.Surface:
    width, height = surface.get_size()
    new_surface = pygame.Surface(new_size, pygame.SRCALPHA)
    scale_x = new_size[0]//width
    scale_y = new_size[1]//height
    for y in range(new_size[1]):
        for x in range(new_size[0]):
            i, j = floor(x // scale_x), floor(y // scale_y)
            rgba = surface.get_at((i, j))
            new_surface.set_at((x, y), rgba)
    return new_surface

def get_image(filename: str, resize_to: tuple = None) -> pygame.Surface:
    try:
        return image_cache[(filename, resize_to)]
    except:
        pass
    image = pygame.image.load(filename)
    if resize_to is None:
        image_cache[(filename, image.get_size())] = image
        return image
    else:
        ret = nearest_neighbor(image, resize_to)
        image_cache[(filename, resize_to)] = ret
        return ret

def get_looped_r(prefix, folder: str = "") -> list:
    direct = assets_folder
    if folder is not None:
        direct = direct+os.sep+folder
    files = [f for f in os.listdir(direct) if f.startswith(prefix) and f.endswith(".png")]
    first = []
    for n in range(1, len(files)+1):
        name = prefix+str(n)+".png"
        img = get_image(direct+os.sep+name)
        first.append(img)
    if len(first) < 3:
        return first
    central = list(first)
    central.pop(0)
    central.pop(len(central)-1)
    central.reverse()
    ret = first + central
    return ret

def get_looped(prefix, folder: str = None) -> list:
    direct = assets_folder
    if folder is not None:
        direct = direct+os.sep+folder
    files = [f for f in os.listdir(direct) if f.startswith(prefix) and f.endswith(".png")]
    ret = []
    for n in range(1, len(files)+1):
        name = prefix+str(n)+".png"
        img = get_image(direct+os.sep+name)
        ret.append(img)
    return ret
