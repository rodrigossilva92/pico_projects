import os
import ustruct
from utime import localtime
from array import array

LOG_EXTENSIONS = ['dt','txt'] # possible log extensions

class DataLog:
    '''Class for data log manipulations on Raspberry Pico'''
    
    def __init__(self,logName,logExt=None,path=None):

        # log name and extension handling
        _logName = logName.split('.')
        if _logName[-1] in LOG_EXTENSIONS:
            self.logName = _logName[0]
            self.logExt = _logName[-1]
        else:
            if logExt == 'txt':
                self.logName = logName
                self.logExt = 'txt'
            else:
                self.logName = logName
                self.logExt = 'dt' # standard extension is 'dt'
                
        if path == None:
            self.path = '/log/'
        else:
            self.path = path
        
        self.logFileName = None
        self.logFileEmpty = None
        
        self.logCreate()
        
        
    def logCreate(self):
        'Creates file to store data log of the current day.'
        
        now = localtime() # Y M D H M S WD YD
        date = '{:04d}{:02d}{:02d}'.format(now[0],now[1],now[2]) #adjust date to YYYYMMDD string format
        self.logFileName = self.path+date+'_'+self.logName+'.'+self.logExt
        
        if self.logExt == 'dt':
            try:
                self.file = open(self.logFileName,'ab') # create binary file in append mode
            except:
                print('Could not create file '+self.logFileName)
                return 0
        elif self.logExt == 'txt':
            try:
                self.file = open(self.logFileName,'a') # create text file in append mode
            except:
                print('Could not create file '+self.logFileName)
                return 0
        self.file.close()
        
        ### check if dt the file is empty
        if self.logExt == 'dt':
            self.file = open(self.logFileName,'rb')
            content = self.file.read()
            if content == b'':
                self.logFileEmpty = True
            else:
                self.logFileEmpty = False
            self.file.close()     
        
    
    def logWrite(self,data):
        'Write data to log file. Input must be a vector of values.'
        ### write to dt file 
        if self.logExt == 'dt':
            try:
                self.file = open(self.logFileName,'ab') # create binary file in append mode
            except:
                print('Could not open file '+self.logFileName)
                return 0
            
            f_data = array('f') # creates array of floats -> 4 bytes each float
            
            if self.logFileEmpty: # first write -> file empty
                f_data.append(len(data))
                self.logFileEmpty = False
            for i in data:
                f_data.append(i)
            self.file.write(f_data)
        
        ### write to txt file
        elif self.logExt == 'txt':
            try:
                self.file = open(self.logFileName,'a') # create binary file in append mode
            except:
                print('Could not open file '+self.logFileName)
                return 0
        
            line = ''
            for i in data:
                line = line+str(i)+' '
            line = line+'\n'
            self.file.write(line)        
        
        self.file.close()
    
    
    def __del__(self):
        self.file.close()


### functions outside of class for reading logs
def logRead(fileName=None):
    'Reads specific fileName log. If no input, reads all files in log directory.'
    ext = None
    path = '/log/'
    if fileName == None: # reads all files in log folder
        os.chdir(path)
        logFiles = os.listdir()
        for fileName in logFiles:
            fileExt = fileName.split('.')
            fileExt = fileExt[-1]
            if fileExt not in LOG_EXTENSIONS:
                continue # ignore file
            fileRead(path+fileName,fileExt)
            os.rename(path+fileName,path+'read/'+fileName)
        
    else: # reads especific file
        fileExt = fileName.split('.')
        fileExt = fileExt[-1]
        if fileExt not in LOG_EXTENSIONS:
            print("File extension not compatible.")
            return 0
        fileName = path+fileName
        fileRead(fileName,fileExt)

def fileRead(fileName,fileExt):
    # read dt file
    if fileExt == 'dt':
        try:
            file = open(fileName,'rb')
        except:
            print('Could not read file '+fileName)
            return 0
        
        content = file.read()    
        size = int(ustruct.unpack('f',content)[0])
        lineSize = size*4
        lineFormat = str(size)+'f'
        for i in range(4,len(content),lineSize):
            line = ustruct.unpack(lineFormat,content[i:i+lineSize]) # BUFFER MAX SIZE 40 BYTES -> 10F
            print(line)
    
    # read txt file    
    if fileExt == 'txt':
        try:
            file = open(fileName, 'r')
        except:
            print('Could not read file '+fileName)
            return 0
        
        content = file.readlines()
        for line in content:
            print(line)   
    
    file.close()
   
    
    
###  EXAMPLE CODE   
# log = DataLog('test.txt')
# log.logWrite([6,7,8,9,10])
# 
# logRead('20210610_test.txt')
