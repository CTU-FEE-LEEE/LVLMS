#!/bin/sh
sleep 20

sudo chmod 777 home/pi/repos/LVLMS/SW/WD_log.txt

if ! pgrep -x "screen" > /dev/null; then
	screen -S "HWWD" -d -m
	screen -r "HWWD" -X stuff $'sudo home/pi/repos/LVLMS/SW/watchdog.py\n'
fi