#This is the main function that starts the webserver and the polling routine

import web
from serial import Serial 
import time
import threading
import logging
import pandora_player
import speech
import PA

log_path = r'test.log'
with open(log_path,'w') as f: pass
logging.basicConfig(filename=log_path,
		    level=logging.DEBUG,
		    format='%(levelname)s - %(asctime)s - %(message)s',
		    datefmt='%Y-%m-%d %H:%M:%S')

#Defining the index page
urls = ('/', 'index')
app = web.application(urls, globals())

port = Serial('/dev/ttyUSB0',9600,timeout=1)
logging.debug('Opened Port')

# define the task of index page
class index:
    # rendering the HTML page
    def GET(self):
        try:
        	#Get values from command.  Should be formatted like the following:
        	#http://<IP Address>.<Port>/?cmd=<command>&value=<value>&zone=<zone (if applicable)>
            getInput = web.input(cmd="")
            command = str(getInput.cmd)        
            
            getInput = web.input(val="")
            value = str(getInput.value)
            
            #If command = pandora, then do the following
            if command.lower()=='pandora':
                pdra = pandora_player.pandora()
                if value.lower()=='start':
                    logging.debug('Starting Pandora')
                    web.popen = pdra.start(web.popen)
                elif value.lower()=='stop' or value.lower()=='q':
                    logging.debug('Stopping Pandora')
                    web.popen = pdra.stop(web.popen)
                else:
                    if web.popen:
                        logging.debug('Runnig Command %s' % value)
                        web.popen = pdra.action(value,web.popen)
                        
            #If command = speech, speak
            elif command.lower()=='speech':
                nval = []
                for val in value:
                    nval.append(val)
                    if val.isdigit():
                        nval.append(' ')
                nval = ''.join(nval)
                nval = nval.replace('  ',' ')
                speech.gspeak(nval)
                
            #If command = pa, turn on or off the PA
            elif command.lower()=='pa':
                if value.lower()=='on':
                    PA.pa(True)
                else:
                    PA.pa(False)
                   
            #Otherwise, perform the specified command on the amp
            else:
                getInput = web.input(zone="")
                zone = str(getInput.zone)
                
                port.flushInput()
        
                PerformCommand(zone,command,value)
        except: pass
        
#Control the amp here
def PerformCommand(zone,command,value):
    if len(zone) > 2:
        zones = [int(zone[i:i+2]) for i in range(0,len(zone),2)]
    elif (float(zone)/10.0).is_integer(): 
        zones = range(int(zone)+1,int(zone)+7)
    else:
        zones = [int(zone)]    
        
    if value.lower() == 'up' or value.lower() == 'down':
        CommandUpDown(zones,command,value)
    else:
        try:
            value = ('%02i' % int(value))
        except: pass
        for channel in zones:
            port.write("<%s%s%s\n\r" % (channel,command,value))
    
        
#Increase/Decrease volume on specified zones
def CommandUpDown(zones,command,value):
    import sqlite3 as lite
    
    con = lite.connect('/home/ajostler/Codes/AndrewWHA/WHA.db')
    
    if value.lower() == 'up':
        add = 1
    elif value.lower() == 'down':
        add = -1
    else:
        return
    
    with con:
        cur = con.cursor()
        for channel in zones:
            cur.execute('SELECT %s from data WHERE channel=?' % (command),(channel,))
            rows = cur.fetchall()
            
            cmd = "<%02i%s%02i\n\r" % (channel,command,rows[0][0]+add)
            port.write(cmd)
            cur.execute('UPDATE data SET %s = ? WHERE channel = ?' % (command),(rows[0][0]+add,channel))            
            
if __name__ == '__main__':
    import poll
    
    time.sleep(1)
    logging.debug('Enter Main')
    exit_flag = False 
    logging.debug('Before try')
    try:
        logging.debug('In try')
        logging.debug("Starting 'poll' thread")
        CP = poll.StoppableThread()
        CP.start()
        logging.debug("'poll' thread started")
    
        logging.debug("Starting 'web' thread")
        web.popen = None
        Web = threading.Thread(target=app.run)#,args=['0.0.0.0:8080'])
        Web.daemon = True
        Web.start()
        logging.debug("'web' thread started")
    
    except:
        logging.debug('In except')
    
    try:
        while True:
            time.sleep(1)
            #logging.debug("infinite loop")
    except:
        logging.debug('Stopping')
        CP.stop()
        CP.join()
        app.stop()
        logging.debug('Stopped')
