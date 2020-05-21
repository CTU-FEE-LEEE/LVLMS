#!/usr/bin/python3

import time, datetime
import telepot
import sys
import os
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from telepot.loop import MessageLoop

dataSensors = [ ['Time','unix t.s.'],
            ['Time',' '],
            ['Level meter','m'],
            ['Level meter','m a.s.l.'],
                                                ]

with open('/home/pi/repos/LVLMS/SW/station.key', 'r') as file: # open and read file with telegram API key
    f = file.read()
file.close()
key = f.splitlines()[0]
reb = f.splitlines()[1]
staNum = f.splitlines()[4]
refPoint = int(f.splitlines()[5]) # fixed referenece point in meter a.s.l.
refDepth = int(f.splitlines()[6]) # referenece depth of sensore relative to refPoint in meter

hiMessage = "Hi,\nthis is the level meter station" + staNum + ".\nUse /help command for overview of commands"
helpMessage = "/hi - welcome message\n/help - overview of commands\n/data - get latest measured data\n/dataFile - get latest data file\n/reboot - get reboot status"

def getDataFile():
    try:
        fileName = "/home/pi/MeasuredData/data_" + str(staNum) +".csv"
        if os.path.exists(fileName) == False:
            fileName = "Cannot reach a file"       

    except Exception as e:
        string = "Error: " + str(e)
        print(string)
        fileName = "Cannot reach a file"

    return fileName

def getData(refPoint,refDepth):
    try:
        #measure data over modbus
        client = ModbusClientclient = ModbusClient(method='rtu', port='/dev/ttyS0', baudrate=9600, stopbits = 1, bytesize = 8, parity = 'N', timeout = 0.5)
        client.connect()
        regAddress = 0x1
        count = 1
        UNIT = 0x1
        rr = client.read_holding_registers(regAddress, 1, unit = UNIT) #levelMeter
        # print(rr.registers[0])
        client.close()
        
        now = datetime.datetime.now()
        data = rr.registers[0]
        data = refPoint - refDepth + data/10000
        val = str(rr.registers[0]/10000)
        #val = "1000"
        
        string = dataSensors[0][0] + ': ' + str(time.time()) + ' ' + dataSensors[0][1] + '\n'
        string = string + dataSensors[1][0] + ': ' + now.strftime("%Y.%m.%d %H:%M:%S") + ' ' + dataSensors[1][1] + '\n'
        string = string + dataSensors[2][0] + ': ' + val + ' ' + dataSensors[2][1] + '\n'
        string = string + dataSensors[3][0] + ': ' + str(data) + ' ' + dataSensors[3][1] + '\n'
        
    except Exception as e:
        string = "Error: " + str(e)
        client.close()

    return string

def rebootStatus():
    try:
        if os.path.exists('/home/pi/repos/LVLMS/SW/reboot.txt'): # check if file exists
            with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r') as file: # read file
                f = file.read()
            file.close()

            if f == 'OFF' or f == 'ON':
                if f == 'OFF':
                    string = "Reboot status: OFF"
                else:
                    string = "Reboot status: ON"

                print(string)
            else:
                with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r+') as file: # if there is not OFF or ON
                    file.truncate(0)
                    file.write('OFF')
                file.close()
                string = "Incorrect content of reboot file\nReboot status set to OFF"
                print(string)
        else:
            with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'w') as file: # write OFF
                file.write('OFF')
                f = 'OFF'
            file.close()
            string = "Missing reboot file\nFile added\nReboot status set to OFF"
            print(string)

    except Exception as e:
        string = "Error: " + str(e)

    return string

def reboot():
    try:
        if os.path.exists('/home/pi/repos/LVLMS/SW/reboot.txt'): # check if file exists
            with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r') as file: # read file
                f = file.read()
            file.close()

            if f == 'OFF' or f == 'ON':
                if f == 'OFF':
                    with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r+') as file: # open, read and write
                        file.truncate(0)
                        file.write('ON')
                    file.close()
                    string = "OFF was changed to ON\nWaiting for reboot..."
                else:
                    with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r+') as file: # open, read and write
                        file.truncate(0)
                        file.write('OFF')
                    file.close()
                    string = "ON was changed to OFF\nRebooting stopped"
            else:
                with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'r+') as file: # if there is not OFF or ON
                    file.truncate(0)
                    file.write('OFF')
                file.close()
                string = "Incorrect content of reboot file\nReboot status set to OFF"
            print(string)
        else:
            with open('/home/pi/repos/LVLMS/SW/reboot.txt', 'w') as file: # write OFF
                file.write('OFF')
                f = 'OFF'
            file.close()
            string = "Missing reboot file\nFile added\nReboot status set to OFF"
            print(string)


    except Exception as e:
        string = "Error: " + str(e)

    return string

def action(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Received: %s' % command)
    if command == '/hi':
        telegram_bot.sendMessage (chat_id, hiMessage)
    elif command == '/data':
        telegram_bot.sendMessage(chat_id, getData(refPoint,refDepth))
    elif command == '/reboot':
        telegram_bot.sendMessage(chat_id, rebootStatus())
    elif command == reb:
        telegram_bot.sendMessage(chat_id, reboot())
    elif command == '/help':
        telegram_bot.sendMessage(chat_id, helpMessage)    
    elif command == '/dataFile':
        fileName = getDataFile()
        if fileName is 'Cannot reach a file':
            telegram_bot.sendMessage(chat_id, fileName)
        else:
            telegram_bot.sendDocument(chat_id, document=open(fileName))


# telegram_bot.sendPhoto (chat_id, photo = "https://i.pinimg.com/avatars/circuitdigest_1464122100_280.jpg")
# telegram_bot.sendDocument(chat_id, document=open('/home/pi/Aisha.py'))
# telegram_bot.sendAudio(chat_id, audio=open('/home/pi/test.mp3'))





telegram_bot = telepot.Bot(key)

print (telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()

print('Up and Running....')

while 1:
    time.sleep(10)
