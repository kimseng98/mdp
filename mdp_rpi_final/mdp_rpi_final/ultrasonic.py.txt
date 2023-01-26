# Getting the libraries we need
from gpiozero import DistanceSensor
from time import sleep

# Initialize ultrasonic sensor
sensor = DistanceSensor(trigger=24, echo=23)
sensor.max_distance = 2
# sensor.threshold_distance = 0.01


while True:
	# Wait 2 seconds
	sleep(0.5)

	
	# Get the distance in metres
	# distance = sensor.distance

	# But we want it in centimetres
	distance = sensor.distance*100

#	# We would get a large decimal number so we will round it to 2 places
#	distance = round(sensor.distance, 2)

	# Print the information to the screen
	print(f"Distance: {distance} cm")
