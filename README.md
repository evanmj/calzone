==========
calzone
==========

calzone - A free, web enabled home alarm system for the raspberry pi, etc.

See the wiki on github for more up to date information:
https://github.com/evanmj/pisecurity/wiki

This program enables a web interface on the raspberry pi using flask for python and WSGI.

It allows OpenId authenticated users defined in config.py to arm and disarm the system.

When a GPIO triggered zone changes state while armed, the alarm will sound.

Alarm options will include audio from the sound card (user provided wav file),
   optionally text message and/or email notifications, 
   visual web display (when accessed),
   eventually maybe a hardware GPIO output for a bell or lighting, etc.
