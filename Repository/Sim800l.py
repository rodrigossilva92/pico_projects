from machine import UART, Pin
from utime import sleep
import ustruct



TXPin = const(12)
RXPin = const(13)
SIM800L = UART(0,9600,parity=None,stop=1,bits=8,rx=Pin(RXPin),tx=Pin(TXPin))

# SIM800L.write('AT'+'\r\n')
while True:
    SIM800L.write('AT'+'\n')
    
    msg = SIM800L.read()
    if msg != None:
        msg = msg.decode()
        break
    
    print(msg)
    sleep(1)
print(msg)
msg = msg.split('\r\n')
if 'OK' in msg:
    print("send")
