#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Recibo como parametros id de UsuarioJuegaSecuencua, idSecuencia
import RPi.GPIO as GPIO
import time
import os
import sys
import pigpio

 
#Almaceno los parametros
idUsuarioJuegaSecuencia = sys.argv[1]
idSecuencia = sys.argv[2]

#print idUsuarioJuegaSecuencia
#print idSecuencia

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


lucesGPIOs={'A':21,'B':3,'C':5,'D':19,'E':11,'F':7,'G':23,'H':15,'I':13,'Z':35}

botonA = 32
botonB = 12
botonC = 16
botonD = 36
botonE = 22
botonF = 18
botonG = 38
botonH = 26
botonI = 24
botonRojo = 40

arrayBotones = {}
arrayBotones[1] = 'A'
arrayBotones[2] = 'B'
arrayBotones[3] = 'C'
arrayBotones[4] = 'D'
arrayBotones[5] = 'E'
arrayBotones[6] = 'F'
arrayBotones[7] = 'G'
arrayBotones[8] = 'H'
arrayBotones[9] = 'I'
arrayBotones[10] = 'R'


archivo = "/home/pi/djangoProjects/scripts/temp.txt"
#Genero el archivo donde voy a ir registrando los botones, y le pongo como cabecera los id-argumentos
encabezadoIntento = "echo '"+idUsuarioJuegaSecuencia+ "' > "+archivo
os.system(encabezadoIntento)
encabezadoSecuencia = "echo '"+idSecuencia+ "' >> "+archivo
os.system(encabezadoSecuencia)

pi = pigpio.pi()


def chequeoBotonPresionado(pataBoton):
	#Tengo que eliminar el rebote con esto.
	#Seguro un boton queda presionado por al menos 50 ms
	time.sleep(0.05)
	#Si el boton esta presionado
	if GPIO.input(pataBoton) == False:
		return True
	else:
		return False

tiempoInicioBoton = time.time()
tiempoSigueBoton = time.time()
tiempoPresionado = 200

botonPresionado = 0
ultimoBotonPresionado = 0
tiempoInicioBoton = 0


while True:
	if chequeoBotonPresionado(botonRojo):
		botonPresionado = 10
		log = arrayBotones[botonPresionado]
		log = "echo '"+log+",200' >> "+archivo
		os.system(log)
		break

#Cuando se pulsó el boton de iniciar, llamo al siguiente script para registrar en la DB
registrarBotonesEnBD = "/usr/bin/python /home/pi/djangoProjects/manage.py shell < /home/pi/djangoProjects/scripts/registroBotonRojoInicioDesdeArchivoEnBD.py"
os.system(registrarBotonesEnBD)

#Apago los RGB
pi.set_PWM_dutycycle(5, 0)
pi.set_PWM_dutycycle(13, 0) 
pi.set_PWM_dutycycle(26, 0)
