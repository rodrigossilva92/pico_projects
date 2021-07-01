
I2C_ADS  = const(0x68) # DS3231 i2c address
DT_REG   = const(0x00) # DS3231 date and time register initial address
CTRL_REG = const(0x0e) # DS3231 control register
STS_REG  = const(0x0f) # DS3231 status register
ALM1_REG = const(0x07) # alarm 1 3 bytes
ALM2_REG = const(0x0b) # alarm 2 3 bytes
                
### auxiliary functions
def bin2bcd(value):
    return value + 6 * (value // 10)
    
def bcd2bin(value):
    return value - 6 * (value >> 4)

class DS3231:
    
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
        
    def setAlarm(self,datetime,alarm=1):
        if alarm == 1: # two possible alarms -> one has seconds
            buffer = bytearray(4)
            buffer[0] = 0
            buffer[1] = bin2bcd(datetime[2]) # minute
            buffer[2] = bin2bcd(datetime[1]) # hour
            buffer[3] = bin2bcd(datetime[0]) # day
            self.i2c.writeto_mem(I2C_ADS,ALM1_REG,buffer)
            
            ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
            ctrl = ctrl | 0b101 # enable alarm 1
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(I2C_ADS,CTRL_REG,ctrl)
            
        elif alarm == 2:
            buffer = bytearray(3)
            buffer[0] = bin2bcd(datetime[2]) # minute
            buffer[1] = bin2bcd(datetime[1]) # hour
            buffer[2] = bin2bcd(datetime[0]) # day
            self.i2c.writeto_mem(I2C_ADS,ALM2_REG,buffer)
            
            ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
            ctrl = ctrl | 0b110 # enable alarm 2
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(I2C_ADS,CTRL_REG,ctrl)

    
    def disableAlarm(self,alarm=None):
        if alarm == None: # disable both alarms
            ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
            ctrl = ctrl & 0b11111100
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(I2C_ADS,CTRL_REG,ctrl)
        elif alarm == 1:
            ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
            ctrl = ctrl & 0b11111110
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(I2C_ADS,CTRL_REG,ctrl)
        elif alarm == 2:
            ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
            ctrl = ctrl & 0b11111101
            ctrl = bytearray([ctrl])
            self.i2c.writeto_mem(I2C_ADS,CTRL_REG,ctrl)
        
#         ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
#         print(bin(ctrl))
    
    def checkAlarm(self):
        ctrl = self.i2c.readfrom_mem(I2C_ADS,CTRL_REG,1)[0]
        ctrl = ctrl & 0b11
        if ctrl == 0b11:
            alarm1 = bytearray(4)
            alarm2 = bytearray(3)
            self.i2c.readfrom_mem_into(I2C_ADS,ALM1_REG,alarm1)
            self.i2c.readfrom_mem_into(I2C_ADS,ALM2_REG,alarm2)
            alarm1_d = bcd2bin(alarm1[3])
            alarm1_h = bcd2bin(alarm1[2])
            alarm1_m = bcd2bin(alarm1[1])
            alarm2_d = bcd2bin(alarm2[2])
            alarm2_h = bcd2bin(alarm2[1])
            alarm2_m = bcd2bin(alarm2[0])
            return "Alarm 1 set to: {} {}:{}\nAlarm 2 set to: {} {}:{}".format(alarm1_d,alarm1_h,alarm1_m,alarm2_d,alarm2_h,alarm2_m)
        
        elif ctrl == 0b01:
            alarm1 = bytearray(4)
            self.i2c.readfrom_mem_into(I2C_ADS,ALM1_REG,alarm1)
            alarm1_d = bcd2bin(alarm1[3])
            alarm1_h = bcd2bin(alarm1[2])
            alarm1_m = bcd2bin(alarm1[1])
            return "Alarm 1 set to: {} {}:{}".format(alarm1_d,alarm1_h,alarm1_m)
        
        elif ctrl == 0b10:
            alarm2 = bytearray(3)
            self.i2c.readfrom_mem_into(I2C_ADS,ALM2_REG,alarm2)
            alarm2_d = bcd2bin(alarm2[2])
            alarm2_h = bcd2bin(alarm2[1])
            alarm2_m = bcd2bin(alarm2[0])
            return "Alarm 2 set to: {} {}:{}".format(alarm2_d,alarm2_h,alarm2_m)
        return "No alarm set"
        
    
    def setTimer(self,t_min,alarm=1):
        'Receives time in minutes to activate alarm'
        now = self.getTime()[2:5]
        alarm_m = now[2] + t_min
        alarm_h = now[1]
        alarm_d = now[0]
        if alarm_m > 59:
            hours   = int(alarm_m / 60)
            alarm_h = alarm_h + hours
            alarm_m = alarm_m % 60
        if alarm_h > 23:
            days = int(alarm_h / 24)
            alarm_d = alarm_d + days
            alarm_h = alarm_h % 24
        datetime = (alarm_d,alarm_h,alarm_m)
        self.setAlarm(datetime,alarm)
        
        
    def __del__(self):
        pass
    
    


from machine import Pin, I2C
from utime import sleep
from time import localtime

i2c = I2C(0,scl=Pin(17),sda=Pin(16))
rtc = DS3231(i2c)


print(rtc.getTime())

# rtc.disableAlarm()
# print(rtc.checkAlarm())
# rtc.setTimer(1)
# print(rtc.checkAlarm())

while True:
    print(localtime())
    print(rtc.getTime())
    print(rtc.checkAlarm())
    sleep(1)



