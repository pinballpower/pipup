from glob import glob 
from random import shuffle

class Trigger(object):

    def __init__(self, line):
        (self.id, self.active, self.description, self.trigger,
          self.screennum , self.playlist ,self.playfile ,
          self.volume,self.priority,self.length,self.counter,
          self.rest_seconds,self.loop,self.defaults) = line.split(",")
          
        self.playfile = self.playfile.replace(".mp4", ".h264")
        
        
    def __str__(self):
        return "{} {} {} {} {} {}".format(self.trigger,
                                          self.screennum, 
                                          self.playlist,
                                          self.playfile,
                                          self.priority,
                                          self.loop)
        
              

class Playlist(object):
    
    def __init__(self, line, basedir):
        (self.screennum,self.folder,self.description,
         self.alphasort,self.restseconds,
         self.volume,self.priority) = line.split(",")
         
        pattern=basedir+"/"+self.folder+"/"+'*.h264'
        files=glob(pattern)
        if self.alphasort:
            self.files=sorted(files)
        else:
            self.files=shuffle(files)
            
        self.currentindex=0
         
    def next_file(self):
        self.currentindex += 1
        if self.currentindex >= len(self.files):
            self.currentindex=0
            
        return self.files[self.currentindex]
            
             
    def __str__(self):
        return "{} {}".format(self.folder, self.files)
        
          
        
        