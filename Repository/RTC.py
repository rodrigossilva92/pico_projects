### auxiliary functions ###
def bin2bcd(value):
    return value + 6 * (value // 10)
    
def bcd2bin(value):
    return value - 6 * (value >> 4)


class BaseRTC:
    
    def __init__(self,i2c,address=0x68):
        self.i2c     = i2c
        self.address = address
       
       
    def setTime(self, datetime):
        buffer = bytearray(7)
        buffer[0] = bin2bcd(datetime[5]) # seconds
        buffer[1] = bin2bcd(datetime[4]) # minutes
        buffer[2] = bin2bcd(datetime[3]) # hours
#         buffer[3] = # day of the week
        buffer[4] = bin2bcd(datetime[2]) # day
        buffer[5] = bin2bcd(datetime[1]) # month
        buffer[6] = bin2bcd(datetime[0]-2000) # year
        self.i2c.writeto_mem(self.address,self.DT_REG,buffer)
  
  
    def getTime(self):
        buffer = bytearray(7)
        self.i2c.readfrom_mem_into(self.address,self.DT_REG,buffer)
        s = bcd2bin(buffer[0])
        m = bcd2bin(buffer[1])
        h = bcd2bin(buffer[2])
#         dow = bcd2bin(buffer[3])
        d = bcd2bin(buffer[4])
        mon = bcd2bin(buffer[5])
        y = bcd2bin(buffer[6])+2000
        datetime = (y,mon,d,h,m,s)
        return datetime
        

# class DS1307(BaseRTC):
#     DT_REG   = const(0x00)
#     CTRL_REG = const(0x07)


class DS3231(BaseRTC):
    DT_REG   = const(0x00)
    ALM1_REG = const(0x07)
    ALM2_REG = const(0x0b)
    CTRL_REG = const(0x0e)
    STS_REG  = const(0x0f)
    
    def setTime(self, datetime):
        status = self.i2c.readfrom_mem(self.address,self.STS_REG,1)[0]
        status &= 0b01111111
        status = bytearray([status])
        self.i2c.writeto_mem(self.address,self.STS_REG,status)
        super().setTime(datetime)
    
    
    def setAlarm(self,alarmtime,alarm=1):
        self.resetAlarms()
        if alarm == 1: # use alarm 1 ->  4 bytes
            buffer = bytearray(4)
            buffer[0] = 0                     # alarm seconds
            buffer[1] = bin2bcd(alarmtime[2]) # alarm minute
            buffer[2] = bin2bcd(alarmtime[1]) # alarm hour
            buffer[3] = bin2bcd(alarmtime[0]) # alarm day
            self.i2c.writeto_mem(self.address,self.ALM1_REG,buffer)
            ctrl = self.i2c.readfrom_mem(self.address,self.CTRL_REG,1)[0]
            ctrl |= 0b101
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(self.address,self.CTRL_REG,ctrl)
        elif alarm == 2: # use alarm 2 -> 3 bytes
            buffer = bytearray(3)
            buffer[0] = bin2bcd(alarmtime[2]) # alarm minute
            buffer[1] = bin2bcd(alarmtime[1]) # alarm hour
            buffer[2] = bin2bcd(alarmtime[0]) # alarm day
            self.i2c.writeto_mem(self.address,self.ALM2_REG,buffer)
            ctrl = self.i2c.readfrom_mem(self.address,self.CTRL_REG,1)[0]
            ctrl |= 0b110
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(self.address,self.CTRL_REG,ctrl)
    
    def enableTimer(self,snooze):
        self.resetAlarms()
        now = self.getTime()[3:5]
        m = now[1] + snooze
        h = now[0] + int(m/60)
        m = m % 60
        h = h % 24
        buffer = bytearray(3)
        buffer[0] = bin2bcd(m) | 0b00000000 # configure bit 7 of each byte to alarm match with hour and minute
        buffer[1] = bin2bcd(h) | 0b00000000
        buffer[2] = 0 | 0b10000000
        self.i2c.writeto_mem(self.address,self.ALM2_REG,buffer)
        ctrl = self.i2c.readfrom_mem(self.address,self.CTRL_REG,1)[0]
        ctrl |= 0b110
        ctrl = bytearray([ctrl])
        self.i2c.writeto_mem(self.address,self.CTRL_REG,ctrl)
#         print(m)
        
        
#         self.setAlarm(,)
    
    
    def disableAlarm(self,alarm=None):
        self.resetAlarms()
        if alarm == None:
            mask = 0b11111100
        elif alarm == 1:
            mask = 0b11111110
        elif alarm == 2:
            mask = 0b11111101
        ctrl = self.i2c.readfrom_mem(self.address,self.CTRL_REG,1)[0]
        ctrl &= mask
        ctrl = bytearray([ctrl])
        self.i2c.writeto_mem(self.address,self.CTRL_REG,ctrl)
        
    
    def checkAlarms(self):
        self.resetAlarms()
        ctrl = self.i2c.readfrom_mem(self.address,self.CTRL_REG,1)[0]
        if ctrl & 0b100 == 0b100:
            if ctrl & 0b1 == 0b1:
                buffer = bytearray(4)
                self.i2c.readfrom_mem_into(self.address,self.ALM1_REG,buffer)
#                 s = bcd2bin(buffer[0])
                m = bcd2bin(buffer[1] & 0b01111111)
                h = bcd2bin(buffer[2] & 0b01111111)
                d = bcd2bin(buffer[3] & 0b01111111)
                print("Alarm 1 set to: Day {} -> {}:{:02d}".format(d,h,m))
            if ctrl & 0b10 == 0b10:
                buffer = bytearray(3)
                self.i2c.readfrom_mem_into(self.address,self.ALM2_REG,buffer)
#                 s = bcd2bin(buffer[0])
                m = bcd2bin(buffer[0] & 0b01111111)
                h = bcd2bin(buffer[1] & 0b01111111)
                d = bcd2bin(buffer[2] & 0b01111111)
                print("Alarm 2 set to: Day {} -> {}:{:02d}".format(d,h,m))
            if ctrl & 0b11 == 0:
                print("No alarm configured.")
    
    def resetAlarms(self):
        status = self.i2c.readfrom_mem(self.address,self.STS_REG,1)[0]
        status &= 0b11111100
        status = bytearray([status])
        self.i2c.writeto_mem(self.address,self.STS_REG,status)

####
from machine import Pin, I2C
from utime import localtime,sleep

i2c = I2C(0,scl=Pin(17),sda=Pin(16))

rtc = DS3231(i2c)
datetime = localtime()[0:6]
rtc.setTime(datetime)

# alarm = (21,18,54)
# rtc.setAlarm(alarm)
# rtc.disableAlarm()
rtc.enableTimer(1)
rtc.checkAlarms()

while True:
    print(rtc.getTime())
    sleep(1)
