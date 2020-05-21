#!/bin/sh

if ! pidof -x GSMtime.py > /dev/null; then
	/home/pi/repos/LVLMS/SW/GSMtime.py > /dev/null &
fi

sleep 20

if ! pidof -x measure.py > /dev/null; then
	runuser -l pi -c '/home/pi/repos/LVLMS/SW/measure.py' > /dev/null &
fi 

sleep 20

if ! pidof -x telBot.py > /dev/null; then
	runuser -l pi -c '/home/pi/repos/LVLMS/SW/telBot.py' > /dev/null &
fi
   