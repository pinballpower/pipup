from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

VIDEO_PATH = Path("../../pupvideo.mp4")

player = {}

for i in range(0,100):
   print(i)
   p = OMXPlayer(VIDEO_PATH, args='--no-osd --no-keys -b')
   p.pause()
   player[i]=p
   sleep(1)

