from dependencies.youtubedl import VideoDownloader
import subprocess
import os


def mainT():
    uInput = str(input("URL (Playlist or Video): "))   
    fname = "song.mp3"
    download = VideoDownloader(uInput,f"{fname}")
    urls,titles  = list(download.playlist_to_urls())
    playlist = list()

    for i in range(len(urls)):
        song = {"url": urls[i], "title": titles[i]}
        playlist.append(song)

    with open('musics\\song.txt', 'w', encoding='UTF-8') as file:
            for video in playlist:
                video: dict
                title = video.get('title')
                download.download('https://www.youtube.com/watch?v='+video.get('url'))
                fwav = title+".wav"
                subprocess.call(['ffmpeg\\bin\\ffmpeg.exe', '-i', "musics\\"+fname, "musics\\"+fwav])
                os.remove("musics\\"+fname)
                file.write(f"{fwav}\n")


    subprocess.call('visualiser\\AudioVisualiser.exe')
    #for video in playlist:
    #    os.remove("musics\\"+str(video.get['title'])+".wav")
    print("DONE...")



if __name__ == "__main__":
    mainT()