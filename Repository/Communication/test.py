from communication import *
from time import localtime

com = Communication('test')

datetime = localtime()[0:6]
com.updateTime(datetime)