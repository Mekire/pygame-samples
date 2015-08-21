#! /usr/bin/env python

"""
Script is identical to eight_dir_move with an adjustment so that the player
moves at the correct speed when travelling at an angle. The script is also
changed to use a variable time step to update the player.
This means that speed is now in pixels per second, rather than pixels per
frame. The advantage of this is that the game will always update at the same
speed, regardless of any frame loss.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import math

import pygame as pg


CAPTION = "Move me with the Arrow Keys"
SCREEN_SIZE = (500, 500)

TRANSPARENT = (0, 0, 0, 0)

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}

# X and Y Component magnitude when moving at 45 degree angles
ANGLE_UNIT_SPEED = math.sqrt(2)/2


class Player(object):
    """
    This class will represent our user controlled character.
    """
    SIZE = (100, 100)
    
    def __init__(self, pos, speed):
        """
        The pos argument is a tuple for the center of the player (x,y);
        speed is given in pixels/second.
        """
        self.rect = pg.Rect((0,0), Player.SIZE)
        self.rect.center = pos
        self.true_pos = list(self.rect.center)
        self.speed = speed
        self.image = self.make_image()

    def make_image(self):
        """
        Creates our hero (a red circle/ellipse with a black outline).
        """
        image = pg.Surface(self.rect.size).convert_alpha()
        image.fill(TRANSPARENT)
        image_rect = image.get_rect()
        pg.draw.ellipse(image, pg.Color("black"), image_rect)
        pg.draw.ellipse(image, pg.Color("red"), image_rect.inflate(-12, -12))
        return image

    def update(self, screen_rect, keys, dt):
        """
        Updates our player appropriately every frame.
        """
        vector = [0, 0]
        for key in DIRECT_DICT:
            if keys[key]:
                vector[0] += DIRECT_DICT[key][0]
                vector[1] += DIRECT_DICT[key][1]
        factor = (ANGLE_UNIT_SPEED if all(vector) else 1)
        frame_speed = self.speed*factor*dt
        self.true_pos[0] += vector[0]*frame_speed
        self.true_pos[1] += vector[1]*frame_speed
        self.rect.center = self.true_pos
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.true_pos = list(self.rect.center)

    def draw(self, surface):
        """
        Draws the player to the target surface.
        """
        surface.blit(self.image, self.rect)


class App(object):
    """
    A class to manage our event, game loop, and overall program flow.
    """
    def __init__(self):
        """
        Get a reference to the display surface; set up required attributes;
        and create a Player instance.
        """
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player(self.screen_rect.center, 190)

    def event_loop(self):
        """
        One event loop. Never cut your game off from the event loop.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type in (pg.KEYUP, pg.KEYDOWN):
                self.keys = pg.key.get_pressed() 

    def render(self):
        """
        Perform all necessary drawing and update the screen.
        """
        self.screen.fill(pg.Color("white"))
        self.player.draw(self.screen)
        pg.display.update()
        
    def main_loop(self):
        """
        One game loop. Simple and clean.
        """
        self.clock.tick(self.fps)/1000.0
        dt = 0.0
        while not self.done:
            self.event_loop()
            self.player.update(self.screen_rect, self.keys, dt)
            self.render()
            dt = self.clock.tick(self.fps)/1000.0


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    App().main_loop()
    pg.quit()
    sys.exit()
    

if __name__ == "__main__":
    main()
