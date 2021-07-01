from machine import UART, Pin
from utime import sleep

TXPin = const(8)
RXPin = const(9)
hc12 = UART(1,9600,parity=None,stop=1,bits=8,rx=Pin(RXPin),tx=Pin(TXPin))

START_COM = 0b10101010
MSG_LEN = 20 # number of bytes in the msg
outMsg = bytearray(20)
outMsg[0] = START_COM

STARTED = False
while True:
    if ~STARTED:
        inMsg = hc12.read(MSG_LEN)
        if inMsg != None:
            print(inMsg)
            if START_COM in inMsg:
                print("start communication")
                hc12.write(outMsg)
                STARTED = True
    
    if STARTED:
        inMsg = hc12.read(MSG_LEN)
        if inMsg != None:
            print(inMsg)
            break
        
        
# print((msg))
# print(len(msg))
# print(type(msg))

            
        
#     sleep(1)
#     sleep(1)




# outMsg = bytearray(10)
# x = hc12.write(outMsg)
# print(x)





        
