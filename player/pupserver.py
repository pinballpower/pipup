from bottle import route, run, template
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import logging
import sys
import threading

omxplayer=None

metadata={}
start_pos=0
end_pos=float('inf')
loop=False

class Looper(threading.Thread):

    def run(self):
        try:  
            while True:
                current=omxplayer.position()
                logging.error(current)
                if current >= end_pos - 0.1:
                    if loop:
                        omxplayer.set_position(start_pos)
                    else:
                        omxplayer.pause()
                sleep(0.01)
        except Exception as e:
            logging.error(e)
   



def get_meta(filename):
    filename=filename.lower()
    if "/" in filename:
        return metadata[filename]

    for f in metadata.keys():
        (dir, file) = f.split("/")
        if file == filename:
            return metadata[f]

    return None

@route('/seek/<milliseconds>')
def seek(milliseconds): 
    omxplayer.set_position(float(milliseconds)/1000)
    return str(milliseconds)

@route('/setloop/<looponoff>')
def setloop(looponoff):
    global loop
    loop=looponoff
    return(str(looponoff))

@route('/play/<filename>')
def play(filename):
    global start_pos
    global end_pos
    try:
        md = get_meta(filename)
        logging.error("filename, md: %s, %s", filename, md)
        start_pos=md["start"]
        end_pos=md["end"]
        omxplayer.set_position(start_pos)
        omxplayer.play()
    except Exception as e:
        logging.error("%s", e)
    

def read_metadata(filename):
    with open(filename, 'r', encoding='utf-8') as infile:
        for line in infile:
            logging.debug("Parsing line %s", line)
            try:
                (file, _frames, _length, _milliseconds, ts_start, ts_end) = line.split()
                file=file.lower()
                metadata[file]={"start": float(ts_start)/1000, "end": float(ts_end)/1000}
            except:
                logging.error("Can't parse line %s", line);

def main():
    global omxplayer 

    try:
        datadir=sys.argv[1]
    except:
        datadir="."

    logging.basicConfig(level=logging.INFO)
    read_metadata(datadir+"/fileinfo.txt")
    omxplayer=OMXPlayer(Path(datadir+"/pupvideo.mp4"))
  
    looper=Looper()
    looper.start() 

    run(host="localhost", port=5000)  


if __name__ == '__main__':
    main()

omxplayer.quit()
