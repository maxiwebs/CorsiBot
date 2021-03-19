# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from corsiApp.models import Usuario, Protocolo, BotonesSecuencias, TomaDeDatos, Intento, EventoRegistrado, DocumentoProtocolo, DocumentoTomaDeDatos, SecuenciaIntento

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Protocolo)
admin.site.register(BotonesSecuencias)
admin.site.register(TomaDeDatos)
admin.site.register(Intento)
admin.site.register(EventoRegistrado)
admin.site.register(DocumentoProtocolo)
admin.site.register(DocumentoTomaDeDatos)
admin.site.register(SecuenciaIntento)

