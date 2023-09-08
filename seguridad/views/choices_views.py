from seguridad.choices.subsistemas_choices import subsistemas_CHOICES
from seguridad.choices.cod_permiso_choices import cod_permiso_CHOICES
from seguridad.choices.opciones_usuario_choices import opciones_usuario_CHOICES
from seguridad.choices.tipo_usuario_choices import tipo_usuario_CHOICES
from transversal.choices.direcciones_choices import direcciones_CHOICES
from seguridad.choices.clase_tercero_choices import clase_tercero_CHOICES
from rest_framework.views import APIView
from rest_framework.response import Response

class SubsistemasChoices(APIView):
    def get(self,request):
        choices = subsistemas_CHOICES
        return Response(choices)

class CodPermisoChoices(APIView):
    def get(self,request):
        choices = cod_permiso_CHOICES
        return Response(choices)
    
class OpcionesUsuarioChoices(APIView):
    def get(self,request):
        choices = opciones_usuario_CHOICES
        return Response(choices)
    
class TipoUsuarioChoices(APIView):
    def get(self,request):
        choices = tipo_usuario_CHOICES
        return Response(choices)
    
class DireccionesChoices(APIView):
    def get(self,request):
        choices = direcciones_CHOICES
        return Response(choices)
    
class ClaseTerceroChoices(APIView):
    def get(self,request):
        choices = clase_tercero_CHOICES
        return Response(choices)