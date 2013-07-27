import sys,os
import pygame as pg

START_SIZE = (500,500)

class Control(object):
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        pg.init()
        self.screen = pg.display.set_mode(START_SIZE,pg.RESIZABLE)
        self.screen_rect = self.screen.get_rect()
        self.image = pg.Surface(START_SIZE).convert()
        self.image_rect = self.image.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(event.size,pg.RESIZABLE)
                self.screen_rect = self.screen.get_rect()

    def update(self):
        self.image.fill(0)
        pg.draw.polygon(self.image,(255,0,0),[(0,500),(500,500),(250,0)])
        if self.screen_rect.size != START_SIZE:
            fit_to_rect = self.image_rect.fit(self.screen_rect)
            fit_to_rect.center = self.screen_rect.center
            scaled = pg.transform.smoothscale(self.image,fit_to_rect.size)
            self.screen.blit(scaled,fit_to_rect)
        else:
            self.screen.blit(self.image,(0,0))

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