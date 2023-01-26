import serial
import time

class STM():
    def __init__(self):
        self.BAUD_RATE = 115200
        self.SERIAL_PORT = "/dev/ttyUSB0"
        self.service = None
        self.STM_MSG_LENGTH = 20

    def connect(self):
        try:
            self.service = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=5)
            time.sleep(1)

            if not self.service:
                print("Connected to STM...")

        except Exception as e:
            print("Error in connecting to STM: " + str(e))
            time.sleep(0.5)
            self.connect()

    def sendMsg(self, msg):
        try:
            self.service.write(msg.encode('utf-8'))
        except Exception as e:
            print('Error in sending message to STM: ' + str(e))
            self.connect()
            time.sleep(0.5)
            self.sendMsg(msg)

    def receiveMsg(self):
        try:
            msg = self.service.read(self.STM_MSG_LENGTH)
            if len(msg) > 0:
                return msg.decode('utf-8')
        except Exception as e:
            print('Error receiving message from STM: ' + str(e))
            self.connect()
            time.sleep(0.5)
            self.receiveMsg()

    def disconnect(self):
        try:
            if self.service:
                self.service.close()
                print('Serial connection closed...')
        except Exception as e:
            print("Error in disconnecting from STM..." + str(e))