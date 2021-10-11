from bottle import route, run
import logging
import subprocess
from glob import glob
import os.path
import time
import sys
from threading import Thread

from trigger import Trigger

player=None
bgplayer=None

bgfile=None 

metadata={}
triggers = []

playing = {
    "file": None,
    "priority": -1,
    }

screens = ["12"]

class Looper(Thread):
    
    def __init__(self):
        super().__init__()
        self.stop = False
        
    def run(self):
        global playing
        global player
        
        while not self.stop:
            time.sleep(0.02)
            if player is not None:
                if player.poll() is None:
                    # player still running
                    logging.debug("player still running")
                    continue
                
                logging.info("Playback of current video has been terminated")
                # player has been terminated
                player = None
                playing["file"]= None,
                playing["priority"]= -1,
        

def fileinfo(filename):
    filename=filename.lower()
    if filename.endswith(".h264"):
        filename=filename[:-5]

    return metadata[filename]


def play_file(filename, loop=False, priority=-1):
    global player
    try:
        oldplayer=None
        if player is not None:
            oldplayer=player

        absfile=fileinfo(filename)["file"]
  
        if loop:
            player=subprocess.Popen(["../hello_video.bin", "--loop", absfile]) 
        else:
            player=subprocess.Popen(["../hello_video.bin", absfile])
            
        playing["file"]=filename
        playing["priority"]=priority   

        # If another video is playing, stop it
        if oldplayer is not None:
            oldplayer.kill()
            
        # if a background loop is playing, stop it
        stop_bgplayer()     

        logging.debug("Started player")
    except Exception as e:
        logging.error("%s", e)
        
def play_background(filename):
    global bgplayer
    
    stop_bgplayer()
    absfile=fileinfo(filename)["file"]
    bgplayer=subprocess.Popen(["../hello_video.bin", "--loop", absfile]) 
         
def stop_player():
    global player
    if player is not None:
        player.kill()
        player = None
        playing["file"]=None
        playing["priority"]=-1
        
def stop_bgplayer():
    global bgplayer
    if bgplayer is not None:
        bgplayer.kill()
        bgplayer = None
   
def process_triggers(event):
    found=False
    for t in triggers:
        logging.debug("Checking %s",t)
        if t.screennum in screens and t.trigger == event:
            found = True
            logging.debug("Processing trigger %s", t)
            process_trigger(t)
            
    if not found:
        logging.error("Trigger %s not found", event)

         
        
def process_trigger(t):
    
    if t.loop=="StopFile":
        if playing["file"]==t.playfile:
            logging.debug("Stopping playback of %s", t.playfile)
            stop_player()
            
    elif t.loop=="StopPlayer":
        if t.priority > playing["priority"]:
            stop_player 
            
    elif t.loop=="Normal" or t.loop=="":
        play_file(t.playfile, loop=False, priority=t.priority)
            
    elif t.loop=="Loop":
        play_file(t.playfile, loop=True, priority=t.priority)
        
    elif t.loop=="SkipSamePrty":
        if playing["priority"] != t.priority:
            logging.debug("Start playback of %s, priority %s",
                          t.playfile, playing["file"],t.priority)
            play_file(t.playfile, loop=False, priority=t.priority)
        else:
            logging.debug("Skipping %s as file %s with same priority %s is already playing",
                          t.playfile, playing["file"],t.priority)
    else:
        logging.info("Trigger loop type %s not yet implemented", t.loop)
                
            
            
@route('/play/<filename>')
def api_play(filename):
    play_file(filename,loop=False)
    
@route('/loop/<filename>')
def api_loop(filename):
    play_file(filename,loop=False)
    
@route('/trigger/<event>')
def api_trigger(event):
    process_triggers(event)
    
def read_files(basedir):
    global triggers
    
    ## Get a list of all files
    for f in glob(basedir+"/*/*.h264"):
        key=os.path.basename(f)[:-5].lower()
        logging.error(key)
        metadata[key]={"file": os.path.abspath(f)}
        
    ## Read the triggers
    with open(basedir+"/triggers.pup", 'r', encoding='utf-8') as infile:
        for line in infile:
            t = Trigger(line)
            triggers.append(t)
            logging.debug("Added trigger %s", t)
            
def main():
    try:
        datadir=sys.argv[1]
    except:
        datadir="."

    logging.basicConfig(level=logging.DEBUG)
    read_files(datadir)

    looperthread=Looper()
    looperthread.start()

    run(host="localhost", port=5000)
    


if __name__ == '__main__':
    main()

