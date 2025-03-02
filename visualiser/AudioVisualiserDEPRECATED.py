from AudioAnalyzer import *
import random
import colorsys
from pydub import AudioSegment
import numpy as np
import multiprocessing as mp


def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]

filenames = list()
index = 0
with open("musics\\song.txt", "r", encoding='UTF-8') as f:
    for song in f:
        filenames.append("musics\\"+song.strip('\n'))
        index += 1
    print(filenames)
current_song = 0
analyzer = AudioAnalyzer()
analyzer.load(filenames[current_song])

pygame.init()

infoObject = pygame.display.Info()

screen_w = int(infoObject.current_w/2.2)
screen_h = int(infoObject.current_h/2.2)
screen_w = int(infoObject.current_w)
screen_h = int(infoObject.current_h)


screen = pygame.display.set_mode([screen_w, screen_h], pygame.NOFRAME | pygame.SRCALPHA)

t = pygame.time.get_ticks()
getTicksLastFrame = t

timeCount = 0

avg_bass = 0
bass_trigger = -30
bass_trigger_started = 0

min_decibel = -80
max_decibel = 80

circle_color = (40, 40, 40)
polygon_default_color = [255, 255, 255]
polygon_bass_color = polygon_default_color.copy()
polygon_color_vel = [0, 0, 0]

poly = []
poly_color = polygon_default_color.copy()

circleX = int(screen_w / 2)
circleY = int(screen_h/2)

min_radius = 100
max_radius = 150
radius = min_radius
radius_vel = 0


bass = {"start": 50, "stop": 100, "count": 12}
heavy_area = {"start": 120, "stop": 250, "count": 40}
low_mids = {"start": 251, "stop": 2000, "count": 50}
high_mids = {"start": 2001, "stop": 6000, "count": 20}

freq_groups = [bass, heavy_area, low_mids, high_mids]


bars = []

tmp_bars = []


length = 0

for group in freq_groups:

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


angle_dt = 360/length

ang = 0

for g in tmp_bars:
    gr = []
    for c in g:
        gr.append(
            RotatedAverageAudioBar(circleX+radius*math.cos(math.radians(ang - 90)), circleY+radius*math.sin(math.radians(ang - 90)), c, (255, 0, 255), angle=ang, width=8, max_height=370))
        ang += angle_dt

    bars.append(gr)

progress_bar_width = screen_w
progress_bar_height = 10
progress_bar_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_width, progress_bar_height)
songSecond = AudioSegment.from_file(filenames[current_song])
song_length_seconds = songSecond.duration_seconds - 130
print(songSecond.duration_seconds)

pygame.mixer.music.load(filenames[current_song])
pygame.mixer.music.play(0)

running = True
while running:
    avg_bass = 0
    poly = []

    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    timeCount += deltaTime

    screen.fill(circle_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    songSecond = AudioSegment.from_file(filenames[current_song])
    song_length_seconds = songSecond.duration_seconds

    for b1 in bars:
        for b in b1:
            b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)

    for b in bars[0]:
        avg_bass += b.avg

    avg_bass /= len(bars[0])

    if avg_bass > bass_trigger:
        if bass_trigger_started == 0:
            bass_trigger_started = pygame.time.get_ticks()
        if (pygame.time.get_ticks() - bass_trigger_started)/1000.0 > 2:
            polygon_bass_color = rnd_color()
            bass_trigger_started = 0
        if polygon_bass_color is None:
            polygon_bass_color = rnd_color()
        newr = min_radius + int(avg_bass * ((max_radius - min_radius) / (max_decibel - min_decibel)) + (max_radius - min_radius))
        radius_vel = (newr - radius) / 0.15

        polygon_color_vel = [(polygon_bass_color[x] - poly_color[x])/0.15 for x in range(len(poly_color))]

    elif radius > min_radius:
        bass_trigger_started = 0
        polygon_bass_color = None
        radius_vel = (min_radius - radius) / 0.15
        polygon_color_vel = [(polygon_default_color[x] - poly_color[x])/0.15 for x in range(len(poly_color))]

    else:
        bass_trigger_started = 0
        poly_color = polygon_default_color.copy()
        polygon_bass_color = None
        polygon_color_vel = [0, 0, 0]

        radius_vel = 0
        radius = min_radius

    radius += radius_vel * deltaTime

    for x in range(len(polygon_color_vel)):
        value = polygon_color_vel[x]*deltaTime + poly_color[x]
        poly_color[x] = value

    for b1 in bars:
        for b in b1:
            b.x, b.y = circleX+radius*math.cos(math.radians(b.angle - 90)), circleY+radius*math.sin(math.radians(b.angle - 90))
            b.update_rect()
            with open('barokWTest.txt', 'a') as f:
                f.write(f"{[(b.rect.points[3][0], b.rect.points[3][1]), (b.rect.points[2][0], b.rect.points[2][1])]}  \n")
            poly.extend([(b.rect.points[3][0], b.rect.points[3][1]), (b.rect.points[2][0], b.rect.points[2][1])])
    poly = [(float(x), float(y)) for x, y in poly]
    pygame.draw.polygon(screen, poly_color, poly)
    pygame.draw.circle(screen, circle_color, (circleX, circleY), int(radius))
    current_time = pygame.mixer.music.get_pos() / 1000.0
    progress_bar_fill_width = int((current_time / song_length_seconds) * progress_bar_width)
    progress_bar_fill_rect = pygame.Rect(0, screen_h - progress_bar_height, progress_bar_fill_width, progress_bar_height)
    pygame.draw.rect(screen, (0, 255, 0), progress_bar_fill_rect)
    pygame.draw.rect(screen, (255, 255, 255), progress_bar_rect, 1)
    font = pygame.font.Font(None, 36)
    song_length_text1 = font.render(f"{int(current_time // 60)}:{int(current_time % 60):02}", True, (80, 80, 80))
    song_length_text2 = font.render(f"/", True, (160, 160, 160))
    song_length_text3 = font.render(f"{int(song_length_seconds // 60)}:{int(song_length_seconds % 60):02}", True, (255, 255, 255))
    screen.blit(song_length_text1, (10,10))
    screen.blit(song_length_text2, (60,10))
    screen.blit(song_length_text3, (70,10))
    if int(current_time) >= int(5):
        break
    pygame.display.flip()

pygame.quit()