import tqdm
from android import *
from stm32 import *
from pcComm import *
import bluetooth
import sys
from predictImage import predict


BUFFER_SIZE = 1024
SEPARATOR = "@.@"
IP_ADDRESS = "192.168.9.9"
PORT = 1234

# Test TCP codes
def TestTCP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP_ADDRESS, PORT))

    # Sending msg
    msg = input("Enter message: ")
    #msg = msg + "\n"
    sock.send(bytes(msg, "utf-8"))

    # Receiving msg
    #pcMsg = sock.recv(1024)
    #print("\n" + str(pcMsg))


    # Receiving image
    received = sock.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    print("ready to receive " + filename + str(filesize))
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = sock.recv(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    sock.close()

def TestBluetooth():
    btObj = Android()
    btObj.connect()

    msg = input("Enter message: ")
    btObj.sendMsg(msg)

    msg1 = btObj.receiveMsg()
    print("Message 1: " + str(msg1))

    msg2 = btObj.receiveMsg()
    print("Message 2: " + str(msg2))

    msg3 = btObj.receiveMsg()
    print("Message 3: " + str(msg3))

    btObj.disconnect()

def TestSTM():
    stm = STM()
    stm.connect()
    print("attempt connect")
    try:
        print("attempting")

        stm.sendMsg("w50")
    except KeyboardInterrupt:
        print("Terminating the program now...")

def TestImagePrediction():
    s = socket.socket()      
    s.connect((IP_ADDRESS, PORT))
    print("Connected")

    while True:
        try:
            commands = s.recv(1024).split()        # TAKEPICTURE OBSTACLE_ID
            if len(commands) > 0:
                if str(commands[0].decode('utf-8')) == "TAKEPICTURE" or str(commands[0].decode('utf-8')) == "ADJUST":
                    obsID = commands[1].decode('utf-8')  # Extract out the OBSTACLE_ID
                    forAdjusting = True if str(commands[0].decode('utf-8')) == "ADJUST" else False
                    data = s.recv(1024)
                    filesize = int(data.decode('utf-8'))
                    print("Filesize", filesize)

                    # Get image from RPI and save locally
                    SAVE_FILE = "RPI/images/to_predict.jpeg"
                    total_data_received = len(data)
                    with open(SAVE_FILE, "wb") as f:
                        while True:
                            data = s.recv(1024)
                            if not data:
                                break

                            f.write(data)
                            total_data_received += len(data)
                            
                            if total_data_received >= filesize:
                                break
                        print("File done")

                    print("Received")

                    predictions = predict(SAVE_FILE, forAdjusting)
                    print("Predictions", predictions)
                    if len(predictions) == 0:
                        if forAdjusting:
                            s.send(bytes("ADJUST NOIMAGE", "utf-8"))
                        else:
                            s.send(bytes("NOIMAGE", "utf-8"))
                    else:
                        if forAdjusting:
                            s.send(bytes(str("ADJUST " + predictions[0][4:] + " " + obsID), "utf-8"))       #Replace "IMG" header with "ADJUST"
                        else:
                            s.send(bytes(str(predictions[0] + " " + obsID), "utf-8"))
                commands = None
        except KeyboardInterrupt:
            s.close()

def TestMultipleMessages():
    s = socket.socket()
    s.connect((IP_ADDRESS, PORT))
    print("Connected")

    ending = "@.@"

    str_received = ""

    while True:
        data = s.recv(1024)

        if data.endswith(ending):
            str_received += data.strip(ending)
            break

        if not data:
            break

        str_received += data

    print("Data fully received:", data)

if __name__ == "__main__":
    TestImagePrediction()
    #TestMultipleMessages()
    #TestBluetooth()
    #TestSTM()
    #TestTCP()
