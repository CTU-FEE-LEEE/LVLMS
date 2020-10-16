#!/usr/bin/python3

import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import socket
import random
import datetime
import sys
import os


def getData():
    try:
        print("Measuring data...")
        client = ModbusClientclient = ModbusClient(method='rtu', port='/dev/ttyS0', baudrate=9600, stopbits = 1, bytesize = 8, parity = 'N', timeout = 0.5)
        client.connect()
        regAddress = 0x0
        count = 1
        UNIT = 0x1
        rr = client.read_holding_registers(regAddress, 1, unit = UNIT) #levelMeter in 0.1 mm
        # print(rr.registers[0])
        msg = "Measured value (ABS) = " + str(rr.registers[0]/100) + " cm"
        print(msg)
        client.close()
        return rr.registers[0]
    except Exception as e:
        print(str(e))
        return -1

def getFakeData():
    print("Measuring fake data...")
    fake = random.randint(-1,10)
    print(fake)
    return fake

def sendData(address, port, staNum, data):
    try:
        print("Sending data...")
        data = str(staNum) + "," + str(data)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
        s.sendall(data.encode("utf-8"))
        s.close()

        return 1

    except Exception as e:
        print(str(e))
        return -1

def saveData(filePath, staNum, data):
    try:
        print("Saveing to file...")
        fileName = filePath + time.strftime("%Y%m%d", time.gmtime()) +"000000_"+ stationName + '_' + str(staNum) + "_data.csv"

        with open(fileName, "a") as f:
            now = datetime.datetime.now()
            f.write("%d,%s,%d,%0.3f\n" % (time.time(), now.strftime("%Y.%m.%d-%H:%M:%S"), staNum, data))
            f.flush()
            sys.stdout.flush()
            os.fsync(f.fileno())
        f.close()
        return 1

    except Exception as e:
        print(str(e))
        return -1
try:
    with open('/home/pi/repos/LVLMS/SW/station.key', 'r') as file: # open and read file with telegram API key
        f = file.read()
    file.close()

    address = f.splitlines()[2]
    port = int(f.splitlines()[3])
    staNum = int(f.splitlines()[4]) # station number
    refPoint = int(f.splitlines()[5]) # fixed referenece point in meter a.s.l.
    refDepth = int(f.splitlines()[6]) # referenece depth of sensore relative to refPoint in meter
    filePath = "/home/pi/MeasuredData/"

except Exception as e:
        print(str(e))


while True:
    try:
        ## Try to get data
        for i in range(20):
            data = getData()
            if data != -1:
                break
            time.sleep(5)

        ## ABS to m a.s.l.
        if data != -1:
            data = refPoint - refDepth + data/10000
            msg = "Measured value (m a.s.l.) = " + str(data) + " m"
            print(msg)
        else:
            msg = "Measured value (error) = " + str(data)
            print(msg)

        ## Try to send data
        for i in range(20):
            if sendData(address, port, staNum, data) == 1:
                break
            time.sleep(5)

        ## Try to save data
        for i in range(20):
            if saveData(filePath, staNum, data) == 1:
                break
            time.sleep(5)

    except Exception as e:
        print(str(e))

    print("Going to sleep...")
    time.sleep(30*60)
