import RPi.GPIO as GPIO
import time
MOVE_ENGINE = 7


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(MOVE_ENGINE, GPIO.OUT, initial=False)
rotateEgn = GPIO.PWM(MOVE_ENGINE, 50)

while True:
    a = input("input time")
    rotateEgn.ChangeDutyCycle(2.5)
    time.sleep(a)
    b = input("input time")
    rotateEgn.ChangeDutyCycle(10)
    time.sleep(b)
