from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from gestion_documental.choices.permisos_gd_choices import permisos_gd_CHOICES
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

# class PermisosGD(APIView):
#     def get(self,request):
#         choices = permisos_gd_CHOICES
#         return Response(choices)
class GetCodConsecutivo(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los perfiles del sistema son los siguientes', 'data': cod_tipos_radicados_LIST}, status=status.HTTP_200_OK) 
