from ustruct import unpack
from array import array
from machine import Pin,UART
from utime import sleep

TXPin = const(12)
RXPin = const(13)
hc12 = UART(0,9600,parity=None,stop=1,bits=8,rx=Pin(RXPin),tx=Pin(TXPin))

def sendFile(fileName,RFDev=None):
    try:
        file = open(fileName, 'rb')
    except:
        print('Could not read file '+fileName)
        return 0

    firstTime = True #flag to send msg size
    
    content = file.read()
    size = int(unpack('f',content)[0])*4 #
#     data_array = array('f')
    for i in range(4,len(content),size):
        if firstTime:
            msg = content[i-4:size]
            firstTime = False
        else:
            msg = content[i:i+size]
        
        ## send over RF module
        print(msg)
        RFDev.write(msg)
        sleep(1)
    
    
    
    
    file.close()
    
    
sendFile('/log/20210610_dht_log.dt',hc12)

