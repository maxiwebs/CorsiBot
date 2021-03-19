#Registro Boton Rojo inicio en la BD junto con sus datos de intento y secuencia
import os
import sys
import time

from corsiApp.models import EventoRegistrado
from corsiApp.models import Intento

with open("/home/pi/djangoProjects/scripts/temp.txt") as archivo:
	#Leo la primer linea para ver si es un 0 (datos ya registrados) o los tengo que registrar.
	primerLinea = archivo.readline()
	#Comparo sacando el salto de linea
	if (primerLinea[:-1] == "0"):
		print "Nada para agregar"
	else:
		#print "Agrego en BD"
		intento = primerLinea
		intentoObj = Intento.objects.get(id=intento[:-1])
		idSecuencia = archivo.readline()
		linea = archivo.readline()
		#Comienzo a levantar los botones presionados
		while linea:
			coma = linea.find(',')
			valorBoton = 'RI'
			#print valorBoton
			tiempoPresionadoMS = linea[coma+1:]
			tipoEvento = "Control"
			linea = archivo.readline()
			b = EventoRegistrado(idIntento = intentoObj, idSec = idSecuencia,
								valorEvento = valorBoton, tipoEvento = tipoEvento, tiempoPresionadoMS = tiempoPresionadoMS)
			b.save()

archivo.close()

#Marco el archivo con un 0 para que no se vuelva a ingresar lo mismo en la BD
temp = "/home/pi/djangoProjects/scripts/temp.txt"
#Genero el archivo donde voy a ir registrando los botones, y le pongo como cabecera los id-argumentos
limpiarTemp = "echo '0' > "+temp
os.system(limpiarTemp)
