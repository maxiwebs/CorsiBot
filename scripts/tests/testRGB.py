import pigpio
import RPi.GPIO as GPIO
import time
import os
import sys

pi = pigpio.pi()

while True:
    pi.set_PWM_dutycycle(5, 255) #Blue
    pi.set_PWM_dutycycle(13, 0) 
    pi.set_PWM_dutycycle(26, 0)

    time.sleep(1)

    pi.set_PWM_dutycycle(5, 0)
    pi.set_PWM_dutycycle(13, 255) #Red
    pi.set_PWM_dutycycle(26, 0)

    time.sleep(1)

    pi.set_PWM_dutycycle(5, 0)
    pi.set_PWM_dutycycle(13, 0)
    pi.set_PWM_dutycycle(26, 255) #Green

    time.sleep(1)

    pi.set_PWM_dutycycle(5, 255)
    pi.set_PWM_dutycycle(13, 255)
    pi.set_PWM_dutycycle(26, 255) #White

    time.sleep(1)


pi.set_PWM_dutycycle(5, 0)
pi.set_PWM_dutycycle(13, 0)
pi.set_PWM_dutycycle(26, 0)

pi.stop()
