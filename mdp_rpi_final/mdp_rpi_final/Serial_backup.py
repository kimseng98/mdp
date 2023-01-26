import serial
import time

# to write to serial port from RPI: echo "hello" > /dev/ttyUSB0

class STM:
    def __init__(self):
        self.serConn = None
        self.serialPort = "/dev/ttyUSB0"
        self.baudRate = 115200
        self.connected = False

    def connectSerial(self):
        try:
            print("waiting for STM serial connection..")
            self.serConn = serial.Serial(self.serialPort, self.baudRate)
            self.connected = True
            print("STM serial connecton succesful, port: " + self.serialPort)
            self.checkReadBuffer()
            
        except Exception as e:
            print("Connect to STM serial failed: " + str(e))
            self.connected = False
    
    def checkReadBuffer(self):
        if (self.serConn.in_waiting > 0):
            print("Serial Read Buffer has " + str(self.serConn.in_waiting) + " bytes, flushing...")
            self.serConn.reset_input_buffer()
            print("done")

    def readMsg(self):
            try:
                recvMsg = self.serConn.read(1).decode("UTF-8").strip()
                if (len(recvMsg) > 0):
                    return recvMsg
                return None
            except Exception as e:
                print("Read from STM failed: " + str(e))
        
    def writeMsg(self, msg):
        try:
            
            print("msg: "+ msg)
            self.serConn.write(msg.encode())
            time.sleep(0.5)
        except Exception as e:
            print("Write to STM failed: " + str(e))



#---------------------- For threading method -------------------

    def readThread(self, android):
        while True:
            if not self.connected:
                break
            try:
                recvMsg = self.serConn.read(8).decode("UTF-8").strip()
                print("Read from STM: " + recvMsg)
                if (len(recvMsg) > 1):

                    if (recvMsg == "echo"):
                        self.writeThread("echoing...")
                        continue

                    if (recvMsg == "reply"):
                        android.writeThread("stm says hello")
                        continue
                    
                    if (recvMsg == "S"):
                        print("STM is done moving")

            except Exception as e:
                print("Read from STM failed: " + str(e))

    def writeThread(self, msg):
        try:
            self.serConn.write(msg.encode())
            print(msg)
            # time.sleep(0.5)
        except Exception as e:
            print("Write to STM failed: " + str(e))
