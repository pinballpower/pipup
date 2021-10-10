from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
from glob import glob

VIDEO_PATH = "../../*/*.mp4"

files=glob(VIDEO_PATH)

playerold=None
player=None

for f in files:
#   if playerold is not None:
#      playerold.pause()
   player=OMXPlayer(f)
   sleep(0.3)
   if playerold is not None:
      playerold.quit()
   playerold=player
   sleep(1)
