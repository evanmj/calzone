#!../flask/bin/python
"""
SYNOPSIS

    alarmlogic.py

DESCRIPTION
    
    This program handles the 'logic' part of the System, and everything that is not web / event based.
	
AUTHOR

    Evan Jensen <evanmj@gmail.com>

LICENSE

    See LICENSE file in project.

VERSION

    v0.1    - Initial
	
TODO

    - Run loop needs work now.  
    - Zone status needs only to be written on a zone change.  
    - History status needs written and history table set up and whatnot if it is not already.
"""

 
import os
import sys
import time

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


def UpdateSettings():   #pulls settings from database

    pass  #todo

#def printzones():
#    """This is for debugging.. prints the zones, with status"""
#    while True:
 #       db.session.commit()
  #      peanuts = db.session.query(models.Zones).all()
   #     for p in peanuts:
    #        print p.name + '      ' + str(p.secured)

def Run():

    #locals
    AllZonesSecured = False
    ZONES_AsArmed = {} # create empty stucture   #todo, maybe do db of this, it won't persist if power outage... or maybe it will?
    ZoneStateStored = False

    #pull Zone information from DB, which creates a ZONES 'cursor' (like a Dict)
    ZONES = db.session.query(models.Zones).all()

    #instantiate hardware class.
    hw = hardware(ZONES)

    while True:
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

        if Armed.value:  
            if not ZoneStateStored: #on first arm since disarm, make a copy$
                for zone in ZONES:      #store the as armed state of th$
                    ZONES_AsArmed[zone.name] = zone.secured #store $
                ZoneStateStored = True     #we have copied the pins.

            for zone in ZONES:
                if ZONES_AsArmed[zone.name] == zone.secured:  #does cur$
                    pass  #still armed.  
                else:           # zones changed state!
                    print 'System Armed: Ahhh! zone changed state.'
                    ZoneStateStored = False
                    Armed.value = '0'  #set system disarmed in db
                    db.session.commit() #write db data
                    #todo: explode with sound
                    #todo: break this for loop!!!!!
        else:                                   #not armed
            print ' '            
            print 'System Disarmed'

            # TODO:  ths can be done in a single db query instead.  Also currently Unused.
            AllZonesSecured = True # set this, so if any are not, we will unset it$
            for zone in ZONES:
            # determine zone secured bit.
                if not zone.secured:
                    AllZonesSecured = False

        time.sleep(1)



#zones, written by 'hardware.py', read by others.
#class Zones(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
#    name = db.Column(db.String(64), unique = True)
#    pin = db.Column(db.SmallInteger, unique = True)
#    secured = db.Column(db.Boolean)#

#status of the alarm system, written by 'alarmlogic.py'
#class AlarmStatus(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
#    attribute = db.Column(db.String(64), unique = True)
#    value = db.Column(db.String(64), unique = True)

#settings table, written by web app, read by others...
#class Settings(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
#    attribute = db.Column(db.String(64), unique = True)
#    value = db.Column(db.String(64), unique = True)

