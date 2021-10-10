import vlc
import time
import os
import glob

inst=vlc.Instance()
media=inst.media_player_new("output2.mp4")
media.play()
print("Seekable: ",media.is_seekable())
print("Length:   ",media.get_length())
print("Chapters: ",media.get_chapter_count())
for i in range(0,100):
 media.set_chapter(i)
 time.sleep(10)
 #media.set_time(i*1000)
 print("Time:     ",media.get_time()) 
