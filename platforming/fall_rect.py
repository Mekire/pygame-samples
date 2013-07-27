"""This shows some basic platforming using only rectangle collision.  The intent
is to demonstrate what rectangle collision lacks."""
import os,sys
from random import randint
import pygame as pg

class _Physics(object):
    def __init__(self):
        self.x_vel = self.y_vel = 0
        self.grav = 0.22
        self.fall = False
    def phys_update(self):
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

class Player(_Physics):
    """Class representing our player."""
    def __init__(self, location,speed):
        _Physics.__init__(self)
        self.image = PLAY_IMG
        self.speed = speed
        self.jump_power = -8.5
        self.rect = self.image.get_rect()
        self.rect.topleft = location

        self.collide_ls = [] #what obstacles does the player collide with

    def get_pos(self,Obstacles):
        """Calculate where our player will end up this frame including collissions."""
        #Has the player walked off an edge?
        if not self.fall and not self.collide_with(Obstacles,[0,1]):
            self.fall = True
        #Has the player landed from a fall or jumped into an object above them?
        elif self.fall and self.collide_with(Obstacles,[0,int(self.y_vel)]):
            self.y_vel = self.adjust_pos(self.collide_ls,[0,int(self.y_vel)],1)
            self.fall = False
        self.rect.y += int(self.y_vel) #Update y position before testing x.
        #Is the player running into a wall?.
        if self.collide_with(Obstacles,(int(self.x_vel),0)):
            self.x_vel = self.adjust_pos(Obstacles,[int(self.x_vel),0],0)
        self.rect.x += int(self.x_vel)
    def adjust_pos(self,Obstacles,offset,off_ind):
        offset[off_ind] += (1 if offset[off_ind]<0 else -1)
        while 1:
            if any(self.collide_with(self.collide_ls,offset)):
                offset[off_ind] += (1 if offset[off_ind]<0 else -1)
            else:
                return offset[off_ind]

    def collide_with(self,Obstacles,offset):
        test = ((self.rect.x+offset[0],self.rect.y+offset[1]),self.rect.size)
        self.collide_ls = []
        for Obs in Obstacles:
            if pg.Rect(test).colliderect(Obs.rect):
                self.collide_ls.append(Obs)
        return self.collide_ls

    def update(self,Surf,Obstacles):
        self.get_pos(Obstacles)
        self.phys_update()
        Surf.blit(self.image,self.rect)

class Block(object):
    """Class representing obstacles."""
    def __init__(self,location):
        self.make_image()
        self.rect = pg.Rect(location,(50,50))
    def make_image(self):
        self.image = pg.Surface((50,50)).convert()
        self.image.fill([randint(0,255) for i in range(3)])
        self.image.blit(SHADE_IMG,(0,0))
    def update(self,Surf):
        Surf.blit(self.image,self.rect)

class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        self.Screen = pg.display.get_surface()
        self.done = False
        self.Player = Player((50,-25), 4)
        self.make_obstacles()
        self.Clock = pg.time.Clock()
        self.fps = 60
    def event_loop(self):
        keys = pg.key.get_pressed()
        self.Player.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.Player.x_vel -= self.Player.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.Player.x_vel += self.Player.speed
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN: #Key down events.
                if event.key == pg.K_SPACE and not self.Player.fall: #Jump
                    self.Player.y_vel = self.Player.jump_power
                    self.Player.fall = True
    def update(self,Surf):
        Surf.fill((50,50,50))
        [obs.update(Surf) for obs in self.Obstacles]
        self.Player.update(Surf,self.Obstacles)
    def main(self):
        while not self.done:
            self.event_loop()
            self.update(self.Screen)
            pg.display.update()
            self.Clock.tick(self.fps)
    def make_obstacles(self):
        self.Obstacles = [Block((400,400)),Block((300,270)),Block((150,170))]
        self.Obstacles += [Block((500+50*i,220)) for i in range(3)]
        for i in range(12):
            self.Obstacles.append(Block((50+i*50,450)))
            self.Obstacles.append(Block((100+i*50,0)))
            self.Obstacles.append(Block((0,50*i)))
            self.Obstacles.append(Block((650,50*i)))

#################################
if __name__ == "__main__":
##    os.environ['SDL_VIDEO_CENTERED'] = '1'

    os.environ['SDL_VIDEO_WINDOW_POS'] = "350,150"
    pg.init()
    SCREENSIZE = (700,500)
    pg.display.set_mode(SCREENSIZE)
    PLAY_IMG  = pg.image.load("smallface.png").convert_alpha()
    SHADE_IMG = pg.image.load("shader.png").convert_alpha()

    RunIt = Control()
    RunIt.main()
    pg.quit();sys.exit()