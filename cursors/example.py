"""
This script demonstrates the usage of the cursor_from_image function.
There are benefits to using a genuine hardware cursor over an image that
follows the mouse. Real cursors respond much faster as they are not drawn
directly by your program logic. If your framerate drops, the cursor will still
operate unaffected.

There are however two disadvantages; we cannot use color, and we
cannot use a cursor larger than 32x32 pixels (doing so results in
mouse.set_cursor acting as a blit which defeats the point). If you are
wishing to implement these features then an image that follows the mouse is
indeed what you want.

Controls:
    With the grab cursor selected, clicking will switch the cursor between the
    grabbing and non-grabbing versions. The keys 0-9 and q,w,e,r will change
    between all the available cursors.

-Sean McKiernan
"""

import os
import sys
import pygame as pg

from cursor import cursor_from_image


SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (50, 50, 60)
CAPTION = "Custom Mouse Cursors"

#This dictionary helps us change the cursor with keyboard input.
CURSOR_TYPES = {"1" : "default",
                "2" : "cross",
                "3" : "dropper",
                "4" : "knight",
                "5" : "open",
                "6" : "diamond",
                "7" : "broken_x",
                "8" : "tri_left",
                "9" : "tri_right",
                "0" : "arrow",
                "q" : "thick_arrow",
                "w" : "sizer_xy",
                "e" : "sizer_x",
                "r" : "sizer_y"}


class Control(object):
    """Not a hair out of place."""
    def __init__(self):
        """
        Prepare the essentials; create our dictionary of cursors; and set
        the initial cursor as desired.
        """
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
        pg.display.set_caption(CAPTION)
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.done = False
        self.keys = pg.key.get_pressed()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.cursor_dict = self.make_cursor_dict()
        self.cursor = self.change_cursor("open")

    def make_cursor_dict(self):
        """
        Create a dictionary that holds cursor data for all of our cursors,
        including the default cursor.
        """
        cursor_image = pg.image.load("cursor_images.png").convert()
        thick = pg.cursors.compile(pg.cursors.thickarrow_strings)
        sizer_x = pg.cursors.compile(pg.cursors.sizer_x_strings)
        sizer_y = pg.cursors.compile(pg.cursors.sizer_y_strings)
        sizer_xy = pg.cursors.compile(pg.cursors.sizer_xy_strings)
        cursors = {
            "cross"    : cursor_from_image(cursor_image, 16, (8,8)),
            "dropper"  : cursor_from_image(cursor_image, 16, (0,15), (16,0)),
            "open"     : cursor_from_image(cursor_image, 24, (12,12), (32,0)),
            "closed"   : cursor_from_image(cursor_image, 24, (12,12), (32,24)),
            "knight"   : cursor_from_image(cursor_image, 32, (16,16), (0,16)),
            "diamond"  : pg.cursors.diamond,
            "broken_x" : pg.cursors.broken_x,
            "tri_left" : pg.cursors.tri_left,
            "tri_right": pg.cursors.tri_right,
            "arrow"    : pg.cursors.arrow,
            "thick_arrow" : ((24,24), (0,0), thick[0], thick[1]),
            "sizer_xy" : ((24,16), (6,6), sizer_xy[0], sizer_xy[1]),
            "sizer_x" : ((24,16), (9,5), sizer_x[0], sizer_x[1]),
            "sizer_y" : ((16,24), (5,9), sizer_y[0], sizer_y[1]),
            "default"  : pg.mouse.get_cursor()}
        return cursors

    def change_cursor(self, name):
        """
        Set the cursor to the value corresponding to name in the
        cursor_dict. Return the cursor_name argument as a convenience.
        """
        pg.mouse.set_cursor(*self.cursor_dict[name])
        template = "{} - Current cursor: {}"
        pg.display.set_caption(template.format(CAPTION, name.capitalize()))
        return name

    def event_loop(self):
        """
        Change between open and closed hands if using the grab cursor.
        Change to other cursors with the keys 0-9 and q,w,e,r.
        """
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.cursor == "open":
                    self.cursor = self.change_cursor("closed")
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if self.cursor == "closed":
                    self.cursor = self.change_cursor("open")
            elif event.type == pg.KEYDOWN:
                key = event.unicode
                if key in CURSOR_TYPES:
                    self.cursor = self.change_cursor(CURSOR_TYPES[key])

    def main_loop(self):
        """The bare minimum for a functioning main loop."""
        while not self.done:
            self.event_loop()
            self.screen.fill(BACKGROUND_COLOR)
            pg.display.update()
            self.clock.tick(self.fps)


def main():
    """Off we go."""
    Control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
