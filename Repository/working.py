from machine import Pin, I2C

i2c = I2C(0,scl=Pin(17),sda=Pin(16))

print(i2c.scan())