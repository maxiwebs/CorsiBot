"""corsiProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from corsiApp import views as views
from corsiApp.views import blinker

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^documentacion/$',views.documentacion, name='documentacion'),
    url(r'^documentacion/$',views.documentacion, name='documentacion'),
    url(r'^documentacion/descargar_protocolo/$',views.descargar_protocolo, name='descargar_protocolo'),
    url(r'^lista_protocolos/$',views.lista_protocolos, name='lista_protocolos'),
    url(r'^lista_protocolos/subir_protocolo/$',views.subir_protocolo, name="subir_protocolo"),
    url(r'^lista_protocolos/subir_toma_datos/$',views.subir_toma_datos, name="subir_toma_datos"),
    url(r'^lista_protocolos/ver/(?P<int_id>\d+)/0/$',views.verProtocolo, name='verProtocolo'),
    url(r'^lista_protocolos/play/(?P<protocolo_id>\w+)/(?P<sec_id>\d+)/$',views.reproducirSecuencia, name='reproducirSecuencia'),
    url(r'^lista_usuarios_toma/(?P<toma_id>\d+)/$',views.lista_usuarios_toma, name='lista_usuarios_toma'),
    url(r'^intentos_usuario/(?P<usr_id>\d+)/$',views.intentos_usuario, name='intentos_usuario'),
    url(r'^ver_botones_intento/(?P<intento_id>\d+)/$',views.ver_botones_intento, name='ver_botones_intento'),
        #url(r'^lista_secuencias/play/(?P<intervencion_id>\w+)/(?P<sec_id>\d+)/$',views.reproducirSecuencia, name='reproducirSecuencia'),
    url(r'^usuario_nuevo/$', views.usuario_nuevo, name='usuario_nuevo'),
    url(r'^usuario/(?P<pk>[0-9]+)/$', views.usuario_ver, name='usuario_ver'),
    url(r'^usuario/(?P<pk>[0-9]+)/edit/$', views.usuario_editar, name='usuario_editar'),
    url(r'^usuario_lista/$', views.usuario_lista, name='usuario_lista'),
    url(r'^agregar_usuario/$', views.agregar_usuario, name='agregar_usuario'),
    url(r'^$',views.inicio),
    url(r'^inicio/$',views.inicio),
    url(r'^ledblink/$',blinker),
    url(r'^rgbTest/$',views.rgbTest,name='rgbTest'),
    url(r'^select_toma_datos/$',views.select_toma_datos,name='select_toma_datos'),
    url(r'^select_toma_datos/select_usr/$',views.select_usr,name='select_usr'),
    url(r'^select_toma_datos/(?P<tomaId>\d+)-(?P<order>\w+)/$',views.ordenar_toma_datos,name='ordenar_toma_datos'),  
    url(r'^jugar/play/$',views.jugarReproducirSec, name='jugarReproducirSec'),
    url(r'^select_toma_datos/select_usr/play_wait_sec/$',views.playWaitSec, name='playWaitSec'),
    url(r'^select_toma_datos/select_usr/ver/$',views.verSecuJugada, name='verSecuJugada'),
    url(r'^jugar/play_wait_sec/ver/(?P<sec_id>\w+)/(?P<usr_id>\w+)/(?P<idIntento>\w+)/(?P<protocolo_id>\w+)/(?P<pid>\w+)/$',views.verSecuJugada, name='verSecuJugada'),
    #url(r'^lista_secuencias/play$',views.reproducirSecuencia),
    url(r'^export_csv/$', views.export_csv, name='export_csv'),
    url(r'^export_csv_extendido/$', views.export_csv_extendido, name='export_csv_extendido'),    
    url(r'^uploadFile/$',views.uploadFile, name='uploadFile'),
    url(r'^select_toma_datos/select_usr/play_wait_sec/checkRedButtonFin/$',views.checkRedButtonFin),
    url(r'^select_toma_datos/select_usr/ver/checkRedButtonInicio/$',views.checkRedButtonInicio),
]

#if settings.DEBUG:
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
