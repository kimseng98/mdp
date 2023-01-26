from multi_threading import MultiThreading
import subprocess
command = "sudo chmod o+rw /var/run/sdp"
subprocess.Popen(command.split())
multiprocess_rpi = MultiThreading()
multiprocess_rpi.start()