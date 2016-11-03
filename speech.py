# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 15:08:02 2016

@author: root
"""

#This routine is used to speak a command 'speak1' uses the pyttsx engine.  'gspeak' uses
#google's tts engine, and sounds much more realistic.

def speak1(tosay):
    import pyttsx
    engine = pyttsx.init()
    engine.setProperty('rate',100)
    engine.setProperty('voice','english-us')
    engine.say(tosay)
    engine.runAndWait()

def gspeak(tosay):
    from gtts import gTTS
    import pygame
    import time
    
    tosay = tosay.replace('?',',')
    
    #Specify location to temporarily save the mp3 file
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    audio_file = "/home/ajostler/Codes/AndrewWHA/tosay.mp3"
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    tts = gTTS(text=tosay,lang="en")
    tts.save(audio_file)

    time.sleep(.5)
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    
if __name__=='__main__':
    gspeak("Incoming call from 1234567890")
