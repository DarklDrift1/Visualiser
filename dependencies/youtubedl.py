from pytubefix import YouTube,Playlist
from moviepy import *

class VideoDownloader:
    def __init__(self, url, fname, isPlaylist = False):
        self.url = url
        self.isPlaylist = isPlaylist
        self.fname = fname

    def download(self, nurl):
        yt = YouTube(nurl)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(filename=self.fname,output_path=f"musics\\")

    def start(self):
        pass

    def playlist_to_urls(self):
        p = Playlist(self.url)
        urls,titles = list(), list()
        for video in p.videos:
            urls.append(video.video_id)
            titles.append(video.title)
            print(video.title)
        return urls, titles
    
    

if __name__ == "__main__":
    dl = VideoDownloader("https://www.youtube.com/watch?v=AKF2K6vXEFk&list=PLGI4nDstEmlEBwU2Ntk0BtySTmBTF-aM-&pp=gAQB", "test.mp3")
    print("__Testing__")
    dl.download("https://www.youtube.com/watch?v=mwDpWBn_lZU")
