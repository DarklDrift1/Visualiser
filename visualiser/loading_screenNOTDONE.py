import pygame as pg
from constants import *
from visualiser import visualiser

class LoadingScreen():
    def __init__(self, game) -> None:
        self.game = game
        self.visualiser = visualiser

        self.font_size = 30
        self.font = pg.font.Font(None, self.font_size)
    
    def run(self):
        while True:
            self.events()
            self.display()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
    
    def display(self):
        # fill background
        self.game.fill(CIRCLE_COLOR)

        self.game.draw_text()

        pg.display.flip()