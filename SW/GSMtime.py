#!/usr/bin/python3
import os
import serial
import re
from datetime import datetime, timedelta
import time

for i in range(20):
    try:
        s = serial.Serial('/dev/ttyUSB1', timeout=1)
        print(s.name)
        s.write(b"AT+CCLK?\r\n")
        ans = s.read(50)
        msg = str(ans)
        msg = re.findall(r'"(.*?)"',msg)
        msg = msg[0]
        print(msg)
        dtm = datetime.strptime(msg,"%Y/%m/%d,%H:%M:%S") + timedelta(hours=2)
        date = dtm.strftime("%Y%m%d")
        time = dtm.strftime("%H:%M:%S")
        print(msg)
        s.close()
        cmd = 'date +%Y%m%d -s "' + date + '"'
        print(cmd)
        os.system(cmd)
        cmd = 'date +%T -s "' + time + '"'
        print(cmd)
        os.system(cmd)
        break

    except Exception as e:
        print(str(e))
    
    time.sleep(60)

