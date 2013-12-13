"""
This script implements a basic sprite that can move in all 8 directions.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


SCREEN_SIZE = (500,500)

WHITE = (255,255,255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

#This global constant serves as a very useful convenience for me.
DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class Player(object):
    """This class will represent our user controlled character."""
    def __init__(self,rect,speed):
        """Arguments are the player's rect (x,y,width,height), and their
        speed (in pixels/frame)"""
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.image = self.make_image()

    def make_image(self):
        """Creates our hero (a red circle/ellipse with a black outline)."""
        image = pg.Surface(self.rect.size).convert_alpha()
        image.fill(TRANSPARENT)
        image_rect = image.get_rect()
        pg.draw.ellipse(image,BLACK,image_rect)
        pg.draw.ellipse(image,RED,image_rect.inflate(-12,-12))
        return image

    def update(self,screen_rect,keys):
        """Updates our player appropriately every frame."""
        for key in DIRECT_DICT:
            if keys[key]:
                self.rect.x += DIRECT_DICT[key][0]*self.speed
                self.rect.y += DIRECT_DICT[key][1]*self.speed
        self.rect.clamp_ip(screen_rect) #Keep player on screen.

    def draw(self,surface):
        """Blit image to the target surface."""
        surface.blit(self.image,self.rect)


class Control(object):
    """Keep things under control."""
    def __init__(self):
        """Initializing in the init; how novel."""
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("Move me with the Arrow Keys.")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,100,100),5)  #Create an instance of Player.
        self.player.rect.center = self.screen_rect.center

    def event_loop(self):
        """One event loop. Never cut your game off from the event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def main_loop(self):
        """One game loop. Simple and clean."""
        while not self.done:
            self.event_loop()
            self.player.update(self.screen_rect,self.keys)
            self.screen.fill(WHITE)
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
