import json
from distutils.util import strtobool

from corsiApp.models import BotonesSecuencias, Protocolo, DocumentoProtocolo

json_data=open("/home/pi/djangoProjects/scripts/archivosSubidos/protocolo.json").read()
experiment = json.loads(json_data)

valoresPorDefault = {
		"tiempoEncendidoLuz": 750,
		"tiempoEntreLuces": 750,
		"tiempoComienzaIntento": 0,
		"timeoutRespuesta": 60000,
		"cantErroresCorte": 0,
		"reverso": "False",
		"botonRojoIniciaTrial":"True",
		"luzComienzaSecuencia":"True",
		"colorLuzComienzaSecuencia":"blue",
		"tiempoLuzComienzaSecuencia":"500",
		"repeticionLuzComienzaSecuencia":"3",
		"intervaloRepeticionLuzComienzaSecuencia":"100",
		"luzEsperaBotones":"True",
		"colorLuzEsperaBotones":"blue",
		"luzAnalisisIntento":"True",
		"colorLuzAnalisisIntento":"yellow",
		"feedbackLuces": "True",
		"colorSecuenciaCorrecta":"green",
		"colorSecuenciaIncorrecta":"red",
		"tiempoLuzFeedback":"200",
		"repeticionLuzFeedback":"3",
		"intervaloRepeticionLuzFeedback":"100",
		"luzEsperaProxSecuencia": "False",
		"colorLuzEsperaProxSecuencia": "blue",
		"feedbackSonido":"True",
		"luzTerminaTomaDatos":"True"
}

valoresProtocolo = {}

if "nombreProtocolo" in json_data:
	valoresProtocolo["nombreProtocolo"] = experiment['protocolo']['nombreProtocolo']
else:
	valoresProtocolo["nombreProtocolo"] = "Sin Nombre"

#Recorro cada uno de los parametros para ver si están definidos. Sino, asigno default.
for parametroActual in valoresPorDefault.keys():
	if parametroActual in json_data:
		valoresProtocolo[parametroActual] = experiment['properties'][parametroActual]
	else:
		valoresProtocolo[parametroActual] = valoresPorDefault[parametroActual]


secuencias = experiment['trials']
cantSecs = len(secuencias)

protocolo = Protocolo(nombreProtocolo = valoresProtocolo['nombreProtocolo'],
					  cantSecs = cantSecs,
					  tiempoEncendidoLuz = valoresProtocolo['tiempoEncendidoLuz'],
					  tiempoEntreLuces = valoresProtocolo['tiempoEntreLuces'],
					  tiempoComienzaIntento = valoresProtocolo['tiempoComienzaIntento'],
					  timeoutRespuesta = valoresProtocolo['timeoutRespuesta'],
					  cantErroresCorte = valoresProtocolo['cantErroresCorte'],
					  reverso = strtobool(valoresProtocolo['reverso']),
					  botonRojoIniciaTrial = strtobool(valoresProtocolo['botonRojoIniciaTrial']),
					  luzComienzaSecuencia = strtobool(valoresProtocolo['luzComienzaSecuencia']),
					  colorLuzComienzaSecuencia = valoresProtocolo['colorLuzComienzaSecuencia'], 
					  tiempoLuzComienzaSecuencia = valoresProtocolo['tiempoLuzComienzaSecuencia'],
					  repeticionLuzComienzaSecuencia = valoresProtocolo['repeticionLuzComienzaSecuencia'],
					  intervaloRepeticionLuzComienzaSecuencia = valoresProtocolo['intervaloRepeticionLuzComienzaSecuencia'],
					  luzEsperaBotones = strtobool(valoresProtocolo['luzEsperaBotones']),
					  colorLuzEsperaBotones = valoresProtocolo['colorLuzEsperaBotones'],
					  luzAnalisisIntento = strtobool(valoresProtocolo['luzAnalisisIntento']),
					  colorLuzAnalisisIntento = valoresProtocolo['colorLuzAnalisisIntento'],
					  feedbackLuces = strtobool(valoresProtocolo['feedbackLuces']),
					  colorSecuenciaCorrecta = valoresProtocolo['colorSecuenciaCorrecta'],
					  colorSecuenciaIncorrecta = valoresProtocolo['colorSecuenciaIncorrecta'],
					  tiempoLuzFeedback = valoresProtocolo['tiempoLuzFeedback'],
					  repeticionLuzFeedback = valoresProtocolo['repeticionLuzFeedback'],
					  intervaloRepeticionLuzFeedback = valoresProtocolo['intervaloRepeticionLuzFeedback'],
			          luzEsperaProxSecuencia = strtobool(valoresProtocolo['luzEsperaProxSecuencia']),
					  colorLuzEsperaProxSecuencia = valoresProtocolo['colorLuzEsperaProxSecuencia'],
					  feedbackSonido = strtobool(valoresProtocolo['feedbackSonido']),
					  luzTerminaTomaDatos = strtobool(valoresProtocolo['luzTerminaTomaDatos'])
					  )

protocolo.save()
idProtocolo = protocolo.id

listaBotones = []
for idSec in range(1, cantSecs+1): 
	secuActual=secuencias[str(idSec)]
	#Me quedo con el booleano sobre si la secuencia es de prueba o no
	secuenciaPrueba = strtobool(secuActual[1])
	#print secuenciaPrueba
	for valorBoton in str(secuActual[0]):
		b = BotonesSecuencias(idProtocolo = protocolo,idSec = idSec,valorBoton = valorBoton, secuenciaPrueba = secuenciaPrueba)
		listaBotones.append (b)

BotonesSecuencias.objects.bulk_create(listaBotones)

