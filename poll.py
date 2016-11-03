# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 20:35:49 2015

@author: root
"""

#This routine is used to poll the amp and perform commands when certain criteria is reached

from serial import Serial
import time
import sqlite3 as lite
import threading
import logging

#I believe this was needed to make this a multi-thread script
class StoppableThread(threading.Thread):
    def __init__(self):
        super(StoppableThread,self).__init__()
        self._stop = False
        
    def run(self):

        pl = poll()
        while True:
            try:
                pl.grabdata()
            except: pass
            time.sleep(.5)
            if self._stop: break
            
    def stop(self):
        self._stop = True
        
    def stopped(self):
        return self._stop.isSet()
        
#Polling class        
class poll(object):

    def __init__(self):
    	#initialize variables
        self.pandora = False
        self.PA = False
        
        #Define the variable used for playing/pausing.  I use p/P
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.playpause = 'p'
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #Specify pandora station numbers
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.station = (0,1,2,3)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        self.idx = 0
        self.data_old = ['' for i in range(0,18)]
        
        #Specify number of amps
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.namps = 2
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        
        #Specify location to save .db file
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.con = lite.connect('/home/ajostler/Codes/AndrewWHA/WHA.db')
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #Specify number of 
        
        self.cur = self.con.cursor()
        self.cur.execute('DROP TABLE IF EXISTS data')
        self.cur.execute('CREATE TABLE data(channel INT,PA INT,PR INT,MU INT,DT INT, VO INT, TR INT, BS INT, BL INT, CH INT)')
		
		#Initialize database
		for n in range(1,self.namps+1)
        	for i in range(n*10+1,n*10+7):
            	self.cur.execute('INSERT INTO data VALUES(?,?,?,?,?,?,?,?,?,?)',[i]*10)            
        	self.con.commit()

        self.cmd = """UPDATE data
                 SET PA = ?,
                     PR = ?,
                     MU = ?,
                     DT = ?,
                     VO = ?,
                     TR = ?,
                     BS = ?,
                     BL = ?,
                     CH = ?
                  WHERE channel = ?"""
            
        #Open serial port - Modify to match your hardware
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.port = Serial('/dev/ttyUSB0',9600,timeout=1)
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    def grabdata(self):
        import requests
        
        self.port.flushInput()
        for n in range(1,self.namps+1)
        	self.port.write("?%2d\n\r" % n*10)
        self.port.readline()
        
        pandora = False
        try:
            for i in range(0,6*self.namps):
                if i == 6 or i == 13: self.port.readline()
                x = self.port.readline()
                
                if len(x) != 27: 
                    #logging.debug('Returning')                    
                    return
                
                
                data = [x[j:j+2] for j in range(4,22,2)]
                data.append(x[2:4])
                PA = data[0] #PA active
                PR = data[1] #Power - 01 on, 00 off
                MU = data[2] #Mute - 01 on, 00 off
                DT = data[3] #Do Not Disturb - 01 on, 00 off
                VO = data[4] #Volume - 01-35
                TR = data[5] #Treble - 01-13
                BS = data[6] #Bass - 01-13
                BL = data[7] #Balance - 01-13
                CH = data[8] #Channel - 01-06
                zone = data[9] #Zone - *1-*6, where *=1,2,3
                
                #If the values have changed from the last poll, update the db file
                if x!=self.data_old[i]:
                    self.cur.execute(self.cmd,data)
                    self.con.commit()
                self.data_old[i] = x
                                    
                #Insert what you want to do when different things are true
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #Below are some examples
                
                #If the current zone is set to channel 1 and the power is on, turn on
                #Pandora at the end of the loop (pandora = false at the beginning of the
                #loop, this is why I wait to turn on until the end of the loop.  If pandora
                #is still set to false, it will stop pandora)     
                if CH=='01' and PR=='01': pandora = True
                
                #If the treble goes above +4, send "tired of track" command to pianobar 
                #to go to the next song.  If it goes below +4, send "Toggle Pause" command
                #to pianobar
                if int(TR)>11 and self.pandora==True:
                    logging.debug('Tired of Track')
                    self.port.write("<%sTR11\n\r" % zone)
                    requests.get("http://0.0.0.0:800/?cmd=pandora&value=t")
                elif int(TR)<11 and self.pandora==True:
                    logging.debug('Pause')
                    self.port.write("<%sTR11\n\r" % zone)
                    requests.get("http://0.0.0.0:800/?cmd=pandora&value=%s" % self.playpause)
                    self.playpause = self.playpause.swapcase()
                    
                #If the bass goes above +4, send "Next Station" command to pianobar.
                #If the bass goes below +4, send "Previous Station" command to pianobar.
                if int(BS)>11 and self.pandora==True:
                    logging.debug('Next Station')
                    self.idx= self.idx + 1
                    if self.idx > len(self.station)-1: self.idx = 0
                    requests.get(r'http://0.0.0.0:800/?cmd=pandora&value=s%s\n' % self.station[self.idx])
                    self.port.write("<%sBS%02i\n\r" % (zone,self.idx+1+7))
                    time.sleep(2)
                    self.port.write("<%sBS11\n\r" % zone)
                elif int(BS)<11 and self.pandora==True:
                    logging.debug('Previous Station')
                    self.idx= self.idx - 1
                    if self.idx < 0: self.idx = len(self.station)-1
                    requests.get(r'http://0.0.0.0:800/?cmd=pandora&value=s%s\n' % self.station[self.idx])
                    self.port.write("<%sBS%02i\n\r" % (zone,self.idx+1+7))
                    time.sleep(2)                    
                    self.port.write("<%sBS11\n\r" % zone)
                    
                #If the channel goes to 06, turn off all the zones.  This is very useful
                #to be able to turn on/off all zones at once from one keypad
                if CH=='06' and PR=='01':
                    logging.debug('All Off')
                    self.port.write("<%sCH01\n\r" % zone)
                    time.sleep(.5)
                    for n in range(1,self.namps+1)
                    	self.port.write("<%2dPR00\n\r" % n)
                    requests.get("http://0.0.0.0:800/?cmd=pandora&value=stop")
				#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				
				
			#This is where we start/stop pandora, depending on the status of pandora from
			#the above loop
            if pandora==True and self.pandora==False:
                logging.debug('Start Pandora')
                self.pandora=True
                requests.get("http://0.0.0.0:800/?cmd=pandora&value=start")
            elif pandora==False and self.pandora==True:
                logging.debug('Stop Pandora')
                self.pandora=False
                self.idx = 0
                requests.get("http://0.0.0.0:800/?cmd=pandora&value=stop")
        except: pass
if __name__=='__main__':
    pl = poll()
    try:
        while True:
            pl.grabdata()
            time.sleep(1)
            #break
    except KeyboardInterrupt:
        pass
