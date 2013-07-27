"""Very basic.  Change the screen color with a mouse click."""
import os,sys  #used for sys.exit and os.environ
import pygame  #import the pygame module
from random import randint

class Control:
    def __init__(self):
        self.color = 0
    def update(self,Surf):
        self.event_loop()  #Run the event loop every frame
        Surf.fill(self.color) #Make updates to screen every frame
    def event_loop(self):
        for event in pygame.event.get(): #Check the events on the event queue
            if event.type == pygame.MOUSEBUTTONDOWN:
                #If the user clicks the screen, change the color.
                self.color = [randint(0,255) for i in range(3)]
            elif event.type == pygame.QUIT:
                pygame.quit();sys.exit()

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'  #Center the screen.
    pygame.init() #Initialize Pygame
    Screen = pygame.display.set_mode((500,500)) #Set the mode of the screen
    MyClock = pygame.time.Clock() #Create a clock to restrict framerate
    RunIt = Control()
    while 1:
        RunIt.update(Screen)
        pygame.display.update() #Update the screen
        MyClock.tick(60) #Restrict framerate
