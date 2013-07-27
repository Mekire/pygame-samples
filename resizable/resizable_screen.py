import sys,os
import pygame as pg


START_SIZE = (500,500)


class Control(object):
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        pg.init()
        self.screen = pg.display.set_mode(START_SIZE,pg.RESIZABLE)
        self.current_resolution = START_SIZE
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.VIDEORESIZE:
                self.current_resolution = event.size
                self.screen = pg.display.set_mode(event.size,pg.RESIZABLE)

    def update(self):
        image = pg.Surface(START_SIZE).convert()
        pg.draw.polygon(image,(255,0,0),[(0,500),(500,500),(250,0)])
        if self.current_resolution != START_SIZE:
            image = pg.transform.smoothscale(image, self.current_resolution)
        self.screen.blit(image,(0,0))

    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    run_it = Control()
    run_it.main()
    pg.quit();sys.exit()