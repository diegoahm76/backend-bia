from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from gestion_documental.choices.permisos_gd_choices import permisos_gd_CHOICES
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST
from gestion_documental.choices.tipo_expediente_choices import tipo_expediente_CHOICES
from gestion_documental.choices.estado_expediente_choices import estado_expediente_CHOICES
from gestion_documental.choices.etapa_actual_expediente_choices import etapa_actual_expediente_CHOICES
from gestion_documental.choices.categoria_archivo_choices import categoria_archivo_CHOICES
from gestion_documental.choices.tipo_origen_doc_choices import tipo_origen_doc_CHOICES
from gestion_documental.choices.tipo_subsistema_creado_choices import tipo_subsistema_creado_CHOICES
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from gestion_documental.choices.operacion_realizada_choices import operacion_realizada_CHOICES







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

class TipoExpediente(APIView):
    def get(self,request):
        choices = tipo_expediente_CHOICES
        return Response(choices)
    
class EstadoExpediente(APIView):
    def get(self,request):
        choices = estado_expediente_CHOICES
        return Response(choices)

class EtapaActualExpediente(APIView):
    def get(self,request):
        choices = etapa_actual_expediente_CHOICES
        return Response(choices)

class CategoriaArchivo(APIView):
    def get(self,request):
        choices = categoria_archivo_CHOICES
        return Response(choices)
    
class TipoOrigenDoc(APIView):
    def get(self,request):
        choices = tipo_origen_doc_CHOICES
        return Response(choices)
    
class TipoSubsistemaCreado(APIView):
    def get(self,request):
        choices = tipo_subsistema_creado_CHOICES
        return Response(choices)
    
class TipoRadicado(APIView):
    def get(self,request):
        choices = TIPOS_RADICADO_CHOICES
        return Response(choices)
    
class OperacionRealizada(APIView):
    def get(self,request):
        choices = operacion_realizada_CHOICES
        return Response(choices)