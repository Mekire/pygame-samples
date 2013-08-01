"""
This shows some basic platforming using only rectangle collision.  The intent
is to demonstrate what rectangle collision lacks.  This version uses collision
functions from pygame.sprite, but no pixel-perfect collision.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pygame as pg
from random import randint


class _Physics(object):
    """A simplified physics class.  Psuedo-gravity is often good enough."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = self.y_vel = 0
        self.grav = 0.22
        self.fall = False

    def physics_update(self):
        """If the player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0


class Player(_Physics,pg.sprite.Sprite):
    """Class representing our player."""
    def __init__(self,location,speed,tester=False):
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = PLAYER_IMAGE
        self.speed = speed
        self.jump_power = -8.5
        self.rect = self.image.get_rect(topleft=location)
        if not tester:
            self.test_sprite = Player(location,speed,True)

    def get_position(self,obstacles):
        """Calculate where our player will end up this frame including
        collissions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            offset = (0,self.y_vel)
            self.rect.y,self.fall = self.check_collisions(offset,1,obstacles)
        if self.x_vel:
            offset = (self.x_vel,0)
            self.rect.x = self.check_collisions(offset,0,obstacles)[0]

    def check_falling(self,obstacles):
        """Checks one pixel below the player to see if the player is still on
        the ground."""
        self.test_sprite.rect = self.rect.move((0,1))
        if not pg.sprite.spritecollideany(self.test_sprite,obstacles):
            self.fall = True

    def check_collisions(self,offset,index,obstacles):
        """This function checks if a collision would occur after moving offset
        pixels.  If a collision is detected position is decremented by one pixel
        and retested.  This continues until we find exactly how far we can
        safely move, or we decide we can't move."""
        unaltered = True
        self.test_sprite.rect = self.rect.move(offset)
        while pg.sprite.spritecollideany(self.test_sprite,obstacles):
            self.test_sprite.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return self.test_sprite.rect[index],unaltered

    def check_keys(self,keys):
        """Find the players self.x_vel based on currently held keys."""
        self.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += self.speed

    def jump(self):
        """Called when the user presses the jump button."""
        if not self.fall:
            self.y_vel = self.jump_power
            self.fall = True

    def update(self,surface,obstacles,keys):
        """Everything we need to stay updated."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()
        surface.blit(self.image,self.rect)


class Block(pg.sprite.Sprite):
    """Class representing obstacles."""
    def __init__(self,location):
        """Location is just an (x,y) coordinate pair."""
        pg.sprite.Sprite.__init__(self)
        self.make_image()
        self.rect = pg.Rect(location,(50,50))

    def make_image(self):
        """Something pretty to look at."""
        self.image = pg.Surface((50,50)).convert()
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
    pg.display.set_mode((700,500))
    PLAYER_IMAGE = pg.image.load("smallface.png").convert_alpha()
    SHADE_IMG = pg.image.load("shader.png").convert_alpha()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
