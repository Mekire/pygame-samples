"""
This script implements a basic sprite that can only move orthogonally.
Orthogonal-only movement is slightly trickier than 8-direction movement
because you can't just create a simple movement vector.
Extra work must be done to make key overlaps execute cleanly.

Written by Sean J. McKiernan 'Mekire'
"""
import os, sys #used for os.environ and sys.exit
#Don't use from pygame.locals import *; take it from a reformed user.
import pygame as pg #I'm lazy, sue me; but, no from * import.

#This global constant serves as a very useful convenience for me.
DIRECTDICT = {pg.K_LEFT  : (-1, 0),
              pg.K_RIGHT : ( 1, 0),
              pg.K_UP    : ( 0,-1),
              pg.K_DOWN  : ( 0, 1)}

class Player:
    """This class will represent our user controlled character.
    Arguments are a Surface to draw the Player to, a rect representing the
    Players location and dimension, the speed (in pixels/frame) of the
    Player, and the players starting direction"""
    def __init__(self,rect,speed,direction=pg.K_RIGHT):
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.direction = direction
        self.oldy = None #the characters previous direction every frame
        self.dir_stack = [] #held arrow keys, in the order they were pressed
        self.walk = False
        self.redraw = False #force redraw if needed

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
        if self.direction != self.oldy:
            self.walkframes = self.walkframe_dict[self.direction]
            self.oldy = self.direction
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

    def update(self,Surf):
        """Updates our player appropriately every frame."""
        self.walk = bool(self.dir_stack)
        self.adjust_images()
        #checks to see if 'walk' is true and updates hero position
        if self.walk:
            self.rect.x += self.speed*DIRECTDICT[self.dir_stack[-1]][0]
            self.rect.y += self.speed*DIRECTDICT[self.dir_stack[-1]][1]
        Surf.blit(self.image,self.rect)

class Control:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.Player = Player((250,250,50,50),3)  #Our Player instance
        self.Clock  = pg.time.Clock() #This clock will let us restrict fps.
        self.done = False
    def event_loop(self):
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN: #all key press events here.
                if event.key in DIRECTDICT:
                    self.Player.dir_stack.append(event.key)
                    self.Player.direction = self.Player.dir_stack[-1]
            elif event.type == pg.KEYUP: #all key-up events here
                if event.key in DIRECTDICT:
                    self.Player.dir_stack.remove(event.key)
                    if self.Player.dir_stack:
                        self.Player.direction = self.Player.dir_stack[-1]
    def main(self):
        """Out main game loop"""
        while not self.done:
            self.event_loop() #run the event loop every frame
            self.screen.fill((100,100,100)) #redraw background before player
            self.Player.update(self.screen) #update the player
            pg.display.update() #now update the screen
            self.Clock.tick(60)

#####
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1' #Center window.
    pg.init()
    pg.display.set_mode((500,500))

    SKEL_IMG = pg.image.load("skelly.png").convert()
    SKEL_IMG.set_colorkey((255,0,255))

    RunIt = Control()
    RunIt.main()
    pg.quit();sys.exit()