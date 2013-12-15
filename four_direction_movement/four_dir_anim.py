"""
This script implements a basic sprite that can only move orthogonally.
Orthogonal-only movement is slightly trickier than 8-direction movement
because you can't just create a simple movement vector.
Extra work must be done to make key overlaps execute cleanly.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg


CAPTION = "4-Direction Movement with Animation"
SCREEN_SIZE = (500,500)
BACKGROUND_COLOR = (100,100,100)
COLOR_KEY = (255,0,255)

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class Player(object):
    """This class will represent our user controlled character."""
    def __init__(self,rect,speed,direction=pg.K_RIGHT):
        """Arguments are a rect representing the Player's location and
        dimension, the speed(in pixels/frame) of the Player, and the Player's
        starting direction (given as a key-constant)."""
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.direction = direction
        self.old_direction = None #The Players previous direction every frame.
        self.direction_stack = [] #Held keys in the order they were pressed.
        self.redraw = False #Force redraw if needed.
        self.image = None
        self.frame  = 0
        self.frames = self.get_frames()
        self.animate_timer = 0.0
        self.animate_fps   = 7.0
        self.walkframes = []
        self.walkframe_dict = self.make_frame_dict()
        self.adjust_images()

    def get_frames(self):
        """Get a list of all frames."""
        sheet = SKEL_IMAGE
        indices = [[0,0],[1,0],[2,0],[3,0]]
        return get_images(sheet,indices,self.rect.size)

    def make_frame_dict(self):
        """Create a dictionary of direction keys to frames. We can use
        transform functions to reduce the size of the sprite sheet we need."""
        frames = {pg.K_LEFT : [self.frames[0],self.frames[1]],
                  pg.K_RIGHT: [pg.transform.flip(self.frames[0],True,False),
                               pg.transform.flip(self.frames[1],True,False)],
                  pg.K_DOWN : [self.frames[3],
                               pg.transform.flip(self.frames[3],True,False)],
                  pg.K_UP   : [self.frames[2],
                               pg.transform.flip(self.frames[2],True,False)]}
        return frames

    def adjust_images(self):
        """Update the sprites walkframes as the sprite's direction changes."""
        if self.direction != self.old_direction:
            self.walkframes = self.walkframe_dict[self.direction]
            self.old_direction = self.direction
            self.redraw = True
        self.make_image()

    def make_image(self):
        """Update the sprite's animation as needed."""
        now = pg.time.get_ticks()
        if self.redraw or now-self.animate_timer > 1000/self.animate_fps:
            if self.direction_stack:
                self.frame = (self.frame+1)%len(self.walkframes)
                self.image = self.walkframes[self.frame]
            self.animate_timer = now
        if not self.image:
            self.image = self.walkframes[self.frame]
        self.redraw = False

    def add_direction(self,key):
        """Add a pressed direction key on the direction stack."""
        if key in DIRECT_DICT:
            self.direction_stack.append(key)
            self.direction = self.direction_stack[-1]

    def pop_direction(self,key):
        """Pop a released key from the direction stack."""
        if key in DIRECT_DICT:
            self.direction_stack.remove(key)
            if self.direction_stack:
                self.direction = self.direction_stack[-1]

    def update(self,screen_rect):
        """Updates our player appropriately every frame."""
        self.adjust_images()
        if self.direction_stack:
            direction_vector = DIRECT_DICT[self.direction_stack[-1]]
            self.rect.x += self.speed*direction_vector[0]
            self.rect.y += self.speed*direction_vector[1]
            self.rect.clamp_ip(screen_rect)

    def draw(self,surface):
        """Draws the player to the target surface."""
        surface.blit(self.image,self.rect)


class Control(object):
    """Being controlling is our job."""
    def __init__(self):
        """Initialize standard attributes, standardly."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock  = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,50,50),3)
        self.player.rect.center = self.screen_rect.center

    def event_loop(self):
        """Add/pop directions from player's direction stack as necessary."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.player.add_direction(event.key)
            elif event.type == pg.KEYUP:
                self.player.pop_direction(event.key)

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION,self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Our main game loop; I bet you'd never have guessed."""
        while not self.done:
            self.event_loop()
            self.player.update(self.screen_rect)
            self.screen.fill(BACKGROUND_COLOR)
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


def get_images(sheet,frame_indices,size):
    """Get desired images from a sprite sheet."""
    frames = []
    for cell in frame_indices:
        frame_rect = ((size[0]*cell[0],size[1]*cell[1]),size)
        frames.append(sheet.subsurface(frame_rect))
    return frames


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    SKEL_IMAGE = pg.image.load("skelly.png").convert()
    SKEL_IMAGE.set_colorkey(COLOR_KEY)
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
