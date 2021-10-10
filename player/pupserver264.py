from bottle import route, run, template
from pathlib import Path
from time import sleep
import logging
import sys
import threading
import subprocess
from glob import glob
import os.path

player=None

metadata={}
loop=False

def get_meta(filename):
    filename=filename.lower()
    if filename.endswith(".h264"):
        filename=filename[:-5]

    return metadata[filename]

@route('/setloop/<looponoff>')
def setloop(looponoff):
    global loop
    loop=looponoff
    return(str(looponoff))

@route('/play/<filename>')
def play(filename):
    global player
    try:
        md = get_meta(filename)
        logging.error("filename, md: %s, %s", filename, md)
        oldplayer=None
        if player is not None:
            oldplayer=player

        absfile=get_meta(filename)["file"]
  
        if loop:
            player=subprocess.Popen(["../hello_video.bin", "--loop", absfile]) 
        else:
            player=subprocess.Popen(["../hello_video.bin", absfile])   

        if oldplayer is not None:
            oldplayer.kill()

        logging.error(player)
    except Exception as e:
        logging.error("%s", e)
    

def read_files(basedir):
    for f in glob(basedir+"/*/*.h264"):
        key=os.path.basename(f)[:-5].lower()
        logging.error(key)
        metadata[key]={"file": os.path.abspath(f)}	
	


def main():
    try:
        datadir=sys.argv[1]
    except:
        datadir="."

    logging.basicConfig(level=logging.INFO)
    read_files(datadir)

    run(host="localhost", port=5000)  


if __name__ == '__main__':
    main()

