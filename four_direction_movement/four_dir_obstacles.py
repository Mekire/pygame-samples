#! /usr/bin/env python

"""
This script is identical to the four_dir_anim.py example except that some
simple obstacles have been added to demonstrate basic collission detection.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import random
import itertools

import pygame as pg


CAPTION = "4-Direction Movement with Obstacles"
SCREEN_SIZE = (500, 500)

BACKGROUND_COLOR = pg.Color("darkslategray")
COLOR_KEY = pg.Color("magenta")

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class Player(pg.sprite.Sprite):
    """
    This time we inherit from pygame.sprite.Sprite. We are going to take
    advantage of the sprite.Group collission functions (though as usual,
    doing all this without using pygame.sprite is not much more complicated).
    """
    SIZE = (50, 50)
    
    def __init__(self, pos, speed, facing=pg.K_RIGHT, *groups):
        """
        The pos argument is a tuple for the center of the player (x,y);
        speed is in pixels/frame; and facing is the Player's starting
        direction (given as a key-constant).
        """
        super(Player, self).__init__(*groups)
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

    def update(self, now, obstacles):
        """
        We have added some logic here for collission detection against the
        sprite.Group, obstacles.
        """
        self.adjust_images(now)
        if self.direction_stack:
            self.movement(obstacles, 0)
            self.movement(obstacles, 1)

    def movement(self, obstacles, i):
        """
        Move player and then check for collisions; adjust as necessary.
        """
        direction_vector = DIRECT_DICT[self.direction]
        self.rect[i] += self.speed*direction_vector[i]
        collision = pg.sprite.spritecollideany(self, obstacles)
        while collision:
            self.adjust_on_collision(collision, i)
            collision = pg.sprite.spritecollideany(self, obstacles)

    def adjust_on_collision(self, collide, i):
        """
        Adjust player's position if colliding with a solid block.
        """
        if self.rect[i] < collide.rect[i]:
            self.rect[i] = collide.rect[i]-self.rect.size[i]
        else:
            self.rect[i] = collide.rect[i]+collide.rect.size[i]

    def draw(self, surface):
        """
        Draw sprite to surface (not used if using group draw functions).
        """
        surface.blit(self.image, self.rect)


class Block(pg.sprite.Sprite):
    """
    Something to run head-first into.
    """
    def __init__(self, pos, *groups):
        """
        The pos argument is where the topleft will be (x, y).
        """
        super(Block, self).__init__(*groups)
        self.image = self.make_image()
        self.rect = self.image.get_rect(topleft=pos)

    def make_image(self):
        """
        Let's not forget aesthetics.
        """
        fill_color = [random.randint(0, 255) for _ in range(3)]
        image = pg.Surface((50,50)).convert_alpha()
        image.fill(fill_color)
        image.blit(SHADE_MASK, (0,0))
        return image


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
        self.blocks = self.make_blocks()
        self.all_sprites = pg.sprite.Group(self.player, self.blocks)

    def make_blocks(self):
        """
        Prepare some obstacles for our player to collide with.
        """
        blocks = pg.sprite.Group()
        for pos in [(400,400), (300,270), (150,170)]:
            Block(pos, blocks)
        for i in range(9):
            Block((i*50,0), blocks)
            Block((450,50*i), blocks)
            Block((50+i*50,450), blocks)
            Block((0,50+50*i), blocks)
        return blocks

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
        self.player.update(now, self.blocks)

    def render(self):
        """
        Perform all necessary drawing and update the screen.
        """
        self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)
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
    global SKEL_IMAGE, SHADE_MASK
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    SKEL_IMAGE = pg.image.load("skelly.png").convert()
    SKEL_IMAGE.set_colorkey(COLOR_KEY)
    SHADE_MASK = pg.image.load("shader.png").convert_alpha()
    App().main_loop()
    pg.quit()
    sys.exit()
    

if __name__ == "__main__":
    main()
