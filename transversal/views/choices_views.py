from transversal.choices.agrupacion_documental_choices import agrupacion_documental_CHOICES
from transversal.choices.tipo_unidad_choices import tipo_unidad_CHOICES

from rest_framework.views import APIView
from rest_framework.response import Response

class TipoUnidadChoices(APIView):
    def get(self,request):
        choices = tipo_unidad_CHOICES
        return Response(choices)

class AgrupacionDocumentalChoices(APIView):
    def get(self,request):
        choices = agrupacion_documental_CHOICES
        return Response(choices)