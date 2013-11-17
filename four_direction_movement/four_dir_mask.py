"""
Filling a request for showing the direction of collision.  This method uses
masks (pixel perfect) collision methods, and is a little (possibly over)
complicated.  It finds the direction of a collision by calculating a finite
difference between colliding mask elements in both directions.  This technique
can be extended to find the actually angle of collision (normal vector)
between two simple colliding shapes.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import random
import pygame as pg


CAPTION = "Find Direction of Collision w/ Masks"

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}

OPPOSITE_DICT = {pg.K_LEFT  : "right",
                 pg.K_RIGHT : "left",
                 pg.K_UP    : "bottom",
                 pg.K_DOWN  : "top"}


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
        self.mask = self.make_mask()
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

    def make_mask(self):
        """Create a collision mask slightly smaller than our sprite so that
        the sprites head can overlap obstacles, adding depth."""
        mask_surface = pg.Surface(self.rect.size).convert_alpha()
        mask_surface.fill((0,0,0,0))
        mask_surface.fill(-1,(10,20,30,30))
        mask = pg.mask.from_surface(mask_surface)
        return mask

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
            self.movement(obstacles,0)
            self.movement(obstacles,1)

    def movement(self,obstacles,i):
        """Uses mask collision and decrements the player's position until
        clear of solid obstacles."""
        change = self.speed*DIRECT_DICT[self.direction_stack[-1]][i]
        self.rect[i] += change
        collides = pg.sprite.spritecollide(self,obstacles,False)
        if collides:
            callback = pg.sprite.collide_mask
            collides = pg.sprite.spritecollide(self,collides,False,callback)
            unaltered = True
            while collides:
                self.rect[i] += (1 if change<0 else -1)
                unaltered = False
                first_collision = collides[0]
                collides = pg.sprite.spritecollide(self,collides,False,callback)
            if not unaltered:
                self.print_collision_direction(first_collision)

    def print_collision_direction(self,collision):
        """Let us see how our implementation works."""
        direction = self.get_collision_direction(collision)
        print("Sprite collided with {} edge.".format(direction))

    def get_collision_direction(self,other_sprite):
        """Find what side of an object the player is running into."""
        dx = self.get_finite_difference(other_sprite,0,self.speed)
        dy = self.get_finite_difference(other_sprite,1,self.speed)
        abs_x,abs_y = abs(dx),abs(dy)
        if abs_x > abs_y:
            return ("right" if dx>0 else "left")
        elif abs_x < abs_y:
            return ("bottom" if dy>0 else "top")
        else:
            return OPPOSITE_DICT[self.direction]

    def get_finite_difference(self,other_sprite,index,delta=1):
        """Find the finite difference in area of mask collision with the
        rects position incremented and decremented in axis index."""
        base_offset = [other_sprite.rect.x-self.rect.x,
                       other_sprite.rect.y-self.rect.y]
        offset_high = base_offset[:]
        offset_low = base_offset[:]
        offset_high[index] += delta
        offset_low[index] -= delta
        first_term = self.mask.overlap_area(other_sprite.mask,offset_high)
        second_term = self.mask.overlap_area(other_sprite.mask,offset_low)
        return first_term - second_term

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
        self.mask = pg.Mask(self.rect.size)
        self.mask.fill()

    def make_image(self):
        """Let's not forget aesthetics."""
        self.image = pg.Surface((50,50)).convert_alpha()
        self.image.fill([random.randint(0,255) for i in range(3)])
        self.image.blit(SHADE_MASK,(0,0))


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
            self.screen.fill(pg.Color("black"))
            self.player.update(self.obstacles)
            self.obstacles.draw(self.screen)
            self.player.draw(self.screen)
            pg.display.update()
            caption = "{} - FPS: {:.2f}".format(CAPTION,self.clock.get_fps())
            pg.display.set_caption(caption)
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
