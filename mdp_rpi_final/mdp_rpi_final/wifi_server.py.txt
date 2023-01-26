import socket
import os
from threading import Thread
from multiprocessing import Process, Queue

class Wifi_Server:
    def __init__(self, port, host):
        self.host = host  # The server's hostname or IP address
        self.port = port  # The port used by the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.conn1 = None
        self.addr1 = None
        # self.conn2 = None
        # self.addr2 = None
        # self.conn3 = None
        # self.addr3 = None
        # self.conn4 = None
        # self.addr4 = None
        self.connected = False
        self.threadCount = 0
        self.msg = Queue()
        self.img = None
        # self.msg1 = None
        # self.msg2 = None
        # self.msg3 = None

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
        except Exception as e:
            print("Wifi server failed: " + str(e))

        print("listening")
        self.socket.listen()
        self.conn1, self.addr1 = self.socket.accept()
        print("PC 1 connected")
        self.socket.listen()
        self.conn2, self.addr2 = self.socket.accept()
        print("PC 2 connected")
        # self.socket.listen()
        # self.conn3, self.addr3 = self.socket.accept()
        # self.socket.listen()
        # self.conn4, self.addr4 = self.socket.accept()
        print("ALL PC connected")
        self.connected = True
        self.thread1 = Thread(target = self.readMsg1)
        self.thread2 = Thread(target = self.readMsg2)
        # self.thread3 = Thread(target = self.readMsg3)
        # self.thread4 = Thread(target = self.readMsg4)

    def writeMsg(self, msg):
        try:
            self.conn1.sendall(msg)
        except:
            print("error sending msg to conn1")
        try:
            self.conn2.sendall(msg)
        except:
            print("error sending msg to conn2")
        # try:
        #     self.conn3.sendall(msg)
        # except:
        #     print("error sending msg to conn3")
        # try:
        #     self.conn4.sendall(msg)
        # except:
        #     print("error sending msg to conn4")

    def readMsg1(self):
        while True:
            data = self.conn1.recv(4096)
            if data:
                print(1)
                print(f"received: {data}")
                # if ("IMAGE_ID" in data.decode("UTF-8")):
                #     self.img = data
                # else:
                self.msg.put_nowait(data)
                
    def readMsg2(self):
        while True:
            data = self.conn2.recv(4096)
            if data:
                print(2)
                print(f"received: {data}")
                # if ("IMAGE_ID" in data.decode("UTF-8")):
                #     self.img = data
                # else:
                self.msg.put_nowait(data)

    def readMsg3(self):
        while True:
            data = self.conn3.recv(4096)
            if data:
                print(3)
                # if ("IMAGE_ID" in data.decode("UTF-8")):
                #     self.img = data
                # else:
                self.msg.put_nowait(data)
                print(f"received: {data}")
                # self.msg.put_nowait(data)
    def readMsg4(self):
        while True:
            data = self.conn4.recv(4096)
            if data:
                print(4)
                print(f"received: {data}")
                if ("IMAGE_ID" in data.decode("UTF-8")):
                    self.img = data
                else:
                    self.msg.put_nowait(data)

        # data1 = self.connection.recv(4096)
        # if data1:
        #     print(f"received: {data1}")
        #     return data1
        # data2 = self.connection.recv(4096)
        # if data2:
        #     print(f"received: {data2}")
        #     return data2

    def readThread(self):
        self.thread1.start()
        self.thread2.start()
        # self.thread3.start()
        # self.thread4.start()

    def disconnect(self):
        self.socket.close()

   

    # def accept_connections(ServerSocket):
    #     Client, address = ServerSocket.accept()
    #     print('Connected to: ' + address[0] + ':' + str(address[1]))
    #     start_new_thread(client_handler, (Client, ))

    # def start_server(host, port):
    #     ServerSocket = socket.socket()
    #     try:
    #         ServerSocket.bind((host, port))
    #     except socket.error as e:
    #         print(str(e))
    #     print(f'Server is listing on the port {port}...')
    #     ServerSocket.listen(3)
    #     while True:
    #         accept_connections(ServerSocket)
            
