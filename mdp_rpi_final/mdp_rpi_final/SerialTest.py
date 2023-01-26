from Serial import STM


STMobject = STM()

STMobject.connectSerial()

while True:
    result = STMobject.readMsg()

    if result == None:
        pass
    else:
        print(result)

# STMobject.writeMsg("hello world")

