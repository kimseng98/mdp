from Serial import STM
from pynput import keyboard
import time

STMobject = STM()

STMobject.serialPort="COM3"

STMobject.connectSerial()



while True:

    dir = 'C'
    speed = 'S'
    with keyboard.Events() as events:
        # Block for as much as possible
        event = events.get(1e6)
        if event.key == keyboard.KeyCode.from_char('s'):
            speed = 'B'
        if event.key == keyboard.KeyCode.from_char('w'):
            speed = 'F'
        if event.key == keyboard.KeyCode.from_char('a'):
            dir = 'L'
        if event.key == keyboard.KeyCode.from_char('d'):
            dir = 'R'
    msg = f"[{speed}{dir},1]"
    time.sleep(0.1)
    print(msg)
    STMobject.writeMsg(msg)
