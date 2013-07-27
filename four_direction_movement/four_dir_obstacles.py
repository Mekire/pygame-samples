import os
import sys
import pygame as pg
from random import randint


DIRECTDICT = {pg.K_LEFT  : (-1, 0),
              pg.K_RIGHT : ( 1, 0),
              pg.K_UP    : ( 0,-1),
              pg.K_DOWN  : ( 0, 1)}


class Player(pg.sprite.Sprite):
    def __init__(self,rect,speed,direction=pg.K_RIGHT):
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.direction = direction
        self.old_direction = None
        self.dir_stack = []
        self.walk = False
        self.redraw = False

        self.spritesheet = SKEL_IMG
        self.image = None
        self.frame_inds = [[0,0],[1,0],[2,0],[3,0]] #loc of frames on sheet
        self.frame  = 0
        self.frames = [] #all frames off the sprite sheet
        self.timer = 0.0 #timer for animation
        self.fps   = 7.0 #fps of animation
        self.walkframes = [] #walkframes for given direction
        self.get_images() #rip images from the sprite sheet
        self.walkframe_dict = self.make_frame_dict()
        self.adjust_images()

    def get_images(self):
        """Get the desired images from the sprite sheet."""
        for cell in self.frame_inds:
            loc = ((self.rect.width*cell[0],self.rect.height*cell[1]),self.rect.size)
            self.frames.append(self.spritesheet.subsurface(loc))

    def make_frame_dict(self):
        frames = {pg.K_LEFT : [self.frames[0],self.frames[1]],
                  pg.K_RIGHT: [pg.transform.flip(self.frames[0],True,False),
                               pg.transform.flip(self.frames[1],True,False)],
                  pg.K_DOWN : [self.frames[3],
                               pg.transform.flip(self.frames[3],True,False)],
                  pg.K_UP   : [self.frames[2],
                               pg.transform.flip(self.frames[2],True,False)]}
        return frames

    def adjust_images(self):
        """update the sprites walkframes as the sprites direction changes"""
        if self.direction != self.old_direction:
            self.walkframes = self.walkframe_dict[self.direction]
            self.old_direction = self.direction
            self.redraw = True
        self.make_image()

    def make_image(self):
        """update the sprites animation as needed"""
        if self.redraw or pg.time.get_ticks()-self.timer > 1000/self.fps:
            if self.walk:
                self.frame = (self.frame+1) % len(self.walkframes)
                self.image = self.walkframes[self.frame]
            self.timer = pg.time.get_ticks()
        if not self.image:
            self.image = self.walkframes[self.frame]
        self.redraw = False

    def update(self,obstacles):
        """Updates our player appropriately every frame."""
        self.walk = bool(self.dir_stack)
        self.adjust_images()
        if self.walk:
            x = self.speed*DIRECTDICT[self.dir_stack[-1]][0]
            y = self.speed*DIRECTDICT[self.dir_stack[-1]][1]
            old_rect = self.rect
            self.rect = self.rect.move(x,y)
            if pg.sprite.spritecollide(self,obstacles,False):
                self.rect = old_rect

    def draw(self,surface):
        surface.blit(self.image,self.rect)


class Block(pg.sprite.Sprite):
    def __init__(self,location):
        pg.sprite.Sprite.__init__(self)
        self.make_image()
        self.rect = pg.Rect(location,(50,50))

    def make_image(self):
        self.image = pg.Surface((50,50)).convert_alpha()
        self.image.fill([randint(0,255) for i in range(3)])
        self.image.blit(SHADE_MASK,(0,0))

    def draw(self,surface):
        Surf.blit(self.image,self.rect)


class Control:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.player = Player((250,250,50,50),3)
        self.obstacles = pg.sprite.Group(self.make_obstacles())
        self.clock  = pg.time.Clock()
        self.done = False

    def make_obstacles(self):
        obstacles = [Block((400,400)),Block((300,270)),Block((150,170))]
        for i in range(9):
            obstacles.append(Block((i*50,0)))
            obstacles.append(Block((450,50*i)))
            obstacles.append(Block((50+i*50,450)))
            obstacles.append(Block((0,50+50*i)))
        return obstacles

    def event_loop(self):
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key in DIRECTDICT:
                    self.player.dir_stack.append(event.key)
                    self.player.direction = self.player.dir_stack[-1]
            elif event.type == pg.KEYUP:
                if event.key in DIRECTDICT:
                    self.player.dir_stack.remove(event.key)
                    if self.player.dir_stack:
                        self.player.direction = self.player.dir_stack[-1]

    def main(self):
        while not self.done:
            self.event_loop()
            self.screen.fill(0)
            self.player.update(self.obstacles)
            self.obstacles.draw(self.screen)
            self.player.draw(self.screen)
            pg.display.update()
            self.clock.tick(60)

#####
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((500,500))

    SKEL_IMG = pg.image.load("skelly.png").convert()
    SKEL_IMG.set_colorkey((255,0,255))
    SHADE_MASK = pg.image.load("shader.png").convert_alpha()

    run_it = Control()
    run_it.main()
    pg.quit();sys.exit()

