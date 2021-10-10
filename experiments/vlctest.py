from vlc import Instance
import time
import os
import glob

class VLC:
    def __init__(self):
        self.Player = Instance('--loop')

    def addPlaylist(self):
        self.mediaList = self.Player.media_list_new()
        for s in glob.glob("*/*.mp4"):
            self.mediaList.add_media(self.Player.media_new(s))
        self.listPlayer = self.Player.media_list_player_new()
        self.listPlayer.set_media_list(self.mediaList)
    def play(self):
        self.listPlayer.play()
    def next(self):
        self.listPlayer.next()
    def pause(self):
        self.listPlayer.pause()
    def previous(self):
        self.listPlayer.previous()
    def stop(self):
        self.listPlayer.stop()

player = VLC()
player.addPlaylist()
player.play()
for i in range(0,100):
    time.sleep(4)
    print(i);
    player.next()

