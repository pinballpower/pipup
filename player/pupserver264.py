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

# a dictionary of players indexed by their screen ids
players = {} 

metadata={}
triggers = []
playlists = {}

class Player():

    def __init__(self, layer = 1):
        self.process = None
        self.file = None
        self.priority = -1
        self.layer = layer
        
    def finish(self):
        self.process = None
        self.file = None
        self.priority = -1
        
    def update(self):
        if self.process is None:
            return
        if self.process.poll() is None:
            return
        # there is still a process, but it has been terminated
        
        self.finish()
        return 
        
    def playing(self):
        self.update()
        return (self.process is not None)
    
    def stop(self):
        self.process.kill()
        self.playing()

    
    def play(self, playlist, filename, loop=False, priority=-1):
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
            oldproc = self.process
    
            absfile=fileinfo(filename)["file"]
      
            layeroption = "-l {}".format(self.layer)
            if loop:
                self.process=subprocess.Popen(["../hello_video.bin", "-i", layeroption, absfile]) 
            else:
                self.process=subprocess.Popen(["../hello_video.bin", layeroption, absfile])
                
            self.file=filename
            self.priority=priority   
    
            # If another video is playing, stop it
            if oldproc is not None:
                oldproc.kill()
                
            logging.debug("Started player")
        except Exception as e:
            logging.error("%s", e)
    
        
                

class Looper(Thread):
    
    def __init__(self):
        super().__init__()
        self.stop = False
        
    def run(self):
        global players
        
        while not self.stop:
            time.sleep(0.02)
            for player in players.values():
                player.update()
        

def fileinfo(filename):
    filename=filename.lower()
    if filename.endswith(".h264"):
        filename=filename[:-5]

    return metadata[filename]

def process_triggers(event):
    found=False
    for t in triggers:
        if t.screennum in players.keys() and t.trigger == event:
            found = True
            logging.debug("Processing trigger %s on player %s", t)
            process_trigger(t, players[t.screennum])
            
    if not found:
        logging.error("Trigger %s not found", event)

        
def process_trigger(t, player):
    
    if t.loop=="StopFile":
        if player.file==t.playfile:
            logging.debug("Stopping playback of %s", t.playfile)
            player.stop()
            
    elif t.loop=="StopPlayer":
        if t.priority > player.priority:
            logging.debug("Stopping playback")
            player.stop() 
        else:
            logging.debug("Not stopping playback as playing video has higher priority")
            
    elif t.loop=="Normal" or t.loop=="":
        logging.debug("Start normal playback of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
        player.play(t.playlist, t.playfile, loop=False, priority=t.priority)
            
    elif t.loop=="Loop" or t.loop=="SetBG":
        logging.debug("Start loop of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
        player.play(t.playlist, t.playfile, loop=True, priority=t.priority)
        
    elif t.loop=="SkipSamePrty":
        if player.priority != t.priority:
            logging.debug("Start playback of %s/%s, priority %s",
                          t.playlist, t.playfile, t.priority)
            player.play(t.playlist, t.playfile, loop=False, priority=t.priority)
        else:
            logging.debug("Skipping %s/%s as file %s with same priority %s is already playing",
                          t.playlist, t.playfile, player.file,t.priority)
        
    else:
        logging.info("Trigger loop type %s not yet implemented", t.loop)
       
            
            
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
    global players
    
    logging.basicConfig(level=logging.INFO)
    
    screenlist=""
    
    try:
        datadir=sys.argv[1]
        screenlist=sys.argv[2]
    except:
        print("Requires datadir and screen list as command line arguments.")
        sys.exit(1)
        
    layer=1
    for screen in screenlist.split(","):
        players[screen]=Player(layer)
        layer += 1

    logging.info("Starting PiPUP server from data directory %s, screennum %s",
                 datadir, players.keys())
    
    read_files(datadir)

    looperthread=Looper()
    looperthread.start()

    run(host="localhost", port=5000)
    

if __name__ == '__main__':
    main()

