#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
 #Se llama de la siguiente forma, donde A B es la secuencia a reproducir

import RPi.GPIO as GPIO
import time
import sys
import pigpio
from distutils.util import strtobool


GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)
GPIO.setup(7,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
#Buzzer
GPIO.setup(35,GPIO.OUT)


lucesGPIOs={'A':21,'B':3,'C':5,'D':19,'E':11,'F':7,'G':23,'H':15,'I':13,'Z':35}

apagar = 0
prender = 1

#CAPTURO ARGUMENTOS CON LOS QUE LLAMO AL SCRIPT
tiempoEncendidoLuz = sys.argv[1]
tiempoEntreLuces = sys.argv[2] 
luzComienzaSecuencia = strtobool(sys.argv[3])
colorLuzComienzaSecuencia = sys.argv[4]
tiempoLuzComienzaSecuencia = sys.argv[5]
repeticionLuzComienzaSecuencia = sys.argv[6]
intervaloRepeticionLuzComienzaSecuencia = sys.argv[7]
secuencia = sys.argv[8:]

pi = pigpio.pi()
#Apago luces al arrancar
pi.set_PWM_dutycycle(5, 0)
pi.set_PWM_dutycycle(13, 0) 
pi.set_PWM_dutycycle(26, 0)

rgb = {"red":[50,0,0],"green":[0,50,0],"blue":[0,0,50],"yellow":[50,50,0],"white":[50,50,50]}

if luzComienzaSecuencia:
	if tiempoLuzComienzaSecuencia != "0":
		tiempoLuzComienzaSecuencia=float(tiempoLuzComienzaSecuencia)/1000

	if intervaloRepeticionLuzComienzaSecuencia != "0":
		intervaloRepeticionLuzComienzaSecuencia=float(intervaloRepeticionLuzComienzaSecuencia)/1000

	r,g,b = rgb[colorLuzComienzaSecuencia]

	for i in range (0,int(repeticionLuzComienzaSecuencia)):
		pi.set_PWM_dutycycle(5, r)
		pi.set_PWM_dutycycle(26, g) 
		pi.set_PWM_dutycycle(13, b)

		time.sleep(tiempoLuzComienzaSecuencia)

		pi.set_PWM_dutycycle(5, 0)
		pi.set_PWM_dutycycle(13, 0) 
		pi.set_PWM_dutycycle(26, 0)
		time.sleep(intervaloRepeticionLuzComienzaSecuencia)

#Demora entre el parpadeo y el comienzo de la secuencia
time.sleep(float(750)/1000)

#REPRODUCIR SECUENCIA
for boton in secuencia:
  GPIO.output(lucesGPIOs[boton],prender)
  time.sleep(float(tiempoEncendidoLuz)/1000)
  GPIO.output(lucesGPIOs[boton],apagar)
  time.sleep(float(tiempoEntreLuces)/1000)
