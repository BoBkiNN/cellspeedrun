from pathlib import Path

import pygame
import os
from math import floor

ASSETS_FOLDER = "assets"

type ImageCacheKey = tuple[Path, tuple[int, int] | None]
"""Tuple of image path to size"""

class Assets:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.image_cache: dict[ImageCacheKey, pygame.Surface] = {}

    def get_image(self, file: Path | str, resize_to: tuple[int, int] | None = None) -> pygame.Surface:
        path = self.folder / file
        key = (path, resize_to)
        if key in self.image_cache:
            return self.image_cache[key]
        
        image = pygame.image.load(path)
        if resize_to is None:
            self.image_cache[(path, image.get_size())] = image
            self.image_cache[(path, None)] = image
            return image
        else:
            ret = nearest_neighbor(image, resize_to)
            self.image_cache[(path, resize_to)] = ret
            return ret

    def list_files(self, subfolder: Path | str | None):
        path = self.folder if not subfolder else self.folder / subfolder
        return os.listdir(path)

    def get_looped_r(self, prefix: str, folder: str = "") -> list[pygame.Surface]:
        first = self.get_looped(prefix, folder)
        central = list(first)
        central.pop(0)
        central.pop(len(central)-1)
        central.reverse()
        ret = first + central
        return ret

    def get_looped(self, prefix: str, folder: str = "") -> list[pygame.Surface]:
        files = [f for f in self.list_files(folder) if f.startswith(prefix) and f.endswith(".png")]
        ret: list[pygame.Surface] = []
        for i in range(len(files)):
            file = f"{prefix}{i+1}.png"
            img = self.get_image(Path(folder) / file if folder else file)
            ret.append(img)
        return ret

def nearest_neighbor(surface: pygame.Surface, new_size: tuple[int, int]) -> pygame.Surface:
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
