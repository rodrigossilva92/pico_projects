from time import localtime

### MESSAGE TYPE ID DEFINITION
STR_COM     = 0b10101010    # start communication
END_COM     = 0b01010101    # end communication
UPD_TIME    = 0b11110000    # update timer
STR_TRANS   = 0b00001111    # start datalog transfer
MSG_OK      = 0b11001100    # confirmation of message received

### MESSAGE = msgID + N x databytes + msgChecksum
MSG_LEN     = 8        # number of bytes of message

class Communication:

    def __init__(self,ser):
        self.ser = ser
        self.started = False    # flag to check if communication has been stablished

    def send(self,msgID,data=[]):
        msg = bytearray(MSG_LEN)
        msg[0] = msgID
        for i in range(len(data)):
            msg[i+1] = data[i]
        for i in range(len(data)+1,MSG_LEN):
            msg[i] = 0b0
        print("Sent: ",end='')
        print(msg)
        #_msg[-1] = self.generateChecksum()
        self.ser.write(msg)

    def receive(self):
        msg = self.ser.read(MSG_LEN)
        print("Received: ",end='')
        print(msg)
        if msg == None: # empty message
            return
#        if self.verifyChecksum(_msg):
#            return _msg
        if msg[0] == STR_COM: # answer handshake
            self.send(STR_COM)
            self.started = True
        elif msg[0] == UPD_TIME: # update RTC
            print("update time")
            y = (msg[1] << 8) | msg[2]
            m = msg[3]
            d = msg[4]
            h = msg[5]
            min = msg[6]
            s = msg[7]
            datetime = (y,m,d,h,min,s)
            print(datetime)

    def generateChecksum(self,msg):
        'Creates a 8 bits checksum.'
        msgSum = sum(msg)
        while (msgSum >> 8) > 255:
            msgSum += (msgSum >> 8)
        checksum = ~msgSum & 255
        return checksum

    def verifyChecksum(self,msg):
        'Verify the message 8 bits checksum.'
        if sum(msg) == 255:
            return True

    def sendHandshake(self):
        'Send start communication signal.'
        if not self.started:
            _msgID = STR_COM
            self.send(_msgID)
            self.receive()
    
    def waitHandshake(self):
        'Wait for communication signal.'
        if not self.started:
            self.receive()
            
    def checkCommunication(self):
        return self.started

    def updateTime(self,retry=5):
        datetime = localtime()[0:6]
        msgID = UPD_TIME
        data = [0]*7
        data[0] = (datetime[0] >> 8) & 0b11111111 # year MSB
        data[1] = datetime[0] & 0b11111111        # year LSB
        data[2] = datetime[1]  # month
        data[3] = datetime[2]  # day
        data[4] = datetime[3]  # hour
        data[5] = datetime[4]  # minute
        data[6] = datetime[5]  # second
        print(data)
        self.send(msgID,data)
        #if self.receive():
        #    return 0
        #self.updateTime(_datetime,_retry-1)


    def endCommunication(self):
        if self.started:
            self.started = False
            
    def __del__(self):
        print("Communication finished.")