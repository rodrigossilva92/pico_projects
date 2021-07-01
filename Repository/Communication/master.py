import serial
from time import sleep, localtime

from Communication import *

hc12 = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
    )

com = Communication(hc12)


while True:
    print("main loop")
    if not com.checkCommunication():
        com.sendHandshake()
    else:
        datetime = localtime()[0:6]
        com.updateTime(datetime)
    sleep(1)