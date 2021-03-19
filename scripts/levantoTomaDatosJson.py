import json
from distutils.util import strtobool

from corsiApp.models import Protocolo, TomaDeDatos, Usuario, DocumentoTomaDeDatos, Intento

ultimoDocumentoIngresado = DocumentoTomaDeDatos.objects.latest('id')
idProtocolo = ultimoDocumentoIngresado.protocolo.id

protocoloObj = Protocolo.objects.get(id = idProtocolo)

json_data=open("/home/pi/djangoProjects/scripts/archivosSubidos/tomaDeDatos.json").read()
experiment = json.loads(json_data)

nombreTomaDeDatos = experiment['tomaDeDatos']['nombreTomaDeDatos']

usuarios = experiment['usuarios']["nombres"]
cantUsuarios = len(usuarios)


#Chequeo si pasaron el mismo numero y protocolo en el formulario, ya que necesito que los nombres sean consistentes en la views
yaIngresado = TomaDeDatos.objects.filter(idProtocolo = protocoloObj, nombreTomaDeDatos = nombreTomaDeDatos)

#Genero un objeto TomaDeDatos que esta asociado al protocolo con igual nombre al que estoy levantando 
tomaDeDatos = TomaDeDatos(idProtocolo = protocoloObj, nombreTomaDeDatos = nombreTomaDeDatos)
tomaDeDatos.save()
listaUsuarios = []

#Por cada usuario voy a generar un intento vacio. Por una cuestión de visualizacion en template select_toma_datos

for usr in usuarios:
	u = Usuario(idTomaDeDatos = tomaDeDatos, nombre = usr)
	listaUsuarios.append(u)

Usuario.objects.bulk_create(listaUsuarios)

#Elimino de la base el documento ingresado
ultimoDocumentoIngresado.delete()