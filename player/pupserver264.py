from bottle import route, run
import logging
import subprocess
import os
import time
import sys
import time
import select
from threading import Thread

try:
    from signal import SIGUSR1, SIGUSR2
except:
    logging.error("Can't use SIGUSR1 and SIGUSER2 on nin-UNIX-Systems")

from puppack import Trigger, Playlist, Screen

# a dictionary of players indexed by their screen ids
players = {} 

# files={}
triggers = []
playlists = {}

basedir="."



class Player():

    def __init__(self, layer = 1):
        self.process = None
        self.file = None
        self.priority = -1
        self.layer = layer
        self.timeout = 5
        self.last_alive= time.time()
        self.poller=None
        
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
        self.process.terminate()
        time.sleep(0.3)
        if self.process.poll() is None:
            self.process.kill()
        self.update()
        
    def check_alive(self):
        if self.last_alive == 0:
            return
        
        if not(self.playing):
            return
        
        now = time.time()
        if now-self.lastalive > self.timeout:
            logging.warning("player for %s seems to be hanging, aborting...", self.file)
            self.stop()
            
    def set_alive(self):
        self.last_alive = time.time()

    
    def play(self, playlist, filename, loop=False, priority=-1):
        absfile=None
        if filename is None or filename=="":
            # Use the playlist instead
            try:
                pl=playlists[playlist]
                absfile=pl.next_file()
                filename=absfile
            except:
                logging.error("couldn't find any file for playlist %s",
                              playlist)
                return

        try:
            oldproc = self.process
    
            if absfile is None:
                absfile=basedir+"/"+playlist+"/"+filename
      
            layeroption = "-l {}".format(self.layer)
            
            if absfile.endswith(".h264"):
                # H264 video files using hello_video
                if loop:
                    logging.info("Looping %s", absfile)
                    self.process=subprocess.Popen(["../hello_video.bin",  "-i", "-p", layeroption, absfile],
                                                  stdout=subprocess.PIPE, bufsize=1)
                    self.lastalive=time.time()
                else:
                    logging.info("Playing %s", absfile)
                    self.process=subprocess.Popen(["../hello_video.bin", "-p", layeroption, absfile],
                                                  stdout=subprocess.PIPE)
                    self.lastalive=time.time()
            elif absfile.endswith(".png"):
                # PNGs using pngview
                logging.info("Displaying %s", absfile)
                self.process=subprocess.Popen(["../pngview", "-b 0", "-n", layeroption, absfile],
                                              stdout=subprocess.PIPE, bufsize=1)
                self.lastalive=0;
                
            else:
                logging.error("type of file %s not supported", absfile)
                
            if self.playing():
                self.poller=select.poll()
                self.poller.register(self.process.stdout,select.POLLIN)
                
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
            time.sleep(1)
            for screen in players.keys():
                p=players[screen]
                if p.playing():
                    logging.info("checking stdout of %s",p)
                    
                    if p.poller is not None and p.poller.poll(1):
                        line = p.process.stdout.readline()
                        p.set_alive()
                        logging.info("%s: %s", screen, line)
                    else:
                        logging.info(":(")
                        p.check_alive();
    

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
    global files
    global playlists
    global screens

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
            
    ## Read the screens
    with open(basedir+"/screens.pup", 'r', encoding='utf-8') as infile:
        for line in infile:
            s = Screen(line)
            if s.screennum in players:
                logging.info("Found configuration for screen %s", s.screennum)
                if len(s.playlist+s.playfile) > 0:
                    players[s.screennum].play( s.playlist, s.playfile, s.loopit, s.priority)
                # TODO: sizing

            
def main():
    global players
    global basedir
    
    logging.basicConfig(level=logging.INFO)
    
    screenlist=""
    
    # TODO: Get this from the system instead of hardcoding it
    width=1920
    height=1080
    
    try:
        basedir=sys.argv[1]
        screenlist=sys.argv[2]
    except:
        print("Requires datadir and screen list as command line arguments.")
        sys.exit(1)
        
    layer=1
    for screen in screenlist.split(","):
        players[screen]=Player(layer)
        layer += 1

    logging.info("Starting PiPUP server from data directory %s, screennum %s",
                 basedir, players.keys())
    
    read_files(basedir)

    looperthread=Looper()
    looperthread.start()

    run(host="localhost", port=5000)
    

if __name__ == '__main__':
    main()

