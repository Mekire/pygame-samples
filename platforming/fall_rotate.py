"""
This is identical to fall_mask, except that the sprite spins when moving
while contacting the ground. Just for fun.  Shows how to cache rotation frames
for times when you find rotation is too expensive to repeat.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg
from random import randint


CAPTION = "Basic Platforming: Rotating our face"


class _Physics(object):
    """A simplified physics class.  Using a 'real' gravity function here, though
    it is questionable whether or not it is worth the effort.  Compare to the
    effect of gravity in fall_rect and decide for yourself."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = self.y_vel = self.y_vel_i = 0
        self.grav = 20
        self.fall = False
        self.time = None

    def physics_update(self):
        """If the player is falling, calculate current y velocity."""
        if self.fall:
            time_now = pg.time.get_ticks()
            if not self.time:
                self.time = time_now
            self.y_vel = self.grav*((time_now-self.time)/1000.0) + self.y_vel_i
        else:
            self.time = None
            self.y_vel = self.y_vel_i = 0


class Player(_Physics,pg.sprite.Sprite):
    """Class representing our player."""
    cache_rotations = {}

    def __init__(self,location,speed):
        """The location is an (x,y) coordinate pair, and speed is the player's
        speed in pixels per frame.  Speed should be an integer."""
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.angle = 0
        self.rect = BASEFACE.get_rect(topleft=location)
        self.image = self.make_image()
        self.mask  = pg.mask.from_surface(BASEFACE)
        self.speed = speed
        self.jump_power = 10

    def make_image(self):
        """Rotate the player's image and cache the surface so that we don't
        need to perform identical rotations more than once."""
        if self.angle in Player.cache_rotations:
            return Player.cache_rotations[self.angle]
        else:
            temp = pg.Surface((self.rect.size)).convert_alpha()
            temp_rect = temp.get_rect()
            temp.fill((0,0,0,0))
            temp.blit(BASEFACE,(0,0))
            face = pg.transform.rotozoom(FACE,self.angle,1)
            face_rect = face.get_rect(center=temp_rect.center)
            temp.blit(face,face_rect)
            Player.cache_rotations[self.angle] = temp
            return temp

    def get_position(self,obstacles):
        """Calculate where our player will end up this frame including
        collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel),1,obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0),0,obstacles)

    def check_falling(self,obstacles):
        """Checks one pixel below the player to see if the player is still on
        the ground."""
        old_rect = self.rect.copy()
        self.rect.move_ip((0,1))
        collisions = pg.sprite.spritecollide(self,obstacles,False)
        if not any(pg.sprite.collide_mask(self,obs) for obs in collisions):
            self.fall = True
        self.rect = old_rect

    def check_collisions(self,offset,index,obstacles):
        """This function checks if a collision would occur after moving offset
        pixels.  If a collision is detected position is decremented by one pixel
        and retested.  This continues until we find exactly how far we can
        safely move, or we decide we can't move."""
        unaltered = True
        self.rect.move_ip(offset)
        collisions = pg.sprite.spritecollide(self,obstacles,False)
        while any(pg.sprite.collide_mask(self,obs) for obs in collisions):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_keys(self,keys):
        """Find the player's self.x_vel based on currently held keys.  Rotate
        the player's image if the player is grounded."""
        self.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += self.speed
        if not self.fall:
            self.angle = (self.angle-self.x_vel)%360

    def jump(self):
        """Called when the user presses the jump button."""
        if not self.fall:
            self.y_vel_i = -self.jump_power
            self.fall = True

    def update(self,surface,obstacles,keys):
        """Everything we need to stay updated."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()
        self.image = self.make_image()
        blit_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image,blit_rect)


class Block(pg.sprite.Sprite):
    """Class representing obstacles."""
    def __init__(self,location):
        """Location is just an (x,y) coordinate pair."""
        pg.sprite.Sprite.__init__(self)
        self.make_image()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = pg.Rect(location,(50,50))

    def make_image(self):
        """Something pretty to look at."""
        self.image = pg.Surface((50,50)).convert_alpha()
        self.image.fill([randint(0,255) for i in range(3)])
        self.image.blit(SHADE_IMG,(0,0))


class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        """Nothing to see here folks.  Move along."""
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,-25), 4)
        self.obstacles = self.make_obstacles()

    def make_obstacles(self):
        """Just adds some arbitrarily placed obstacles to a sprite.Group."""
        obstacles = [Block((400,400)),Block((300,270)),Block((150,170))]
        obstacles += [Block((500+50*i,220)) for i in range(3)]
        for i in range(12):
            obstacles.append(Block((50+i*50,450)))
            obstacles.append(Block((100+i*50,0)))
            obstacles.append(Block((0,50*i)))
            obstacles.append(Block((650,50*i)))
        return pg.sprite.Group(obstacles)

    def event_loop(self):
        """We can always quit, and the player can sometimes jump."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def update(self):
        """Redraw all screen objects and update the player."""
        self.screen.fill((50,50,50))
        self.obstacles.draw(self.screen)
        self.player.update(self.screen,self.obstacles,self.keys)
        caption = "{} - FPS: {:.2f}".format(CAPTION,self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode((700,500))
    BASEFACE = pg.image.load("base_face.png").convert_alpha()
    FACE  = pg.image.load("just_face.png").convert_alpha()
    SHADE_IMG = pg.image.load("shader.png").convert_alpha()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
