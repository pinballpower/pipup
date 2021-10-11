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
        
          
        
        
        