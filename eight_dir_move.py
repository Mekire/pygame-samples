"""
This script implements a basic sprite that can move in all 8 directions.
-Written by Sean J. McKiernan 'Mekire'
"""
import os
import sys
import pygame as pg

#This global constant serves as a very useful convenience for me.
DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
              pg.K_RIGHT : ( 1, 0),
              pg.K_UP    : ( 0,-1),
              pg.K_DOWN  : ( 0, 1)}


class Player(object):
    """This class will represent our user controlled character."""
    def __init__(self,rect,speed):
        """Arguments are the players rect (x,y,width,height), and the
        speed (in pixels/frame)"""
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.image = self.make_image()

    def make_image(self):
        """Creates our hero (a red circle/ellipse with a black outline)
        If you want to use an image this is the place."""
        image = pg.Surface((self.rect.size)).convert_alpha()
        image.fill((0,0,0,0))
        pg.draw.ellipse(image,(0,0,0),(1,1,self.rect.size[0]-2,self.rect.size[1]-2))
        pg.draw.ellipse(image,(255,0,0),(6,6,self.rect.size[0]-12,self.rect.size[1]-12))
        return image

    def update(self,surface,keys):
        """Updates our player appropriately every frame."""
        for key in DIRECT_DICT:
            if keys[key]:
                self.rect.x += DIRECT_DICT[key][0]*self.speed
                self.rect.y += DIRECT_DICT[key][1]*self.speed
        self.rect.clamp_ip(surface.get_rect()) #Keep player on screen.
        surface.blit(self.image,self.rect)


class Control(object):
    """Keep things under control."""
    def __init__(self):
        """Initializing in the init; how novel."""
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("Move me with the Arrow Keys.")
        self.screen = pg.display.set_mode((500,500))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,100,100),5)  #Create an instance of Player.
        self.player.rect.center = self.screen_rect.center

    def event_loop(self):
        """One event loop.  Never cut your game off from the event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def main_loop(self):
        """One game loop.  Simple and clean."""
        while not self.done:
            self.event_loop()
            self.screen.fill(-1) #Cute way to fill with white.
            self.player.update(self.screen,self.keys)
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
