from dependencies.youtubedl import VideoDownloader
import subprocess
import os
import hashlib

hashtype = "MD5"
illegal_chars = ('*','>','<','\\','/','|','?',':','"')

def main_playlist():
    uInput = str(input("URL (Playlist or Video): "))   
    fname = "song.mp3"
    download = VideoDownloader(uInput,f"{fname}",True)
    urls,titles  = list(download.playlist_to_urls())
    playlist = list()

    for i in range(len(urls)):
        song = {"url": urls[i], "title": titles[i]}
        playlist.append(song)

    with open("musics\\songtitles.txt", 'w', encoding="UTF-8") as f:
        for video in playlist:
            video: dict
            title = video.get('title')
            for char in illegal_chars:
                title = title.replace(char, "")
                print(title)
            download.playlist_download('https://www.youtube.com/watch?v='+video.get('url'))
            fwav = title+".wav"
            subprocess.call(['ffmpeg\\bin\ffmpeg.exe', '-i', "musics\\"+fname, f"musics\\{fwav}"])
            os.remove("musics\\"+fname)
            fwav = fwav.replace(".wav", "")
            f.write(f"{fwav}\n")

    folder_hash()

    subprocess.call(['python', 'visualiser\\game.py'])
    print("DONE...")

def main_video():
    uInput = str(input("URL (Playlist or Video): "))   
    fname = "song.mp3"   
    download = VideoDownloader(uInput,f"{fname}")
    with open("musics\\songtitles.txt", 'w', encoding="UTF-8") as f:
        title = download.title()
        for char in illegal_chars:
                title = title.replace(char, "")
                print(title)
        download.vid_download()
        fwav = title+".wav"
        subprocess.call(['ffmpeg\\bin\\ffmpeg.exe', '-i', f'musics\\{fname}', f"musics\\{fwav}"])
        os.remove(f"musics\\{fname}")
        fwav = fwav.replace('.wav', "")
        f.write(f"{fwav}\n")
        
    folder_hash()

    subprocess.call(['python', 'visualiser\\game.py'])


def folder_hash():

    with open('musics\\songs.txt', 'w') as fw, open("musics\\songtitles.txt", 'r', encoding='UTF-8') as fr:
        for file in fr:
            file = file.replace('\n', '')
            path = os.path.join("musics", file+".wav")
            if os.path.isdir(path):
                wav_to_hash(path)
            else:
                 md5 = wav_to_hash(path)
            print(path)
            os.rename(path, f"musics\\{md5}.wav")
            fw.write(f"{md5}.wav\n")

def wav_to_hash(filth_path):
    with open(filth_path, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(1024*1024):
            file_hash.update(chunk)
    return file_hash.hexdigest()

main_video()