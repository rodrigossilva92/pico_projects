
I2C_ADS = const(0x68) # DS1307 i2c address
DT_REG  = const(0x00) # DS1307 date and time register initial address
SQW_REG = const(0x07) # DS1307 square wave register address
                
### auxiliary functions
def bin2bcd(value):
    return value + 6 * (value // 10)
    
def bcd2bin(value):
    return value - 6 * (value >> 4)

class DS1307:
    
    def __init__(self,i2c):
        self.i2c = i2c
    
    def updateTime(self, datetime):
        year = datetime[0]
        month = datetime[1]
        day = datetime[2]
        hour = datetime[3]
        minu = datetime[4]
        sec = datetime[5]                
        
        buffer = bytearray(7)
        buffer[0] = bin2bcd(sec)
        buffer[1] = bin2bcd(minu)
        buffer[2] = bin2bcd(hour)
        buffer[4] = bin2bcd(day)
        buffer[5] = bin2bcd(month)
        buffer[6] = bin2bcd(year-2000)
        self.i2c.writeto_mem(I2C_ADS,DT_REG,buffer)
    
    def getTime(self):
        buffer = bytearray(7)
        self.i2c.readfrom_mem_into(I2C_ADS,DT_REG,buffer)
        year  = bcd2bin(buffer[6]) + 2000
        month = bcd2bin(buffer[5])
        day   = bcd2bin(buffer[4])
        dow   = bcd2bin(buffer[3])
        hour  = bcd2bin(buffer[2])
        minu  = bcd2bin(buffer[1])
        sec   = bcd2bin(buffer[0])
        return (year,month,day,hour,minu,sec)
        
    def setAlarm(self):
        pass    
        
    
    def __del__(self):
        pass
    
    


from machine import Pin, I2C
from utime import localtime

i2c = I2C(0,scl=Pin(17),sda=Pin(16))
extRTC = DS1307(i2c)

datetime = localtime()[0:6]

print(datetime)

# extRTC.updateTime(datetime)
print(extRTC.getTime())
# print(extRTC.getTime())




