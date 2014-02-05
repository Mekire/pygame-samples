"""
This shows some basic platforming using only rectangle collision. The intent
is to demonstrate what rectangle collision lacks. This version uses collision
functions from pygame.sprite, but no pixel-perfect collision.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import random
import pygame as pg


CAPTION = "Basic Platforming: Rectangle Collision"
SCREEN_SIZE = (700, 500)
BACKGROUND_COLOR = (50, 50, 50)


class _Physics(object):
    """A simplified physics class. Psuedo-gravity is often good enough."""
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


class Player(_Physics, pg.sprite.Sprite):
    """Class representing our player."""
    def __init__(self, location, speed):
        """
        The location is an (x,y) coordinate pair, and speed is the player's
        speed in pixels per frame. Speed should be an integer.
        """
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = PLAYER_IMAGE
        self.speed = speed
        self.jump_power = -8.5
        self.rect = self.image.get_rect(topleft=location)

    def get_position(self, obstacles):
        """Calculate the player's position this frame, including collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel) , 1, obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0), 0, obstacles)

    def check_falling(self, obstacles):
        """If player is not contacting the ground, enter fall state."""
        self.rect.move_ip((0,1))
        if not pg.sprite.spritecollideany(self, obstacles):
            self.fall = True
        self.rect.move_ip((0,-1))

    def check_collisions(self, offset, index, obstacles):
        """This function checks if a collision would occur after moving offset
        pixels.  If a collision is detected position is decremented by one
        pixel and retested. This continues until we find exactly how far we can
        safely move, or we decide we can't move."""
        unaltered = True
        self.rect.move_ip(offset)
        while pg.sprite.spritecollideany(self, obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_keys(self, keys):
        """Find the player's self.x_vel based on currently held keys."""
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

    def update(self, obstacles, keys):
        """Everything we need to stay updated."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()

    def draw(self,surface):
        """Blit the player to the target surface."""
        surface.blit(self.image, self.rect)


class Block(pg.sprite.Sprite):
    """A class representing solid obstacles."""
    def __init__(self, location):
        """The location argument is an (x,y) coordinate pair."""
        pg.sprite.Sprite.__init__(self)
        self.make_image()
        self.rect = pg.Rect(location, (50,50))

    def make_image(self):
        """Something pretty to look at."""
        color = [random.randint(0, 255) for _ in range(3)]
        self.image = pg.Surface((50,50)).convert()
        self.image.fill(color)
        self.image.blit(SHADE_IMG, (0,0))


class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        """Nothing to see here folks. Move along."""
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,-25), 4)
        self.obstacles = self.make_obstacles()

    def make_obstacles(self):
        """Adds some arbitrarily placed obstacles to a sprite.Group."""
        obstacles = [Block((400,400)), Block((300,270)), Block((150,170))]
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
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def update(self):
        """Update held keys and the player."""
        self.keys = pg.key.get_pressed()
        self.player.update(self.obstacles, self.keys)

    def draw(self):
        """Draw all necessary objects to the display surface."""
        self.screen.fill(BACKGROUND_COLOR)
        self.obstacles.draw(self.screen)
        self.player.draw(self.screen)

    def display_fps(self):
        """Show the programs FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    PLAYER_IMAGE = pg.image.load("smallface.png").convert_alpha()
    SHADE_IMG = pg.image.load("shader.png").convert_alpha()
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
