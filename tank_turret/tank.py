"""Demonstrates rotating an object without the center shifting and moving objects
at angles using simple trigonometry. Left and Right arrows to rotate cannon.
Spacebar to fire."""
import pygame as pg
import sys,os,math

class Turret(object):
    def __init__(self,loc):
        self.orig_barrel = TURRET.subsurface((0,0,150,150))
        self.barrel = self.orig_barrel.copy()
        self.base   = TURRET.subsurface((300,0,150,150))
        self.rect = self.barrel.get_rect(center = loc)
        self.base_rect = self.rect.copy()
        self.angle = 90
        self.spin = 0
        self.rotate_speed = 3
        self.rotate(True)
    def event_manager(self,event,Objects):
        keys = pg.key.get_pressed()
        self.spin = 0
        #Ifs not elifs; these all need to run.
        if keys[pg.K_RIGHT]:
            self.spin -= 1
        if keys[pg.K_LEFT]:
            self.spin += 1
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                Objects.append(Laser(self.rect.center,self.angle))
    def update(self,Surf):
        self.rotate()
        Surf.blit(self.base,self.base_rect)
        Surf.blit(self.barrel,self.rect)
    def rotate(self,force=False):
        if self.spin or force:
            oldcenter = self.rect.center
            self.angle += self.rotate_speed*self.spin
            self.barrel = pg.transform.rotate(self.orig_barrel,self.angle)
            self.rect = self.barrel.get_rect(center=oldcenter)

class Laser(object):
    def __init__(self,loc,angle):
        self.orig_laser = TURRET.subsurface((150,0,150,150))
        self.angle = -math.radians(angle-135)
        self.image = pg.transform.rotate(self.orig_laser,angle)
        self.rect = self.image.get_rect(center=loc)
        self.move = [self.rect.x,self.rect.y]
        self.speed_mag = 5
        self.speed = (self.speed_mag*math.cos(self.angle),
                      self.speed_mag*math.sin(self.angle))
        self.done = False
    def update(self,Surf):
        self.move[0] += self.speed[0]
        self.move[1] += self.speed[1]
        self.rect.topleft = self.move
        self.remove(Surf)
        Surf.blit(self.image,self.rect)
    def remove(self,Surf):
        if not self.rect.colliderect(Surf.get_rect()):
            self.done = True

class Control(object):
    def __init__(self):
        self.Screen = pg.display.get_surface()
        self.done = False
        self.Clock = pg.time.Clock()
        self.fps = 60
        self.Cannon = Turret((250,250))
        self.Objects = []
    def event_loop(self):
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True
            self.Cannon.event_manager(event,self.Objects)
    def update(self):
        self.Screen.fill((50,50,50))
        self.Cannon.update(self.Screen)
        for Obj in self.Objects[:]:
            Obj.update(self.Screen)
            if Obj.done:
                self.Objects.remove(Obj)
    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.flip()
            self.Clock.tick(self.fps)

#######
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    SCREENSIZE = (500,500)
    pg.display.set_mode(SCREENSIZE)
    TURRET = pg.image.load("turret.png").convert()
    TURRET.set_colorkey((255,0,255))

    RunIt = Control()
    RunIt.main()
    pg.quit();sys.exit()