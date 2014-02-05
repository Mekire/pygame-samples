"""
This is an example showing movement in 8-directions; but using image frames
only in the four orthogonal directions. I am still using the direction stack
even though it is a bit complex so that the player's frame matches the
key held; not just the last key pressed. This example also uses a timestep for
updating at a constant framerate, and has accurate 45 degree movement speed.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import math
import random
import pygame as pg


CAPTION = "8-Direction Movement w/ 4-Direction Animation"
SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (40, 40, 40)
TRANSPARENT = (0, 0, 0, 0)
COLOR_KEY = (255, 0, 255)

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}

#X and Y Component magnitude when moving at 45 degree angles
ANGLE_UNIT_SPEED = math.sqrt(2)/2


class Player(pg.sprite.Sprite):
    """
    This time we inherit from pygame.sprite.Sprite.  We are going to take
    advantage of the sprite.Group collission functions (though as usual, doing
    all this without using pygame.sprite is not much more complicated).
    """
    def __init__(self, rect, speed, direction=pg.K_RIGHT):
        """
        Arguments are a rect representing the Player's location and
        dimension, the speed(in pixels/frame) of the Player, and the Player's
        starting direction (given as a key-constant).
        """
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.remainder = [0, 0]  #Adjust rect in integers; save remainders.
        self.mask = self.make_mask()
        self.speed = speed  #Pixels per second; not pixels per frame.
        self.direction = direction
        self.old_direction = None  #The Players previous direction every frame.
        self.direction_stack = []  #Held keys in the order they were pressed.
        self.redraw = False  #Force redraw if needed.
        self.image = None
        self.frame  = 0
        self.frames = self.get_frames()
        self.animate_timer = 0.0
        self.animate_fps = 7.0
        self.walkframes = []
        self.walkframe_dict = self.make_frame_dict()
        self.adjust_images()

    def make_mask(self):
        """
        Create a collision mask slightly smaller than our sprite so that
        the sprite's head can overlap obstacles; adding depth.
        """
        mask_surface = pg.Surface(self.rect.size).convert_alpha()
        mask_surface.fill(TRANSPARENT)
        mask_surface.fill(pg.Color("white"), (10,20,30,30))
        mask = pg.mask.from_surface(mask_surface)
        return mask

    def get_frames(self):
        """Get a list of all frames."""
        sheet = SKEL_IMAGE
        indices = [[0,0], [1,0], [2,0], [3,0]]
        return get_images(sheet, indices, self.rect.size)

    def make_frame_dict(self):
        """
        Create a dictionary of direction keys to frames. We can use
        transform functions to reduce the size of the sprite sheet needed.
        """
        frames = {pg.K_LEFT : [self.frames[0], self.frames[1]],
                  pg.K_RIGHT: [pg.transform.flip(self.frames[0], True, False),
                               pg.transform.flip(self.frames[1], True, False)],
                  pg.K_DOWN : [self.frames[3],
                               pg.transform.flip(self.frames[3], True, False)],
                  pg.K_UP   : [self.frames[2],
                               pg.transform.flip(self.frames[2], True, False)]}
        return frames

    def adjust_images(self):
        """Update the sprite's walkframes as the sprite's direction changes."""
        if self.direction != self.old_direction:
            self.walkframes = self.walkframe_dict[self.direction]
            self.old_direction = self.direction
            self.redraw = True
        self.make_image()

    def make_image(self):
        """Update the sprite's animation as needed."""
        now = pg.time.get_ticks()
        if self.redraw or now-self.animate_timer > 1000/self.animate_fps:
            self.frame = (self.frame+1)%len(self.walkframes)
            self.image = self.walkframes[self.frame]
            self.animate_timer = now
        if not self.image:
            self.image = self.walkframes[self.frame]
        self.redraw = False

    def add_direction(self, key):
        """Add a pressed direction key on the direction stack."""
        if key in DIRECT_DICT:
            if key in self.direction_stack:
                self.direction_stack.remove(key)
            self.direction_stack.append(key)
            self.direction = self.direction_stack[-1]

    def pop_direction(self, key):
        """Pop a released key from the direction stack."""
        if key in DIRECT_DICT:
            if key in self.direction_stack:
                self.direction_stack.remove(key)
            if self.direction_stack:
                self.direction = self.direction_stack[-1]

    def update(self, obstacles, dt):
        """Adjust the image and move as needed."""
        vector = [0, 0]
        for key in self.direction_stack:
            vector[0] += DIRECT_DICT[key][0]
            vector[1] += DIRECT_DICT[key][1]
        factor = (ANGLE_UNIT_SPEED if all(vector) else 1)
        frame_speed = self.speed*factor*dt
        self.remainder[0] += vector[0]*frame_speed
        self.remainder[1] += vector[1]*frame_speed
        vector[0], self.remainder[0] = divfmod(self.remainder[0], 1)
        vector[1], self.remainder[1] = divfmod(self.remainder[1], 1)
        if vector != [0, 0]:
            self.adjust_images()
            self.movement(obstacles, vector[0], 0)
            self.movement(obstacles, vector[1], 1)

    def movement(self, obstacles, offset, i):
        """Move player and then check for collisions; adjust as necessary."""
        self.rect[i] += offset
        collisions = pg.sprite.spritecollide(self, obstacles, False)
        callback = pg.sprite.collide_mask
        while pg.sprite.spritecollideany(self, collisions, callback):
            self.rect[i] += (1 if offset<0 else -1)
            self.remainder[i] = 0

    def draw(self, surface):
        """Draw method seperated out from update."""
        surface.blit(self.image, self.rect)


class Block(pg.sprite.Sprite):
    """Something to run head-first into."""
    def __init__(self, location):
        """The location argument is where I will be located."""
        pg.sprite.Sprite.__init__(self)
        self.image = self.make_image()
        self.rect = self.image.get_rect(topleft=location)
        self.mask = pg.mask.from_surface(self.image)

    def make_image(self):
        """Let's not forget aesthetics."""
        image = pg.Surface((50,50)).convert_alpha()
        image.fill([random.randint(0, 255) for _ in range(3)])
        image.blit(SHADE_MASK, (0,0))
        return image


class Control(object):
    """Being controlling is our job."""
    def __init__(self):
        """Initialize standard attributes standardly."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,50,50), 190)
        self.player.rect.center = self.screen_rect.center
        self.obstacles = self.make_obstacles()

    def make_obstacles(self):
        """Prepare some obstacles for our player to collide with."""
        obstacles = [Block((400,400)), Block((300,270)), Block((150,170))]
        for i in range(9):
            obstacles.append(Block((i*50,0)))
            obstacles.append(Block((450,50*i)))
            obstacles.append(Block((50+i*50,450)))
            obstacles.append(Block((0,50+50*i)))
        return pg.sprite.Group(obstacles)

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

    def draw(self):
        """Draw all elements to the display surface."""
        self.screen.fill(BACKGROUND_COLOR)
        self.obstacles.draw(self.screen)
        self.player.draw(self.screen)

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Our main game loop; I bet you'd never have guessed."""
        delta = self.clock.tick(self.fps)/1000.0
        while not self.done:
            self.event_loop()
            self.player.update(self.obstacles, delta)
            self.draw()
            pg.display.update()
            delta = self.clock.tick(self.fps)/1000.0
            self.display_fps()


def get_images(sheet, frame_indices, size):
    """Get desired images from a sprite sheet."""
    frames = []
    for cell in frame_indices:
        frame_rect = ((size[0]*cell[0],size[1]*cell[1]), size)
        frames.append(sheet.subsurface(frame_rect))
    return frames


def divfmod(x, y):
    """Identical to the builtin divmod but using math.fmod to retain signs."""
    fmod = math.fmod(x, y)
    div = (x-fmod)//y
    return div, fmod


def main():
    """Initialize, load our images, and run the program."""
    global SKEL_IMAGE, SHADE_MASK
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    SKEL_IMAGE = pg.image.load("skelly.png").convert()
    SKEL_IMAGE.set_colorkey(COLOR_KEY)
    SHADE_MASK = pg.image.load("shader.png").convert_alpha()
    Control().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
