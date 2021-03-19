#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Recibo como parametros id de UsuarioJuegaSecuencua, idSecuencia

import RPi.GPIO as GPIO
import time
import os
import sys

#Subprocess
import subprocess
from subprocess import Popen, PIPE
import os
import signal
import psutil
import json
import commands

from distutils.util import strtobool


import pigpio
pi = pigpio.pi()

#Seteo el entorno de Django para registrar en la BD
sys.path.append('/home/pi/djangoProjects/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corsiProject.settings")
import django
django.setup()

from corsiApp.models import EventoRegistrado
from corsiApp.models import Intento

#La carga de contexto de Django demora 3 segundos, pero le saco 750 por el delay entre el parpadeo y reproducir secs 
tiempoCargaContexto = 2600

#tiempo de espera entre la muestra y la aceptación de botones
tiempoComienzaIntento = sys.argv[1]

#Obtengo el tiempo que debe esperar hasta capturar, para no capturar mientras se reproduce
#Calculado en funcion de cuantos botones son y cuanto tiempo estan prendidos y cuanto intervalo hay entre ellos.
tiempoReproduceSecuencia = sys.argv[2]

#Almaceno los parametros
idUsuarioJuegaSecuencia = sys.argv[3]
idSecuencia = sys.argv[4]

intentoObj = Intento.objects.get(id=idUsuarioJuegaSecuencia)

#Capturo argumentos de Feedback RGBs
luzEsperaBotones = strtobool(sys.argv[5])
colorLuzEsperaBotones = sys.argv[6]
luzAnalisisIntento = strtobool(sys.argv[7])
colorLuzAnalisisIntento = sys.argv[8]
tiempoLucesComienzaSecuencia = sys.argv[9]


#Es el tiempo que debo esperar hasta habilitar la captura de botones.
#Está determinado por la reproduccion de la secuencia más el parpadeo inicial menos el tiempo que demora Django en cargar el contexto 
tiempoEsperaTotal = float(int(tiempoComienzaIntento)+int(tiempoReproduceSecuencia)+int(tiempoLucesComienzaSecuencia)-tiempoCargaContexto)/1000
if tiempoEsperaTotal > 0:
	#Espero hasya que se termine de reproducir la secuencia
	time.sleep(tiempoEsperaTotal)


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


lucesGPIOs={'A':21,'B':3,'C':5,'D':19,'E':11,'F':7,'G':23,'H':15,'I':13}

botonA = 32
botonB = 12
botonC = 16
botonD = 36
botonE = 22
botonF = 18
botonG = 38
botonH = 26
botonI = 24
botonStop = 40


arrayBotones = {}
arrayBotones[1] = ('A', botonA)
arrayBotones[2] = ('B', botonB)
arrayBotones[3] = ('C', botonC)
arrayBotones[4] = ('D', botonD)
arrayBotones[5] = ('E', botonE)
arrayBotones[6] = ('F', botonF)
arrayBotones[7] = ('G', botonG)
arrayBotones[8] = ('H', botonH)
arrayBotones[9] = ('I', botonI)
arrayBotones[10] = ('RF', botonStop)

rgb = {"red":[50,0,0],"green":[0,50,0],"blue":[0,0,50],"yellow":[50,50,0],"white":[50,50,50]}

def chequeoBotonPresionado(pataBoton):
	#Si el boton esta presionado
	lista = [GPIO.input(q) for (_,q) in arrayBotones.values()]
	if sum(lista) <= 8:
		print lista
	
	return lista[pataBoton-1]==0

tiempoInicioBoton = time.time()
tiempoSigueBoton = time.time()

ultimoBotonPresionado = 0
tiempoInicioBoton = 0

apagar = 0
prender = 1


def revisar_io():
	lista = [GPIO.input(q)==0 for (_,q) in arrayBotones.values()]
	valor_suma = sum(lista)

	botonPresionado = (lista.index(1) + 1) if lista.count(1) else 0

	return (lista, valor_suma, botonPresionado)

#Si hay que encender una luz de espera botones
if luzEsperaBotones:
	r,g,b = rgb[colorLuzEsperaBotones]
	pi.set_PWM_dutycycle(5, r)
	pi.set_PWM_dutycycle(26, g) 
	pi.set_PWM_dutycycle(13, b)


#Registro el evento de Inicio Tiempo Respuesta (ITR)
inicioTiempoRespuesta = EventoRegistrado(idIntento = intentoObj, idSec = idSecuencia, valorEvento = "ITR",
										tipoEvento = "Control")
inicioTiempoRespuesta.save()

tiempoInicio = time.time()

while True:
	botonPresionado = 0

	start = time.time()
	(_, valor_suma, botonPresionado) = revisar_io()
	if valor_suma == 1:
		start = time.time()
		letra_actual = arrayBotones[botonPresionado][0]
		if letra_actual != "RF":
			GPIO.output(lucesGPIOs[letra_actual],prender)
		botonPresionado_rebote = True
		#Me quedo esperando mientras esta presionado
		while botonPresionado_rebote == True:
			time.sleep(0.200)
			(_, valor_suma, botonPresionado_next) = revisar_io()
			if valor_suma == 0:
				botonPresionado_rebote = False
			elif valor_suma > 1:
				#Registro una X en el log para indicar que apreto 2 botones
				valorBoton = "X"
				tiempoPresionado = 0
				b = EventoRegistrado(idIntento = intentoObj, idSec = idSecuencia,
							valorEvento = valorBoton, tipoEvento = tipoEvento, tiempoPresionadoMS = tiempoPresionadoMS)
				b.save()

		if letra_actual != "RF":
			#print "Chequeo Boton, letra"
			GPIO.output(lucesGPIOs[letra_actual],apagar)
			tipoEvento = "Boton"

		if letra_actual == "RF":
			#print "Chequeo Boton, rojo"
			start = 0
			tipoEvento = "Control"
			if luzAnalisisIntento:
				r,g,b = rgb[colorLuzAnalisisIntento]
				pi.set_PWM_dutycycle(5, r)
				pi.set_PWM_dutycycle(26, g) 
				pi.set_PWM_dutycycle(13, b)

			botonPresionado = 10

	#Muestro/Cuento solo si se aprieta un boton nuevo
	if botonPresionado != ultimoBotonPresionado and botonPresionado != 0: 
		#Cuando suelto, muestro	
		end = time.time()
		#Lo paso a milisegundos y le resto un overhead de 100 ms
		tiempoPresionado = ((end - start)*1000)-100
		tiempoDesdeInicio = ((end - tiempoInicio)*1000)-100
		#Harcodeo 200 para no esperar a que termine de apretar el boton rojo.
		if botonPresionado == 10:
			tiempoPresionado = 200

		#String a guardar en archivo
		ultimoBotonPresionado = botonPresionado		

	if ultimoBotonPresionado != 0 or botonPresionado == 10:
		valorBoton = arrayBotones[botonPresionado][0]
		tiempoPresionadoMS=format(int(tiempoPresionado))
		b = EventoRegistrado(idIntento = intentoObj, idSec = idSecuencia,
							valorEvento = valorBoton, tipoEvento = tipoEvento, 
							tiempoPresionadoMS = tiempoPresionadoMS, tiempoDesdeInicio = tiempoDesdeInicio)
		b.save()

		if botonPresionado == 10:
			break

		#Limpio el boton presionado porque asumo que solto
		botonPresionado = 0
		ultimoBotonPresionado = 0

#Cuando se pulsó el boton de terminar, llamo al siguiente script para registrar en la DB

#Apago los RGBs para evaluar si fue correcto o no
pi.set_PWM_dutycycle(5, 0)
pi.set_PWM_dutycycle(13, 0) 
pi.set_PWM_dutycycle(26, 0)