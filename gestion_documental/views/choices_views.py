from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from rest_framework.views import APIView
from rest_framework.response import Response

class TipoClasificacion(APIView):
    def get(self,request):
        choices = tipo_clasificacion_CHOICES
        return Response(choices)

class TiposMediosDoc(APIView):
    def get(self,request):
        choices = tipos_medios_doc_CHOICES
        return Response(choices)

class DisposicionFinalSeries(APIView):
    def get(self,request):
        choices = disposicion_final_series_CHOICES
        return Response(choices)