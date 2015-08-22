#! /usr/bin/env python

"""
This script implements a basic sprite that can only move orthogonally.
Orthogonal-only movement is slightly trickier than 8-direction movement
because you can't just create a simple movement vector.
Extra work must be done to make key overlaps execute cleanly.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import itertools

import pygame as pg


CAPTION = "4-Direction Movement with Animation"
SCREEN_SIZE = (500, 500)

BACKGROUND_COLOR = pg.Color("slategray")
COLOR_KEY = pg.Color("magenta")

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class Player(object):
    """
    This class will represent our user controlled character.
    """
    SIZE = (50, 50)
    
    def __init__(self, pos, speed, facing=pg.K_RIGHT):
        """
        The pos argument is a tuple for the center of the player (x,y);
        speed is in pixels/frame; and facing is the Player's starting
        direction (given as a key-constant).
        """
        self.speed = speed
        self.direction = facing
        self.old_direction = None # Player's previous direction every frame.
        self.direction_stack = [] # Held keys in the order they were pressed.
        self.redraw = True # Forces redraw if needed.
        self.animate_timer = 0.0
        self.animate_fps = 7
        self.image = None
        self.walkframes = None
        self.walkframe_dict = self.make_frame_dict()
        self.adjust_images()
        self.rect = self.image.get_rect(center=pos)

    def make_frame_dict(self):
        """
        Create a dictionary of direction keys to frame cycles. We can use
        transform functions to reduce the size of the sprite sheet needed.
        """
        frames = split_sheet(SKEL_IMAGE, Player.SIZE, 4, 1)[0]
        flips = [pg.transform.flip(frame, True, False) for frame in frames]
        walk_cycles = {pg.K_LEFT : itertools.cycle(frames[0:2]),
                       pg.K_RIGHT: itertools.cycle(flips[0:2]),
                       pg.K_DOWN : itertools.cycle([frames[3], flips[3]]),
                       pg.K_UP   : itertools.cycle([frames[2], flips[2]])}
        return walk_cycles

    def adjust_images(self, now=0):
        """
        Update the sprite's walkframes as the sprite's direction changes.
        """
        if self.direction != self.old_direction:
            self.walkframes = self.walkframe_dict[self.direction]
            self.old_direction = self.direction
            self.redraw = True
        self.make_image(now)

    def make_image(self, now):
        """
        Update the sprite's animation as needed.
        """
        elapsed = now-self.animate_timer > 1000.0/self.animate_fps
        if self.redraw or (self.direction_stack and elapsed):
            self.image = next(self.walkframes)
            self.animate_timer = now
        self.redraw = False

    def add_direction(self, key):
        """
        Add a pressed direction key on the direction stack.
        """
        if key in DIRECT_DICT:
            if key in self.direction_stack:
                self.direction_stack.remove(key)
            self.direction_stack.append(key)
            self.direction = self.direction_stack[-1]

    def pop_direction(self, key):
        """
        Pop a released key from the direction stack.
        """
        if key in DIRECT_DICT:
            if key in self.direction_stack:
                self.direction_stack.remove(key)
            if self.direction_stack:
                self.direction = self.direction_stack[-1]

    def get_event(self, event):
        """
        Handle events pertaining to player control.
        """
        if event.type == pg.KEYDOWN:
            self.add_direction(event.key)
        elif event.type == pg.KEYUP:
            self.pop_direction(event.key)

    def update(self, now, screen_rect):
        """
        Updates our player appropriately every frame.
        """
        self.adjust_images(now)
        if self.direction_stack:
            direction_vector = DIRECT_DICT[self.direction]
            self.rect.x += self.speed*direction_vector[0]
            self.rect.y += self.speed*direction_vector[1]
            self.rect.clamp_ip(screen_rect)

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
        self.clock  = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player(self.screen_rect.center, 3)

    def event_loop(self):
        """
        Pass events on to the player.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type in (pg.KEYUP, pg.KEYDOWN):
                self.keys = pg.key.get_pressed() 
            self.player.get_event(event)

    def display_fps(self):
        """
        Show the program's FPS in the window handle.
        """
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def update(self):
        """
        Update the player.
        The current time is passed for purposes of animation.
        """
        now = pg.time.get_ticks()
        self.player.update(now, self.screen_rect)

    def render(self):
        """
        Perform all necessary drawing and update the screen.
        """
        self.screen.fill(BACKGROUND_COLOR)
        self.player.draw(self.screen)
        pg.display.update()
        
    def main_loop(self):
        """
        Our main game loop; I bet you'd never have guessed.
        """
        while not self.done:
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(self.fps)
            self.display_fps()


def split_sheet(sheet, size, columns, rows):
    """
    Divide a loaded sprite sheet into subsurfaces.
    
    The argument size is the width and height of each frame (w,h)
    columns and rows are the integer number of cells horizontally and
    vertically.
    """
    subsurfaces = []
    for y in range(rows):
        row = []
        for x in range(columns): 
            rect = pg.Rect((x*size[0], y*size[1]), size)
            row.append(sheet.subsurface(rect))
        subsurfaces.append(row)
    return subsurfaces


def main():
    """
    Prepare our environment, create a display, and start the program.
    """
    global SKEL_IMAGE
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    SKEL_IMAGE = pg.image.load("skelly.png").convert()
    SKEL_IMAGE.set_colorkey(COLOR_KEY)
    App().main_loop()
    pg.quit()
    sys.exit()
    

if __name__ == "__main__":
    main()
