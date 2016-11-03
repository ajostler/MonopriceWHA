#This routine is called to interact with pianobar

import os,subprocess,time,logging

class pandora(object):
	
	#If pianobar isn't started, start it.
    def start(self,popen=None):

        if not popen:
            with open(os.devnull, "w") as fnull: popen = subprocess.Popen('pianobar', stdout = fnull, stderr = fnull)
        if popen.poll():
            with open(os.devnull, "w") as fnull: popen = subprocess.Popen('pianobar', stdout = fnull, stderr = fnull)
        return popen            
        
    #Run a command.  The commands are defined in the pianobar .config file.      
    def action(self,command,popen=None):
        if command[-1]!='\n':
            command+='\n'
            #print("The command is: %s" % command)
        popen = self.start(popen=popen)
        
        #Specify the location of the fifo file
        os.system("echo '%s' >> /root/.config/pianobar/ctl&" % command)
        return popen
        
    #kill the pianobar process that was started by the 'start' command
    def stop(self,popen=None):
        try:
            print(popen.poll())
            print(popen.pid)
            popen.kill()
            return None
        except:
            pass
            print('not dead')
            return popen
