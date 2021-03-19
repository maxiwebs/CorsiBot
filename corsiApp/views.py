# -*- coding: utf-8 -*-
# encoding=utf8
from __future__ import unicode_literals
from django.shortcuts import render
from .forms import UsuarioForm
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

#CARGAR ARCHIVOS
from django.contrib import messages 
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from datetime import date

#GPIO2
from django.http import HttpResponse
import RPi.GPIO as GPIO
import time
import sys

import csv

#Subprocess
import subprocess
from subprocess import Popen, PIPE
import os
import signal
import psutil
import json

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)
GPIO.setup(7,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
#RGB
GPIO.setup(19,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)

#Buzzer
GPIO.setup(35,GPIO.OUT)


lucesGPIOs={'A':21,'B':3,'C':5,'D':19,'E':11,'F':7,'G':23,'H':15,'I':13,'Z':35}
#GPIO2

#Botones
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

rgb = {"red":[50,0,0],"green":[0,50,0],"blue":[0,0,50],"yellow":[50,50,0],"white":[50,50,50]}

from corsiApp.models import Protocolo
from corsiApp.models import Usuario
from corsiApp.models import BotonesSecuencias
from corsiApp.models import TomaDeDatos
from corsiApp.models import Intento
from corsiApp.models import EventoRegistrado
from corsiApp.models import DocumentoProtocolo
from corsiApp.models import DocumentoTomaDeDatos
from corsiApp.models import SecuenciaIntento


from corsiApp.forms import DocumentoProtocoloForm
from corsiApp.forms import DocumentoTomaDeDatosForm


def inicio(request):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	return render(request,'inicio.html',{})

     
def subir_protocolo(request):
	if request.method == 'POST':
		form = DocumentoProtocoloForm(request.POST, request.FILES)
		if form.is_valid():

			form.save()

			#Renombro archivo
			renombroArchivo = "mv /home/pi/djangoProjects/scripts/archivosSubidos/* /home/pi/djangoProjects/scripts/archivosSubidos/protocolo.json"
			os.system(renombroArchivo)

			#Ejecuto el script para subir el nuevo protocolo a la BD
			subirProtocolo = "/usr/bin/python /home/pi/djangoProjects/manage.py shell < /home/pi/djangoProjects/scripts/levantoProtocoloJson.py"
			os.system(subirProtocolo)

			try: 
				#Abro el archivo para quedarme solo con el nombre del protocolo
				json_data=open("/home/pi/djangoProjects/scripts/archivosSubidos/protocolo.json").read()
				experiment = json.loads(json_data)
				nombreProtocolo = experiment['protocolo']['nombreProtocolo']

				limpiarArchivo = "rm /home/pi/djangoProjects/scripts/archivosSubidos/*"
				os.system(limpiarArchivo)

			except:
				limpiarArchivo = "rm /home/pi/djangoProjects/scripts/archivosSubidos/*"
				os.system(limpiarArchivo)

				#Mensaje error archivo
				mensaje = 1
				return render(request, 'secuencias/protocolo_nuevo.html', {'form': form, 'mensaje':mensaje})

			#Si se ingreso bien en la BD			
			try:
				protocolos = Protocolo.objects.filter(nombreProtocolo = nombreProtocolo)
				if protocolos.count() == 1:
					protocolo = Protocolo.objects.latest('id')
					botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
					return render(request,'secuencias/listado_secuencias.html',{"botonesSecuencias":botonesSecuencias,
																	"protocolo": protocolo})
				elif protocolos.count() > 1:
					#Ya había un protocolo con ese nombre, tengo que borrar el ultimo ingresado
					ultimoIngresado = Protocolo.objects.latest('id')
					ultimoIngresado.delete()
					#Mensaje de error repetido
					mensaje = 2
					return render(request, 'secuencias/protocolo_nuevo.html', {'form': form, 'mensaje':mensaje})	

			except Protocolo.DoesNotExist:
				#Elimino el registro del documento porque hubo error en el json
				registroSubido = DocumentoProtocolo.objects.filter(nombreProtocolo = nombreProtocolo).delete()
				#Mensaje de error en el json
				mensaje = 1
				return render(request, 'secuencias/protocolo_nuevo.html', {'form': form, 'mensaje':mensaje})

	else:
		form = DocumentoProtocoloForm()
		#Mensaje para subir archivo
		mensaje = 0
		return render(request, 'secuencias/protocolo_nuevo.html', {'form': form, 'mensaje':mensaje})


def subir_toma_datos(request):
	if request.method == 'POST':
		form = DocumentoTomaDeDatosForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			idProtocolo = request.POST['protocolo']
			protocoloObj = Protocolo.objects.get(id = idProtocolo)

			#Renombro archivo
			renombroArchivo = "mv /home/pi/djangoProjects/scripts/archivosSubidos/* /home/pi/djangoProjects/scripts/archivosSubidos/tomaDeDatos.json"
			os.system(renombroArchivo)

			#Ejecuto el script para subir la nueva toma de datos a la BD
			subirTomaDeDatos = "/usr/bin/python /home/pi/djangoProjects/manage.py shell < /home/pi/djangoProjects/scripts/levantoTomaDatosJson.py"
			os.system(subirTomaDeDatos)

			#Abro Toma de datos para ver el nombre
			json_data=open("/home/pi/djangoProjects/scripts/archivosSubidos/tomaDeDatos.json").read()

			try: 
				experiment = json.loads(json_data)
				nombreTomaDeDatos = experiment['tomaDeDatos']['nombreTomaDeDatos']
				limpiarArchivo = "rm /home/pi/djangoProjects/scripts/archivosSubidos/*"
				os.system(limpiarArchivo)

			except:
				limpiarArchivo = "rm /home/pi/djangoProjects/scripts/archivosSubidos/*"
				os.system(limpiarArchivo)

				mensaje = 1
				return render(request, 'secuencias/toma_datos_nueva.html', {'form': form, 'mensaje':mensaje})
 

			limpiarArchivo = "rm /home/pi/djangoProjects/scripts/archivosSubidos/*"
			os.system(limpiarArchivo)

			try:
				ingresada = TomaDeDatos.objects.filter(nombreTomaDeDatos = nombreTomaDeDatos)
				if ingresada.count() == 1:
					tomaDeDatosObj = TomaDeDatos.objects.latest('id')
					#Voy a iterar por intentos. En este momento todos tienen 1 vacio
					intentosTomaDatos = Intento.objects.filter(idUsr__idTomaDeDatos = tomaDeDatosObj)
					botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocoloObj).order_by('idSec')
					lista_usuarios_toma = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj)
					return render(request,'usuarios/toma_datos_usuarios.html',{"lista_usuarios_toma":lista_usuarios_toma, 
																			"tomaDatos": tomaDeDatosObj,
																			"intentosTomaDatos": intentosTomaDatos})
				elif ingresada.count() > 1:
					tomaDeDatosObj = TomaDeDatos.objects.latest('id')
					tomaDeDatosObj.delete()

					#Mensaje de error.
					mensaje = 2
					return render(request, 'secuencias/toma_datos_nueva.html', {'form': form, 'mensaje':mensaje})

			except TomaDeDatos.DoesNotExist:
				#Elimino el registro del documento porque hubo error en el json
				registroSubido = DocumentoTomaDeDatos.objects.filter(protocolo = protocoloObj, numeroTomaProtocolo = numeroTomaProtocolo).delete()
				#Mensaje de error.
				mensaje = 1
				return render(request, 'secuencias/toma_datos_nueva.html', {'form': form, 'mensaje':mensaje})

	else:
		form = DocumentoTomaDeDatosForm()
		#Mensaje para subir archivo
		mensaje = 0
		return render(request, 'secuencias/toma_datos_nueva.html', {'form': form, 'mensaje':mensaje})
			

#Muestra la lista de todos los protocolos cargados
def lista_protocolos(request):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	lista_protocolos = Protocolo.objects.order_by('cantSecs')
	return render(request,'secuencias/listado_protocolos.html',{"lista_protocolos":lista_protocolos})

def verProtocolo(request,int_id):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	protocolo = Protocolo.objects.get(id=int_id)
	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
	lista_tomasDeDatos = TomaDeDatos.objects.filter(idProtocolo = protocolo).order_by('-idProtocolo')
	return render(request,'secuencias/listado_secuencias.html',{"botonesSecuencias":botonesSecuencias,
																"protocolo": protocolo,
																"lista_tomasDeDatos":lista_tomasDeDatos})

def lista_secuencias(request):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	lista_secuencias = BotonesSecuencias.objects.order_by('idProtocolo');
	#Acá combino el template con lo obtenido en la BD de forma que en el template me reemplazara las ocurrencias de BotonesSecuencias del for por la lista_secuencias que obtiene aqui
	return render(request,'secuencias/listado_secuencias.html',{"BotonesSecuencias":lista_secuencias})

def lista_usuarios_toma(request,toma_id):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	tomaDeDatosObj = TomaDeDatos.objects.get(id=toma_id)
	lista_usuarios_toma = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj)
	intentosTomaDatos = Intento.objects.filter(idUsr__idTomaDeDatos = tomaDeDatosObj)
	return render(request,'usuarios/toma_datos_usuarios.html',{"lista_usuarios_toma":lista_usuarios_toma, 
																"tomaDatos": tomaDeDatosObj,
																"intentosTomaDatos": intentosTomaDatos})

def intentos_usuario(request,usr_id):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	usuario = Usuario.objects.get(id=usr_id)
	lista_intentos = Intento.objects.filter(idUsr = usuario)
	return render(request,'usuarios/intentos_usuario.html',{"lista_intentos":lista_intentos,"usuario":usuario})

def ver_botones_intento(request,intento_id):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	intentoObj = Intento.objects.get(id = intento_id)
	protocolo = Protocolo.objects.get(id=intentoObj.idUsr.idTomaDeDatos.idProtocolo.id)
	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
	botonesPresionados = EventoRegistrado.objects.filter(idIntento = intentoObj, tipoEvento = "Boton").order_by('idSec')
	secuenciasCorrectasIncorrectas = SecuenciaIntento.objects.filter(idIntento = intentoObj)
	paginaPrev = "verBotonesIntento"

	return render(request,'usuarios/ver_botones_intento.html',{"botonesSecuencias":botonesSecuencias,
																"botonesPresionados":botonesPresionados,
																"secuenciasCorrectasIncorrectas": secuenciasCorrectasIncorrectas,
																"intento":intentoObj, "paginaPrev":paginaPrev})


def reproducirSecuencia(request, protocolo_id,sec_id):
	protocolo = Protocolo.objects.get(id=protocolo_id)
	botonesSecuencia = BotonesSecuencias.objects.filter(idProtocolo = protocolo, idSec= sec_id)
	for boton in botonesSecuencia:
		GPIO.output(lucesGPIOs[boton.valorBoton],1)
		time.sleep(protocolo.tiempoEncendidoLuz/float(1000))
		GPIO.output(lucesGPIOs[boton.valorBoton],0)
		time.sleep(protocolo.tiempoEntreLuces/float(1000))

	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
	return render(request,'secuencias/listado_secuencias.html',{"botonesSecuencias":botonesSecuencias,
																"protocolo": protocolo})

#JUGAR
def select_toma_datos(request):#Muestra el listado de Toma de Datos disponibles
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	#Si seleccionaron alguna toma de datos, la busco
	if request.method=="POST":
		tomaDeDatos_id = request.POST['tomaId']
		tomaDeDatosObj = TomaDeDatos.objects.get(id=tomaDeDatos_id)
	else:
		#Si no seleccionaron ninguna, me quedo con la  ultima toma de datos cargada
		tomaDeDatosObj = TomaDeDatos.objects.latest('id')

	protocolo = tomaDeDatosObj.idProtocolo
	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
	lista_tomasDeDatos = TomaDeDatos.objects.order_by('-idProtocolo');
	#Obtengo los usuarios para esa toma de datos
	lista_usuarios = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj);
	ordenIntentos = "null"

	return render(request,'secuencias/select_toma_datos.html',{"lista_usuarios":lista_usuarios, 
														"lista_tomasDeDatos":lista_tomasDeDatos,
														"protocolo": protocolo,
														"tomaDeDatos": tomaDeDatosObj,
														"ordenIntentos": ordenIntentos,
														"botonesSecuencias": botonesSecuencias})

def ordenar_toma_datos(request,tomaId,order):#Ordena la toma de datos segun el criterio seleccionado 
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	tomaDeDatosObj = TomaDeDatos.objects.get(id=tomaId)

	protocolo = tomaDeDatosObj.idProtocolo
	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
	lista_tomasDeDatos = TomaDeDatos.objects.order_by('-idProtocolo');
	#Obtengo los usuarios para esa toma de datos
	if order == "intasc":
		lista_usuarios = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj).order_by('cantIntentos');
		ordenIntentos = "intasc"
	elif order == "intdesc":
		lista_usuarios = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj).order_by('-cantIntentos');
		ordenIntentos = "intdesc"
	else:
		lista_usuarios = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj);
		ordenIntentos = "null"

	return render(request,'secuencias/select_toma_datos.html',{"lista_usuarios":lista_usuarios, 
														"lista_tomasDeDatos":lista_tomasDeDatos,
														"protocolo": protocolo,
														"tomaDeDatos": tomaDeDatosObj,
														"ordenIntentos": ordenIntentos,														
														"botonesSecuencias": botonesSecuencias})


def select_usr(request):#Muestra el listado de Usuarios para esa toma de Datos
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	tomaDeDatos_id = request.POST['tomaId']
	tomaDeDatosObj = TomaDeDatos.objects.get(id=tomaDeDatos_id)
	intentosTomaDatos = Intento.objects.filter(idUsr__idTomaDeDatos = tomaDeDatosObj)
	#Obtengo los usuarios para esa toma de datos
	lista_usuarios = Usuario.objects.filter(idTomaDeDatos = tomaDeDatosObj);
	return render(request,'secuencias/select_usr.html',{"lista_usuarios":lista_usuarios, 
														"intentosTomaDatos": intentosTomaDatos})

def playWaitSec(request): #Reproduce secuencia y espera a que el usuario haga el trial

	usr_id = request.POST['usrId']
	usrObj = Usuario.objects.get(id=usr_id)
	tomaDeDatosObj = TomaDeDatos.objects.get(id = usrObj.idTomaDeDatos.id)
	protocolo = Protocolo.objects.get(id=tomaDeDatosObj.idProtocolo.id)
	idProtocolo = protocolo.id
	sec_id = request.POST['idSec']
	accion = request.POST['accion']
	usuario = Usuario.objects.get(id=usr_id)

	tiempoEncendidoLuz = protocolo.tiempoEncendidoLuz
	tiempoEntreLuces = protocolo.tiempoEntreLuces

	tiempoComienzaIntento = protocolo.tiempoComienzaIntento
	timeoutRespuesta = (protocolo.timeoutRespuesta)/1000
	
	luzComienzaSecuencia = protocolo.luzComienzaSecuencia
	colorLuzComienzaSecuencia = protocolo.colorLuzComienzaSecuencia
	tiempoLuzComienzaSecuencia = protocolo.tiempoLuzComienzaSecuencia
	repeticionLuzComienzaSecuencia = protocolo.repeticionLuzComienzaSecuencia
	intervaloRepeticionLuzComienzaSecuencia = protocolo.intervaloRepeticionLuzComienzaSecuencia
	luzEsperaBotones = protocolo.luzEsperaBotones
	colorLuzEsperaBotones = protocolo.colorLuzEsperaBotones
	luzAnalisisIntento = protocolo.luzAnalisisIntento
	colorLuzAnalisisIntento = protocolo.colorLuzAnalisisIntento

	#Actualizo la ultimaFechaEvaluacion de la toma de datos
	tomaDeDatosObj.ultimaFechaEvaluacion = date.today()
	tomaDeDatosObj.save()

	listaBotones = []

	#Puede estar aqui para jugar o porque desde verSecuJugada Dieron Finalizar en lugar de siguienteSec
	if accion == "finalizado":
		#Mato el proceso que escucha el botonRojoInicio
		pid = int(request.POST['idProcess'])
		#Por si no termino correctamente el proceso que escuchaba botonInicio, lo mando a matar
		if psutil.pid_exists(pid):
			os.kill(pid, signal.SIGTERM)

		#Levanto el intento
		idIntento = request.POST['idIntento']

		#Me voy a la pantalla de ver los botones del intento
		intentoObj = Intento.objects.get(id = idIntento)

		#Si finalizo el operador, pongo el codigo de Operador Termina Intento, asociado a la siguiente sec
		intentoFinalizado = EventoRegistrado(idIntento = intentoObj, idSec = sec_id, valorEvento = "OTI",
												tipoEvento = "Control")
		intentoFinalizado.save()

		botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo).order_by('idSec')
		botonesPresionados = EventoRegistrado.objects.filter(idIntento = intentoObj, tipoEvento = "Boton").order_by('idSec')
		secuenciasCorrectasIncorrectas = SecuenciaIntento.objects.filter(idIntento = intentoObj)
		paginaPrev = "verSecuJugada"
		#Prendo verde
		os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
		
		return render(request,'usuarios/ver_botones_intento.html',{"botonesSecuencias":botonesSecuencias,
																"botonesPresionados":botonesPresionados,
																"secuenciasCorrectasIncorrectas":secuenciasCorrectasIncorrectas,
																"intento":intentoObj,"paginaPrev":paginaPrev})


	else: #En el caso que no hayan apretado el boton de finalizar (uso normal)
		#Levanto la secuencia a mostrar
		secuencia = BotonesSecuencias.objects.filter(idSec=sec_id, idProtocolo = protocolo)
		#Llamo al script que reproduce la secuencia, para eso le paso la lista como argumento
		for boton in secuencia:
			listaBotones.append(boton.valorBoton)

		processSec = subprocess.Popen(["/usr/bin/python","/home/pi/djangoProjects/scripts/reproducirSecuencia.py",
										format(tiempoEncendidoLuz),format(tiempoEntreLuces),
										format(luzComienzaSecuencia),format(colorLuzComienzaSecuencia),
										format(tiempoLuzComienzaSecuencia),format(repeticionLuzComienzaSecuencia),
										format(intervaloRepeticionLuzComienzaSecuencia)]+listaBotones)

		#Calculo el tiempo que debe esperar el script de captura (capturoBotones) para no registrar botones mientras se reproduce.
		tiempoReproduceSecuencia = ((tiempoEncendidoLuz+tiempoEntreLuces)*len(listaBotones))
		
		#Si hay luz de comienza secuencia, calculo el tiempo que demora prenderlas
		if luzComienzaSecuencia:
			tiempoLucesComienzaSecuencia = (tiempoLuzComienzaSecuencia+intervaloRepeticionLuzComienzaSecuencia)*repeticionLuzComienzaSecuencia	
		else:
			tiempoLucesComienzaSecuencia = 0

		#Levanto el booleano secuenciaPrueba
		secuenciaPrueba = secuencia[0].secuenciaPrueba 

		#La sec_id se va incrementando así que puedo calcular cuantas me faltan con respecto al total
		cantSecsFaltantes = protocolo.cantSecs-int(sec_id)+1 #Le sumo 1 porque le actual aun resa jugarla
		#Si es la primer secuencia de la protocolo, registro los datos de Intento
		if sec_id == '1':
			#Almaceno en BD el intento que va a hacer el usuario
			intento = Intento(idUsr=usuario)
			intento.save()
			idIntento = intento.id
			usuario.cantIntentos += 1
			usuario.save()

		else:
			#Levanto el intento
			idIntento = request.POST['idIntento']
			intento = Intento.objects.get(id=idIntento)
			idIntento = intento.id

			pid = int(request.POST['idProcess'])
			#Por si no termino correctamente el proceso que escuchaba botonInicio, lo mando a matar
			if psutil.pid_exists(pid):
				os.kill(pid, signal.SIGTERM)

		cantErroresConsecutivos = intento.erroresConsecutivos

		#Puedo estar en este lugar porque apretaron boton rojo de inicio (RI) o porque inicio el operador (OI)
		#En caso de que haya sido por operador, registro OI en la BD
		#Chequeo si hay un RI en la BD, en caso contrario, ingreso un OI
		botonInicioPresionado = EventoRegistrado.objects.filter(idIntento = intento, idSec = sec_id, 
											tipoEvento = 'Control', valorEvento = 'RI')
		#En caso de que no haya boton rojo presionado
		if botonInicioPresionado.count() == 0:
			#Registro en la BD OI, Operador Inicio
			inicioPorOperador = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "OI",
												tipoEvento = "Control")
			inicioPorOperador.save()

		#Llamo al script que registra los botones que se aprietan y le paso los Ids de intento y secuencia para luego registrar en la DB
		process = subprocess.Popen(["/usr/bin/python","/home/pi/djangoProjects/scripts/capturoBotones.py",
									format(tiempoComienzaIntento),format(tiempoReproduceSecuencia),format(idIntento),format(sec_id),
									format(luzEsperaBotones),format(colorLuzEsperaBotones),
									format(luzAnalisisIntento),format(colorLuzAnalisisIntento), format(tiempoLucesComienzaSecuencia)])

		idProcess = process.pid
		return render(request,'secuencias/reproducir_esperar_secuencia.html',{"idProtocolo":idProtocolo,"usuario":usuario, 
																			  "secId":sec_id,"idIntento":idIntento,
																			  "idProcess":idProcess, "cantSecsFaltantes":cantSecsFaltantes,
																			  "cantErroresConsecutivos":cantErroresConsecutivos,
																			  "botonesSecuencia":secuencia,
																			  "secuenciaPrueba":secuenciaPrueba,
																			  "timeoutRespuesta":timeoutRespuesta})
#archivo = "/home/pi/djangoProjects/scripts/temp.txt"


def verSecuJugada(request): #Ve el resultado del intento, lo que pulsó el usuario
	#Por si cortó por timeout y quedó alguna luz prendida, apago los botones.
	for letra_actual in lucesGPIOs:
		GPIO.output(lucesGPIOs[letra_actual],0)

	sec_id = request.POST['idSec']
	usr_id = request.POST['usrId']
	idIntento = request.POST['idIntento']
	protocolo_id = request.POST['idProtocolo']
	pid = int(request.POST['idProcess'])
	validezSecuencia = request.POST['validez']
	secuenciaPrueba = request.POST['secuenciaPrueba']

	intento = Intento.objects.get(id=idIntento)
	cantErroresConsecutivos=intento.erroresConsecutivos
	protocoloObj = Protocolo.objects.get(id=protocolo_id)
	cantSecsFaltantes = protocoloObj.cantSecs-int(sec_id)
	usuario = Usuario.objects.get(id=usr_id)
	cantMaxErroresConsecutivos = protocoloObj.cantErroresCorte
	reverso = protocoloObj.reverso


	#Variables booleanas de control
	fuerzoUltimaSec = False
	computoErrores = True
	
	#Levanto el listado de secuencias y los botones presionados
	secuencia = BotonesSecuencias.objects.filter(idSec=sec_id, idProtocolo = protocoloObj)
	botonesPresionados = EventoRegistrado.objects.filter(idIntento = intento, idSec = sec_id, tipoEvento = 'Boton').order_by('timeStamp')

	#Si no apretó ningún boton, agrego un guión (-)
	#Esto lo hago por una cuestión de visualización en el template. No pude resolver tener una secuencia intermedia sin
	#botones, pues se desplazan para arriba y desalinean con respecto a los botones de la secuencia.
	#Para evitar tener que registrar esto, tendria que modificar el template ver_botones_intento.html y recorrer los 
	#eventosRegistrados de otra manera, quizas no solo los de tipo "Boton" 
	if botonesPresionados.count() == 0:
		valorBoton = "-"
		tipoEvento = "Boton"
		tiempoPresionadoMS = 0
		b = EventoRegistrado(idIntento = intento, idSec = sec_id,
							valorEvento = valorBoton, tipoEvento = tipoEvento, tiempoPresionadoMS = tiempoPresionadoMS)
		b.save()


	#Puedo estar en este lugar porque:
		#el usuario presionó el boton rojo de FIN (RF) 
		#se venció el timeout 
		#el operador terminó manualmente.
	#En este ultimo caso habrá que ver si lo hizo con una secuencia valida o si la anuló
	
	#Chequeo si hay un RF en la BD, en caso contrario, ingreso un OF
	botonFinPresionado = EventoRegistrado.objects.filter(idIntento = intento, idSec = sec_id, 
										tipoEvento = 'Control', valorEvento = 'RF')

	#En caso de que no haya boton rojo presionado
	if botonFinPresionado.count() == 0:
		#Por si no termino correctamente el proceso que escuchaba botones, lo mando a matar y ejecuto el script que me inserta los botones presionados en la BD (salvo que ya estén insertos)
		os.kill(pid, signal.SIGTERM)

		if validezSecuencia == "finalizado":
			#Si finalizo el operador, pongo el codigo de Operador Termina Intento
			#Necesito registrar el tiempo de finalizacion, lo estimo desde el ultimo boton registrado
			ultimoBotonRegistrado = EventoRegistrado.objects.last()
			#Le agrego 10 segs (arbitrariamente)
			tiempoFinTrial = ultimoBotonRegistrado.tiempoDesdeInicio+10000

			intentoFinalizado = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "OTI",
													tipoEvento = "Control", tiempoDesdeInicio = tiempoFinTrial)
			intentoFinalizado.save()
	
			#Mato el proceso que escucha el botonRojoInicio
			if psutil.pid_exists(pid):
				os.kill(pid, signal.SIGTERM)

			botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocoloObj).order_by('idSec')
			botonesPresionados = EventoRegistrado.objects.filter(idIntento = intento, tipoEvento = "Boton").order_by('idSec')
			secuenciasCorrectasIncorrectas = SecuenciaIntento.objects.filter(idIntento = intento)
			paginaPrev = "verSecuJugada"
			#Prendo verde
			os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")

			return render(request,'usuarios/ver_botones_intento.html',{"botonesSecuencias":botonesSecuencias,
																	"botonesPresionados":botonesPresionados,
																	"secuenciasCorrectasIncorrectas":secuenciasCorrectasIncorrectas,
																	"intento":intento, "paginaPrev":paginaPrev})



		elif validezSecuencia == "anulada": #Si la secuencia es anulada por el operador, registro OAS (Operador Anula Secuencia)
			#Necesito registrar el tiempo de finalizacion, lo estimo desde el ultimo boton registrado
			ultimoBotonRegistrado = EventoRegistrado.objects.last()
			#Le agrego 5000 ms (arbitrariamente)
			tiempoFinTrial = ultimoBotonRegistrado.tiempoDesdeInicio+5000

			secuenciaAnulada = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "OAS",
												tipoEvento = "Control", tiempoDesdeInicio = tiempoFinTrial)
			secuenciaAnulada.save()
			#Seteo en false para que no compute errores
			computoErrores = False

			#Impacto en secuenciaIntento
			secuenciaIntento, created = SecuenciaIntento.objects.update_or_create(idIntento = intento, idSec = sec_id, correcto = False)


		elif validezSecuencia == "timeout":

			registrarTimeout = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "TO",
												tipoEvento = "Control", tiempoDesdeInicio = protocoloObj.timeoutRespuesta)
			registrarTimeout.save()

		elif validezSecuencia == "valida":
			#Necesito registrar el tiempo de finalizacion, lo estimo desde el ultimo boton registrado
			ultimoBotonRegistrado = EventoRegistrado.objects.last()
			#Le agrego 500 ms (arbitrariamente)
			tiempoFinTrial = ultimoBotonRegistrado.tiempoDesdeInicio+500

			#Registro en la BD OF, Operador Fin
			finPorOperador = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "OF",
												tipoEvento = "Control", tiempoDesdeInicio = tiempoFinTrial)
			finPorOperador.save()

	#Si debo computar los errores
	if computoErrores:
		#Chequeo si es una secuencia de prueba o si realizó la prueba correctamente (o ambas)
		if secuenciaPresionadaOK(secuencia,botonesPresionados,reverso):
			#Impacto en secuenciaIntento
			secuenciaIntento, created = SecuenciaIntento.objects.update_or_create(idIntento = intento, idSec = sec_id, correcto = True)
			#Limpio cantErroresConsecutivos
			cantErroresConsecutivos = 0

			#Si está habilitado el feedback general
			if protocoloObj.feedbackLuces or secuenciaPrueba == "True":
				#Llamo a la función para el feedback correcto de luces/sonido
				feedbackSecuenciaCorrecta(protocoloObj)

			#Si esta activado el feedback de sonido, pero no el de luces
			elif protocoloObj.feedbackSonido and not(protocoloObj.feedbackLuces):

				#Repito 3 veces el beep para indicar que es OK
				for i in range (0,3):
					GPIO.output(lucesGPIOs['Z'],1)
					time.sleep(0.3)
					GPIO.output(lucesGPIOs['Z'],0)
					time.sleep(0.3)


		else: #Si no fue correcto el intento 
			secuenciaIntento, created = SecuenciaIntento.objects.update_or_create(idIntento = intento, idSec = sec_id, correcto = False)

			#Chequeo si tengo que dar feedback, en cualquiera de los dos casos lo hago
			if secuenciaPrueba == "True" or protocoloObj.feedbackLuces:
				#Llamo a la función para el feedback correcto de luces/sonido
				feedbackSecuenciaIncorrecta(protocoloObj)

			#Si esta activado el feedback de sonido, pero no el de luces
			elif protocoloObj.feedbackSonido and not(protocoloObj.feedbackLuces):
				#Prendo sonido continuo para indicar error
				GPIO.output(lucesGPIOs['Z'],1)
				time.sleep(1)
				GPIO.output(lucesGPIOs['Z'],0)
	

			if secuenciaPrueba != "True":
				#Si fue un error y no era una secuencia de prueba incremento cantidad de errores
				cantErroresConsecutivos=intento.erroresConsecutivos+1


			#Si supero la cantidad maxima de errores consecutivos (y esto no esta desactivado)
			if  cantErroresConsecutivos >= cantMaxErroresConsecutivos and cantMaxErroresConsecutivos != 0:
				#Grabo en la BD el fin por cantidad de errores (EF)
				finPorMaxErrores = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "EF",
													tipoEvento = "Control")
				finPorMaxErrores.save()			
				#Pongo como ultima secuencia para que no permita continuar
				fuerzoUltimaSec = True
				#Proceso de fantasia para mostrar un codigo de finalizacion
				idProcess = 99998
				#Muestro Finalizacion con fin rojo

				if protocoloObj.luzTerminaTomaDatos:
					secuenciaFinEvaluacion("mal")

		#Actualizo en el objeto para cualquiera de los dos casos
		intento.erroresConsecutivos = cantErroresConsecutivos
		intento.save()
	else:
		#Si no computo errores, me quedo con lo que tenia antes
		cantErroresConsecutivos=intento.erroresConsecutivos

	#Si forcé la ultima secuencia
	if fuerzoUltimaSec:
		ultimaSec = True
		next_sec = 0
		os.system("pigs p 5 0; pigs p 13 0; pigs p 26 0")

	else:
		next_sec = int(sec_id)+1;
		#Calculo si es la ultima secuencia para no mostrar boton de "Siguiente Secuencia" en el template
		ultimaSec = (protocoloObj.cantSecs == int(sec_id))

		#Obtengo la cantidad de botones de la proxima secuencia
		cantBotonesProxSec = BotonesSecuencias.objects.filter(idSec=next_sec, idProtocolo = protocoloObj).count()

	#Si tengo que prender luz para esperar el comienzo de la proxima secuencia
	if protocoloObj.luzEsperaProxSecuencia:
		r,g,b = rgb[protocoloObj.colorLuzEsperaProxSecuencia]
		stringComandoRGB = "pigs p 5 "+format(r)+"; pigs p 26 "+format(g)+"; pigs p 13 "+format(b)					
		#Ejecuto la operacion para prender los leds rgb
		os.system(stringComandoRGB)
	else:
		#Sino, apago
		os.system("pigs p 5 0; pigs p 26 0; pigs p 13 0")

	#Si no es la última secuencia, crea el proceso que escucha el boton rojo para pasar a la siguiente
	if ultimaSec == False:
		#Si esta habilitado para comenzar el trial con el botonRojo
		if protocoloObj.botonRojoIniciaTrial:
			#Llamo al script que va a escuchar si se presiona el boton rojo para inciar la siguiente secuencia
			process = subprocess.Popen(["/usr/bin/python","/home/pi/djangoProjects/scripts/botonRojoInicio.py",format(idIntento),format(next_sec)])
			idProcess = process.pid
		else:
			#Invento idProcess cualquiera
			idProcess = 9997
	elif fuerzoUltimaSec == False and ultimaSec == True: #Si es la ultima secuencia, pero no forzada, invento un idProcess de fantasia
		idProcess = 9997
		if protocoloObj.luzTerminaTomaDatos:
			secuenciaFinEvaluacion("Ok")

	#Si es la última secuencia, muestro el análisis total del Intento
	if ultimaSec == True:
		botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocoloObj).order_by('idSec')
		botonesPresionados = EventoRegistrado.objects.filter(idIntento = intento, tipoEvento = "Boton").order_by('idSec')
		secuenciasCorrectasIncorrectas = SecuenciaIntento.objects.filter(idIntento = intento)
		#Flag que me sirve para mostrar un boton volver o inicio en el template
		paginaPrev = "verSecuJugada"

		return render(request,'usuarios/ver_botones_intento.html',{"botonesSecuencias":botonesSecuencias,
																"botonesPresionados":botonesPresionados,
																"secuenciasCorrectasIncorrectas":secuenciasCorrectasIncorrectas,
																"intento":intento,"paginaPrev":paginaPrev})
	else:#Si no es la ultima secuencia
		return render(request,'secuencias/ver_secu_jugada.html',{"idProtocolo":protocolo_id,"idIntento": idIntento,"usuario":usuario, 
								 "secId":sec_id, "next_sec":next_sec, "ultima_sec": ultimaSec, 
								 "cantSecsFaltantes":cantSecsFaltantes, "cantErroresConsecutivos":cantErroresConsecutivos,
								 "botonesPresionados":botonesPresionados,
								 "botonesSecuencia":secuencia,"idProcess":idProcess,
								 "secuenciaPrueba":secuenciaPrueba,
								 "reverso":reverso,
								 "secuenciaIntento":secuenciaIntento,
								 "cantBotonesProxSec":cantBotonesProxSec})

#Cuando una secuencia es correcta puede prender luces verdes y/o sonido
def feedbackSecuenciaCorrecta(protocoloObj):
	colorSecuenciaCorrecta = protocoloObj.colorSecuenciaCorrecta
	tiempoLuzFeedback = protocoloObj.tiempoLuzFeedback


	if tiempoLuzFeedback != "0":
		tiempoLuzFeedback=float(tiempoLuzFeedback)/1000
	repeticionLuzFeedback = protocoloObj.repeticionLuzFeedback
	intervaloRepeticionLuzFeedback = protocoloObj.intervaloRepeticionLuzFeedback
	
	if intervaloRepeticionLuzFeedback != "0":
		intervaloRepeticionLuzFeedback=float(intervaloRepeticionLuzFeedback)/1000

	#Repito N veces el verde para indicar que es OK
	for i in range (0,int(repeticionLuzFeedback)):
		r,g,b = rgb[colorSecuenciaCorrecta]
		stringComandoRGB = "pigs p 5 "+format(r)+"; pigs p 26 "+format(g)+"; pigs p 13 "+format(b)					
		#Ejecuto la operacion para prender los leds rgb
		os.system(stringComandoRGB)

		if protocoloObj.feedbackSonido:
			GPIO.output(lucesGPIOs['Z'],1)
		time.sleep(tiempoLuzFeedback)
		#Apago Luces y sonido
		os.system("pigs p 5 0; pigs p 13 0; pigs p 26 0")
		GPIO.output(lucesGPIOs['Z'],0)
		time.sleep(intervaloRepeticionLuzFeedback)


#Cuando una secuencia es incorrecta puede prender luces rojas y/o sonido
def feedbackSecuenciaIncorrecta(protocoloObj):
	colorSecuenciaIncorrecta = protocoloObj.colorSecuenciaIncorrecta
	tiempoLuzFeedback = protocoloObj.tiempoLuzFeedback
	if tiempoLuzFeedback != "0":
		tiempoLuzFeedback=float(tiempoLuzFeedback)/1000

	repeticionLuzFeedback = protocoloObj.repeticionLuzFeedback
	intervaloRepeticionLuzFeedback = protocoloObj.intervaloRepeticionLuzFeedback
	if intervaloRepeticionLuzFeedback != "0":
		intervaloRepeticionLuzFeedback=float(intervaloRepeticionLuzFeedback)/1000

	#Si el sonido está activado lo prendo
	if protocoloObj.feedbackSonido:
		GPIO.output(lucesGPIOs['Z'],1)

	#Repito N veces el "rojo" para indicar que es Mal
	for i in range (0,int(repeticionLuzFeedback)):
		r,g,b = rgb[colorSecuenciaIncorrecta]
		stringComandoRGB = "pigs p 5 "+format(r)+"; pigs p 26 "+format(g)+"; pigs p 13 "+format(b)					
		os.system(stringComandoRGB)
		time.sleep(tiempoLuzFeedback)

		#Apago rojo
		os.system("pigs p 5 0; pigs p 13 0; pigs p 26 0")
		time.sleep(intervaloRepeticionLuzFeedback)

	#Apago sonido
	GPIO.output(lucesGPIOs['Z'],0)


def secuenciaFinEvaluacion(bienMal):
	#Muestro secuencia de colores para indicar que termino
	x=0
	while (x<2):
		os.system("pigs p 5 50; pigs p 13 0; pigs p 26 0")
		time.sleep(0.2)
		os.system("pigs p 5 0; pigs p 13 50; pigs p 26 0")
		time.sleep(0.2)
		os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
		time.sleep(0.2)
		os.system("pigs p 5 0; pigs p 13 0; pigs p 26 0")
		x=x+1

	if bienMal == "Ok":
		#Prendo Verde para indicar que termino mal
		os.system("pigs p 5 0; pigs p 13 0; pigs p 26 50")

	else:
		#Prendo Rojo para indicar que termino mal
		os.system("pigs p 5 50; pigs p 13 0; pigs p 26 0")


#################EXPORTO CSVs###################
#Exporta en formato csv los intentos solicitados
def export_csv(request):

	tipo = request.POST['tipo']
	if tipo == "extendido":
		response = export_csv_extendido(request)
	else:#Si es de tipo resumido
	
		#Levanto lo que quiero exportar
		export = request.POST['export']

		# Create the HttpResponse object with the appropriate CSV header.
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="export.csv"'
		writer = csv.writer(response)
		
		if export == "todo":
			#Todos los intentos de todos los protocolos
			intentos = Intento.objects.all()

		elif export == "protocolo":
				idTomaDatos = request.POST['tomaDatosEnProtocolo']
				#Si el idTomaDatos es 0, quiero todas las tomas de datos del protocolo
				if idTomaDatos == "0":
					#Todos los intentos del protocolo
					idProtocolo = request.POST['idProtocolo']
					intentos = Intento.objects.filter(idUsr__idTomaDeDatos__idProtocolo__id = idProtocolo)
				else:
					intentos = Intento.objects.filter(idUsr__idTomaDeDatos__id = idTomaDatos)

		elif export == "tomaDatos":
			#Todos los intentos de la toma de datos
			idTomaDatos = request.POST['idTomaDatos']
			intentos = Intento.objects.filter(idUsr__idTomaDeDatos__id = idTomaDatos)
		
		elif export == "usuario":
			#Todos los intentos de un usuario
			idUsr = request.POST['idUsr']
			intentos = Intento.objects.filter(idUsr__id = idUsr)
		
		elif export == "intento":
			#Todos los intentos de un usuario
			idIntento = request.POST['idIntento']
			intentos = Intento.objects.filter(id = idIntento)

		dataIntentos = []

		for intento in intentos:
			data = []
			data = exportIntento(intento)
			dataIntentos.append(data)

		#Exporto al archivo .csv
		for intento in dataIntentos:
			writer.writerows(intento)

	return response


def export_csv_extendido(request):

	#Levanto lo que quiero exportar
	export = request.POST['export']

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="export_extendido.csv"'
	writer = csv.writer(response)

	protocolos = []
	tomasDeDatos = []
	intentos = []
	intentosProtocolo = []

	if export == "todo":
		indiceProtocolos = 0
	 	protocolos = list(Protocolo.objects.all())
		for protocolo in protocolos:
			tomasDeDatosProtocolo = list(TomaDeDatos.objects.filter(idProtocolo = protocolo))
			tomasDeDatos.append(tomasDeDatosProtocolo)
			for tomaDatos in tomasDeDatosProtocolo:
				intentosTomaDeDatos = list(Intento.objects.filter(idUsr__idTomaDeDatos = tomaDatos))
				intentos.append(intentosTomaDeDatos)

			intentosProtocolo.append(intentos)
			intentos = []

	if export == "protocolo":
 			idProtocolo = request.POST['idProtocolo']
 			protocolo = Protocolo.objects.get(id = idProtocolo)
 			protocolos.append(protocolo)

	 		idTomaDatos = request.POST['tomaDatosEnProtocolo']	 		
	 		#Si el idTomaDatos es 0, quiero todas las tomas de datos del protocolo
	 		if idTomaDatos == "0":
	 			#Todos las tomas de Datos del protocolo
	 			tomasDeDatosProtocolo = list(TomaDeDatos.objects.filter(idProtocolo__id = idProtocolo))
		 		tomasDeDatos.append(tomasDeDatosProtocolo)

	 		else:
	 			#Todos las tomas de Datos del protocolo
	 			tomasDeDatosProtocolo = list(TomaDeDatos.objects.filter(id = idTomaDatos))

	 		tomasDeDatos.append(tomasDeDatosProtocolo)
			for tomaDatos in tomasDeDatosProtocolo:
				intentosTomaDeDatos = list(Intento.objects.filter(idUsr__idTomaDeDatos = tomaDatos))
				intentos.append(intentosTomaDeDatos)

			intentosProtocolo.append(intentos)

	elif export == "intento":
	 	#Todos los intentos de un usuario
	 	idIntento = request.POST['idIntento']
	 	intento = Intento.objects.filter(id = idIntento)
	 	intentosTomaDeDatos = []
	 	intentosTomaDeDatos.append(list(intento))
	 	intentosProtocolo.append(list(intentosTomaDeDatos))

	 	tomaDatos = TomaDeDatos.objects.filter(id = intento[0].idUsr.idTomaDeDatos.id)
	 	tomasDeDatos.append(list(tomaDatos))

	 	protocolo = Protocolo.objects.get(id = intento[0].idUsr.idTomaDeDatos.idProtocolo.id)
	 	protocolos.append(protocolo) 		

 	#Muestro lo solicitado de forma ordenada (Protocolo->TomaDatos->Intentos)
 	for i in range(0,len(protocolos)):
 		#Muestro los datos de cada protocolo
		dataProtocolo, secuenciasProtocolo = datos_csv_extendido_protocolo(request,protocolos[i])
		#Almaceno el encabezado del protocolo
		writer.writerows(dataProtocolo)
		
		for j in range(0,len(tomasDeDatos[i])):
			dataTomaDatos = datos_csv_extendido_tomaDatos(tomasDeDatos[i][j])
			#Almaceno el encabezado del protocolo
			writer.writerows(dataTomaDatos)
			for k in range(0,len(intentosProtocolo[i][j])):
				#print "Protocolo: "+str(i)
				#print "TomaDatos: "+str(j)
				#print "Intento: "+str(k)
				dataIntento = datos_csv_extendido_intento(intentosProtocolo[i][j][k],secuenciasProtocolo)
				writer.writerows(dataIntento)

	return response

def datos_csv_extendido_protocolo(request,protocolo):

	dataProtocolo = []

	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo)

	dataProtocolo.append(["Protocolo:",protocolo.nombreProtocolo])
	dataProtocolo.append(["#Secuencias:",protocolo.cantSecs])
	dataProtocolo.append(["tiempoEncendidoLuz:",protocolo.tiempoEncendidoLuz])
	dataProtocolo.append(["tiempoEntreLuces:",protocolo.tiempoEntreLuces])
	dataProtocolo.append(["tiempoComienzaIntento:",protocolo.tiempoComienzaIntento])
	dataProtocolo.append(["timeoutRespuesta:",protocolo.timeoutRespuesta])
	dataProtocolo.append(["cantErroresCorte:",protocolo.cantErroresCorte])
	dataProtocolo.append(["IdSec","Botones Secuencia","Secuencia Prueba"])

	idSecActual = 0
	secAcum = []
	fila = []
	botonesPresionados = []
	controlInicio = "0"
	controlFin = "0"
	secuenciaPrueba = "No"
	secuenciaCorrecta = False
	secuenciasProtocolo = []

	#Agrupo los valores de botones segun el idSec
	for boton in botonesSecuencias:
		#Si cambio la secuencia
		if boton.idSec != idSecActual:
			#Grabo lo anterior (excepto al principio, vacio)
			if idSecActual != 0:
				fila.extend([botonesSec])
				fila.extend([str(secuenciaPrueba)])
				dataProtocolo.append(fila)
				controlInicio = "-"
				botonesPresionados = []
				controlFin = "-"
				secuenciaCorrecta = False
				#Me almaceno cada secuencia para después.
				secuenciasProtocolo.append([botonesSec])

			#Actualizo idSec
			idSecActual = boton.idSec

			#Empiezo a juntar nueva fila
			fila = [boton.idSec]
			secuenciaPrueba = boton.secuenciaPrueba
			botonesSec = [boton.valorBoton.encode("ascii")]
			
		else: #Si todavia tengo botones de la misma secuencia original
			#Agrego el valor del boton a la fila
			botonesSec.extend([boton.valorBoton.encode("ascii")])

	#Almaceno el ultimo guardado
	secuenciasProtocolo.append([botonesSec])
	fila.extend([botonesSec])
	fila.extend([str(secuenciaPrueba)])
	dataProtocolo.append(fila)

	return dataProtocolo,secuenciasProtocolo

def datos_csv_extendido_tomaDatos(tomaDatos):
	dataTomaDatos = []
	#Agrego nombre de la toma de datos.
	dataTomaDatos.append(["Toma de Datos:",tomaDatos.nombreTomaDeDatos])
	dataTomaDatos.append(["fechaCreacion:",tomaDatos.fechaCreacion])
	dataTomaDatos.append(["ultimaFechaEvaluacion:",tomaDatos.ultimaFechaEvaluacion])

	return dataTomaDatos

#Devuelve los datos de un intento para pasar a formato csv
def datos_csv_extendido_intento(intento,secuenciasProtocolo):
	dataIntento = []
	protocolo = intento.idUsr.idTomaDeDatos.idProtocolo

	numRegistroToma = 1

	dataIntento.append(["Usuario","idEvaluacion","numRegistroToma","idSec","timeStamp",
					"Tipo Evento","Valor Evento","Tiempo Presionado","Tiempo Desde Inicio"])

	#Inicio Log
	dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,"0",intento.timeStamp,"Control","INICIO LOG","0","0"])
	numRegistroToma+=1

	#Guardo todos los eventos registrados para el intento
	eventosRegistrados = EventoRegistrado.objects.filter(idIntento = intento)

	#Me quedo con el primero para manejar indices
	idSecAnterior = eventosRegistrados[0].idSec

	#Para cada evento/boton, registro una fila	
	for eventoRegistrado in list(eventosRegistrados):
		if eventoRegistrado.idSec == idSecAnterior:
			tiempoUltimoEventoRegistrado = eventoRegistrado.tiempoDesdeInicio
			dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,eventoRegistrado.idSec,
								eventoRegistrado.timeStamp,eventoRegistrado.tipoEvento,
								eventoRegistrado.valorEvento,
								eventoRegistrado.tiempoPresionadoMS,tiempoUltimoEventoRegistrado])

			#Incremento el numero de registro para la toma
			numRegistroToma+=1

		else: #Si pase a la siguiente, tengo que poner el resultado del trial anterior (Correcto/Incorrecto)
			botonesPresionados = []
			try:
				#Guardo todos los botones presionados
				eventosBotones = EventoRegistrado.objects.filter(idIntento = intento, idSec = eventoRegistrado.idSec-1, tipoEvento = "Boton").values("valorEvento")
				for botonPresionado in list(eventosBotones):
					botonesPresionados.extend(botonPresionado['valorEvento'].encode("ascii"))

			except:
				print("Algo sucede con los botones de la secuencia "+format(boton.idSec))

			#Analizo si lo presionado fue correcto
			correcto = (botonesPresionados == secuenciasProtocolo[eventoRegistrado.idSec-2][0])

			dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,eventoRegistrado.idSec-1,
								"Correcto",correcto,secuenciasProtocolo[eventoRegistrado.idSec-2][0],botonesPresionados,tiempoUltimoEventoRegistrado])
			numRegistroToma+=1

			tiempoUltimoEventoRegistrado = eventoRegistrado.tiempoDesdeInicio
			dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,eventoRegistrado.idSec,
					eventoRegistrado.timeStamp,eventoRegistrado.tipoEvento,
					eventoRegistrado.valorEvento,
					eventoRegistrado.tiempoPresionadoMS,tiempoUltimoEventoRegistrado])
			numRegistroToma+=1


		#Pongo como idSecAnterior el que acaba de pasar para analizar cuando cambia
		idSecAnterior = eventoRegistrado.idSec

	idSecActual = idSecAnterior

	#Voy a registrar la correctitud de la ultima secuencia jugada, a menos que se haya Terminado el Intento
	if eventoRegistrado.valorEvento == "OTI":

		botonesPresionados = []
		try:
			#Guardo todos los botones presionados
			eventosBotones = EventoRegistrado.objects.filter(idIntento = intento, idSec = eventoRegistrado.idSec, tipoEvento = "Boton").values("valorEvento")
			for botonPresionado in list(eventosBotones):
				botonesPresionados.extend(botonPresionado['valorEvento'].encode("ascii"))

		except:
			print("Algo sucede con los botones de la secuencia "+format(boton.idSec))


		#Analizo si lo presionado fue correcto
		correcto = (botonesPresionados == secuenciasProtocolo[eventoRegistrado.idSec-1][0])

		dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,eventoRegistrado.idSec,
							"Correcto",correcto,secuenciasProtocolo[eventoRegistrado.idSec-1][0],botonesPresionados,tiempoUltimoEventoRegistrado])
		numRegistroToma+=1
		idSecActual+=1

	else: #Si es otro tipo de fin (RF,OAS,TO,OF)
		#Pongo el resultado del ultimo trial jugado
		botonesPresionados = []
		try:
			#Guardo todos los botones presionados
			eventosBotones = EventoRegistrado.objects.filter(idIntento = intento, idSec = eventoRegistrado.idSec, tipoEvento = "Boton").values("valorEvento")
			for botonPresionado in list(eventosBotones):
				botonesPresionados.extend(botonPresionado['valorEvento'].encode("ascii"))

		except:
			print("Algo sucede con los botones de la secuencia "+format(boton.idSec))

		#Analizo si lo presionado fue correcto
		correcto = (botonesPresionados == secuenciasProtocolo[eventoRegistrado.idSec-1][0])
		dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,eventoRegistrado.idSec,
							"Correcto",correcto,secuenciasProtocolo[eventoRegistrado.idSec-1][0],botonesPresionados,tiempoUltimoEventoRegistrado])
		#Avanzo para que el while no analice la correctitud, recién hecha
		idSecActual+=1

	numRegistroToma+=1

	#Al terminar de recorrer los eventos registrados, tengo que ver si había más botones en la secuencia
	#que no fueron presionados. En ese caso registro todo lo que falta como No Evaluado
	while (idSecActual <= protocolo.cantSecs):
		#Solo tengo que poner analisis de (in)correctitud para las secuencias restantes
		dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,idSecActual,
							"Correcto","No Evaluado",secuenciasProtocolo[idSecActual-1][0],"[]",0])
		numRegistroToma+=1
		idSecActual+=1

	#Fin Log
	dataIntento.append([intento.idUsr.nombre,intento.id,numRegistroToma,"","","Control","FIN LOG","",""])

	return dataIntento


#Devuelve los datos de un intento para pasar a formato csv
def exportIntento(intento):
	dataIntento = []

	protocolo = intento.idUsr.idTomaDeDatos.idProtocolo
	botonesSecuencias = BotonesSecuencias.objects.filter(idProtocolo = protocolo)

	dataIntento.append(["Protocolo:",protocolo.nombreProtocolo])
	dataIntento.append(["Toma de Datos:",intento.idUsr.idTomaDeDatos.nombreTomaDeDatos])
	dataIntento.append(["Usuario:",intento.idUsr.nombre])
	dataIntento.append(["id Evaluacion:",intento.id])
	dataIntento.append(["Errores Consecutivos:",intento.erroresConsecutivos])
	dataIntento.append(["Fecha/Hora:",intento.timeStamp])
	dataIntento.append(["IdSec","Botones Secuencia","Secuencia Prueba","Control Inicio","Botones Presionados","Control Fin","Correcto", "Tiempo en ms"])

	idSecActual = 0
	secAcum = []
	fila = []
	botonesPresionados = []
	controlInicio = "0"
	controlFin = "0"
	secuenciaPrueba = "No"
	secuenciaCorrecta = False

	#Agrupo los valores de botones segun el idSec
	for boton in botonesSecuencias:
		#Si cambio la secuencia
		if boton.idSec != idSecActual:
			#Grabo lo anterior (excepto al principio, vacio)
			if idSecActual != 0:
				fila.extend([botonesSec])
				fila.extend([str(secuenciaPrueba)])
				fila.extend([controlInicio])
				fila.extend([botonesPresionados])
				fila.extend([controlFin])
				fila.extend([str(secuenciaCorrecta)])
				fila.extend([str(tiempoTotalTrial)])
				dataIntento.append(fila)
				controlInicio = "-"
				botonesPresionados = []
				controlFin = "-"
				secuenciaCorrecta = False

			#Actualizo idSec
			idSecActual = boton.idSec

			#Empiezo a juntar nueva fila
			fila = [boton.idSec]
			secuenciaPrueba = boton.secuenciaPrueba
			botonesSec = [boton.valorBoton.encode("ascii")]

			eventosSecuenciaControl = EventoRegistrado.objects.filter(idIntento = intento, idSec = boton.idSec, tipoEvento = "Control")

			try:
				#Guardo el evento de control de Inicio (OI,RI)
				controlInicio = eventosSecuenciaControl[0].valorEvento.encode("ascii")
			except:
				print("No se jugo secuencia "+format(boton.idSec))
			try:
				#Guardo todos los botones presionados
				eventosBotones = EventoRegistrado.objects.filter(idIntento = intento, idSec = boton.idSec, tipoEvento = "Boton").values("valorEvento")
				for botonPresionado in list(eventosBotones):
					botonesPresionados.extend(botonPresionado['valorEvento'].encode("ascii"))

			except:
				print("Algo sucede con los botones de la secuencia "+format(boton.idSec))

			try:
				#Guardo el evento de control de Fin (RF,OF,OAS,OTI)
				controlFin = eventosSecuenciaControl[len(eventosSecuenciaControl)-1].valorEvento.encode("ascii")
			except:
				print("Problemas con el final de la secuencia "+format(boton.idSec))

			try:
				queryCorrectitud = SecuenciaIntento.objects.filter(idIntento = intento, idSec = boton.idSec)
				secuenciaCorrecta = queryCorrectitud[0].correcto
			except:
				print("Problemas al obtener correctitud de la secuencia "+format(boton.idSec))

			try:
				#Obtengo el tiempo total de la secuencia
				eventosRegistrados = EventoRegistrado.objects.filter(idIntento = intento, idSec = boton.idSec)
				ultimoEventoRegistrado = eventosRegistrados[eventosRegistrados.count()-1]
				tiempoTotalTrial = ultimoEventoRegistrado.tiempoDesdeInicio
			except:
				print("Problemas al tiempo total de la secuencia "+format(boton.idSec))
				#Si no se jugo ese trial, lo pongo en 0
				tiempoTotalTrial = 0
		else: #Si todavia tengo botones de la misma secuencia original
			#Agrego el valor del boton a la fila
			botonesSec.extend([boton.valorBoton.encode("ascii")])

	#Almaceno el ultimo guardado
	fila.extend([botonesSec])
	fila.extend([str(secuenciaPrueba)])
	fila.extend([controlInicio])
	fila.extend([botonesPresionados])
	fila.extend([controlFin])
	fila.extend([str(secuenciaCorrecta)])
	fila.extend([str(tiempoTotalTrial)])
	dataIntento.append(fila)
	#Agrego espacio para separar Intentos
	dataIntento.append('')	

	return dataIntento


#Chequeo si la secuencia presionada por el usuario fue correcta:
def secuenciaPresionadaOK(secuencia,botonesPresionados,reverso):
	#Primero chequeo que sea la misma cantidad de Botones, sino ya no es Ok
	if (len(secuencia) != len(botonesPresionados)):
		return False

	if (not reverso):
		#Comparo boton a boton para ver si hay alguno distinto
		for i in range(len(secuencia)):
			#Me fijo si hay alguna X (apretó dos botones juntos)
			if (secuencia[i].valorBoton == "X"):
				return False
			if (secuencia[i].valorBoton != botonesPresionados[i].valorEvento):
				return False
	else:
		#Comparo boton a boton (de forma reversa) para ver si hay alguno distinto
		for i in range(len(secuencia)):
			#Me fijo si hay alguna X (apretó dos botones juntos)
			if (secuencia[i].valorBoton == "X"):
				return False
			if (secuencia[i].valorBoton != botonesPresionados[len(secuencia)-i-1].valorEvento):
				return False
	#Sino salio antes es porque está todo OK
	return True 

def checkRedButtonFin(request):
	sec_id = request.POST['idSec']
	#sec_id = 2
	idIntento = request.POST['idIntento']
	#idIntento = 91
	usr_id = request.POST['usrId']
	intento = Intento.objects.get(id=idIntento)
	protocolo_id = request.POST['idProtocolo']
	protocoloObj = Protocolo.objects.get(id=protocolo_id)
	

	#Genero la consulta con la BD para saber si presionaron el boton Rojo de finalizar
	botonFinPresionado = EventoRegistrado.objects.filter(idIntento = intento, idSec = sec_id, 
										tipoEvento = 'Control', valorEvento = 'RF')
	if botonFinPresionado.count() > 0:
		response = {'status': 1}
		#return HttpResponse()
	else:
		response = {'status': 0}

	return HttpResponse(json.dumps(response), content_type='application/json')
	
def checkRedButtonInicio(request):
	sec_id = request.POST['idSec']
	idIntento = request.POST['idIntento']
	usr_id = request.POST['usrId']
	intento = Intento.objects.get(id=idIntento)
	protocolo_id = request.POST['idProtocolo']
	protocoloObj = Protocolo.objects.get(id=protocolo_id)

	#Genero la consulta con la BD para saber si presionaron el boton Rojo de finalizar
	botonInicioPresionado = EventoRegistrado.objects.filter(idIntento = intento, idSec = sec_id, 
										tipoEvento = 'Control', valorEvento = 'RI')
	if botonInicioPresionado.count() > 0:
		response = {'status': 1}
	else:
		response = {'status': 0}

	return HttpResponse(json.dumps(response), content_type='application/json')

#Cuando presiona el boton de Detener, llama a esta vista con parametros GET
def finalizarIntento(request):
	idIntento = request.GET['idIntento']
	pid = int(request.GET['pid'])
	sec_id = request.POST['idSec']

	#Mato el proceso que estaba esperando al boton rojo de fin (en verSecuJugada) o todos los botones (en playWaitSec)
	if psutil.pid_exists(pid):
		os.kill(pid, signal.SIGTERM)

	#Registro el evento de finalización del intento
	intento = Intento.objects.get(id=idIntento)
	intentoFinalizado = EventoRegistrado(idIntento = intento, idSec = sec_id, valorEvento = "OTI",
												tipoEvento = "Control")
	intentoFinalizado.save()
	#Termino yendo al inicio (por ahora no muestro resumen)
	jugar(request)

def jugarReproducirSec(request): #Reproduce secuencia y almacena el intento en la DB
	sec_id = request.POST['idSec']
	usr_id = request.POST['usrId']
	#Almaceno en BD el intento que va a hacer el usuario
	intento = Intento(idSec=sec_id, idUsr=usr_id)
	intento.save() 
	secuencia = BotonesSecuencias.objects.filter(idSec=sec_id)
	for boton in secuencia:
		GPIO.output(lucesGPIOs[boton.valorBoton],1)
		time.sleep(1)
		GPIO.output(lucesGPIOs[boton.valorBoton],0)
		time.sleep(0.500)
	lista_secuencia = BotonesSecuencias.objects.order_by('idSec');
	return render(request,'secuencias/esperar_secuencia.html',{"usuario":usr_id, "secId":sec_id})


#USUARIOS

def agregar_usuario(request):
	os.system("pigs p 5 0; pigs p 26 50; pigs p 13 0")
	if request.method == "POST":
		idTomaDeDatos = request.POST['idTomaDeDatos']
		tomaDeDatosObj = TomaDeDatos.objects.get(id = idTomaDeDatos)
		nombre = request.POST['nombreUsuario']
		try:
			usuario = Usuario.objects.get(idTomaDeDatos = tomaDeDatosObj, nombre = nombre)
		except Usuario.DoesNotExist:
			usuario = Usuario(idTomaDeDatos = tomaDeDatosObj, nombre = nombre)
			usuario.save()

		return redirect('lista_usuarios_toma',idTomaDeDatos)

def usuario_lista(request):
	lista_secuencia = BotonesSecuencias.objects.order_by('idSec');
	lista_usuarios = Usuario.objects.order_by('nombre');
	return render(request,'usuarios/usuario_lista.html',{"lista_usuarios":lista_usuarios})

def usuario_ver(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/usuario_ver.html', {'usuario': usuario})
	
def usuario_nuevo(request):
	if request.method == "POST":
		form = UsuarioForm(request.POST)
		if form.is_valid():
			usuario = form.save(commit=False)
			usuario.save()
			return redirect('usuario_lista')
	else:
		form = UsuarioForm()
	return render(request, 'usuarios/usuario_editar.html', {'form': form})

def usuario_editar(request,pk):
	usuario = get_object_or_404(Usuario, pk=pk)
	if request.method == "POST":
		form = UsuarioForm(request.POST, instance=usuario)
		if form.is_valid():
			usuario = form.save(commit=False)
			usuario.save()
			return redirect('usuario_ver', pk=usuario.pk)
	else:
		form = UsuarioForm(instance=usuario)
		return render(request, 'usuarios/usuario_editar.html', {'form': form})
		
def documentacion(request):
	return render(request,'documentacion.html',{})

def descargar_protocolo(request):
	return render(request,'documentacion.html',{})


#GPIO2
def blinker(request):
	os.system("pigs p 5 50; pigs p 13 50; pigs p 26 50")
	if 'on' in request.POST:
		GPIO.output(lucesGPIOs['A'],1)
		GPIO.output(lucesGPIOs['B'],1)
		GPIO.output(lucesGPIOs['C'],1)
		GPIO.output(lucesGPIOs['D'],1)
		GPIO.output(lucesGPIOs['E'],1)
		GPIO.output(lucesGPIOs['F'],1)
		GPIO.output(lucesGPIOs['G'],1)
		GPIO.output(lucesGPIOs['H'],1)
		GPIO.output(lucesGPIOs['I'],1)
		GPIO.output(lucesGPIOs['Z'],1)
	elif 'off' in request.POST:
		GPIO.output(lucesGPIOs['A'],0)
		GPIO.output(lucesGPIOs['B'],0)
		GPIO.output(lucesGPIOs['C'],0)
		GPIO.output(lucesGPIOs['D'],0)
		GPIO.output(lucesGPIOs['E'],0)
		GPIO.output(lucesGPIOs['F'],0)
		GPIO.output(lucesGPIOs['G'],0)
		GPIO.output(lucesGPIOs['H'],0)
		GPIO.output(lucesGPIOs['I'],0)
		GPIO.output(lucesGPIOs['Z'],0)
	return render(request,'gpio/control.html')

def rgbTest(request):
	if 'r' in request.POST:
		r = int(request.POST['r'])
		g = int(request.POST['g'])
		b = int(request.POST['b'])
	else: 
		r = 0
		g = 0
		b = 0

	os.system("pigs p 5 "+format(r)+"; pigs p 26 "+format(g)+"; pigs p 13 "+format(b))

	return render(request,'gpio/rgbTest.html', {'r': r,'g': g,'b': b})


def bry(request):
	return render(request, 'brython/prueba.html', {})


#SUBIR ARCHIVOS
def handle_uploaded_file(f):
	return HttpResponseRedirect('secuencias/uploadOk.html')

def uploadFile(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			handle_uploaded_file(request.FILES['file'])
	else:
		form = UploadFileForm()
	return render(request, 'secuencias/uploadFile.html', {'form': form})
