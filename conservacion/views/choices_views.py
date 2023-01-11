from rest_framework.views import APIView
from rest_framework.response import Response

from conservacion.choices.tipo_vivero_choices import tipo_vivero_CHOICES
from conservacion.choices.origen_recursos_vivero_choices import origen_recursos_vivero_CHOICES
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES

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