from machine import mem32
from utime import localtime

### Register address definition
SETUP_0 = 0x4005c004
SETUP_1 = 0x4005c008
CTRL    = 0x4005c00c
RTC_0   = 0x4005c01c
RTC_1   = 0x4005c018
    
class RTC:
    
    def __init__(self):
        pass        
    
    def updateRTC(self,dt=None):
        if dt == None:
            dt = localtime()
        else:
            if len(dt) < 6:
                print("Enter with a tuple of 6 values: (YYYY, MM, DD, HH, MMM, SS)")
                return
        setup_0_value = (dt[0] << 12) | (dt[1] << 8) | dt[2]
        setup_1_value = (dt[3] << 16) | (dt[4] << 8) | dt[5]
        
        mem32[SETUP_0] = setup_0_value
        mem32[SETUP_1] = setup_1_value
        mem32[CTRL] = mem32[CTRL] | (0b1 << 4) # set load bit to 1
    
    def readRTC(self):
        rtc_0_value = mem32[RTC_0]
        rtc_1_value = mem32[RTC_1]
        
        y = (rtc_1_value >> 12) & 0b111111111111
        m = (rtc_1_value >> 8) & 0b1111
        d = rtc_1_value & 0b11111
        h = (rtc_0_value >> 16) & 0b11111
        mi = (rtc_0_value >> 8) & 0b111111
        s = rtc_0_value & 0b111111
        
        return(y,m,d,h,mi,s)
    
    


