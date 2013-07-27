"""
This script implements a basic sprite that can move in all 8 directions.
-Written by Sean J. McKiernan 'Mekire'
"""
import os,sys #used for os.environ and sys.exit
import pygame as pg

#This global constant serves as a very useful convenience for me.
DIRECTDICT = {pg.K_LEFT  : (-1, 0),
              pg.K_RIGHT : ( 1, 0),
              pg.K_UP    : ( 0,-1),
              pg.K_DOWN  : ( 0, 1)}

class Player:
    """This class will represent our user controlled character.
    Arguments are the players rect (x,y,width,height), and the
    speed (in pixels/frame)"""
    def __init__(self,rect,speed):
        self.rect = pg.Rect(rect)
        self.speed = speed
        self.movement = [0,0]
        self.make_image()
    def make_image(self):
        """Creates our hero (a red circle/ellipse with a black outline)
        If you want to use an image, or specify how to animate it,
        this is the place."""
        self.image = pg.Surface((self.rect.size)).convert_alpha()
        self.image.fill((0,0,0,0))
        pg.draw.ellipse(self.image,(0,0,0),(1,1,self.rect.size[0]-2,self.rect.size[1]-2))
        pg.draw.ellipse(self.image,(255,0,0),(6,6,self.rect.size[0]-12,self.rect.size[1]-12))
    def update(self,Surf):
        """Updates our player appropriately every frame."""
        self.rect.move_ip(self.movement)
        self.draw(Surf)
    def draw(self,Surf):
        Surf.blit(self.image,self.rect)

###############################################
def quit_game():
    """Call this anytime the program needs to close cleanly."""
    pg.quit();sys.exit()

def game(Player):
    """Our event loop goes here."""
    for event in pg.event.get():
        Player.movement = [0,0]
        keys = pg.key.get_pressed()
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
             quit_game()
        for key in DIRECTDICT:
            if keys[key]:
                for i in (0,1):
                    Player.movement[i] += DIRECTDICT[key][i]*Player.speed

def main(Surf,Player):
    """The main function calls the draw functions in the order they are required.
    Then updates the entire screen."""
    game(Player) #run the event loop
    Surf.fill((255,255,255)) #redraw background before player
    Player.update(Surf) #update the player
    pg.display.update() #now update the screen

######################################################################
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1' #Center window.
    Surface = pg.display.set_mode((500,500))
    pg.init()
    Myclock = pg.time.Clock() #Will allow us to restrict frames per second.
    Myplayer = Player((250,250,100,100),3)  #Create an instance of Player.
    while 1:
        main(Surface,Myplayer)   #Run main in an infinite loop.
        Myclock.tick(60) #Limit program to this FPS.
