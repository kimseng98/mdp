import serial
import time
import pygame
import json


# to write to serial port from RPI: echo "hello" > /dev/ttyUSB0

class STM_old:
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
            self.serConn.reset_input_buffer()   
            recvMsg = self.serConn.read(1).decode("UTF-8").strip()
            if (len(recvMsg) > 0):    
                return recvMsg
            return None
        except Exception as e:
            print("Read from STM failed: " + str(e))




    def writeMsg1(self, msg):
        try:
            print("msg: " + msg)
            self.serConn.write(msg.encode())
        except Exception as e:
            print("Write to STM failed: " + str(e))

    # ---------------------- For threading method -------------------

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




class move_order:
    def __init__(self, direction, angle, distance):
        self.direction = direction
        self.angle = angle
        self.distance = distance
        self.run_command = True


class STM(STM_old):

    def get_rt_from_dis(self,distance):
        dur = str(distance)
        dur = dur.zfill(5)
        return dur


    def char_to_angle(self, char,angle):

        if char == 'C':
            angle = 0
        elif char == 'R':
            angle =90
        elif char == 'L':
            angle =-90
        elif char == 'D':
            angle = int(angle)
        elif char == 'A':
            angle = -(int(angle))
        return angle

    def writeMsg(self, msg):
        try:
            speed = msg[0]
            dirction = msg[1]
            steps = msg[3:]

            if(speed == 'F'):
                self.forward_turn(steps,self.char_to_angle(dirction,steps))
                print(f"speed: {str(speed)}, direction: {str(dirction)}, steps: {str(steps)}")
            if(speed == 'B'):
                self.backward_turn(steps,self.char_to_angle(dirction,steps))
                print(f"speed: {str(speed)}, direction: {str(dirction)}, steps: {str(steps)}")
            # if(speed == 'S'):
            #     self.stop()
            #     print(f"stop")


        except Exception as e:
            print("Write to STM failed: " + str(e))


    def forward_turn(self,distance,angle):
        if angle == 0:
            dir = 'C'
        elif angle >0:
            dir = 'R'
        elif angle<0:
            dir = "L"
        if dir =='R' and angle!=90:
            dir = 'D'
            distance = angle
        if dir =='L' and angle!=-90:
            dir = 'A'
            distance = angle
        distance = abs(int(distance))
        # distance = self.get_forward_distance_calibration_values(distance)


        duration_str = self.get_rt_from_dis(distance)
        self.writeMsg1(f"[F{dir},{duration_str}]")




    def backward_turn(self, distance, angle):
        if angle == 0:
            dir = 'C'
        elif angle <0:
            dir = 'L'
        elif angle >0:
            dir = "R"
        if dir =='L' and angle!=90:
            dir = 'D'
            distance = angle
        if dir =='R' and angle!=-90:
            dir = 'A'
            distance = angle

        distance = abs(int(distance))

        # distance = self.get_backward_distance_calibration_values(distance)

        duration_str = self.get_rt_from_dis(distance)
        self.writeMsg1(f"[B{dir},{duration_str}]")


        # self.stop()

    def stop(self,distance="5000", angle=0):
        print(f"[SC,10000]")
        self.writeMsg1(f"[SC,0]")

    def get_forward_distance_calibration_values(self, input_vale):
        output_value = input_vale
        forward_table = {
                        "0": 0,
                        "10": 6,
                        "20": 14,
                        "30": 24,
                        "40": 35,
                        "50": 47,
                        "60": 58,
                        "70": 69,
                        "80": 79,
                        "90": 88,
                        "100": 97,
                        "110": 105,
                        "120": 112,
                        "130": 120,
                        "140": 127,
                        "150": 136,
                        "160": 147,
                        "170": 160,
                        "180": 177,
                        "190": 198,
                        "200": 226,
                        }

        try:
            output_value = forward_table[str(input_vale)]
        except:
            output_value = input_vale

        return  output_value

    def get_backward_distance_calibration_values(self, input_vale):
        output_value = input_vale
        backward_table = {
                        "0": 0,
                        "10": 8,
                        "20": 17,
                        "30": 27,
                        "40": 37,
                        "50": 46,
                        "60": 57,
                        "70": 67,
                        "80": 77,
                        "90": 88,
                        "100": 99,
                        "110": 110,
                        "120": 121,
                        "130": 132,
                        "140": 143,
                        "150": 154,
                        "160": 165,
                        "170": 176,
                        "180": 187,
                        "190": 199,
                        "200": 210,
                        }

        try:
            output_value = backward_table[str(input_vale)]
        except:
            output_value = input_vale

        return output_value



    def run_command(self,command):


        direction = command.direction
        angle = command.angle
        distance = command.distance
        run_command = command.run_command

        # print(f"running {direction} {angle} {distance}")

        if not run_command:
            return

        if direction == "F":
            self.forward_turn(distance,angle)
        elif direction == "B":
            self.backward_turn(distance,angle)
        # elif direction == "S":
        #    self.stop(distance, angle)
        # else:
        #     self.stop("10",0)




    def time_to_sleep(self, command):
        pass

    def run_queue(self, queue):
        while True:

            try:
                current_command = queue.pop(0)
                self.run_command(current_command)

            except Exception as e:
                # self.stop()
                print(e)

            time.sleep(1)

if __name__ == "__main__":
    queue = []
    stm = STM()
    stm.connectSerial()
 #   for i in range(10):
#	    stm.forward_turn(20,00)
#	    time.sleep(1)
#	    stm.backward_turn(20,0)
#	    time.sleep(1)

    stm.forward_turn(20000, 0)

#    time.sleep(2)


 #   temp_move_order = move_order("F",0,1825) # min 15/99999
  #  queue.append(temp_move_order)

 #   temp_move_order = move_order("F",90,1500) # min 15/99999
 #   queue.append(temp_move_order)

#    temp_move_order = move_order("F",-90,1000) # min 15/99999
 #   queue.append(temp_move_order)

   # for i in range(100):
    # semi ok 4* 3 point turn
    #    temp_move_order = move_order("F",-90,8000) # min 15/99999
     #   queue.append(temp_move_order)
        #

        #
      #  temp_move_order = move_order("F", 0, 800)  # min 15/99999
       # queue.append(temp_move_order)

      #  temp_move_order = move_order("S", -0, 10000)  # min 15/99999
       # queue.append(temp_move_order)

# semi ok 4* 3 point turn

    # stm.run_command(temp_move_order)

    # queue.append(temp_move_order)
    #
   # print("Queue:", queue)
   # stm.run_queue(queue)


    pass






