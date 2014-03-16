"""
Demonstrates rotating an object without the center shifting and moving objects
at angles using simple trigonometry. Left and Right arrows to rotate cannon.
Spacebar to fire.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import math
import pygame as pg


CAPTION = "Tank Turret: Keyboard"
SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (50, 50, 50)
COLOR_KEY = (255, 0, 255)

SPIN_DICT = {pg.K_LEFT  :  1,
             pg.K_RIGHT : -1}


class Turret(object):
    """Shooting lasers with absolute precision."""
    def __init__(self, location):
        """Location is an (x,y) coordinate pair."""
        self.original_barrel = TURRET.subsurface((0,0,150,150))
        self.barrel = self.original_barrel.copy()
        self.base = TURRET.subsurface((300,0,150,150))
        self.rect = self.barrel.get_rect(center=location)
        self.base_rect = self.rect.copy()
        self.angle = 90
        self.spin = 0
        self.rotate_speed = 3
        self.rotate(True)

    def rotate(self, force=False):
        """
        Rotate our barrel image and set the new rect's center to the
        old rect's center to ensure our image doesn't shift around.
        """
        if self.spin or force:
            self.angle += self.rotate_speed*self.spin
            self.barrel = pg.transform.rotate(self.original_barrel, self.angle)
            self.rect = self.barrel.get_rect(center=self.rect.center)

    def get_event(self, event, objects):
        """Our turret is passed events from the Control event loop."""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                objects.add(Laser(self.rect.center, self.angle))

    def update(self, keys):
        """Update our Turret and draw it to the surface."""
        self.spin = 0
        for key in SPIN_DICT:
            if keys[key]:
                self.spin += SPIN_DICT[key]
        self.rotate()

    def draw(self, surface):
        """Draw base and barrel to the target surface."""
        surface.blit(self.base, self.base_rect)
        surface.blit(self.barrel, self.rect)


class Laser(pg.sprite.Sprite):
    """
    A class for our laser projectiles.  Using the pygame.sprite.Sprite class
    this time, though it is just as easily done without it.
    """
    def __init__(self, location, angle):
        """
        Takes a coordinate pair, and an angle in degrees.  These are passed
        in by the Turret class when the projectile is created.
        """
        pg.sprite.Sprite.__init__(self)
        self.original_laser = TURRET.subsurface((150,0,150,150))
        self.angle = -math.radians(angle-135)
        self.image = pg.transform.rotate(self.original_laser, angle)
        self.rect = self.image.get_rect(center=location)
        self.move = [self.rect.x, self.rect.y]
        self.speed_magnitude = 5
        self.speed = (self.speed_magnitude*math.cos(self.angle),
                      self.speed_magnitude*math.sin(self.angle))
        self.done = False

    def update(self, screen_rect):
        """
        Because pygame.Rect's can only hold ints, it is necessary to hold
        the real value of our movement vector in another variable.
        """
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
        self.remove(screen_rect)

    def remove(self, screen_rect):
        """If the projectile has left the screen, remove it from any Groups."""
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Control(object):
    """Why so controlling?"""
    def __init__(self):
        """
        Prepare necessities; create a Turret; and create a Group for our
        laser projectiles.
        """
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.cannon = Turret((250,250))
        self.objects = pg.sprite.Group()

    def event_loop(self):
        """Events are passed on to the Turret."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            self.cannon.get_event(event, self.objects)

    def update(self):
        """Update turret and all lasers."""
        self.cannon.update(self.keys)
        self.objects.update(self.screen_rect)

    def draw(self):
        """Draw all elements to the display surface."""
        self.screen.fill(BACKGROUND_COLOR)
        self.cannon.draw(self.screen)
        self.objects.draw(self.screen)

    def display_fps(self):
        """Show the program's FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """"Same old story."""
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.flip()
            self.clock.tick(self.fps)
            self.display_fps()


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    TURRET = pg.image.load("turret.png").convert()
    TURRET.set_colorkey(COLOR_KEY)
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
