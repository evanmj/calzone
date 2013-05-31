#!../flask/bin/python
"""
SYNOPSIS

    hardware.py

DESCRIPTION
    
	Raspberry Pi Hardware GPIO Pin control.
	This program will take an input of 'ZONES' from the main Alarm Logic Program and update it with inputs and eventually outputs.
    Effort was expended here to not require root priv to read/write the I/O.
    Requires:  wiringPi installed.

	'exporting' pins via wiringpi will populate them in:
    /sys/class/gpio/gpio#/value

    +----------+------+--------+------+-------+
    | wiringPi | GPIO | Name   | Mode | Value |
    +----------+------+--------+------+-------+
    |      0   |  17  | GPIO 0 |      |       |
    |      1   |  18  | GPIO 1 |      |       |
    |      2   |  21  | GPIO 2 |      |       |
    |      3   |  22  | GPIO 3 |      |       |
    |      4   |  23  | GPIO 4 |      |       |
    |      5   |  24  | GPIO 5 |      |       |
    |      6   |  25  | GPIO 6 |      |       |
    |      7   |   4  | GPIO 7 |      |       |
    |      8   |   0  | SDA    |      |       |
    |      9   |   1  | SCL    |      |       |
    |     10   |   8  | CE0    |      |       |
    |     11   |   7  | CE1    |      |       |
    |     12   |  10  | MOSI   |      |       |
    |     13   |   9  | MISO   |      |       |
    |     14   |  11  | SCLK   |      |       |
    |     15   |  14  | TxD    | ALT0 |       |
    |     16   |  15  | RxD    | ALT0 |       |
    +----------+------+--------+------+-------+

     Pull up resistors are enabled on each input pin, so they will see 3.3v.  
     If you ground them out through the zones, the 3.3v will go away (pulled down through ground).
	 Note: An external 10k resistor on the GPIO pins will protect them from unintential short to ground if
	      they are misconfigured as an output by mistake.  Grounding an output pin with no protection 
		  resistor will damage your rPi!
     
     Zone Wiring:
    
        + 3.3v  ---<10k pull up internal>-------| |---------| |---------| |--------| |--------<GND>
                                               sensor       sensor      sensor     sensor

AUTHOR

    Evan Jensen <evanmj@gmail.com>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.

VERSION

    v0.1    - Initial
	
TODO

     - Handle Outputs
	 - Handled Inverting of Inputs/Outputs by Request
	 - Add rev2 PinDict and auto-determine board revision
"""



import os 

# call with hw = Hardware(ZONES)  
class Hardware:
   

    def __init__(self, ZONES):
        """Hardware Class Initialization"""
		
		#Get arguments
		self.ZONES = ZONES
		
        #Create Dict to relate 'wiringPi' pins to 'GPIO' numbered pins for export command
        #(we want to use wiringPi pins)
		#TODO:  Consider rPi Rev 2 Boards... 
        self.PinDict = {0: 17, 1: 18,2: 21,3: 22,4: 23,5: 24,6: 25,7: 4,8: 0,9: 1,10: 8,11: 7,12: 10,13: 9,14: 11,15: 14,16: 15 }

		os.system("gpio unexportall")  #remove exports if they exist

        print '--------------'
        print 'Setting up IO:'
        print '--------------'
        #use wiringPi to set up input pins
        for zone in ZONES:
            print "Setting Input, wiringPi pin: " + str(zone.pin) + " gpio pin: " + str(PinDict[int(zone.pin)])
            #set pin to input (using wiringpi numbers, not gpio numbers)
			os.system("gpio mode " + str(zone.pin) + " in")
            #set pull up resistor
			os.system("gpio mode " + str(zone.pin) + " up")  
			#export must take gpio pins as argument! doh. use the pindict here to translate wiringPi pin to broadcom pin num
            os.system("gpio export " + str(PinDict[zone.pin]) + " in") 

        # TODO:  Use wiringPi to set up output pins if needed. (Lights, Sirens, Flame Throwers, etc.)
		
    def UpdateZones(self, ZONES):
        """Updates the 'secured' bit of ZONES from GPIO hardware
		
		This function will read the hardware GPIO pins defined in the ZONES structure,
		and update them with either secured (   ) or unsecured (   ).
		"""
		
		for zone in ZONES:   # for every zone in our list of zone dictionaries

            #this could be better :P  Note,     is 'secured'
            value = open('/sys/class/gpio/gpio' + str(PinDict[zone.pin]) + '/value','r').read().rstrip()    

            if value == '0':
            zone.secured = True
                else:
            zone.secured = False
         	
		
        return ZONES

 #
 #  End New Code Here
 #
 #
 #
 #


## All this stuff will be handled in alarm logic, for instance initializing the zones in the DB.
import time
from config import CONFIGZONES  # TODO: Remove this when zones are defined from the web.  pull from alarmlogic or passed in?
    
def init_depricated(self):    #todo: make real __init__
    """Init the GPIO pins from the input and output lists configured in config.py"""
 
    #read database to see if it needs initialized for the first time
    zonecheck = models.Zones.query.get(1)

    #if ZONES are not yet defined
    if zonecheck is None:

        #define sample zones from config.py
        for zone in CONFIGZONES:
            u = models.Zones(name=zone['name'], pin=zone['pin'])
            db.session.add(u)        

#TODO: add this back when zones are all moved to web based config
        #define sample zones
        #u = models.Zones(name='Sample Zone 1', pin=0)
        #db.session.add(u)

    #write data
    db.session.commit()  
    db.session.expunge(zonecheck)
    
    print '--------------'
    print 'Defined Zones:'
    print '--------------'

    ZONES = models.Zones.query.all()    
    for zone in ZONES:
        print zone.name
    
    

def loop(self):   
    """Run as some sane interval to keep IO up to date in structures.
	
	Inputs: this function does a one time update of the IO (inputs) and populates the ZONES values.
    Outputs: TODO: this function takes the OUTPUTS structure and sends the values to the physical pins.
	
	
	"""

    print '--------------------------------'
    print 'Starting Hardware Update Loop...'
    print '--------------------------------'

    #session = db.session.merge()
    ZONES = models.Zones.query.all()    

    while True:

        print 'Reading Zones'


        ZONES = models.Zones.query.all()    

        for zone in ZONES:   # for every zone in our list of zone dictionaries

            #this could be better :P  Note,     is 'secured'
            value = open('/sys/class/gpio/gpio' + str(PinDict[zone.pin]) + '/value','r').read().rstrip()    

            if value == '0':
            zone.secured = True
                else:
            zone.secured = False
            
            #session.add(zone)
        db.session.commit()
        time.sleep(1)
		
		
def clearzones():  #todo, move this to the main almlogic app.
    """Remove all defined zones from the database."""

    ZONES = models.Zones.query.all()

    for zone in ZONES:
        db.session.delete(zone)    #kill all zones
        session.commit()           #do it.
    session.expunge(ZONES)