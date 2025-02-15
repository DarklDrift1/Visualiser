from youtubedl import Download
import subprocess
import os

def main():
    url = input("URL: ")
    fname = "dlsong.mp3"

    downloadSong = Download(url,fname)
    downloadSong.start()

    fwav = fname.replace('.mp3', '.wav')
    subprocess.call(['ffmpeg', '-i', "musics\\"+fname, "musics\\"+fwav])
    os.remove("musics\\"+fname)
    with open('musics\song.txt', 'w') as file:
        file.write(fwav)
    subprocess.call(['python', 'visualiser\\audioVisualiser.py'])
    os.remove("musics\\"+fwav)

if __name__ == "__main__":
    main()
    input("Press Enter to close!!!")