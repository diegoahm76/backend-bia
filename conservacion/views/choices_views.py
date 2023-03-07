from rest_framework.views import APIView
from rest_framework.response import Response

from conservacion.choices.tipo_vivero_choices import tipo_vivero_CHOICES
from conservacion.choices.origen_recursos_vivero_choices import origen_recursos_vivero_CHOICES
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.choices.tipo_incidencia_choices import tipo_incidencia_CHOICES
from conservacion.choices.estado_aprobacion_choices import estado_aprobacion_CHOICES
from conservacion.choices.tipo_baja_choices import tipo_baja_CHOICES
from conservacion.choices.tipo_bien_choices import tipo_bien_CHOICES




class TipoViveroChoices(APIView):
    def get(self,request):
        choices = tipo_vivero_CHOICES
        return Response(choices)

class OrigenRecursosViveroChoices(APIView):
    def get(self,request):
        choices = origen_recursos_vivero_CHOICES
        return Response(choices)
    
class CodEtapaLoteChoices(APIView):
    def get(self,request):
        choices = cod_etapa_lote_CHOICES
        return Response(choices)
    
class TipoIncidencia(APIView):
    def get(self,request):
        choices = tipo_incidencia_CHOICES
        return Response(choices)
    
class EstadoAprobacion(APIView):
    def get(self,request):
        choices = estado_aprobacion_CHOICES
        return Response(choices)

class TipoBien(APIView):
    def get(self,request):
        choices = tipo_bien_CHOICES
        return Response(choices)

class TipoBaja(APIView):
    def get(self,request):
        choices = tipo_baja_CHOICES
        return Response(choices)