"""
This script is identical to the four_dir_anim.py example except that some
simple obstacles have been added to demonstrate basic collission detection.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import random
import pygame as pg


CAPTION = "4-Direction Movement with Obstacles"
SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (40, 40, 40)
COLOR_KEY = (255, 0, 255)

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
    def __init__(self, rect, speed, direction=pg.K_RIGHT):
        """
        Arguments are a rect representing the Player's location and
        dimension, the speed(in pixels/frame) of the Player, and the Player's
        starting direction (given as a key-constant).
        """
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.speed = speed
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

    def get_frames(self):
        """Get a list of all frames."""
        sheet = SKEL_IMAGE
        indices = [[0,0], [1,0], [2,0], [3,0]]
        return get_images(sheet, indices, self.rect.size)

    def make_frame_dict(self):
        """
        Create a dictionary of direction keys to frames. We can use
        transform functions to reduce the size of the sprite sheet we need.
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
            if self.direction_stack:
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

    def update(self, obstacles):
        """
        We have added some logic here for collission detection against the
        sprite.Group, obstacles.
        """
        self.adjust_images()
        if self.direction_stack:
            self.movement(obstacles, 0)
            self.movement(obstacles, 1)

    def movement(self, obstacles, i):
        """Move player and then check for collisions; adjust as necessary."""
        direction_vector = DIRECT_DICT[self.direction]
        self.rect[i] += self.speed*direction_vector[i]
        collisions = pg.sprite.spritecollide(self, obstacles, False)
        while collisions:
            collision = collisions.pop()
            self.adjust_on_collision(self.rect, collision, i)

    def adjust_on_collision(self, rect_to_adjust, collide, i):
        """Adjust player's position if colliding with a solid block."""
        if rect_to_adjust[i] < collide.rect[i]:
            rect_to_adjust[i] = collide.rect[i]-rect_to_adjust.size[i]
        else:
            rect_to_adjust[i] = collide.rect[i]+collide.rect.size[i]

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

    def make_image(self):
        """Let's not forget aesthetics."""
        image = pg.Surface((50,50)).convert_alpha()
        image.fill([random.randint(0, 255) for _ in range(3)])
        image.blit(SHADE_MASK, (0,0))
        return image


class Control(object):
    """Being controlling is our job."""
    def __init__(self):
        """Initialize standard attributes, standardly."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = Player((0,0,50,50), 3)
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

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Our main game loop; I bet you'd never have guessed."""
        while not self.done:
            self.event_loop()
            self.player.update(self.obstacles)
            self.screen.fill(BACKGROUND_COLOR)
            self.obstacles.draw(self.screen)
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


def get_images(sheet, frame_indices, size):
    """Get desired images from a sprite sheet."""
    frames = []
    for cell in frame_indices:
        frame_rect = ((size[0]*cell[0],size[1]*cell[1]), size)
        frames.append(sheet.subsurface(frame_rect))
    return frames


if __name__ == "__main__":
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
