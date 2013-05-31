==========
pisecurity
==========

NOTE:  This code is not complete and does not fully work yet!!!

This program enables a web interface on the raspberry pi using flask.

It allows openid users defined in config.py to arm and disarm the system.

When a GPIO triggered zone changes state while armed, the alarm will sound.

Alarm options will include audio from the sound card (user provided wav file),
   optionally text message and/or email notifications, 
   visual web display (when accessed),
   eventually maybe a hardware GPIO output for a bell or lighting, etc.

========
Features
========

Currently Supported:

    (Note this is a Work in Progress, gpio working, web working, db working)
    
    configurable zones
    configurable users (OpenID Logins)
    configurable OpenID providers
    web access via desktop, tablet, phone, etc.
    rememeber users per device

Things that are planned for near future support:

    configurable alarm siren (wav file)
    configurable door/zone entry sound (when unarmed)
    zone secure/breach history via web
    arm / disarm history with link to user    
    configurable settings such as volume ramps, siren timouts, etc.
    
Things that 'would be nice' to eventually support:

    gpio output for alarm horns / sounders
    wireless zones
    X10 motion detectors/lighting/etc
    web based configuration of all settings
    dyanmic dns support

Things that are never planned to be supported:

    video/camera monitoring/recording (zoneminder does this better)
          If the rpi camera reaches anything useful, it is too close to possible intruders!

    text message / phone calls to 911 or other emergency services (too much liability)

