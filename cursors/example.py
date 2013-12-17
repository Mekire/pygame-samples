import os
import sys
import pygame as pg

from cursor import cursor_from_image


SCREEN_SIZE = (500,500)
BACKGROUND_COLOR = (50,50,60)

CURSOR_TYPES = {"1" : "default",
                "2" : "cross",
                "3" : "dropper",
                "4" : "knight",
                "5" : "open"}


class Control(object):
    def __init__(self):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.done = False
        self.keys = pg.key.get_pressed()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.cursor_dict = self.make_cursor_dict()
        self.cursor = self.change_cursor("open")

    def make_cursor_dict(self):
        cursor_image = pg.image.load("cursor_images.png").convert()
        cursors = {"cross" : cursor_from_image(cursor_image,16,(8,8)),
                  "dropper" : cursor_from_image(cursor_image,16,(0,15),(16,0)),
                  "open" : cursor_from_image(cursor_image,24,(12,12),(32,0)),
                  "closed" : cursor_from_image(cursor_image,24,(12,12),(32,24)),
                  "knight" : cursor_from_image(cursor_image,32,(16,16),(0,16)),
                  "default" : pg.mouse.get_cursor()}
        return cursors

    def change_cursor(self,cursor_name):
        pg.mouse.set_cursor(*self.cursor_dict[cursor_name])
        return cursor_name

    def event_loop(self):
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
        while not self.done:
            self.event_loop()
            self.screen.fill(BACKGROUND_COLOR)
            pg.display.update()
            self.clock.tick(self.fps)


def main():
    Control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
