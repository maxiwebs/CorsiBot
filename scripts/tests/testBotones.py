import RPi.GPIO as GPIO
import time    

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(32, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(36, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(38, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_UP)

while True:
	input_stateA = GPIO.input(12)
	input_stateB = GPIO.input(16)
	input_stateC = GPIO.input(18)
	input_stateD = GPIO.input(22)
	input_stateE = GPIO.input(24)
	input_stateF = GPIO.input(26)
	input_stateG = GPIO.input(32)
	input_stateH = GPIO.input(36)
	input_stateI = GPIO.input(38)
	input_stateR = GPIO.input(40)

	if input_stateA == False:
		print('Boton pulsado A')
		time.sleep(0.3)
        
	if input_stateB == False:
		print('Boton pulsado B')
		time.sleep(0.3)

	if input_stateC == False:
		print('Boton pulsado C')
		time.sleep(0.3)
        
	if input_stateD == False:
		print('Boton pulsado D')
		time.sleep(0.3)

	if input_stateE == False:
		print('Boton pulsado E')
		time.sleep(0.3)
        
	if input_stateF == False:
		print('Boton pulsado F')
		time.sleep(0.3)

	if input_stateG == False:
		print('Boton pulsado G')
		time.sleep(0.3)
        
	if input_stateH == False:
		print('Boton pulsado H')
		time.sleep(0.3)

	if input_stateI == False:
		print('Boton pulsado I')
		time.sleep(0.3)
        
	if input_stateR == False:
		print('Boton pulsado R')
		time.sleep(0.3)