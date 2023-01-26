from Serial import STM
from android import Android
from wifi_server import Wifi_Server
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from multiprocessing import Process, Queue
import time
import json
import base64
from ast import literal_eval
import subprocess


class MultiThreading():
    def __init__(self):
        self.android = Android()
        self.stm = STM()
        self.PC = Wifi_Server(65432, "192.168.37.1")
        self.messageQueue = Queue()
        self.stmInstrQueue = Queue()
        self.imageQueue = Queue()
        self.totalObstacle = 0
        self.currentObstacle = 0
        # self.latestImg = 0
        self.path = "/home/pi/Desktop/MDP/Pics/"
        # 0 = left, 1 = right
        self.firstDirection = 0
        self.secondDirection = 0
        self.isFirstDetected = False
        self.isSencondDetected = False
        # /home/pi/Desktop/MDP/Pics/obstacle1.jpg
        self.filename = "ostacle"+ str(self.currentObstacle) +".jpg"
        

    def start(self):
        Process(target=self.streaming).start()
        try:
            print("starting connection")
            while self.PC.connected == False:
                print("waiting for PC connection")
                self.PC.start_server()
            while self.android.connected == False:
                print("waiting for ANDROID connection")
                self.android.connect()
            while self.stm.connected == False:
                print("waiting for STM connection")
                self.stm.connectSerial()
        except Exception as e:
            print(e)
        print("all connected")
        self.androidReadProcess = Process(target=self.readAndroid, args=(self.messageQueue, self.stmInstrQueue))
        self.stmReadProcess = Process(target=self.readSTM, args=(self.messageQueue, self.stmInstrQueue))
        self.algoReadProcess = Process(target=self.readPC, args=(self.messageQueue, self.stmInstrQueue))
        self.writeProcess = Process(target=self.writeTo, args=(self.messageQueue, self.stmInstrQueue))
        # self.disconnectProcess = Process(target=self.disconnect)

        #start the processes
        print("starting processes")
        # self.androidReadProcess.start()
        self.stmReadProcess.start()
        self.algoReadProcess.start()
        self.writeProcess.start()

        # self.disconnectProcess.start()

        # stmi testing
        # Right Turn
        # STMImsg = {
        #     "to":"STM",
        #     "header":"STMI",
        #     "body": "[['FR 45','FL 45','FL 45','FR 45']]"
        # }
        # STMImsg = {
        #     "to":"STM",
        #     "header":"STMI",
        #     "body": "[['FL 90','FR 90','FR 90','FC 50','FR 90','FR 90','FL 90','FC 30']]"
        # }

        # self.handlePC(json.dumps(STMImsg), self.messageQueue, self.stmInstrQueue)

        # algo test
        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "OBS",
        #         "body": "[1,2,19,S],[2,7,13,N],[3,11,8,E],[4,16,17,W],[5,20,10,W],[6,14,3,E]"
        #     }))

        # test image file
        # time.sleep(10)
        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "PHOTO_COLLAGE",
        #         "body": "PHOTO_COLLAGE"
        #     }))


        # A2test code
        # self.picam.captureImageWithObsID(1)

        # # test image file
        # time.sleep(10)
        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "CV",
        #         "body": "Pics/obstacle1.jpg"
        #     }))

        # time.sleep(15)

        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "CV",
        #         "body": "Pics/obstacle2.jpg"
        #     }))

        # time.sleep(15)

        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "CV",
        #         "body": "Pics/obstacle3.jpg"
        #     }))
        # A5
        # self.picam.captureVideo()
        # time.sleep(10)
        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "CV",
        #         "body": "Pics/video.h264"
        #     }))

        # self.picam.captureImageWithObsID(2)

        # print("send TEST messages to PC, STM and ANDROID")
        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "PC",
        #         "header": "TEST",
        #         "body": "hello PC, connected to RPI"
        #     }))

        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "STM",
        #         "header": "TEST",
        #         "body": "hello STM, connected to RPI"
        #     }))

        # self.messageQueue.put_nowait(json.dumps({   
        #         "to": "ANDROID",
        #         "header": "TEST",
        #         "body": "hello ANDROID, connected to RPI"
        #     }))

        # {
        #     "to": "STM",
        #     "header": "TEST_MOVEMENT",
        #     "body": "BC10"
        # }

         # {
        #     "to": "RPI",
        #     "header": "DONE",
        #     "body": "DONE"
        # }


        # [F 130 ]
        # [B 10  , RF 91 , F 50  , LB 86 , F 10  ]
        # [B 20  , LF 86 , F 10  ]
        # [B 30  , RF 91 , LF 86 , RF 91 , F 10  , RB 85 , F 10  ]
        # [B 10  , LF 86 , B 70  , RB 85 , F 10  ]
        # [B 10  , RF 91 , F 50  , LF 86 , F 30  , LB 86 , RB 85 , F 10  ]

        # [[F 130 ],[B 10  , RF 91 , F 50  , LB 86 , F 10  ],[B 20  , LF 86 , F 10  ],[B 30  , RF 91 , LF 86 , RF 91 , F 10  , RB 85 , F 10  ],[B 10  , LF 86 , B 70  , RB 85 , F 10  ],[B 10  , RF 91 , F 50  , LF 86 , F 30  , LB 86 , RB 85 , F 10  ]]

    def streaming(self):
        subprocess.call(["python stream.py"], shell=True)
        

    def writeTo(self, messageQueue, stmInstrQueue):
            while True:
                try:
                    if not messageQueue.empty():
                        msg = json.loads(messageQueue.get())
                        if (msg['to'] == "ANDROID"):
                            if not ("ROBOT" in msg['header']):
                                print("RPI is writing to: " + msg['to'])
                                print("Writing: "+ msg['header'] + ": " + msg['body'] )
                            self.android.writeMsg(str(msg))
                            continue
                        
                        if (msg['to'] == "STM"):
                            print("RPI is writing to: " + msg['to'])
                            print("Writing: "+ msg['header'] + ": " + msg['body'] )
                            print("msg: "+str(msg["body"]))

                            stmi_string = str(msg["body"])
                            self.stm.writeMsg(stmi_string)

                            continue
                        
                        if (msg['to'] == "PC"):
                            if(msg['header'] == "CV"):
                                with open(msg["body"], "rb") as file:
                                    converted_string = base64.b64encode(file.read())
                                    self.PC.writeMsg(converted_string)
                                    # print(converted_string)    
                                    
                                    # time.sleep(2)
                                    IMG_DONE_STR = "IMG_DONE"
                                    self.PC.writeMsg(IMG_DONE_STR.encode(encoding="UTF-8",errors="strict"))
                                    print("IMG_DONE")

                            else:
                                print("RPI is writing to: " + msg['to'])
                                print("Writing: "+ msg['header'] + ": " + msg['body'])
                                self.PC.writeMsg(str(msg).encode(encoding="UTF-8",errors="strict"))  
                            continue
                        
                except Exception as e:
                    print("WriteTo failed: " + str(e))
                    raise e

                # time.sleep(0.5)

    def handleAndroid(self, msg, messageQueue,stmInstrQueue):
        msg_json = json.loads(msg)

        if msg_json["header"] == "OBS":
            messageQueue.put_nowait(json.dumps({   
                "to": "PC",
                "header": "OBS",
                "body": str(msg_json["body"])
            }))
        elif msg_json["header"] == "TEST_MOVEMENT":
            messageQueue.put_nowait(json.dumps({ 
                "to": "STM",
                "header": "TEST_MOVEMENT",
                "body": str(msg_json["body"])
            }))
            
        elif msg_json["header"] == "START":
            # put the first intruction into the message
            if not stmInstrQueue.empty():
                stmInstruction = stmInstrQueue.get()
                print("instruction queue size: "+str(stmInstrQueue.qsize()))
                print("current stm instruction: " + stmInstruction)
                messageQueue.put_nowait(json.dumps({   
                    "to": "PC",
                    "header": "START",
                    "body": "START"
                }))
                messageQueue.put_nowait(json.dumps({   
                    "to": "STM",
                    "header": "STMI",
                    "body": str(stmInstruction)
                }))
                 
            else:
                print("stmInstrQueue is empty")

    def handlePC(self, msg, messageQueue, stmInstrQueue):
        try:
            msg_json = json.loads(msg)
        except Exception as e:
            print(e)
            return
        if msg_json["header"] == "STMI":
            print("STM instructions received: " + msg_json["body"])
            # split the intructions, adding IMG at the end of each array and put into the stmInstrQueue
            # update the total obstacle self.totalObstacle
            STMI = literal_eval(msg_json["body"])
            print(STMI)
            for obstacle in STMI:
                for STMI in obstacle:
                    stmInstrQueue.put_nowait(STMI)

            photoCollage = "PHOTO_COLLAGE"
            stmInstrQueue.put_nowait(photoCollage)
            print("instruction queue size: "+str(stmInstrQueue.qsize()))

        elif msg_json["header"] == "POS":
            print("STM POS instructions received: " + msg_json["body"])
            messageQueue.put_nowait(json.dumps({   
                "to": "ANDROID",
                "header": "POS",
                "body": str(msg_json["body"])
            }))

        elif msg_json["header"] == "IMAGE_ID":
            direction = 0
            if msg_json["body"] == "38":
                print("Next should turn right")
                direction = 1
            else:
                print("Next should turn left")
                direction = 0
            if (not isFirstDetected):
                isFirstDetected = True
                firstDirection = direction
            elif (not isSencondDetected):
                isSencondDetected = True
                secondDirection = direction
        else:
            messageQueue.put_nowait(json.dumps({   
                "to": msg_json['to'],
                "header": msg_json['header'],
                "body": str(msg_json["body"])
            }))

    # handle messages from STM
    def handleSTM(self, msg, messageQueue, stmInstrQueue):
        if msg == "D":
            print("=====================================================")
            print("Intruction done")
            messageQueue.put_nowait(json.dumps({   
                "to": "ANDROID",
                "header": "DONE",
                "body": "DONE"
            }))
            # put the next intruction into the message
            if not stmInstrQueue.empty():
                stmInstruction = stmInstrQueue.get()
                print("instruction queue size: "+ str(stmInstrQueue.qsize()))
                if("IMG" in stmInstruction):
                    # print("=====================================================")
                    # print("current stm instruction: IMG")
                    # self.currentObstacle += 1
                    # time.sleep(2)
                    # path = self.picam.captureImageWithObsID(self.currentObstacle)
                    # # convert imagefile to string base64 and send it to PC
                    # time.sleep(2)
                    # messageQueue.put_nowait(json.dumps({
                    # "to": "PC",
                    # "header": "CV",
                    # "body": path
                    # }))
                    # messageQueue.put_nowait(json.dumps({   
                    #     "to": "ANDROID",
                    #     "header": "IMAGE_ID",
                    #     "body": str(self.latestImg)
                    # }))
                    print("Intruction done")
                    messageQueue.put_nowait(json.dumps({   
                        "to": "ANDROID",
                        "header": "DONE",
                        "body": "DONE"
                    }))
                    
                    print("=====================================================")
                    stmInstruction = stmInstrQueue.get()
                    print("instruction queue size: "+ str(stmInstrQueue.qsize()))
                    print("current stm instruction: " + stmInstruction)
                    
                    if(stmInstruction == "PHOTO_COLLAGE"):
                        time.sleep(20)
                        messageQueue.put_nowait(json.dumps({
                            "to": "PC",
                            "header": "PHOTO_COLLAGE",
                            "body": "PHOTO_COLLAGE"
                        }))
                        time.sleep(10)
                        self.disconnect()
                        # end mission
                    else:
                        messageQueue.put_nowait(json.dumps({
                            "to": "STM",
                            "header": "STMI",
                            "body": str(stmInstruction)
                        }))
                else:
                    print("current stm instruction: " + stmInstruction)
                    messageQueue.put_nowait(json.dumps({
                        "to": "STM",
                        "header": "STMI",
                        "body": str(stmInstruction)
                    }))
            else:
                print("stmInstrQueue is empty")

    def readAndroid(self, messageQueue, stmInstrQueue):
        while True:
            try:
                msg = self.android.readMsg()
                if (msg is not None):
                    print("Read from Android: " + msg)
                    self.handleAndroid(msg, messageQueue, stmInstrQueue)
            except Exception as e:
                print("Read from Android failed (process): " + str(e))
                raise e
            
    def readSTM(self, messageQueue, stmInstrQueue):
        # self.picam = picam()
        # self.stm.writeMsg("FC 1")

        while True:
            try:
                msg = self.stm.readMsg()
                if (msg is not None):
                    print("Read from STM: " + msg)
                    self.handleSTM(msg, messageQueue, stmInstrQueue)
                    msg=None
            except Exception as e:
                print("Read from STM failed (process): " + str(e))
                raise e

    def readPC(self, messageQueue, stmInstrQueue):
        self.PC.readThread()
        while True:
            try:
                if (self.PC.msg.qsize() > 0):
                    data = self.PC.msg.get()
                    print("Read from PC: " + data.decode("UTF-8"))
                    self.handlePC(data.decode("UTF-8"), messageQueue, stmInstrQueue)
                # if (self.PC.img is not None):
                #     if (self.PC.img != 0):
                #         data = self.PC.img.decode("UTF-8")
                #         try:
                #             msg_json = json.loads(data)
                #             self.latestImg = msg_json["body"]
                #         except Exception as e:
                #             print(e)
            except Exception as e:
                print("Read from PC failed (process): " + str(e))
                raise e

    def disconnect(self):
        # stringInput = str(input("enter 'dc' to disconnect"))
        # self.androidReadProcess.kill()
        # self.stmReadProcess.kill()
        # self.algoReadProcess.kill()
        # self.writeProcess.kill()

        self.PC.disconnect()
        self.android.disconnect()
        print("=====================================================")
        print("PC and Anroid disconnected")
        exit()
            