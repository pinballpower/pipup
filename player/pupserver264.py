from bottle import route, run, template
from pathlib import Path
from time import sleep
import logging
import sys
import threading
import subprocess

player=None

metadata={}
loop=False

def get_meta(filename):
    filename=filename.lower()
    if "/" in filename:
        return metadata[filename]

    for f in metadata.keys():
        (dir, file) = f.split("/")
        if file == filename:
            return metadata[f]

    return None

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

        result=subprocess.run(["../hello_video.bin", "../../Ball_Lock/"+filename]) 
        logging.error(result)
    except Exception as e:
        logging.error("%s", e)
    

def read_metadata(filename):
    with open(filename, 'r', encoding='utf-8') as infile:
        for line in infile:
            logging.debug("Parsing line %s", line)
            try:
                (file, _frames, _length, _milliseconds, ts_start, ts_end) = line.split()
                file=file.lower().replace(".mp4","")
                metadata[file]={"start": float(ts_start)/1000, "end": float(ts_end)/1000}
            except:
                logging.error("Can't parse line %s", line);

def main():
    try:
        datadir=sys.argv[1]
    except:
        datadir="."

    logging.basicConfig(level=logging.INFO)
    read_metadata(datadir+"/fileinfo.txt")

    run(host="localhost", port=5000)  


if __name__ == '__main__':
    main()

