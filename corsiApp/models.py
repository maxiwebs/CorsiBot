# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from datetime import date

#import django_tables2 as tables


class Protocolo(models.Model):
	nombreProtocolo = models.CharField(max_length=100, default = 0)
	cantSecs = models.IntegerField(default=0)
	tiempoEncendidoLuz = models.IntegerField(default=750)
	tiempoEntreLuces = models.IntegerField(default=750)
	tiempoComienzaIntento = models.IntegerField(default=0)
	timeoutRespuesta = models.IntegerField(default=60000)
	cantErroresCorte = models.IntegerField(default=0)
	reverso = models.BooleanField(default = False)
	botonRojoIniciaTrial = models.BooleanField(default = True)
	luzComienzaSecuencia = models.BooleanField(default = True)
	colorLuzComienzaSecuencia = models.CharField(max_length=20, default = "blue")
	tiempoLuzComienzaSecuencia = models.IntegerField(default=500)
	repeticionLuzComienzaSecuencia = models.IntegerField(default=3)
	intervaloRepeticionLuzComienzaSecuencia = models.IntegerField(default=100)
	luzEsperaBotones = models.BooleanField(default = True)
	colorLuzEsperaBotones = models.CharField(max_length=20, default = "blue")
	luzAnalisisIntento = models.BooleanField(default = True)
	colorLuzAnalisisIntento = models.CharField(max_length=20, default = "yellow")
	feedbackLuces = models.BooleanField(default = True)
	colorSecuenciaCorrecta = models.CharField(max_length=20, default = "green")
	colorSecuenciaIncorrecta = models.CharField(max_length=20, default = "red")
	tiempoLuzFeedback = models.IntegerField(default=200)
	repeticionLuzFeedback = models.IntegerField(default=3)
	intervaloRepeticionLuzFeedback = models.IntegerField(default=100)
	luzEsperaProxSecuencia = models.BooleanField(default = True)
	colorLuzEsperaProxSecuencia = models.CharField(max_length=20, default = "blue")
	feedbackSonido = models.BooleanField(default = True)
	luzTerminaTomaDatos = models.BooleanField(default = True)

	def __unicode__(self):
		return "{0} - {1}".format(self.id, self.nombreProtocolo)

	def get_fields(self):
	    return [(field.name, field.value_to_string(self)) for field in Protocolo._meta.fields]

class DocumentoProtocolo(models.Model):
	documento = models.FileField(upload_to='.')

	def __unicode__(self):
		return "{0}".format(self.documento)


class BotonesSecuencias(models.Model):
    idProtocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, default=0)
    idSec = models.IntegerField(default=0)
    valorBoton = models.CharField(max_length=1)
    secuenciaPrueba = models.BooleanField(default = False)

    def __unicode__(self):
        #return self.valorBoton, self.idSec
		return "{0}, {1}, {2}, {3}".format(self.idProtocolo, self.idSec, self.secuenciaPrueba, self.valorBoton)

class TomaDeDatos(models.Model):
	idProtocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, default=0)
	nombreTomaDeDatos = models.TextField(max_length=50, default = "nombre")
	fechaCreacion = models.DateField(auto_now_add=True)
	ultimaFechaEvaluacion = models.DateField(null = True, blank=True)

	def __unicode__(self):
		return "{0}, {1}, {2}, {3}, {4}".format(self.id, self.nombreTomaDeDatos,self.idProtocolo.nombreProtocolo, self.fechaCreacion, self.ultimaFechaEvaluacion)

class DocumentoTomaDeDatos(models.Model):
	protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, default=0)
	documento = models.FileField(upload_to='.')

	def __unicode__(self):
		return "{0}, {1}".format(self.protocolo.id, self.documento)

class Usuario(models.Model):
	idTomaDeDatos = models.ForeignKey(TomaDeDatos, on_delete=models.CASCADE, default=0)
	nombre = models.CharField(max_length=20)
	cantIntentos = models.IntegerField(default=0)
 
	def __unicode__(self):
		return "{0} - {1}".format(self.nombre, self.idTomaDeDatos)

class Intento(models.Model):
	idUsr = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=0)
	erroresConsecutivos = models.IntegerField(default=0)
	timeStamp=models.DateTimeField(default=datetime.now)
	
	def __unicode__(self):
		return "{0}, {1}".format(self.idUsr, self.timeStamp)

#REGISTRO DE BOTONES PRESIONADOS/EVENTOS OCURRIDOS
class EventoRegistrado(models.Model):
	idIntento = models.ForeignKey(Intento, on_delete=models.CASCADE, default=0)
	idSec = models.IntegerField(default=0)
	valorEvento = models.CharField(max_length=3)
	tipoEvento = models.CharField(max_length=7) #Boton/Control
	tiempoPresionadoMS = models.IntegerField(default = 100)
	timeStamp=models.DateTimeField(default=datetime.now)
	tiempoDesdeInicio = models.IntegerField(default = 0)
	
	def __unicode__(self):
		return "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(self.valorEvento, self.tipoEvento, self.tiempoPresionadoMS,
												self.idSec, self.idIntento.id, self.timeStamp, self.tiempoDesdeInicio)

#Booleano que me indica si el intento para una secuencia es correcto o incorrecto
class SecuenciaIntento(models.Model):
	idIntento = models.ForeignKey(Intento, on_delete=models.CASCADE, default=0)
	idSec = models.IntegerField(default=0)
	correcto = models.BooleanField(default = True)

	def __unicode__(self):
		return "{0}, {1}, {2}".format(self.idIntento.id, self.idSec, self.correcto)
