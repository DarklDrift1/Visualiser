from pytubefix import YouTube
from moviepy import *

class Download:
    def __init__(self, url,fname):
        self.url = url
        self.fname = fname

    def start(self):
        yt = YouTube(self.url)

        audio_stream = yt.streams.filter(only_audio=True).first()


        audio_stream.download(filename=self.fname, output_path="musics\\")
    
    def ftitle(self):
        return YouTube(self.url).title()

if __name__ == "__main__":
    dl = Download("https://www.youtube.com/watch?v=vS_a8Edde8k", "test.mp3")
    print("__Testing__")
    dl.start()

