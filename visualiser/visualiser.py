from AudioAnalyzer import *
import random
import colorsys
from pydub import AudioSegment
import numpy as np
import math
import time
#import json
#from mss import mss
#import win32api,win32gui,win32con
import pygame as pg 
from constants import *
#import threading

class visualiser():
    def __init__(self,game,filenames,titles,screen_w,screen_h):
        self.game = game
        self.current_song_index = 0
        self.filenames = filenames
        self.frame_count = 0
        self.current_song = self.filenames[self.current_song_index]
        self.titles = titles
        self.running = True
        self.radius = MIN_RADIUS
        self.font = pg.font.Font(None, 36)
        self.analyzer = AudioAnalyzer()
        self.avg_bass = 0
        self.poly = list()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.getTicksLastFrame = 0
        self.t = pg.time.get_ticks()
        self.getTicksLastFrame = self.t
        self.timeCount = 0
        self.isHoM = False
        self.isMoving = False
        self.isTransparent = False
        self.avg_bass = 0
        self.timeout = 0
        self.background = pg.image.load("monitor-1.png")
        self.bass_trigger_started = 0
        self.wait_trigger_started = 0
        self.polygon_bass_color = None
        self.polygon_color_vel = [0, 0, 0]
        self.poly_color = POLYGON_DEFAULT_COLOR.copy()
        self.radius = MIN_RADIUS
        self.radius_vel = 0
        self.min_decibel = -80
        self.max_decibel = 80
        self.slide_val = 0
        self.bars = self.calcbars()
        self.current_title = self.titles[self.current_song_index]
        self.songSecond = AudioSegment.from_file(self.current_song)
        self.song_length_seconds = self.songSecond.duration_seconds
        self.progress_bar_width = self.screen_w
        self.progress_bar_height = 10
        if True:
            self.run()

    def text_display(self):
        self.progress_bar_rect = pg.Rect(0, self.screen_h - self.progress_bar_height, self.progress_bar_width, self.progress_bar_height)
        self.progress_bar_fill_width = int((self.current_time / self.song_length_seconds) * self.progress_bar_width)
        self.progress_bar_fill_rect = pg.Rect(0, self.screen_h - self.progress_bar_height, self.progress_bar_fill_width, self.progress_bar_height)
        self.song_length_text1 = self.font.render(f"{int(self.current_time // 60)}:{int(self.current_time % 60):02}", True, (255, 255, 255))
        self.current_song_text = self.font.render(f"{int(self.current_song_index+1)}/{len(self.titles)}", True, (255,255,255))
        self.current_song_title_text = self.font.render(f"{str(self.current_title)}", True, (255,255,255))
        self.song_length_text2 = self.font.render(f"/{int(self.song_length_seconds // 60)}:{int(self.song_length_seconds % 60):02}", True, (128,128,128))
        self.game.blit(self.current_song_text, (self.screen_w - self.current_song_text.get_width() - 10, self.screen_h - self.current_song_text.get_height() - self.song_length_text1.get_height() - 10))
        self.game.blit(self.song_length_text2, (self.screen_w - self.song_length_text2.get_width() - 10, self.screen_h - self.song_length_text2.get_height() - 10))
        self.game.blit(self.song_length_text1, (self.screen_w - self.song_length_text1.get_width() - self.song_length_text2.get_width() - 10, self.screen_h - self.song_length_text1.get_height() - 10))
        self.game.blit(self.current_song_title_text, ((self.screen_w / 2) - (self.current_song_title_text.get_width() / 2), self.current_song_title_text.get_height() - 20))
        pg.draw.rect(self.game, (0, 255, 0), self.progress_bar_fill_rect)
        pg.draw.rect(self.game, (255, 255, 255), self.progress_bar_rect, 1)

    def calcbars(self):
        # Create audio bars
        bars = []
        tmp_bars = []
        ang = 0
        length = 0
        for group in FREQ_GROUPS:
        
            g = []

            s = group["stop"] - group["start"]

            count = group["count"]

            reminder = s%count

            step = int(s/count)

            rng = group["start"]

            for i in range(count):
            
                arr = None

                if reminder > 0:
                    reminder -= 1
                    arr = np.arange(start=rng, stop=rng + step + 2)
                    rng += step + 3
                else:
                    arr = np.arange(start=rng, stop=rng + step + 1)
                    rng += step + 2

                g.append(arr)

                length += 1

            tmp_bars.append(g)

        ang = 0
        angle_dt = 360/length
        for g in tmp_bars:
            gr = []
            for c in g:
                gr.append(RotatedAverageAudioBar(
                    self.screen_w // 2 + self.radius * math.cos(math.radians(ang - 90)),
                    self.screen_h // 2 + self.radius * math.sin(math.radians(ang - 90)),
                    c, (255, 0, 255), angle=ang, width=8, max_height=370
                ))
                ang += angle_dt
            bars.append(gr)
        return bars

    def rnd_color(self):
        h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
        #if True: # This makes the colors' saturation 0 | a.k.a makes everything black and white
            #s = 0
        self.rndcolor = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
        return self.rndcolor

    def run(self):
        self.start_song()
        while self.running:
            self.events()
            self.display()

    def events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False   
                # event handler
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_LEFT:
                    self.current_song_index -= 1
                    time.sleep(0.1)
                    self.song_switch()
                if e.key == pg.K_RIGHT:
                    self.current_song_index += 1
                    time.sleep(0.1)
                    self.song_switch()
                if self.current_song_index > len(self.filenames) or 0 > self.current_song_index:
                    self.running = False
    
    def start_song(self):
        # Starts the specified song
        self.special_check()
        self.analyzer.load(self.current_song)
        pg.mixer.music.load(self.current_song)
        pg.mixer.music.play(0)

    def special_check(self):
        # Checks if the song is a SPECIAL one
        self.isTransparent = False
        if self.current_title == "RXLZQ - Through the Screen":
            self.game.blit(self.background, (0,0))
            self.HoM_surface = pg.Surface((self.screen_w, self.screen_h))
            self.isHoM = True
            self.isMoving = True
        else:
            self.isMoving = False
            self.isHoM = False
            self.isTransparent = False
                
    def song_switch(self):
        # Switches the song based on user input
        pg.mixer.music.stop()
        pg.mixer.music.unload()
        self.current_song = self.filenames[self.current_song_index]
        self.current_title = self.titles[self.current_song_index]
        self.songSecond = AudioSegment.from_file(self.current_song)
        self.song_length_seconds = self.songSecond.duration_seconds
        self.start_song()

    def display(self):
        # Screen display
        self.avg_bass = 0
        self.poly = []
        if self.isHoM == True:
            if self.frame_count >= 5:
                self.HoM_surface.fill((0,0,0))
        else:
            self.game.fill(CIRCLE_COLOR)
        self.current_time = pg.mixer.music.get_pos() / 1000.0

        # Calculate delta time
        self.t = pg.time.get_ticks()
        self.deltaTime = (self.t - self.getTicksLastFrame) / 1000.0
        self.getTicksLastFrame = self.t
        self.timeCount += self.deltaTime

        # Update audio bars
        for b1 in self.bars:
            for b in b1:
                b.update_all(self.deltaTime, pg.mixer.music.get_pos() / 1000.0, self.analyzer)

        # Calculate average bass level
        for b in self.bars[0]:
            self.avg_bass += b.avg
        self.avg_bass /= len(self.bars[0])

        # Adjust radius and color based on bass level
        if self.avg_bass > BASS_TRIGGER:
            if self.bass_trigger_started == 0:
                self.bass_trigger_started = pg.time.get_ticks()
            if (pg.time.get_ticks() - self.bass_trigger_started) / 1000.0 > 2:
                self.polygon_bass_color = self.rnd_color()
                self.bass_trigger_started = 0
            if self.polygon_bass_color is None:
                self.polygon_bass_color = self.rnd_color()
                if self.isMoving == True:
                    self.slide = MIN_RADIUS//2 + int(self.avg_bass * ((MAX_RADIUS - MIN_RADIUS) / (self.max_decibel - self.min_decibel)) + (MAX_RADIUS - MIN_RADIUS) + random.choice([0,5,10,25]))
                    self.slide_val += random.choice([self.slide,self.slide])
                if self.slide_val <= -(self.screen_w//2)-(self.radius//2):
                    self.slide_val = self.screen_w//2
                elif self.slide_val >= (self.screen_w//2)+(self.radius//2):
                    self.slide_val = -self.screen_w//2
            newr = MIN_RADIUS + int(self.avg_bass * ((MAX_RADIUS - MIN_RADIUS) / (self.max_decibel - self.min_decibel)) + (MAX_RADIUS - MIN_RADIUS))
            self.radius_vel = (newr - self.radius) / 0.15
            self.polygon_color_vel = [(self.polygon_bass_color[x] - self.poly_color[x]) / 0.15 for x in range(len(self.poly_color))]
        elif self.radius > MIN_RADIUS:
            self.bass_trigger_started = 0
            self.polygon_bass_color = None
            self.radius_vel = (MIN_RADIUS - self.radius) / 0.15
            self.polygon_color_vel = [(POLYGON_DEFAULT_COLOR[x] - self.poly_color[x]) / 0.15 for x in range(len(self.poly_color))]
        else:
            self.polygon_bass_color = None
            self.polygon_color_vel = [0, 0, 0]
            self.bass_trigger_started = 0
            self.poly_color = POLYGON_DEFAULT_COLOR.copy()
            self.radius_vel = 0
            self.radius = MIN_RADIUS

        # Update radius and color
        self.radius += self.radius_vel * self.deltaTime
        for x in range(len(self.polygon_color_vel)):
            value = self.polygon_color_vel[x] * self.deltaTime + self.poly_color[x]
            self.poly_color[x] = value

        # Update bar positions and draw polygons
        for b1 in self.bars:
            for b in b1:
                b.x, b.y = (self.screen_w // 2) + self.radius * math.cos(math.radians(b.angle - 90)) - self.slide_val, self.screen_h // 2 + self.radius * math.sin(math.radians(b.angle - 90))
                b.update_rect()
                self.poly.extend([(b.rect.points[3][0], b.rect.points[3][1]), (b.rect.points[2][0], b.rect.points[2][1])])
        try:
            self.poly = [(np.float64(x), np.float64(y)) for x, y in self.poly]
            pg.draw.polygon(self.game, self.poly_color, self.poly)
            if self.timeout >= 4:
                self.running = False
                print(f"ERROR TIMEOUT (Error Code: ASS_PAIN) Trys: {self.timeout}")
                quit()
        except ValueError:
            self.poly_color = POLYGON_DEFAULT_COLOR
            print("LOG: PolyColor Error")
            self.timeout += 1

        # Draw the circle
        pg.draw.circle(self.game, CIRCLE_COLOR, (self.screen_w / 2 - self.slide_val, self.screen_h / 2), int(self.radius))
        self.text_display()
        if int(self.current_time) >= int(self.song_length_seconds):
            self.current_song_index += 1
            self.song_switch()
        pg.display.flip()
        self.timeout = 0
        self.frame_count += 1
        