from gestion_documental.choices.rango_edad_choices import RANGO_EDAD_LIST
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from gestion_documental.choices.tipos_medios_doc_choices import tipos_medios_doc_CHOICES
from gestion_documental.choices.disposicion_final_series_choices import disposicion_final_series_CHOICES
from gestion_documental.choices.permisos_gd_choices import permisos_gd_CHOICES
from gestion_documental.choices.estructura_tipos_expediente_choices import tipo_expediente_LIST
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST
from gestion_documental.choices.tipo_expediente_choices import tipo_expediente_CHOICES
from gestion_documental.choices.estado_expediente_choices import estado_expediente_CHOICES
from gestion_documental.choices.etapa_actual_expediente_choices import etapa_actual_expediente_CHOICES
from gestion_documental.choices.categoria_archivo_choices import categoria_archivo_CHOICES
from gestion_documental.choices.tipo_origen_doc_choices import tipo_origen_doc_CHOICES
from gestion_documental.choices.tipo_subsistema_creado_choices import tipo_subsistema_creado_CHOICES
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from gestion_documental.choices.operacion_realizada_choices import operacion_realizada_CHOICES
from gestion_documental.choices.pqrsdf_choices import cond_tipos_pqr_list
from gestion_documental.choices.tipo_dato_alojar_choices import tipo_dato_alojar_CHOICES
from gestion_documental.choices.tipo_acceso_choices import tipo_acceso_list
from gestion_documental.choices.tipo_elemento_choices import tipo_elemento_CHOICES
from gestion_documental.choices.cod_nivel_consecutivo_choices import cod_nivel_consecutivo_CHOICES
from gestion_documental.choices.tipo_consulta_pqrsdf_choices import tipo_consulta_pqrsdf_CHOICES
from gestion_documental.choices.tipo_representacion_pqrsdf_choices import tipo_representacion_pqrsdf_CHOICES
from gestion_documental.choices.estado_pqrsdf_choices import estado_pqrsdf_CHOICES

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
class GetCod_tipo_PQR(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los perfiles del sistema son los siguientes', 'data':cond_tipos_pqr_list }, status=status.HTTP_200_OK) 

class GetEstruc_tipo_exp(APIView):
    def get(self, request):
        return Response({'success':True, 
                         'detail':'Las estructuras de los tipos de expediente  son los siguientes',
                          'data':tipo_expediente_LIST },
                            status=status.HTTP_200_OK) 
#tipo_expediente_LIST

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
    
class TipoElemento(APIView):
    def get(self,request):
        choices = tipo_elemento_CHOICES
        return Response(choices)
    
class TipoDatoAlojar(APIView):
    def get(self,request):
        choices = tipo_dato_alojar_CHOICES
        return Response(choices)   
    
class TipoAcceso(APIView):
    def get(self,request):
        choices = tipo_acceso_list
        return Response(choices)   
    
class RangoEdad(APIView):
    def get(self,request):
        choices = RANGO_EDAD_LIST
        return Response(choices)  
    
class CodNivelConsecutivo(APIView):
    def get(self,request):
        choices = cod_nivel_consecutivo_CHOICES
        return Response(choices) 
#RANGO_EDAD_LIST

class TipoConsultaPQRSDF(APIView):
    def get(self, request):
        choices = tipo_consulta_pqrsdf_CHOICES
        return Response(choices)
    
class TipoRepresentacionPQRSDF(APIView):
    def get(self, request):
        choices = tipo_representacion_pqrsdf_CHOICES
        return Response(choices)

class EstadoPQRSDF(APIView):
    def get(self, request):
        choices = estado_pqrsdf_CHOICES
        return Response(choices)