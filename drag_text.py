"""A very simple example showing how to drag an item with the mouse."""
import os,sys
import pygame as pg

class Character:
    def __init__(self,rect):
        self.rect = pg.Rect(rect)
        self.click = False
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill((255,0,0))

        self.text,self.text_rect = self.setup_font()

    def update(self,surface):
        if self.click:
            self.rect.center = pg.mouse.get_pos()
        self.text_rect.center = self.rect.centerx,self.rect.centery+90
        surface.blit(self.image,self.rect)
        surface.blit(self.text,self.text_rect)

    def setup_font(self):
      font = pg.font.SysFont('timesnewroman', 30)
      message = "I'm a red square"
      label = font.render(message, 1, (255,255,255))
      label_rect = label.get_rect()
      return label,label_rect

def main(Surface,Player):
    game_event_loop(Player)
    Surface.fill(0)
    Player.update(Surface)
def game_event_loop(Player):
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if Player.rect.collidepoint(event.pos):
                Player.click = True
        elif event.type == pg.MOUSEBUTTONUP:
            Player.click = False
        elif event.type == pg.QUIT:
            pg.quit(); sys.exit()

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    Screen = pg.display.set_mode((1000,600))
    MyClock = pg.time.Clock()
    MyPlayer = Character((0,0,150,150))
    MyPlayer.rect.center = Screen.get_rect().center
    while 1:
        main(Screen,MyPlayer)
        pg.display.update()
        MyClock.tick(60)