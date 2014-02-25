"""
Demonstrates how to create a resizable display. Aspect ratio is not maintained.
Unless you have a good reason for doing so, it is generally smarter to detect
the resolution of the user and scale all elements once at load time. This
avoids the overhead with needing to scale while running.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


CAPTION = "Resizable Display"
SCREEN_START_SIZE = (500, 500)


class Control(object):
    """A simple control class."""
    def __init__(self):
        """
        Initialize all of the usual suspects. If the os.environ line is
        included, then the screen will recenter after it is resized.
        """
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        pg.init()
        pg.display.set_caption(CAPTION)
        self.screen = pg.display.set_mode(SCREEN_START_SIZE, pg.RESIZABLE)
        self.screen_rect = self.screen.get_rect()
        self.image = pg.Surface(SCREEN_START_SIZE).convert()
        self.image_rect = self.image.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()

    def event_loop(self):
        """
        We are going to catch pygame.VIDEORESIZE events when the user
        changes the size of the window.
        """
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(event.size, pg.RESIZABLE)
                self.screen_rect = self.screen.get_rect()

    def update(self):
        """
        Draw all objects on a surface the size of the start window just as
        we would normally draw them on the display surface. Check if the
        current resolution is the same as the original resolution. If so blit
        the image directly to the display; if not, resize the image first.
        """
        self.image.fill(pg.Color("black"))
        screen_size = self.screen_rect.size
        triangle_points = [(0,500), (500,500), (250,0)]
        pg.draw.polygon(self.image, pg.Color("red"), triangle_points)
        if screen_size != SCREEN_START_SIZE:
            pg.transform.smoothscale(self.image, screen_size, self.screen)
        else:
            self.screen.blit(self.image, (0,0))

    def main_loop(self):
        """Loop-dee-loop."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
