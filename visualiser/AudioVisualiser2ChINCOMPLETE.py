from AudioAnalyzer import *
import random
import colorsys
from pydub import AudioSegment
import numpy as np
import multiprocessing as mp
import pygame
import math
import time
import wave

# Constants for visual settings
CIRCLE_COLOR = (40, 40, 40)
POLYGON_DEFAULT_COLOR = [255, 255, 255]
MIN_RADIUS = 100
MAX_RADIUS = 150
BASS_TRIGGER = -30

# Frequency band definitions
FREQ_GROUPS = [
    {"start": 50, "stop": 100, "count": 12},
    {"start": 120, "stop": 250, "count": 40},
    {"start": 251, "stop": 2000, "count": 50},
    {"start": 2001, "stop": 6000, "count": 20},
]

# Function to generate a random color
def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]

def save_wav_channel(fn, wav, channel):
    '''
    Take Wave_read object as an input and save one of its
    channels into a separate .wav file.
    '''
    # Read data
    nch   = wav.getnchannels()
    depth = wav.getsampwidth()
    wav.setpos(0)
    sdata = wav.readframes(wav.getnframes())

    # Extract channel data (24-bit data not supported)
    typ = { 1: np.uint8, 2: np.uint16, 4: np.uint32 }.get(depth)
    if not typ:
        raise ValueError("sample width {} not supported".format(depth))
    if channel >= nch:
        raise ValueError("cannot extract channel {} out of {}".format(channel+1, nch))
    print ("Extracting channel {} out of {} channels, {}-bit depth".format(channel+1, nch, depth*8))
    data = np.fromstring(sdata, dtype=typ)
    ch_data = data[channel::nch]

    # Save channel to a separate file
    outwav = wave.open(fn, 'w')
    outwav.setparams(wav.getparams())
    outwav.setnchannels(1)
    outwav.writeframes(ch_data.tostring())
    outwav.close()

# Load audio files
filenames = []
with open("musics\\song.txt", "r", encoding='UTF-8') as f:
    for song in f:
        filenames.append("musics\\" + song.strip('\n'))
print(filenames)

#wav = wave.open(filenames[0])
#save_wav_channel('ch1.wav', wav, 0)
#save_wav_channel('ch2.wav', wav, 1)
audio = AudioSegment.from_file(filenames[0])
left, right = audio.split_to_mono()
left_balance_adjusted = left.apply_gain_stereo(+2, -99)
right_balance_adjusted = right.apply_gain_stereo(-99, +2)
file_handle = left_balance_adjusted.export("left.wav", format="wav")
file_handle = right_balance_adjusted.export("right.wav", format="wav")
print(left, right)

# Initialize Pygame
pygame.init()
infoObject = pygame.display.Info()
screen_w = infoObject.current_w
screen_h = infoObject.current_h
screen = pygame.display.set_mode([screen_w, screen_h], pygame.NOFRAME | pygame.SRCALPHA)

# Create audio analyzer
analyzer_left = AudioAnalyzer()
analyzer_left.load('left.wav')
analyzer_right = AudioAnalyzer()
analyzer_right.load('right.wav')
#analyzer_right.show()
#analyzer_left.show()

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

# Create audio bars
bars_left = []
tmp_bars_l = []
bars_right = []
tmp_bars_r = []
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

    tmp_bars_l.append(g)

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

    tmp_bars_r.append(g)

ang = 0
angle_dt = 360/length

for g in tmp_bars_l:
    gr = []
    for c in g:
        gr.append(RotatedAverageAudioBar(
            screen_w // 2 + radius * math.cos(math.radians(ang - 90)),
            screen_h // 2 + radius * math.sin(math.radians(ang - 90)),
            c, (255, 0, 255), angle=ang, width=8, max_height=370
        ))
        ang += angle_dt
    bars_left.append(gr)

for g in tmp_bars_r:
    gr = []
    for c in g:
        gr.append(RotatedAverageAudioBar(
            screen_w // 2 + radius * math.cos(math.radians(ang - 90)),
            screen_h // 2 + radius * math.sin(math.radians(ang - 90)),
            c, (255, 0, 255), angle=ang, width=8, max_height=370
        ))
        ang += angle_dt
    bars_right.append(gr)


with open('barsLeft.txt', 'w') as f:
    for bars in bars_left:
        for bar in bars:
            f.write(f"{bar.rng} \n")
with open('barsRight.txt', 'w') as f:
    for bars in bars_right:
        for bar in bars:
            f.write(f"{bar.rng} \n")

# Load and play music
songSecond = AudioSegment.from_file(filenames[0])
song_length_seconds = songSecond.duration_seconds
pygame.mixer.music.load(filenames[0])
pygame.mixer.music.play(0)

# Progress bar settings
progress_bar_width = screen_w
progress_bar_height = 10
progress_bar_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_width, progress_bar_height)

# Function to handle song changes
    #def song_controller():
    #    current_song_index = 0
    #    while True:
    #        for event in pygame.event.get():
    #            if event.type == pygame.KEYDOWN:
    #                if event.key == pygame.K_SPACE:
    #                    current_song_index = (current_song_index + 1) % len(filenames)
    #        time.sleep(0.1)
current_song_index = 0
current_song_title = filenames[current_song_index].strip("music\\.wav")
if __name__ == "__main__":
    # Create and start the song controller process
    #song_controller_process = mp.Process(target=song_controller)
    #song_controller_process.start()
    current_song = current_song_index

    # Main loop
    running = True
    while running:
        avg_bass = 0
        poly_left = []
        poly_right = []

        # Calculate delta time
        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t
        timeCount += deltaTime
        
        if current_song_index != len(filenames):    
            if current_song_index != current_song:
                time.sleep(2)
                poly_color = POLYGON_DEFAULT_COLOR.copy()
                pygame.mixer.music.unload()
                analyzer_left.load(filenames[current_song_index])
                pygame.mixer.music.load(filenames[current_song_index])
                pygame.mixer.music.play(0)
                print(f"Playing song: {filenames[current_song_index]} || {current_song_index} || {len(filenames)}")
                songSecond = AudioSegment.from_file(filenames[current_song_index])
                song_length_seconds = songSecond.duration_seconds
                current_song = current_song_index
                current_song_title = filenames[current_song].strip("music\\.wav")
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

        # Clear the screen
        screen.fill(CIRCLE_COLOR)

        # Update audio bars
        for b1_l in bars_left:
            for b_l in b1_l:
                b_l.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer_left)

        # Update audio bars
        for b1_r in bars_right:
            for b_r in b1_r:
                b_r.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer_right)

        # Calculate average bass level
        for b in bars_left[0]:
            avg_bass += b.avg
        avg_bass /= len(bars_left[0])

        # Adjust radius and color based on bass level
        if avg_bass > BASS_TRIGGER:
            if bass_trigger_started == 0:
                bass_trigger_started = pygame.time.get_ticks()
            if (pygame.time.get_ticks() - bass_trigger_started) / 1000.0 > 2:
                polygon_bass_color = rnd_color()
                bass_trigger_started = 0
            if polygon_bass_color is None:
                polygon_bass_color = rnd_color()
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
        for b1 in bars_left:
            for b in b1:
                b.x, b.y = (screen_w // 2) + radius * math.cos(math.radians(b.angle - 90)), screen_h // 2 + radius * math.sin(math.radians(b.angle - 90))
                b.update_rect()
                poly_left.extend([(b.rect.points[3][0], b.rect.points[3][1]), (b.rect.points[2][0], b.rect.points[2][1])])
        poly_left = [(float(x), float(y)) for x, y in poly_left]
        pygame.draw.polygon(screen, poly_color, poly_left)

        # Draw the circle
        pygame.draw.circle(screen, CIRCLE_COLOR, (screen_w // 2, screen_h // 2), int(radius))

        # Draw progress bar
        current_time = pygame.mixer.music.get_pos() / 1000.0
        progress_bar_fill_width = int((current_time / song_length_seconds) * progress_bar_width)
        progress_bar_fill_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_fill_width, progress_bar_height)
        pygame.draw.rect(screen, (0, 255, 0), progress_bar_fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), progress_bar_rect, 1)

        # Display time
        font = pygame.font.Font(None, 36)
        song_length_text1 = font.render(f"{int(current_time // 60)}:{int(current_time % 60):02}", True, (255, 255, 255))
        current_song_text = font.render(f"{int(current_song+1)}/{len(filenames)}", True, (255,255,255))
        current_song_title_text = font.render(f"{str(current_song_title)}", True, (255,255,255))
        song_length_text2 = font.render(f"/{int(song_length_seconds // 60)}:{int(song_length_seconds % 60):02}", True, (128,128,128))
        screen.blit(current_song_text, (screen_w - current_song_text.get_width() - 10, screen_h - current_song_text.get_height() - song_length_text1.get_height() - 10))
        screen.blit(song_length_text2, (screen_w - song_length_text2.get_width() - 10, screen_h - song_length_text2.get_height() - 10))
        screen.blit(song_length_text1, (screen_w - song_length_text1.get_width() - song_length_text2.get_width() - 10, screen_h - song_length_text1.get_height() - 10))
        screen.blit(current_song_title_text, ((screen_w / 2) - (current_song_title_text.get_width() / 2), current_song_title_text.get_height() - 20))

        if int(current_time) >= int(song_length_seconds):
            break

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    #song_controller_process.join()
