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
class hardware:
   
    def __init__(self, ZONES):
        """Hardware Class Initialization"""

        print 'initing hardware'
		
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
        for zone in self.ZONES:
            print "Setting Input, wiringPi pin: " + str(zone.pin) + " gpio pin: " + str(self.PinDict[int(zone.pin)])
            #set pin to input (using wiringpi numbers, not gpio numbers)
            os.system("gpio mode " + str(zone.pin) + " in")
            #set pull up resistor
            os.system("gpio mode " + str(zone.pin) + " up")  
            #export must take gpio pins as argument! doh. use the pindict here to translate wiringPi pin to broadcom pin num
            os.system("gpio export " + str(self.PinDict[zone.pin]) + " in") 

        # TODO:  Use wiringPi to set up output pins if needed. (Lights, Sirens, Flame Throwers, etc.)
		
    def UpdateZones(self, ZONES):
        """Updates the 'secured' bit of ZONES from GPIO hardware
		
        This function will read the hardware GPIO pins defined in the ZONES structure,
        and update them with either secured (   ) or unsecured (   ).
        """

        #create local to work with
	self.ZONES = ZONES 
		
        for zone in self.ZONES:   # for every zone in our list of zone dictionaries

            #this could be better :P  Note,     is 'secured'  #todo, use gpio read pin instead, maybe can ditch pindict.  #a=os.popen("your command").read()
            value = open('/sys/class/gpio/gpio' + str(self.PinDict[zone.pin]) + '/value','r').read().rstrip()    

            if value == '0':
                zone.secured = True
            else:
                zone.secured = False
         	
		
        return self.ZONES

