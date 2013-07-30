"""
This example is identical to the standard turret in tank.py, except the Turret
now follows the mouse and fires with the left mouse button; instead of using the
keyboard.
"""

import os
import sys
import math
import pygame as pg


class Turret(object):
    """Mouse guided lasers."""
    def __init__(self,location):
        """Location is an (x,y) coordinate pair."""
        self.original_barrel = TURRET.subsurface((0,0,150,150))
        self.barrel = self.original_barrel.copy()
        self.base = TURRET.subsurface((300,0,150,150))
        self.rect = self.barrel.get_rect(center=location)
        self.base_rect = self.rect.copy()
        self.angle = self.get_angle(pg.mouse.get_pos())

    def get_angle(self,mouse):
        """Finds the new angle between the center of the Turret and the mouse."""
        offset = (self.rect.centerx-mouse[0],self.rect.centery-mouse[1])
        self.angle = math.degrees(math.atan2(*offset))-135
        old_center = self.rect.center
        self.barrel = pg.transform.rotate(self.original_barrel,self.angle)
        self.rect = self.barrel.get_rect(center=old_center)

    def get_event(self,event,objects):
        """Fire lasers on left click.  Recalculate angle if mouse is moved."""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                objects.add(Laser(self.rect.center,self.angle))
        elif event.type == pg.MOUSEMOTION:
            self.get_angle(event.pos)

    def update(self,surface,keys):
        """Update our Turret and draw it to the surface."""
        surface.blit(self.base,self.base_rect)
        surface.blit(self.barrel,self.rect)


class Laser(pg.sprite.Sprite):
    """A class for our laser projectiles.  Using the pygame.sprite.Sprite class
    this time, though it is just as easily done without it."""
    def __init__(self,location,angle):
        """Takes a coordinate pair, and an angle in degrees.  These are passed
        in by the Turret class when the projectile is created."""
        pg.sprite.Sprite.__init__(self)
        self.original_laser = TURRET.subsurface((150,0,150,150))
        self.angle = -math.radians(angle-135)
        self.image = pg.transform.rotate(self.original_laser,angle)
        self.rect = self.image.get_rect(center=location)
        self.move = [self.rect.x,self.rect.y]
        self.speed_magnitude = 5
        self.speed = (self.speed_magnitude*math.cos(self.angle),
                      self.speed_magnitude*math.sin(self.angle))
        self.done = False

    def update(self,surface):
        """Because pygame.Rect's can only hold ints, it is necessary to preserve
        the real value of our movement vector in another variable."""
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
        self.remove(surface)
        surface.blit(self.image,self.rect)

    def remove(self,surface):
        """If the projectile has left the screen, remove it from any Groups."""
        if not self.rect.colliderect(surface.get_rect()):
            self.kill()


class Control(object):
    """Why so controlling?"""
    def __init__(self):
        """Prepare necessities; create a Turret; and create a Group for our
        laser projectiles."""
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.cannon = Turret((250,250))
        self.objects = pg.sprite.Group()

    def event_loop(self):
        """Events are passed on to the Turret."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            self.cannon.get_event(event,self.objects)

    def update(self):
        """Redraw the screen, the Turret, and any Lasers."""
        self.screen.fill((50,50,50))
        self.cannon.update(self.screen,self.keys)
        self.objects.update(self.screen)

    def main_loop(self):
        """"Same old story."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((500,500))
    TURRET = pg.image.load("turret.png").convert()
    TURRET.set_colorkey((255,0,255))
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()