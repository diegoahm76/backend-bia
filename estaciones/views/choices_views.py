from rest_framework.views import APIView
from rest_framework.response import Response

from estaciones.choices.variable_climatica_choices import variable_climatica_CHOICES
from estaciones.choices.estaciones_choices import cod_tipo_estacion_choices

class VariableClimatica(APIView):
    def get(self,request):
        choices = variable_climatica_CHOICES
        return Response(choices)
    
class CodigoEstaciones(APIView):
    def get(self,request):
        choices = cod_tipo_estacion_choices
        return Response(choices)