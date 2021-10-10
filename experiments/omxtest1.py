from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

VIDEO_PATH = Path("output2.mp4")

player = OMXPlayer(VIDEO_PATH)

print ("Metadata: ",player.metadata())

for i in range(0,100):
    sleep(5)
    player.set_position(i)

player.quit()
