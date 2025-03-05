import pygame as pg
from visualiser import visualiser
from constants import *
import threading

def main():
    # Load song titles
    titles = []
    with open("musics\\songtitles.txt", 'r', encoding="UTF-8") as f:
        for song in f:
            titles.append(song.strip('\n'))

    # Load audio files
    filenames = []
    with open("musics\\songs.txt", "r", encoding='UTF-8') as f:
        for song in f:
            filenames.append("musics\\" + song.strip('\n'))
    print(filenames)

    # Start PyGame
    pg.init()
    infoObject = pg.display.Info()
    screen_w = infoObject.current_w
    screen_h = infoObject.current_h
    screen = pg.display.set_mode([screen_w, screen_h], pg.NOFRAME | pg.SRCALPHA)
    font = pg.font.Font(None, 36)
    visualiser1 = visualiser(screen,filenames,titles,screen_w,screen_h)
    visualiser_thread = threading.Thread(target=visualiser1.run)
    visualiser_thread.start()
    
    visualiser_thread.join()

main()