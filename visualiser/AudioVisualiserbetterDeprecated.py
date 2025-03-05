from AudioAnalyzer import *
import random
import colorsys
from pydub import AudioSegment
import numpy as np
import math
import time
import json
from mss import mss
import win32api,win32gui,win32con
import pygame
from constants import *

def minimize_all_windows():
    win32api.keybd_event(0x5B, 0, ) # LWIN
    win32api.keybd_event(0x44, 0, ) # D
    win32api.keybd_event(0x5B, 0, 2) 
    win32api.keybd_event(0x44, 0, 2)
    time.sleep(2)
    with mss() as scr:
        scr.shot()

def find_and_focus_pygame_window():
    # Definiáljuk a keresett ablak nevét
    window_name = "pygame window"

    # Keresés az ablakok között
    hwnd = win32gui.FindWindow(None, window_name)

    if hwnd:
        # Ha megtaláltuk az ablakot, fókuszálunk rá
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Abla helyreállítása, ha minimalizálva van
        win32gui.SetForegroundWindow(hwnd)  # Fókuszálás az ablakra
        print(f"A '{window_name}' ablak fókuszálva lett.")
    else:
        print(f"A '{window_name}' ablak nem található.")

isInsomnia = False

# Function to generate a random color
def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    if isInsomnia:
        s = 1
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]

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

# Initialize Pygame
pygame.init()
minimize_all_windows()
infoObject = pygame.display.Info()
screen_w = infoObject.current_w
screen_h = infoObject.current_h
screen = pygame.display.set_mode([screen_w, screen_h], pygame.NOFRAME | pygame.SRCALPHA)
font = pygame.font.Font(None, 36)
loading_text = font.render("Loading", True, (255,255,255))
screen.blit(loading_text, (0,0))
pygame.display.flip()
# Futtatjuk a funkciót
find_and_focus_pygame_window()
current_song_index = 8
current_song_title = titles[current_song_index]
current_song_hash = filenames[current_song_index]

# Create audio analyzer
analyzer = AudioAnalyzer()
analyzer.load(filenames[current_song_index])

# Initialize variables
t = pygame.time.get_ticks()
getTicksLastFrame = t
timeCount = 0
avg_bass = 0
bass_trigger_started = 0
polygon_bass_color = None
polygon_color_vel = [0, 0, 0]
poly_color = POLYGON_DEFAULT_COLOR.copy()
radius = MIN_RADIUS
radius_vel = 0
min_decibel = -80
max_decibel = 80

def desaturate(surface, saturation_factor):
    # Screen to Pixel Data
    arr = pygame.surfarray.array3d(surface)
    # Grey scale
    gray = np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140])
    # Saturation
    global rdata
    desaturated = gray[..., np.newaxis] + (arr - gray[..., np.newaxis]) * saturation_factor
    rdata = pygame.surfarray.make_surface(desaturated.astype(np.uint8))
    return pygame.surfarray.make_surface(desaturated.astype(np.uint8))


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
            screen_w // 2 + radius * math.cos(math.radians(ang - 90)),
            screen_h // 2 + radius * math.sin(math.radians(ang - 90)),
            c, (255, 0, 255), angle=ang, width=8, max_height=370
        ))
        ang += angle_dt
    bars.append(gr)
isSpecial = True

with open("Configs.json", 'r') as f:
    json_data = json.load(f)
    settings: dict = json_data.get("settings")
isMoving,isTransparent,isOne,isPlaylist = settings.values()
default_isMoving,default_isTransparent,default_isOne,default_isPlaylist = isMoving,isTransparent,isOne,isPlaylist
isSakuya = False
isMash = False

if isSpecial == True:
    isTransparent = False
    if current_song_title == "RXLZQ - Through the Screen":
        isMash = True
        isMoving = True
        transparent_surface = pygame.Surface((screen_w, screen_h))
        transparent_surface.fill((0, 0, 0))
    elif current_song_title == "Night of Nights (Flowering nights remix)  By COOL&CREATEbeatMARIO":
        isSakuya = True
        isMash = False
        isTransparent = False
        isMoving = False
        sakuya_pic = pygame.image.load("sakuya.png")
        sakuya_head_pic = pygame.image.load("sakuya_head.png")

background = pygame.image.load("monitor-1.png")
sakuya_pic = pygame.image.load("sakuya.png")



# Load and play music
songSecond = AudioSegment.from_file(filenames[current_song_index])
song_length_seconds = songSecond.duration_seconds
pygame.mixer.music.load(filenames[current_song_index])
pygame.mixer.music.play(0)

# Progress bar settings
progress_bar_width = screen_w
progress_bar_height = 10
progress_bar_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_width, progress_bar_height)



if __name__ == "__main__":
    frame_count = 0
    current_song = current_song_index
    slide_val = 0
    slide_to_middle = False
    index = 0


    # Main loop
    running = True
    while running:
        avg_bass = 0
        poly = []
        if isTransparent:
            screen.blit(background, (0,0))
        elif isMash:
            if index == 10:
                screen.blit(transparent_surface, (0, 0))
            else:
                index += 1
                screen.blit(background, (0,0))
        else:
            screen.fill(CIRCLE_COLOR)

        # Calculate delta time
        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t
        timeCount += deltaTime
        
        if current_song_index != len(filenames):    
            if current_song_index != current_song:
                isMoving,isTransparent,isOne,isPlaylist = default_isMoving,default_isTransparent,default_isOne,default_isPlaylist
                poly_color = POLYGON_DEFAULT_COLOR.copy()
                pygame.mixer.music.unload()
                analyzer.load(filenames[current_song_index])
                pygame.mixer.music.load(filenames[current_song_index])
                pygame.mixer.music.play(0)
                print(f"Playing song: {filenames[current_song_index]} || {current_song_index} || {len(filenames)}")
                songSecond = AudioSegment.from_file(filenames[current_song_index])
                song_length_seconds = songSecond.duration_seconds
                current_song = current_song_index
                current_song_title = titles[current_song].strip("music\\.wav")
                if isSpecial:
                    isTransparent = False
                    isSakuya = False
                    isMash = False
                    isMoving = False
                    if current_song_title == "RXLZQ - Through the Screen":
                        isMoving = True
                        isMash = True
                        screen.fill(CIRCLE_COLOR)
                        screen.blit(background, (0,0))
                        transparent_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
                        transparent_surface.fill((0, 0, 0, 0))
                    elif current_song_title == "Night of Nights (Flowering nights remix)  By COOL&CREATEbeatMARIO":
                        isSakuya = True
                        sakuya_pic = pygame.image.load("sakuya.png")
                        sakuya_head_pic = pygame.image.load("sakuya_head.png")
        else:
            break

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_song_index = current_song_index + 1
                    time.sleep(0.1)
            if event.type == pygame.QUIT:
                running = False


        # Update audio bars
        for b1 in bars:
            for b in b1:
                b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)

        # Calculate average bass level
        for b in bars[0]:
            avg_bass += b.avg
        avg_bass /= len(bars[0])

        # Adjust radius and color based on bass level
        if avg_bass > BASS_TRIGGER:
            if bass_trigger_started == 0:
                bass_trigger_started = pygame.time.get_ticks()
            if (pygame.time.get_ticks() - bass_trigger_started) / 1000.0 > 2:
                polygon_bass_color = rnd_color()
                bass_trigger_started = 0
            if polygon_bass_color is None:
                polygon_bass_color = rnd_color()
                if isMoving == True:
                    slide = MIN_RADIUS//2 + int(avg_bass * ((MAX_RADIUS - MIN_RADIUS) / (max_decibel - min_decibel)) + (MAX_RADIUS - MIN_RADIUS) + random.choice([-25,-10,-5,0,5,10,25]))
                    slide_val += random.choice([slide,-slide])
            newr = MIN_RADIUS + int(avg_bass * ((MAX_RADIUS - MIN_RADIUS) / (max_decibel - min_decibel)) + (MAX_RADIUS - MIN_RADIUS))
            radius_vel = (newr - radius) / 0.15
            polygon_color_vel = [(polygon_bass_color[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]
        elif radius > MIN_RADIUS:
            bass_trigger_started = 0
            polygon_bass_color = None
            radius_vel = (MIN_RADIUS - radius) / 0.15
            polygon_color_vel = [(POLYGON_DEFAULT_COLOR[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]
        else:
            bass_trigger_started = 0
            poly_color = POLYGON_DEFAULT_COLOR.copy()
            polygon_bass_color = None
            polygon_color_vel = [0, 0, 0]
            radius_vel = 0
            radius = MIN_RADIUS


        # Update radius and color
        radius += radius_vel * deltaTime
        for x in range(len(polygon_color_vel)):
            value = polygon_color_vel[x] * deltaTime + poly_color[x]
            poly_color[x] = value

        # Update bar positions and draw polygons
        for b1 in bars:
            for b in b1:
                b.x, b.y = (screen_w // 2) + radius * math.cos(math.radians(b.angle - 90)) - slide_val, screen_h // 2 + radius * math.sin(math.radians(b.angle - 90))
                b.update_rect()
                poly.extend([(b.rect.points[2][0], b.rect.points[2][1]), (b.rect.points[1][0], b.rect.points[1][1])])
        poly = [(np.float64(x), np.float64(y)) for x, y in poly]
        pygame.draw.polygon(screen, poly_color, poly)

        # Draw the circle
        pygame.draw.circle(screen, CIRCLE_COLOR, (screen_w / 2 - slide_val, screen_h / 2), int(radius))


        # Draw progress bar
        current_time = pygame.mixer.music.get_pos() / 1000.0
        progress_bar_fill_width = int((current_time / song_length_seconds) * progress_bar_width)
        progress_bar_fill_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_fill_width, progress_bar_height)
        if isSakuya:
            screen.blit(sakuya_pic, (10, (screen_h/2) - (sakuya_pic.get_height())/2))
            screen.blit(sakuya_head_pic, (progress_bar_fill_width - (sakuya_head_pic.get_width() / 2), screen_h - (sakuya_head_pic.get_height() - progress_bar_height) - 10))
        pygame.draw.rect(screen, (0, 255, 0), progress_bar_fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), progress_bar_rect, 1)

        # Display time
        song_length_text1 = font.render(f"{int(current_time // 60)}:{int(current_time % 60):02}", True, (255, 255, 255))
        current_song_text = font.render(f"{int(current_song+1)}/{len(titles)}", True, (255,255,255))
        current_song_title_text = font.render(f"{str(current_song_title)}", True, (255,255,255))
        song_length_text2 = font.render(f"/{int(song_length_seconds // 60)}:{int(song_length_seconds % 60):02}", True, (128,128,128))
        screen.blit(current_song_text, (screen_w - current_song_text.get_width() - 10, screen_h - current_song_text.get_height() - song_length_text1.get_height() - 10))
        screen.blit(song_length_text2, (screen_w - song_length_text2.get_width() - 10, screen_h - song_length_text2.get_height() - 10))
        screen.blit(song_length_text1, (screen_w - song_length_text1.get_width() - song_length_text2.get_width() - 10, screen_h - song_length_text1.get_height() - 10))
        screen.blit(current_song_title_text, ((screen_w / 2) - (current_song_title_text.get_width() / 2), current_song_title_text.get_height() - 20))


        if int(current_time) >= int(song_length_seconds):
            current_song_index += 1

        # Update the display
        # Update desaturated surface every 5 frames
        #if frame_count % 50 == 0:
        #    desaturated_surface = desaturate(screen, 0.5)
        #screen.blit(desaturated_surface, (0, 0))
        pygame.display.flip()
        frame_count += 1

    # Quit Pygame
    pygame.quit()
    #song_controller_process.join()
