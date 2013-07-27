"""Demonstrates two different methods of punching a hole in a surface.
I then extend one of the methods in gradient_hole to show more complex effects.
The hole will follow the mouse cursor."""
import pygame as pg
import sys,os

class Control:
    def __init__(self):
        self.done = False
        self.Clock = pg.time.Clock()
        self.rect = pg.Rect((0,0,600,600))

    def event_loop(self):
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.done = True

    def make_hole(self,Surf):
        hole = pg.Surface((Surf.get_size())).convert()
        hole.set_colorkey((255,0,255))
        hole.fill((0,0,0)) #Experiment with changing this color.
        pg.draw.ellipse(hole,(255,0,255), self.rect)
##        hole.set_alpha(200)  #Uncomment and experiment with changing this value.
        Surf.blit(hole,(0,0))

    def make_hole_alpha(self,Surf):
        hole = pg.Surface((Surf.get_size())).convert_alpha()
        hole.fill((255,255,255,200)) #Experiment with changing this color
        pg.draw.ellipse(hole,(0,0,0,0), self.rect)
        Surf.blit(hole,(0,0))

    def gradient_hole(self,Surf):
        hole = pg.Surface((Surf.get_size())).convert_alpha()
        Color = pg.Color(50,0,0,255) #Experiment with changing this color
        hole.fill(Color)

        step = (-50,-10) #Change ammount to shrink each rect by
        alpha_step = 20 #Change amount to change transparency per step
        steps = min(self.rect.width//abs(step[0]),self.rect.height//abs(step[1]))
        shrink_rect = self.rect.copy()

        for i in range(steps):
            if Color.a-alpha_step >= 0:
                Color.a -= alpha_step
            else:
                Color.a = 0
            pg.draw.ellipse(hole,Color,shrink_rect)
            shrink_rect.inflate_ip(step)
            #inflate should auto-adjust center, but in the case of a step of -1,-1 it fails.
            shrink_rect.center = self.rect.center
        Surf.blit(hole,(0,0))

    def update(self,Surf):
        """Uncomment the version you want to test."""
        self.rect.center = pg.mouse.get_pos()
        Surf.blit(FRACTAL,(0,0))
##        self.make_hole(Surf)
##        self.make_hole_alpha(Surf)
        self.gradient_hole(Surf)

    def main(self,Surf):
        while not self.done:
            self.event_loop()
            self.update(Surf)
            pg.display.update()
            self.Clock.tick(60)

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    SCREENSIZE = (1000,650)
    SCREEN = pg.display.set_mode(SCREENSIZE)
    FRACTAL = pg.image.load("frac.jpg").convert()
    RunIt = Control()
    RunIt.main(SCREEN)
    pg.quit();sys.exit()