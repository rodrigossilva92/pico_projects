from machine import Pin, UART
from utime import localtime, sleep, time
from array import array
from ustruct import pack
from dht import DHT
from DataLog import DataLog

### setup
readStepTime = const(5) # time between data aquisition in seconds
lastRead = 0 ### todo # cuidado aqui 

sensorPin = const(28) # pin used by dht sensor
sensor = DHT(Pin(sensorPin), 'DHT22') # dht22 sensor instance created with pin 28 as data pin input

dht_log = DataLog('dht_log') #creates dht log

ledPin = const(18)
led = Pin(ledPin,Pin.OUT)
ledTimer = const(1)
ledValue = 0
ledLastTime = 0


TXPin = const(12)
RXPin = const(13)
hc12 = UART(0,9600,parity=None,stop=1,bits=8,rx=Pin(RXPin),tx=Pin(TXPin))


### main loop
while True:
    now = time()
    
    if now - lastRead > readStepTime:
        date = localtime() # y m d h m s wd yd
        day = '{:04d}{:02d}{:02d}'.format(date[0],date[1],date[2])
        hour = '{:02d}{:02d}{:02d}'.format(date[3],date[4],date[5])

        hum = sensor.getHumidity()
        temp = sensor.getTemperature()
            
        data = [float(day),float(hour),temp,hum]
#         print(data)
#         dht_log.logWrite(data)

        lastRead = now
    if now - ledLastTime > ledTimer:
        if ledValue == 0:
            ledValue = 1
            led.value(ledValue)
        else:
            ledValue = 0
            led.value(ledValue)
        ledLastTime = now
    

        

        
    
        
    
    
    
    
    
    
    
    


