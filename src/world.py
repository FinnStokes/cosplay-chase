import pygame
from pygame.locals import *
import pytmx
import pytmx.util_pygame as pytmxutil

class Level():
    """A tile-based level"""

    def __init__(self, filename):
        self.data = pytmxutil.load_pygame(filename)

    def passable(self, pos):
        for i in self.data.visible_tile_layers:
            print(int(pos[0]), int(pos[1]), i)
            tile = self.data.get_tile_properties(int(pos[0]), int(pos[1]), i)
            return tile['Passable']

    def draw(self, rect, surface):
        surface_blit = surface.blit
        tw = self.data.tilewidth
        th = self.data.tileheight
        top = rect.top
        left = rect.left

        if self.data.background_color:
            surface.fill(pygame.Color(self.data.background_color))

        for layer in self.data.visible_layers:
            # draw map tile layers
            if isinstance(layer, pytmx.TiledTileLayer):
                # iterate over the tiles in the layer
                for x, y, image in layer.tiles():
                    surface_blit(image, (x * tw - left, y * th - top))
