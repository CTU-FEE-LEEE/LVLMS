#!/usr/bin/python3

# sudo modprobe bcm_wdt - raspberry
# http://raspberrypi.werquin.com/post/44890705367/a-hardware-watchdog-to-monitor-a-deamon-running

#
import _thread
import time
import os
import signal
import psutil
from watchdogdev import *
import sys
import datetime

#### Declaration ###############################################

wd = watchdog('/dev/watchdog')
g_interrupt = 0
g_HWWDSleep = 1
errCnt = 2
dataPath = "/home/pi/MeasuredData"

#### Function definition ###############################################

def hwwd():
    while g_interrupt == 0:
        """
        Hardware watchdog
        """
        #print "WD on, left:",wd.get_time_left()
        wd.keep_alive()
        time.sleep(g_HWWDSleep)
    # HWWD Off
    wd.magic_close()
    print("HW-WD off")

def conTest(hostname = "www.google.com"):
    """
    Connection test - ping to server
    google.com by default
    """
    response = os.system("ping -c 1 -w 4 " + hostname + " > /dev/null 2>&1")
    return response

def getSize(start_path = '.'):
    """
    Return folder size
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getMemUsage():
    """
    Return precentage usage of memory
    """
    info = psutil.virtual_memory()
    msg = "Memory usage is " + str(info.percent) + "%"
    print(msg)
    return info.percent

def prcsRunning(process = "default"):
    """
    Checks if the process is running
    """
    if os.system("ps -A | grep " + process) == 0:
        return True
    else:
        return False

def writeLog(report):
    """
    Write a report line to log file with current time
    """
    try:
        with open("/home/pi/repos/LVLMS/SW/WD_log.txt", "a") as f:
            now = datetime.datetime.now()
            f.write("%d, %s, %s\n" % (time.time(), now.strftime("%Y.%m.%d_%H:%M:%S"), str(report)))
            f.flush()
            sys.stdout.flush()
            os.fsync(f.fileno())            
        f.close()
    except Exception as e:
        print("Cannot write to log file (WD_log.txt)")
        print(str(e))

def reboot(msg = "default"):
    """
    Soft reboot of tuhe system
    """
    # stop WH WD
    g_interrupt = 1
    # wait for HWWD process
    time.sleep(g_HWWDSleep+1)

    writeLog("Rebooting: " + msg)
    os.system('reboot')

#### Main Procedure ###############################################

def main():
    global g_interrupt
    global sleepTime
    global dataPath
    global WDLogPath
    global errCnt
    folderSize = -1
    sleepTime = 40*60

    # error coutners
    errCntConn = 0
    errCntFolder = 0
    errCntProcess = 0

    # Handler for key interrupt
    def handler(signum, frame):
        global g_interrupt
        g_interrupt = 1

    try:
        print("Sarting HWWD")
        _thread.start_new_thread(hwwd,())
    except Exception as e:
        print("Error: unable to start thread")
        print(str(e))
        wd.magic_close()

    writeLog("Starting watchdog daemon")
    #after HW WD is on,wait 10 min
    print("Waiting 5 min for all processes")
    print("Do not terminate now!")
    
    time.sleep(300)

    signal.signal(signal.SIGINT, handler)


    while g_interrupt == 0:
        print("Testing...")
        ## connection test
        if conTest("85.207.12.165") == 0: # chemkomex address
            print("Connection test: PASS")
            errCntConn  = 0
        else:
            errCntConn += 1
            msg = "Connection test: FAIL. Connection error counter:" + str(errCntConn)
            writeLog(msg)
            print(msg)

        if errCntConn >= 2*errCnt:
            reboot("Connection test error - exceed boundaries")
            break
            
        ## Running process tests
        processFlag = 0
        process = "measure"
        if prcsRunning(process):
            print("Running process \"" + process + "\" test: PASS")
        else:
            processFlag = 1
            msg = "Running process \"" + process + "\" test: FAIL"
            writeLog(msg)
            print(msg)

        process = "telBot"
        if prcsRunning(process):
            print("Running process \"" + process + "\" test: PASS")
        else:
            processFlag = 1
            msg = "Running process \"" + process + "\" test: FAIL"
            writeLog(msg)
            print(msg)
            
        if processFlag == 1:
            errCntProcess += 1
        else:
            errCntProcess = 0

        if errCntProcess >= errCnt:
            reboot("Running process tests - exceed boundaries")
            break
        
        ## Folder size test
        if folderSize != getSize(dataPath):
            print("Folder size test: PASS")
            errCntFolder = 0
            folderSize = getSize(dataPath)
        else:
            errCntFolder += 1
            msg = "Folder size test: FAIL. Folder size error counter: " + str(errCntFolder)
            writeLog(msg)
            print(msg)

        if errCntFolder >= errCnt:
            reboot("Folder size test error - exceed boundaries")
            break
        
        ## Memory usage test
        if getMemUsage() < 95:
            print("Memory usage test: PASS")
        else:
            msg = "Memory usage test: FAIL. Memory usage:" + str(getMemUsage()) + "%"
            print(msg)
            reboot("Memory usage test error - " + str(getMemUsage()) + "% used")
        
        ## Reboot request test
        try:
            rebootFilePath = '/home/pi/repos/LVLMS/SW/reboot.txt'
            if os.path.exists(rebootFilePath): # check if file exists
                with open(rebootFilePath, 'r') as file: # read file
                    f = file.read()
                file.close()

                if f == 'OFF' or f == 'ON':
                    if f == 'ON':
                        with open(rebootFilePath, 'r+') as file: # switch to off
                            file.truncate(0)
                            file.write('OFF')
                        file.close()
                        msg = "Reboot request test: Reboot requested"
                        print(msg)
                        reboot(msg)
                    else:
                        msg = "Reboot request test: PASS"
                else:
                    with open(rebootFilePath, 'r+') as file: # if there is not OFF or ON
                        file.truncate(0)
                        file.write('OFF')
                    file.close()
                    os.chmod(rebootFilePath, 0o777)
                    msg = "Reboot request test: Incorrect content - file modified"
                print(msg)
            else:
                with open(rebootFilePath, 'w') as file: # write OFF
                    file.write('OFF')
                file.close()
                os.chmod(rebootFilePath, 0o777)
                msg = "Reboot request test: Missing reboot file - file added"
                print(msg)

        except Exception as e:
            msg = "Error: " + str(e)
            print(msg)
            writeLog(str(msg))        
        
        print("Testing done")

        #sleep section
        print("--------------------------")
        for i in range(2*sleepTime):
            if g_interrupt == 1:
                break
            time.sleep(0.5)

    print("\nEnding...")
    time.sleep(g_HWWDSleep+1)
    wd.magic_close()
    writeLog("Closing watchdog daemon")
    print("Done")



if __name__ == "__main__":
    main()
