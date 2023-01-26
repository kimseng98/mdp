import socket
import time
import os

class PcComm():
    def __init__(self):
        self.IP_ADDDRESS = "192.168.37.1"
        self.serverSocket = None
        self.nPort = 22
        self.imgClient = None
        self.imgClientIP = None
        self.algoClient = None
        self.algoClientIP = None

        self.numConnections = 0
        self.isConnected = False
        self.msgQueue = []
        self.BUFFER_SIZE = 1024

        self.connect()

    def connect(self):
        try:
            if not self.isConnected:
                self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Ensures address can immediately be reused even after multiple iterations
                self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.serverSocket.bind((self.IP_ADDDRESS, self.nPort))
                self.serverSocket.listen(2)

                print("RPi is listening for PC communication...")
                self.imgClient, self.imgClientIP = self.serverSocket.accept()
                self.numConnections += 1
                print("RPi is connected to " + str(self.imgClient))

                self.algoClient, self.algoClientIP = self.serverSocket.accept()
                self.numConnections += 1
                print("RPi is connected to " + str(self.algoClient))
                print("Number of concurrent connections: " + str(self.numConnections))

                self.isConnected = True

        except Exception as e:
            print("Connection Error: " + str(e))
            self.connect()

    def disconnect(self):
        try:
            if self.serverSocket:
                self.serverSocket.close()
                print("RPi socket closed...")

            if self.imgClient:
                self.imgClient.close()
                print("Image Rec client socket closed...")

            if self.algoClient:
                self.algoClient.close()
                print("Algo client socket closed...")

            self.isConnected = False

        except Exception as e:
            print("Error in disconnecting from PC: " + str(e))

    def sendMsgToImg(self, msg=""):
        try:
            if msg != "":
                if self.isConnected:
                    self.imgClient.send(bytes(msg, "utf-8"))
                    FILE_TO_READ = "a.jpeg"
                    filesize = os.path.getsize(FILE_TO_READ)
                    self.imgClient.send(bytes(str(filesize), "utf-8"))
                    time.sleep(0.5)

                    with open(FILE_TO_READ, "rb") as img_file:
                        img_bytes = img_file.read()
                        self.imgClient.send(img_bytes)
                    print("Successfully sent image to server...")

                else:
                    print("In sendMsgToImg() function, RPI is not connected properly...")
                    self.connect()
                    return False

        except Exception as e:
            print("Error in sending: " + str(e))
            self.connect()
            self.sendMsgToImg(msg)

    def sendMsgToAlgo(self, msg=""):
        try:
            if msg != "":
                if self.isConnected:
                    msgLength = msg.encode("UTF-8")
                    self.algoClient.send(len(msgLength).to_bytes(2, byteorder="big"))
                    self.algoClient.send(msgLength)
                    print("In sendMsgToAlgo() function, Message has been sent to Algo: " + str(msg))
                    return True

                else:
                    print("In sendMsgToAlgo() function, RPI is not connected properly...")
                    self.connect()
                    return False
        except Exception as e:
            print("Error in sending: " + str(e))
            self.connect()
            self.sendMsgToAlgo(msg)

    def receiveMsgFromImg(self):
        try:
            msgReceived = self.imgClient.recv(self.BUFFER_SIZE).decode("utf-8")
            if str(msgReceived) != "":
                print("In receiveMsgFromImg() function, Message received is: " + str(msgReceived))
                return msgReceived
            else:
                return None

        except Exception as e:
            print("Error in receiving: " + str(e))
            self.connect()
            self.receiveMsgFromImg()

    def receiveMsgFromAlgo(self):
        try:
            msgReceived = self.algoClient.recv(self.BUFFER_SIZE).decode("utf-8")
            if str(msgReceived) != "":
                print("In receiveMsgFromAlgo() function, Message received is: " + str(msgReceived))
                return msgReceived
            else:
                return None

        except Exception as e:
            print("Error in receiving: " + str(e))
            self.connect()
            self.receiveMsgFromImg()