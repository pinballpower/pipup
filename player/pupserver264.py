from bottle import route, run
import logging
import subprocess
from glob import glob
import os.path
import time
import sys
from threading import Thread

try:
    from signal import SIGUSR1, SIGUSR2
except:
    logging.error("Can't use SIGUSR1 and SIGUSER2 on nin-UNIX-Systems")

from puppack import Trigger, Playlist

players =None
bgplayer=None

bgfile=None 

metadata={}
triggers = []
playlists = {}

playing = {
    "file": None,
    "priority": -1,
    }

screen = 0

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
                    continue
                
                logging.info("Playback of current video has been terminated")
                # player has been terminated
                player = None
                playing["file"]= None,
                playing["priority"]= -1,
                
                unpause_bgplayer()
        

def fileinfo(filename):
    filename=filename.lower()
    if filename.endswith(".h264"):
        filename=filename[:-5]

    return metadata[filename]


def play_file(playlist, filename, loop=False, priority=-1):
    global player
    
    if filename is None or filename=="":
        # Use the playlist instead
        try:
            pl=playlists[playlist]
            filename=os.path.basename(pl.next_file())
        except:
            logging.error("couldn't find any file for playlist %s",
                          playlist)
    
    if filename is None or filename=="":
        logging.info("ignoring playfile request for empty file name")
        return
    
    try:
        oldplayer=None
        if player is not None:
            oldplayer=player

        absfile=fileinfo(filename)["file"]
  
        if loop:
            player=subprocess.Popen(["../hello_video.bin", "-", absfile]) 
        else:
            player=subprocess.Popen(["../hello_video.bin", absfile])
            
        playing["file"]=filename
        playing["priority"]=priority   

        # If another video is playing, stop it
        if oldplayer is not None:
            oldplayer.kill()
            
        # if a background loop is playing, stop it
        pause_bgplayer()     

        logging.debug("Started player")
    except Exception as e:
        logging.error("%s", e)
        
def play_background(filename=None):
    global bgplayer
    global bgfile
    
    if filename is None:
        filename = bgfile
        
    bgfile=filename
    
    stop_bgplayer()
    stop_player()
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
    logging.debug("Killing background player")
    if bgplayer is not None:
        bgplayer.kill()
        bgplayer = None
        
def pause_bgplayer():
    global bgplayer
    if bgplayer is not None:
        try: 
            bgplayer.send_signal(SIGUSR1)
            logging.debug("Sent USR1 to background player")
        except:
            stop_bgplayer()
        

def unpause_bgplayer():
    global bgplayer
    if bgplayer is not None:
        try: 
            bgplayer.send_signal(SIGUSR2)
            logging.debug("Sent USR2 to background player")
        except:
            play_background()
    else:
        play_background()
   
def process_triggers(event):
    found=False
    for t in triggers:
        if t.screennum==screen and t.trigger == event:
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
            logging.debug("Stopping playback")
            stop_player 
        else:
            logging.debug("Not stopping playback as playing video has higher priority")
            
    elif t.loop=="Normal" or t.loop=="":
        logging.debug("Start normal playback of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
        play_file(t.playlist, t.playfile, loop=False, priority=t.priority)
            
    elif t.loop=="Loop":
        logging.debug("Start loop of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
        play_file(t.playlist, t.playfile, loop=True, priority=t.priority)
        
    elif t.loop=="SkipSamePrty":
        if playing["priority"] != t.priority:
            logging.debug("Start playback of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
            play_file(t.playlist, t.playfile, loop=False, priority=t.priority)
        else:
            logging.debug("Skipping %s/%s as file %s with same priority %s is already playing",
                          t.playlist, t.playfile, playing["file"],t.priority)
    elif t.loop=="SetBG":
        play_background(t.playfile)
        
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
        metadata[key]={"file": os.path.abspath(f)}
        
    ## Read the triggers
    with open(basedir+"/triggers.pup", 'r', encoding='utf-8') as infile:
        for line in infile:
            t = Trigger(line)
            triggers.append(t)
            logging.debug("Added trigger %s", t)
            
    ## Read the playlists
    with open(basedir+"/playlists.pup", 'r', encoding='utf-8') as infile:
        for line in infile:
            p = Playlist(line, basedir)
            playlists[p.folder]=p
            logging.debug("Added playlist %s", p)
            
def main():
    global screen 
    
    try:
        datadir=sys.argv[1]
        screen=sys.argv[2]
    except:
        datadir="."
        screen=12

    logging.basicConfig(level=logging.INFO)
    
    logging.info("Starting PiPUP server from data directory %s, screennum %s",
                 datadir, screen)
    
    read_files(datadir)

    looperthread=Looper()
    looperthread.start()

    run(host="localhost", port=5000)
    

if __name__ == '__main__':
    main()

