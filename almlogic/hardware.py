#!../flask/bin/python
"""
SYNOPSIS

    hardware.py

DESCRIPTION
    
    Raspberry Pi Hardware GPIO Pin control.
    This program will take an input of 'ZONES' from the main Alarm Logic Program and update it with inputs and eventually outputs.
    Effort was expended here to not require root priv to read/write the I/O.
    Requires:  wiringPi installed.

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

    NOTE:  Rev2 boards have extra pins usable!

    Pull up resistors are enabled on each input pin, so they will see 3.3v.  
    If you ground them out through the zones, the 3.3v will go away (pulled down through ground).
    Note: An external 10k resistor on the GPIO pins will protect them from unintential short to ground if
    they are misconfigured as an output by mistake.  Grounding an output pin with no protection 
    resistor will damage your rPi!
     
    Zone Wiring (Passive reed switch type):
    
        + 3.3v  ---<10k pull up internal>-------| |---------| |---------| |--------| |--------<GND>
                                               sensor       sensor      sensor     sensor

AUTHOR

    Evan Jensen <evanmj@gmail.com>

LICENSE

    See LICENSE file in project.

VERSION

    v0.1    - Initial
	
TODO

    - Handle Outputs
    - Handled Inverting of Inputs/Outputs by Request
    - Add rev2 PinDict and auto-determine board revision
"""



import os 

# call with hw = Hardware(ZONES)  
class hardware:
   
    def __init__(self, ZONES):
        """Hardware Class Initialization"""

        print 'initing hardware'
		
        #Get arguments
        self.ZONES = ZONES
		
        print '--------------'
        print 'Setting up IO:'
        print '--------------'

        #use wiringPi to set up input pins
        for zone in self.ZONES:
            print "Setting Input, wiringPi pin: " + str(zone.pin) + " gpio pin: " + str(self.PinDict[int(zone.pin)])
            #set pin to input (using wiringpi numbers, not gpio numbers)
            os.system("gpio mode " + str(zone.pin) + " in")
            #set pull up resistor
            os.system("gpio mode " + str(zone.pin) + " up")  

        # TODO:  Use wiringPi to set up output pins if needed. (Lights, Sirens, Flame Throwers, etc.)
		
    def UpdateZones(self, ZONES):
        """Updates the 'secured' bit of ZONES from GPIO hardware
		
        This function will read the hardware GPIO pins (using wiringPi numbers)
        defined in the ZONES structure, and update them with either secured (low) or unsecured (high).
        """

        #create local to work with
	self.ZONES = ZONES 
		
        for zone in self.ZONES:   # for every zone in our list of zone dictionaries

            #read pin status using gpio program
            value = os.popen("gpio -p read " + str(zone.pin)).read().rstrip()

            #convert string returned by wiringPi to a boolean
            if value == '0':
                zone.secured = True
            else:
                zone.secured = False
         	
        #send ZONES back to calling application
        return self.ZONES

