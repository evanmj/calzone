#!../flask/bin/python
"""
SYNOPSIS

    Calzone -- alarmlogic.py

DESCRIPTION
    
    This program handles the 'logic' part of the System, and everything that is not web / event based.
	
AUTHOR

    Evan Jensen <evanmj@gmail.com>

LICENSE

    See LICENSE file in project.

TODO

"""

 
import os
import sys
import time
from datetime import datetime

#get pygame for audio
import pygame

#get database models and objects
from almlogic import models
from almlogic import db

#get user configured zones
from config import CONFIGZONES  # TODO: Remove this when zones are defined from the web.

#import hardware class from hardware module
from hardware import hardware  

def init():   
    """This function initializes the Alarm System

        Initialization includes checking for defined zones, populating the database if they are not defined...
        It will also create the other tables if they do not exist.
        Finally, it will instantiate the hardware class, which updates the ZONES structure from the GPIO pins.

    """

    print 'initializing almlogic'

    #read database to see if it needs initialized for the first time
    zonecheck = models.Zones.query.get(1)

    #if ZONES are not yet defined
    if zonecheck is None:
        #define zones from config.py
        for zone in CONFIGZONES:
            u = models.Zones(name=zone['name'], pin=zone['pin'])
            db.session.add(u)
            db.session.commit()
    
    #TODO: add this back when zones are all moved to web based config
    #define sample zones
    #u = models.Zones(name='Sample Zone 1', pin=0)
    #db.session.add(u)

    print '--------------'
    print 'Defined Zones:'
    print '--------------'

    ZONES = models.Zones.query.all()
    for zone in ZONES:
        print zone.name

    # default all settings here?!? or elsewhere?  Probably will do this the same as the settings table below, 
    # but set all the settings if not yet populated.

    #Check if AlarmStatus DB Table is populated yet
    alarmstatus = models.AlarmStatus.query.get(1)

    if alarmstatus is None:
        # populate initial data elements
        a = models.AlarmStatus(attribute = 'Armed', value = '0')
        db.session.add(a)

    db.session.commit()  # write to db
    db.session.close()   # close session?

    #init pygame audio mixer
    pygame.mixer.init()


def UpdateSettings():   #pulls settings from database

    pass  #todo

def StartAlarmSound(soundfile):
    """This funcion will start the alarm wav file provided"""
    pygame.mixer.music.load(soundfile)
    #play sound, loop forever
    pygame.mixer.music.play(-1)

def StopAlarmSound():
    print 'Stopping alarm Sound...'
    pygame.mixer.music.fadeout(1500)

def CheckForZoneChange(ZONES_Copy, ZONES):
    """This function will check zones for change, and logs changes to the DB."""
    
    #locals
    AtLeastOneChanged = False

    #start with zones matching
    for zone in ZONES:
        if ZONES_Copy[zone.name] == zone.secured:  #does current status match what we stored?
            pass
        #zones changed state!
        else:
            #set flag for return data, but finish this loop.
            AtLeastOneChanged = True
            # was it secured and went unsecrued, or vice versa?
            if ZONES_Copy[zone.name] == True:  
                #log change from secured to unsecured
                now = datetime.now()
                z = models.History(source = zone.name, event = 'Zone Breached', timestamp = now)
                db.session.add(z)
            else:
                pass #log change from unsecured to secured here
                now = datetime.now()
                z = models.History(source = zone.name, event = 'Zone Secured', timestamp = now)
                db.session.add(z)
            #store ZONES and state changes to DB (only if something changed)
            db.session.commit()

    #let calling apps know we changed zone state.
    if AtLeastOneChanged:
        return True
    else:
        #made it with no zones mismatching
        return False

def Run():

    #locals
    AllZonesSecured = False
    Alarming = False # holds alarming status... if alarming, siren should be sounding, etc.  #TODO: move this to status db
    ZONES_AsArmed = {} # create empty stucture   
    ZONES_LastLoop = {}
    ZonesChanged = False
    ZoneStateStored_Armed = False
    SoundEnabled = True

    #pull Zone information from DB, which creates a ZONES 'cursor' (like a Dict)
    ZONES = db.session.query(models.Zones).all()

    #instantiate hardware class.
    hw = hardware(ZONES)
    #get fresh zone data from hardware...
    hw.UpdateZones(ZONES)

    #store zone copy for first loop through
    for zone in ZONES:
        ZONES_LastLoop[zone.name] = zone.secured #store zone state

    try:
        while True:
            #clear debug screen
            os.system('clear')

            db.session.commit()

            #See if we are armed or not from the db (which gets its information from the web interface(flask))
            Armed = db.session.query(models.AlarmStatus).filter_by(attribute = "Armed").first()
            print Armed.attribute + ' ' + Armed.value

            #get fresh zone data from hardware... 
            ZONES = hw.UpdateZones(ZONES)

            #debug output on screen of zones (justified left with padding)
            for zone in ZONES:
                print zone.name.ljust(20) + str(zone.secured)

            if Armed.value == '1' and not Alarming:  
                print 'main armed loop running'
                #see if zones changed since last loop.... 
                if ZonesChanged:                
                    #Note: the system stays armed even if alarming, until a user disarms.
                    print 'System Armed: Ahhh! zone changed state while Armed!.'
                    ZoneStateStored_Armed = False
                    Alarming = True
                    #timestamp zone change
                    now = datetime.now()
                    #write history database
                    z = models.History(source = zone.name, event = 'Alarming!', timestamp = now)
                    db.session.add(z) 
                    #write the db data which should include the changes in the ZONES cursor
                    db.session.commit() 
                    #start sounding alarm
                    if SoundEnabled:
                        StartAlarmSound('alarm_missle_launch.wav')
                else:
                    print 'no change in zones.'
            elif Armed.value == '0':                            #not armed
                print 'System Disarmed'


            #system is in alarm state, probably siren is sounding, user has not acknowledged it yet.
            if Alarming and Armed.value == '1':
                print 'System is Alarming!!!!'
                #more will go here.

            #system is alarming, but user has just acknowledged it by a disarm request via the web, timeout s$
            if Alarming and Armed.value == '0':
                StopAlarmSound()
                print 'Setting Internal status back to not alarming.'
                Alarming = False

            #find out if zones changed, and log changes to the db.
            ZonesChanged = CheckForZoneChange(ZONES_LastLoop, ZONES)

            #store zone copy for next loop
            for zone in ZONES:
                ZONES_LastLoop[zone.name] = zone.secured #store zone state
            

            # AllZonesSecured is just for a notice on the web that says all doors/windows/zones are secured.
            # Note, you can arm the system with one or more zones unsecured, but it should warn you, etc.
            #      This is needed because I have a screen dog door and I'd like to be able to leave the
            #      back door open and still arm the system and watch for state change.

            # TODO:  ths can be done in a single db query instead.  Also currently Unused.
            AllZonesSecured = True # set this, so if any are not, we will unset it$
            for zone in ZONES:
            # determine zone secured bit.
                if not zone.secured:
                    AllZonesSecured = False


            #nap for one cycle
            time.sleep(1)
    except KeyboardInterrupt:
        pygame.mixer.quit()
    return 0
