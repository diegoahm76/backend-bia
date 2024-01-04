from gestion_documental.choices.central_digitalizacion_choices import ESTADO_SOLICITUD_CHOICES, TIPO_SOLICITUD_CHOICES
from gestion_documental.choices.estado_asignacion_choices import ESTADO_ASIGNACION_CHOICES
from gestion_documental.choices.estado_solicitud_choices import ESTADO_SOLICITUD_TAREA_CHOICES
from gestion_documental.choices.rango_edad_choices import RANGO_EDAD_LIST
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES
from gestion_documental.choices.tipo_zonas_choices import TIPO_ZONAS_CHOICES
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
from gestion_documental.choices.pqrsdf_choices import TIPO_SOLICITUD_PQRSDF, cond_tipos_pqr_list
from gestion_documental.choices.tipo_dato_alojar_choices import tipo_dato_alojar_CHOICES
from gestion_documental.choices.tipo_acceso_choices import tipo_acceso_list
from gestion_documental.choices.tipo_elemento_choices import tipo_elemento_CHOICES
from gestion_documental.choices.cod_nivel_consecutivo_choices import cod_nivel_consecutivo_CHOICES
from gestion_documental.choices.tipo_consulta_pqrsdf_choices import tipo_consulta_pqrsdf_CHOICES
from gestion_documental.choices.tipo_representacion_pqrsdf_choices import tipo_representacion_pqrsdf_CHOICES
from gestion_documental.choices.estado_pqrsdf_choices import estado_pqrsdf_CHOICES
from gestion_documental.choices.pqrsdf_choices import (FORMA_PRESENTACION)
from gestion_documental.choices.medio_almacenamiento_choices import medio_almacenamiento_CHOICES
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.choices.origen_archivo_choices import origen_archivo_CHOICES
from gestion_documental.choices.codigo_relacion_titular_choices import cod_relacion_persona_titular_CHOICES
from gestion_documental.choices.codigo_forma_presentacion_choices import cod_forma_presentacion_CHOICES

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestion_documental.choices.tipos_tareas_choices import TIPOS_TAREA_CHOICES
from gestion_documental.choices.tipos_transferencia_choices import TIPOS_TRANSFERENCIA
from gestion_documental.choices.pqrsdf_choices import TIPOS_PQR


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
    
class FormaPresentacionPQRSDF(APIView):
    def get(self, request):
        choices = FORMA_PRESENTACION
        return Response(choices)
    
class MediosDeAlmacenamiento(APIView):
    def get(self, request):
        choices = medio_almacenamiento_CHOICES
        return Response(choices)
    
class TipoArchivosChoices(APIView):
    def get(self, request):
        choices = tipo_archivo_CHOICES
        return Response(choices)

class OrigenArchivoChoices(APIView):
    def get(self, request):
        choices = origen_archivo_CHOICES
        return Response(choices)

class TipoZonasChoices(APIView):
    def get(self, request):
        choices = TIPO_ZONAS_CHOICES
        return Response(choices)
    
class TipoSolicitud(APIView):
    def get(self, request):
        choices = TIPO_SOLICITUD_CHOICES
        return Response(choices)

class EstadoSolicitud(APIView):
    def get(self, request):
        choices = ESTADO_SOLICITUD_CHOICES
        return Response(choices)
class CodRelacionPersonaTitularChoices(APIView):
    def get(self, request):
        choices = cod_relacion_persona_titular_CHOICES
        return Response(choices)
    
class CodFormaPresentacion(APIView):
    def get(self, request):
        choices = cod_forma_presentacion_CHOICES
        return Response(choices)
    
#BANDEJA DE TAREAS
class TipoTarea(APIView):
    def get(self, request):
        choices = TIPOS_TAREA_CHOICES
        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)
       
    
class EstadoAsignacionTarea(APIView):
    def get(self, request):
        choices = ESTADO_ASIGNACION_CHOICES 

        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)
#ESTADO_SOLICITUD_CHOICES
class EstadoSolicitudTarea(APIView):
    def get(self, request):
        choices = ESTADO_SOLICITUD_TAREA_CHOICES 

        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)
class TiposTransferencias(APIView):
    def get(self, request):
        choices = TIPOS_TRANSFERENCIA 

        return Response({'success': True, 'detail':'Se encontraron los siguientes registros', 'data':choices}, status=status.HTTP_200_OK)
    
#TIPO_PQRSDF
class TipoPqrsdf(APIView):
    def get(self, request):
        choices = TIPOS_PQR
        return Response(choices)
    
#TIPO_SOLICITUD_PQRSDF
class TipoSolicitudPQRSDF(APIView):
    def get(self, request):
        choices = TIPO_SOLICITUD_PQRSDF
        return Response(choices)
    
