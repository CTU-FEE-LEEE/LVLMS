import socket
import sys
import struct
import threading
import time
import os
from datetime import datetime

port = 3125

path = '/'
stationName = 'LVLMS'
staNum = '1'


def saveFile(message,staNum):
    filename = path + time.strftime("%Y%m%d", time.gmtime()) +"000000_"+ stationName + '_' + staNum + "_data.csv"
    now = datetime.now()

    with open(filename, "a") as f:
        f.write("%d,%s,%s\n" % (time.time(), now.strftime("%Y.%m.%d-%H:%M:%S"), message))
        f.flush()
        sys.stdout.flush()
        os.fsync(f.fileno())
    f.close()


def server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), port))
    print ('Socket binded to port 3125')
    s.listen(5)
    print ('socket is listening')

    while True:
        clientSocket, addr = s.accept()
        now = datetime.now() # current date and time
        d = now.strftime("%m/%d/%Y, %H:%M:%S")
        print(d, ': Got connection from ', addr)
        message = clientSocket.recv(100)
        message = message.decode("utf-8")

        saveFile(message,staNum)
        print(message)
        clientSocket.close()

t = threading.Thread(target = server, name = 'server', daemon = True, args = [port])
t. start()

while True:
    time.sleep(0.2)
