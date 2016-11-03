# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 17:07:44 2016

@author: root
"""


#This module is used to trigger a relay which sends power to the PA on 

def pa(on):
    import RPi.GPIO as GPIO
    
    PApin = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PApin,GPIO.OUT,initial=1)
    
    global vol,vol_raised
    
    if on:
        GPIO.output(PApin,0)
    else:
        GPIO.output(PApin,1)
        
if __name__=='__main__':
    pa(False)