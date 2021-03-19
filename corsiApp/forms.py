from django import forms
from django.forms import ModelForm, ClearableFileInput

from corsiApp.models import Usuario
from corsiApp.models import DocumentoProtocolo
from corsiApp.models import DocumentoTomaDeDatos


class UsuarioForm(forms.ModelForm):

	class Meta:
		model = Usuario
		fields = ('nombre',)

 
class DocumentoProtocoloForm(forms.ModelForm):
    class Meta:
        model = DocumentoProtocolo
        fields = ('documento',)

class DocumentoTomaDeDatosForm(forms.ModelForm):
    class Meta:
        model = DocumentoTomaDeDatos
        fields = ('protocolo','documento',)