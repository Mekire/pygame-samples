"""
This script is identical to the four_dir_anim.py example except that some simple
obstacles have been added to demonstrate basic collission detection.

Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg
from random import randint


DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class Player(pg.sprite.Sprite):
    """This time we inherit from pygame.sprite.Sprite.  We are going to take
    advantage of the sprite.Group collission functions (though as usual, doing
    all this without using pygame.sprite is not much more complicated)."""
    def __init__(self,rect,speed,direction=pg.K_RIGHT):
        """Arguments are a rect representing the Player's location and
        dimension, the speed(in pixels/frame) of the Player, and the Player's
        starting direction (given as a key-constant)."""
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.direction = direction
        self.old_direction = None #The Players previous direction every frame.
        self.direction_stack = [] #Held keys in the order they were pressed.
        self.redraw = False #Force redraw if needed.
        self.image = None
        self.frame_inds = [[0,0],[1,0],[2,0],[3,0]]
        self.frame  = 0
        self.frames = self.get_images(SKEL_IMAGE,self.frame_inds,self.rect.size)
        self.animate_timer = 0.0
        self.animate_fps   = 7.0
        self.walkframes = []
        self.walkframe_dict = self.make_frame_dict()
        self.adjust_images()

    def get_images(self,sheet,frame_indexes,size):
        """Get the desired images from the sprite sheet."""
        frames = []
        for cell in frame_indexes:
            frame_rect = ((size[0]*cell[0],size[1]*cell[1]),size)
            frames.append(sheet.subsurface(frame_rect))
        return frames

    def make_frame_dict(self):
        """Create a dictionary of direction keys to frames. We can use transform
        functions to reduce the size of the sprite sheet we need."""
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
        time_now = pg.time.get_ticks()
        if self.redraw or time_now-self.animate_timer > 1000/self.animate_fps:
            if self.direction_stack:
                self.frame = (self.frame+1) % len(self.walkframes)
                self.image = self.walkframes[self.frame]
            self.animate_timer = time_now
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

    def update(self,obstacles):
        """We have added some logic here for collission detection against the
        sprite.Group, obstacles."""
        self.adjust_images()
        if self.direction_stack:
            old_rect = self.rect.copy()
            self.rect.x += self.speed*DIRECT_DICT[self.direction_stack[-1]][0]
            self.rect.y += self.speed*DIRECT_DICT[self.direction_stack[-1]][1]
            if pg.sprite.spritecollide(self,obstacles,False):
                self.rect = old_rect

    def draw(self,surface):
        """Draw method seperated out from update."""
        surface.blit(self.image,self.rect)


class Block(pg.sprite.Sprite):
    """Something to run head-first into."""
    def __init__(self,location):
        """The location argument is where I will be located."""
        pg.sprite.Sprite.__init__(self)
        self.make_image()
        self.rect = pg.Rect(location,(50,50))

    def make_image(self):
        """Let's not forget aesthetics."""
        self.image = pg.Surface((50,50)).convert_alpha()
        self.image.fill([randint(0,255) for i in range(3)])
        self.image.blit(SHADE_MASK,(0,0))


class Control(object):
    """Being controlling is our job."""
    def __init__(self):
        """Initialize standard attributes standardly."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock  = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,50,50),3)
        self.player.rect.center = self.screen_rect.center
        self.obstacles = pg.sprite.Group(self.make_obstacles())

    def make_obstacles(self):
        """Prepare some obstacles for our player to collide with."""
        obstacles = [Block((400,400)),Block((300,270)),Block((150,170))]
        for i in range(9):
            obstacles.append(Block((i*50,0)))
            obstacles.append(Block((450,50*i)))
            obstacles.append(Block((50+i*50,450)))
            obstacles.append(Block((0,50+50*i)))
        return obstacles

    def event_loop(self):
        """Our event loop. Add and pop directions from the player's direction
        stack as necessary."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.player.add_direction(event.key)
            elif event.type == pg.KEYUP:
                self.player.pop_direction(event.key)

    def main_loop(self):
        """Our main game loop; I bet you'd never have guessed."""
        while not self.done:
            self.event_loop()
            self.screen.fill(0)
            self.player.update(self.obstacles)
            self.obstacles.draw(self.screen)
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((500,500))
    SKEL_IMAGE = pg.image.load("skelly.png").convert()
    SKEL_IMAGE.set_colorkey((255,0,255))
    SHADE_MASK = pg.image.load("shader.png").convert_alpha()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
