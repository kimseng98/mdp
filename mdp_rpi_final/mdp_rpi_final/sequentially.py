import signal
import os
import sys
from Serial import STM
from android import Android
from wifi_server import Wifi_Server
import json
import subprocess
from multiprocessing import Process, Queue, Manager
from gpiozero import DistanceSensor
import math
import time

def readSTM():
    while True:
        try:
            msg = stm.readMsg()
            if (msg is not None):
                print("Read from STM: " + msg)
                if msg == "D":
                    # count_done+=1
                    isDone.value = 1

        except Exception as e:
            print("Read from STM failed (process): " + str(e))
            raise e

def calibrateFor45():
    for i in range(4):
        stm.writeMsg(f"FA 84")
        time.sleep(1)
    while True:
        pass

def FA45():
    stm.writeMsg(f"FA 45")

def FD45():
    stm.writeMsg(f"FD 45")

def FA90():
    stm.writeMsg(f"FA 84")

def FD90():
    stm.writeMsg(f"FD 85")

def waitForDone():
    while not isDone.value == 1:
        pass
    isDone.value = 0

def readPC():
    PC.readThread()
    while True:
        try:
            if (PC.msg.qsize() > 0):
                data = PC.msg.get()
                print("Read from PC: " + data.decode("UTF-8"))
                data_json = json.loads(data)
                if(data_json['header'] == 'IMAGE_ID'):
                    firstDirection.value = data_json['body']
                    # print("First direction: " + firstDirection.value)
        except Exception as e:
            print("Read from PC failed (process): " + str(e))
            raise e

def streaming():
    subprocess.call(["python stream.py"], shell=True)
    print("Streaming Start")

def connection():
    print("starting connection")
    while PC.connected == False:
        print("waiting for PC connection")
        PC.start_server()
        PCReadProcess.start()
    while android.connected == False:
        print("waiting for ANDROID connection")
        android.connect()
    while stm.connected == False:
        print("waiting for STM connection")
        stm.connectSerial()
        STMReadProcess.start()
#    calibrateFor45()

# mission start,
def getDistance():
    distance = ultrasonic.distance*100
    print(f"sensor detect:{str(math.floor(distance))}")
    return math.floor(distance)

def firstObstacle(first_Obstacle_Distance):
    STMI = "FC "+ str(first_Obstacle_Distance-25)
    print(f"STMI: {STMI}" )
    print("First distance: " + str(first_Obstacle_Distance))
    stm.writeMsg(STMI)
    waitForDone()

    print(f"first_obstacle: {firstDirection.value}")

    if(str(firstDirection.value) == "38"):
        isSecondDetected = True
        FD45()
        waitForDone()
        FA45()
        waitForDone()
        stm.writeMsg(f"FC 5")
        waitForDone()
        FA45()
        waitForDone()
        FD45()
        waitForDone()


        # if(secondDirection == first_img):
        #     stm.writeMsg(f"FD 45")
        #     stm.writeMsg(f"FC 47")
        #     second_Obstacle_Distance = getDistance()
        #     # get the distance here and move till clear the second obstacle
            
        # else:
        #     stm.writeMsg(f"FC 4")
        #     stm.writeMsg(f"FA 45")
        #     stm.writeMsg(f"FD 47")

        # stm.writeMsg(f"FR 90")
        # stm.writeMsg(f"FL 90")
        # stm.writeMsg(f"FL 90")
        # stm.writeMsg(f"FR 90")
    else:
        isSecondDetected = True
        FA45()
        waitForDone()
        FD45()
        waitForDone()
        # if(secondDirection == first_img)
        stm.writeMsg(f"FC 5")
        waitForDone()
        FD45()
        waitForDone()
        FA45()
        waitForDone()

        # stm.writeMsg(f"FL 90")
        # stm.writeMsg(f"FR 90")
        # stm.writeMsg(f"FR 90")
        # stm.writeMsg(f"FL 90")
    #Done here

def secondObstacle(second_Obstacle_Distance):
    while (getDistance() < 32):
        stm.writeMsg(f"BC 1")
        waitForDone()
    second_Obstacle_Distance.value = int(getDistance())
    print("Second distance: " + str(second_Obstacle_Distance.value))
    STMI ="FC "+ str(second_Obstacle_Distance.value-30)
    if(second_Obstacle_Distance.value-30 > 0):
        stm.writeMsg(STMI)
        waitForDone()
    # second_img = secondDirection
    print(f"second_obstacle: {firstDirection.value}")
    
    if(str(firstDirection.value) == "38"):
        FD90()
        waitForDone()
        stm.writeMsg(f"FC 10")
        waitForDone()
        FA90()
        waitForDone()
        FA90()
        waitForDone()
        stm.writeMsg(f"FC 70")
        waitForDone()
        FA90()
        waitForDone()
    else:
        FA90()
        waitForDone()
        stm.writeMsg(f"FC 10")
        waitForDone()
        FD90()
        waitForDone()
        FD90()
        waitForDone()
        stm.writeMsg(f"FC 70")
        waitForDone()
        FD90()
        waitForDone()

def finalDistance(distance):
    stm.writeMsg(f"FC " + str(second_Obstacle_Distance.value+ 90))
    waitForDone()
    if(firstDirection.value == "38"):
        FA90()
        waitForDone()
        stm.writeMsg(f"FC 15")
        waitForDone()
        FD90()
        waitForDone()
    else:
        FD90()
        waitForDone()
        stm.writeMsg(f"FC 15")
        waitForDone()
        FA90()
        waitForDone()
    finalLength = getDistance()
    stm.writeMsg(f"FC " + str(finalLength-10))
    waitForDone()
   # while (not getDistance() < 20):
    #    stm.writeMsg(f"FC 2")
     #   waitForDone()
    #Done
def quitHandler(signum, frame):
    pass


# misson prep
isFirstDetected = False
isSecondDetected = False
android = Android()
stm = STM()
PC = Wifi_Server(65432, "192.168.37.1")
image_Queue = Queue()
ultrasonic = DistanceSensor(trigger=24, echo=23)
ultrasonic.max_distance = 2
ultrasonic.threshold_distance = 0.01
first_Obstacle_Distance = 0

manager = Manager()
firstDirection = manager.Value("i", 0)
isDone = manager.Value("t", 0)
second_Obstacle_Distance = manager.Value("q", 0)
process = Process(target=streaming)
first_img = 0
second_img = 0
PCReadProcess = Process(target=readPC)
STMReadProcess = Process(target=readSTM)
count_done = 0

command = "sudo chmod o+rw /var/run/sdp"
subprocess.Popen(command.split())

# try:
process.start()
connection()

# wait for start
isFirstDetected = True

# start = False
# while start == False:
#     try:
#         print("waiting for START")
#         data = android.readMsg()
#         if (data is not None):
#             print("Read from Android: " + str(data))
#             json_msg = json.loads(str(data))
#             if(json_msg['header'] == "START"):
#                 start = True
#     except:
#         print("Error waiting for Start")

#calibrateFor45()

print("first obstacle")
first_Obstacle_Distance = getDistance()
print(f"first_distance: {first_Obstacle_Distance}")
firstObstacle(int(first_Obstacle_Distance))

print("second obstacle")
print(f"second_distance: {second_Obstacle_Distance.value}")
secondObstacle(second_Obstacle_Distance)


finalDistance(second_Obstacle_Distance.value + 20)
process.kill()
signal.signal(signal.SIGINT, quitHandler)
PC.writeMsg(("PHOTO_COLLAGE").encode(encoding = "UTF-8", errors = "strict"))
print("End")
os._exit(1)
# except:
#     PC.disconnect()
#     android.disconnect()
#     print("=====================================================")
#     print("PC and Anroid disconnected")
#     exit()



