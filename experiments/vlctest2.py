import glob
import time
import socket
from threading import Thread

class Player():
    def __init__(self):
        self.is_initiated = False
        self.SEEK_TIME = 20
        self.MAX_VOL = 512
        self.MIN_VOL = 0
        self.DEFAULT_VOL = 256
        self.VOL_STEP = 13
        self.current_vol = self.DEFAULT_VOL

    def toggle_play(self):
        if not self.is_initiated:
            self.is_initiated = True
            self.thrededreq("loop on")
            for s in glob.glob("*/*.mp4"):
                self.thrededreq("add "+s)
            print("Init Playing")
            return
        self.thrededreq("pause")
        print("Toggle play")


    def next(self):
        if not self.is_initiated:
            self.toggle_play()
            return
        self.thrededreq("next")
        print("Next")
        pass

    def prev(self):
        if not self.is_initiated:
            self.toggle_play()
            return
        self.thrededreq("prev")
        print("Previous")
        pass

    def req(self, msg: str, full=False):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Connect to server and send data
                sock.settimeout(0.7)
                sock.connect(('127.0.0.1', 44500))
                response = ""
                received = ""
                sock.sendall(bytes(msg + '\n', "utf-8"))
                # if True:
                try:
                    while (True):
                        received = (sock.recv(1024)).decode()
                        response = response + received
                        if full:
                            b = response.count("\r\n")
                            if response.count("\r\n") > 1:
                                sock.close()
                                break
                        else:
                            if response.count("\r\n") > 0:
                                sock.close()
                                break
                except:
                    response = response + received
                    pass
                sock.close()
                return response
        except Exception as e:
            print(e)
            return None
            pass

    def thrededreq(self, msg):
        Thread(target=self.req, args=(msg,)).start()

#'vlc --intf rc --rc-host 127.0.0.1:44500' you need to run the vlc player from command line to allo controlling it via TCP
player=Player()
player.toggle_play()
for i in range(0,100):
    time.sleep(4)
    player.next()
#player.prev()

