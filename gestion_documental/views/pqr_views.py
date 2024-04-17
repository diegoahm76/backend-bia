
import ast
import copy
from datetime import datetime, timedelta, timezone
import json
import os
import subprocess
from transversal.models.entidades_models import SucursalesEmpresas
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, fields, Count, Func,DateTimeField
from django.forms import model_to_dict
from django.db.models import Value as V
from django.db.models import IntegerField
from django.db.models.functions import Now, ExtractDay
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import  AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer
from gestion_documental.views.conf__tipos_exp_views import ConfiguracionTipoExpedienteAgnoGetConsect
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, FormatosTiposMedio, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.models.expedientes_models import ArchivosDigitales , DocumentosDeArchivoExpediente, ConcesionesAccesoAExpsYDocs, ExpedientesDocumentales,IndicesElectronicosExp,Docs_IndiceElectronicoExp, InventarioDocumental
from gestion_documental.models.bandeja_tareas_models import TareasAsignadas, ReasignacionesTareas
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionPQR, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MediosSolicitud, MetadatosAnexosTmp, RespuestaPQR, T262Radicados, TiposPQR, modulos_radican
from rest_framework.response import Response
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.serializers.pqr_serializers import AnexoRespuestaPQRSerializer, MediosSolicitudSerializer, PersonaSerializer, SucursalesEmpresasSerializer,UnidadOrganizacionalSerializer, AnexoSerializer, AnexosPQRSDFPostSerializer, AnexosPQRSDFSerializer, AnexosPostSerializer, AnexosPutSerializer, AnexosSerializer, ArchivosSerializer, EstadosSolicitudesSerializer, InfoDenunciasPQRSDFPostSerializer, InfoDenunciasPQRSDFPutSerializer, InfoDenunciasPQRSDFSerializer, MediosSolicitudCreateSerializer, MediosSolicitudDeleteSerializer, MediosSolicitudSearchSerializer, MediosSolicitudUpdateSerializer, MetadatosPostSerializer, MetadatosPutSerializer, MetadatosSerializer, PQRSDFGetSerializer, PQRSDFPanelSerializer, PQRSDFPostSerializer, PQRSDFPutSerializer, PQRSDFSerializer, PersonasSerializer, RadicadoPostSerializer, RespuestaPQRSDFPanelSerializer, RespuestaPQRSDFPostSerializer, TiposPQRGetSerializer, TiposPQRUpdateSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate, Estados_PQRDelete
from django.core.exceptions import ObjectDoesNotExist
from seguridad.utils import Util
########################################################################
import imaplib
import email
import os
from email.header import decode_header
import base64
import hashlib
from rest_framework.pagination import PageNumberPagination
from rest_framework import status as drf_status
# import magic
########################################################################

from django.db.models import Q
from django.db import transaction
from transversal.models.personas_models import Personas
from transversal.serializers.personas_serializers import PersonasFilterSerializer
from transversal.views.alertas_views import AlertasProgramadasCreate
class TiposPQRGet(generics.ListAPIView):
    serializer_class = TiposPQRGetSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

        instance=TiposPQR.objects.filter(cod_tipo_pqr=pk)
        if not instance:
            raise NotFound("No existen tipos de radicado")
        
        serializer = self.serializer_class(instance, many=True)

                         
        return Response({'succes':True, 'detail':'Se encontró los siguientes registross','data':serializer.data}, status=status.HTTP_200_OK)


class TiposPQRUpdate(generics.UpdateAPIView):
    serializer_class = TiposPQRUpdateSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:    
            data = request.data
            instance = TiposPQR.objects.filter(cod_tipo_pqr=pk).first()
            
            if not instance:
                raise NotFound("No se existe un tipo de radicado con este codigo.")
            
            instance_previous=copy.copy(instance)
            serializer = self.serializer_class(instance,data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            #AUDITORIA 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"Nombre":instance.nombre}
            valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 153,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    

class GetPQRSDFForStatus(generics.ListAPIView):
    serializer_class = PQRSDFSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_persona_titular):
        pqrsdf = self.queryset.filter(Q(id_persona_titular = id_persona_titular) & 
                                      Q(Q(id_radicado = 0) | Q(id_radicado = None) | Q(~Q(id_radicado=0) & Q(requiere_rta = True) & Q(fecha_rta_final_gestion = None))))
        if pqrsdf:
            serializador = self.serializer_class(pqrsdf, many = True)
            return Response({'success':True, 'detail':'Se encontraron PQRSDF asociadas al titular','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No se encontraron PQRSDF asociadas al titular'},status=status.HTTP_200_OK) 


class GetPQRSDFForPanel(generics.RetrieveAPIView):
    serializer_class = PQRSDFPanelSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_PQRSDF):
        try:
            data_pqrsdf = self.queryset.filter(id_PQRSDF = id_PQRSDF).first()
            
            if data_pqrsdf:
                serializador = self.serializer_class(data_pqrsdf, many = False)
                return Response({'success':True, 'detail':'Se encontro el PQRSDF por el id consultado','data':serializador.data},status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No Se encontro el PQRSDF por el id consultado'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PQRSDFCreate(generics.CreateAPIView):
    serializer_class = PQRSDFPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data_pqrsdf = json.loads(request.data.get('pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))
                id_persona_guarda = ast.literal_eval(request.data.get('id_persona_guarda', ''))

                debe_radicar = isCreateForWeb and data_pqrsdf['es_anonima']
                denuncia = data_pqrsdf['denuncia']
                fecha_actual = datetime.now()
                valores_creados_detalles = []

                util_PQR = Util_PQR()
                anexos = util_PQR.set_archivo_in_anexo(data_pqrsdf['anexos'], request.FILES, "create")

                #Crea el pqrsdf
                data_PQRSDF_creado = self.create_pqrsdf(data_pqrsdf, fecha_actual)

                #Guarda el nuevo estado Guardado en la tabla T255
                historicoEstadosCreate = HistoricoEstadosCreate()
                historicoEstadosCreate.create_historico_estado(data_PQRSDF_creado, 'GUARDADO', id_persona_guarda, fecha_actual)
                
                #Crea la denuncia si el tipo del PQRSDF es de tipo Denuncia
                if(data_PQRSDF_creado['cod_tipo_PQRSDF'] == "D"):
                    denunciasCreate = DenunciasCreate()
                    denunciasCreate.crear_denuncia(denuncia, data_PQRSDF_creado['id_PQRSDF'])

                #Guarda los anexos en la tabla T258 y la relación entre los anexos y el PQRSDF en la tabla T259 si tiene anexos
                if anexos:
                    anexosCreate = AnexosCreate()
                    valores_creados_detalles = anexosCreate.create_anexos_pqrsdf(anexos, data_PQRSDF_creado['id_PQRSDF'], None, isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    if update_requiere_digitalizacion:
                        data_PQRSDF_creado = self.update_requiereDigitalizacion_pqrsdf(data_PQRSDF_creado)

                #Auditoria
                descripcion_auditoria = self.set_descripcion_auditoria(data_PQRSDF_creado)
                self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles)

                #Si tiene que radicar, crea el radicado
                if debe_radicar:
                    radicarPQRSDF = RadicarPQRSDF()
                    data_radicado = radicarPQRSDF.radicar_pqrsdf(request, data_PQRSDF_creado['id_PQRSDF'], id_persona_guarda, isCreateForWeb)
                    data_PQRSDF_creado = data_radicado['pqrsdf']
                
                return Response({'success':True, 'detail':'Se creo el PQRSDF correctamente', 'data':data_PQRSDF_creado}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def create_pqrsdf(self, data, fecha_actual):
        data_pqrsdf = self.set_data_pqrsdf(data, fecha_actual)
        serializer = self.serializer_class(data=data_pqrsdf)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
    
    def update_requiereDigitalizacion_pqrsdf(self, data_PQRSDF_creado):
        PrsdfUpdate = PQRSDFUpdate()
        pqr_instance = PQRSDF.objects.filter(id_PQRSDF = data_PQRSDF_creado['id_PQRSDF']).first()
        data_pqrsdf_update = copy.deepcopy(data_PQRSDF_creado)
        data_pqrsdf_update['requiere_digitalizacion'] = False
        pqrsdf_update = PrsdfUpdate.update_pqrsdf(pqr_instance, data_pqrsdf_update)
        return pqrsdf_update

    def set_data_pqrsdf(self, data, fecha_actual):
        data['fecha_registro'] = data['fecha_ini_estado_actual'] = fecha_actual
        data['requiere_digitalizacion'] = True if data['cantidad_anexos'] != 0 else False
    
        estado = EstadosSolicitudes.objects.filter(nombre='GUARDADO').first()
        data['id_estado_actual_solicitud'] = estado.id_estado_solicitud
    
        return data

    def set_descripcion_auditoria(self, pqrsdf):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf['cod_tipo_PQRSDF']).first()

        persona = Personas.objects.filter(id_persona = pqrsdf['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = pqrsdf['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(pqrsdf['fecha_registro']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC' if isCreateForWeb else 'CR',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)


class PQRSDFUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = PQRSDFPostSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                #Obtiene los datos enviado en el request
                pqrsdf = json.loads(request.data.get('pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))

                pqrsdf_db = self.queryset.filter(id_PQRSDF=pqrsdf['id_PQRSDF']).first()
                if pqrsdf_db:
                    denuncia = pqrsdf['denuncia']
                    anexos = pqrsdf['anexos']
                    fecha_actual = datetime.now()

                    #Actualiza la denuncia en caso de que la tenga
                    self.procesa_denuncia(denuncia, pqrsdf_db.cod_tipo_PQRSDF, pqrsdf['cod_tipo_PQRSDF'], pqrsdf['id_PQRSDF'])

                    #Actualiza los anexos y los metadatos
                    data_auditoria_anexos = self.procesa_anexos(anexos, request.FILES, pqrsdf['id_PQRSDF'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    pqrsdf['requiere_digitalizacion'] = False if update_requiere_digitalizacion else True
                    
                    #Actuaiza pqrsdf
                    pqrsdf_update = self.update_pqrsdf(pqrsdf_db, pqrsdf)

                    #Auditoria
                    descripcion_auditoria = self.set_descripcion_auditoria(pqrsdf_update)
                    self.auditoria(request, descripcion_auditoria, isCreateForWeb, data_auditoria_anexos)
                    
                    return Response({'success':True, 'detail':'Se editó el PQRSDF correctamente', 'data': pqrsdf_update}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'No se encontró el PQRSDF para actualizar'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update_pqrsdf(self, pqrsdf_db, pqrsdf_update):
        try:
            serializer = self.serializer_class(pqrsdf_db, data=pqrsdf_update)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data
        except Exception as e:
            raise ValidationError(str(e))
    
    def procesa_denuncia(self, denuncia, cod_tipo_PQRSDF_DB, cod_tipo_PQRSDF, id_PQRSDF):
        if cod_tipo_PQRSDF_DB == 'D' and cod_tipo_PQRSDF == 'D':
            denunciasUpdate = DenunciasUpdate()
            denunciasUpdate.put(denuncia)

        elif cod_tipo_PQRSDF_DB == 'D' and not cod_tipo_PQRSDF == 'D':
            denunciasDelete = DenunciasDelete()
            denunciasDelete.delete(id_PQRSDF)

        elif denuncia and not cod_tipo_PQRSDF_DB == 'D' and cod_tipo_PQRSDF == 'D':
            denunciasCreate = DenunciasCreate()
            denunciasCreate.crear_denuncia(denuncia, id_PQRSDF)

    def procesa_anexos(self, anexos, archivos, id_PQRSDF, isCreateForWeb, fecha_actual):
        data_auditoria_create = []
        data_auditoria_update = []
        data_auditoria_delete = []

        anexos = [] if not anexos else anexos
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        anexos_pqr_DB = Anexos_PQR.objects.filter(id_PQRSDF = id_PQRSDF)
        if anexos_pqr_DB:
            util_PQR = Util_PQR()
            data_anexos_create = [anexo for anexo in anexos if anexo['id_anexo'] == None]
            anexos_create = util_PQR.set_archivo_in_anexo(data_anexos_create, archivos, "create")
            
            data_anexos_update = [anexo for anexo in anexos if not anexo['id_anexo'] == None]
            anexos_update = util_PQR.set_archivo_in_anexo(data_anexos_update, archivos, "update")

            ids_anexos_update = [anexo_update['id_anexo'] for anexo_update in anexos_update]
            anexos_delete = [anexo_pqr for anexo_pqr in anexos_pqr_DB if getattr(anexo_pqr,'id_anexo_id') not in ids_anexos_update]

            anexosCreate = AnexosCreate()
            anexosUpdate = AnexosUpdate()
            anexosDelete = AnexosDelete()

            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos_create, id_PQRSDF, None, isCreateForWeb, fecha_actual)
            data_auditoria_update = anexosUpdate.put(anexos_update, fecha_actual)
            data_auditoria_delete = anexosDelete.delete(anexos_delete)
            
        else:
            anexosCreate = AnexosCreate()
            util_PQR = Util_PQR()
            anexos_create = util_PQR.set_archivo_in_anexo(anexos, archivos, "create")
            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos_create, id_PQRSDF, None, isCreateForWeb, fecha_actual)

        return {
            'data_auditoria_create': data_auditoria_create,
            'data_auditoria_update': data_auditoria_update,
            'data_auditoria_delete': data_auditoria_delete
        }
    
    def set_descripcion_auditoria(self, pqrsdf):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf['cod_tipo_PQRSDF']).first()

        persona = Personas.objects.filter(id_persona = pqrsdf['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = pqrsdf['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(pqrsdf['fecha_registro']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_detalles['data_auditoria_update'],
            "valores_creados_detalles": valores_detalles['data_auditoria_create'],
            "valores_eliminados_detalles": valores_detalles['data_auditoria_delete']
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
class PQRSDFDelete(generics.RetrieveDestroyAPIView):
    serializer_class = PQRSDFSerializer
    borrar_estados = Estados_PQRDelete
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        try:
            with transaction.atomic():
                #Parametros para eliminacion
                if request.query_params.get('id_PQRSDF')==None or request.query_params.get('isCreateForWeb')==None:
                    raise ValidationError('No se ingresaron parámetros necesarios para eliminar el PQRSDF')
                id_PQRSDF = int(request.query_params.get('id_PQRSDF', 0))
                isCreateForWeb = ast.literal_eval(request.query_params.get('isCreateForWeb', False))

                valores_eliminados_detalles = []
                pqrsdf_delete = self.queryset.filter(id_PQRSDF = id_PQRSDF).first()
                if pqrsdf_delete:
                    if not pqrsdf_delete.id_radicado:
                        #Elimina los anexos, anexos_pqr, metadatos y el archivo adjunto
                        anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = id_PQRSDF)
                        if anexos_pqr:
                            anexosDelete = AnexosDelete()
                            valores_eliminados_detalles = anexosDelete.delete(anexos_pqr)

                        #Elimina el estado creado en el historico
                        self.borrar_estados.delete(self, id_PQRSDF)
                        #Elimina la denuncia en caso de que se tenga una denuncia asociada al pqrsdf
                        denunciasDelete = DenunciasDelete()
                        denunciasDelete.delete(id_PQRSDF)
                        #Elimina el pqrsdf
                        pqrsdf_delete.delete()
                        #Auditoria
                        descripcion_auditoria = self.set_descripcion_auditoria(pqrsdf_delete)
                        self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_eliminados_detalles)

                        return Response({'success':True, 'detail':'El PQRSDF ha sido descartado'}, status=status.HTTP_200_OK)
                    else:
                        raise NotFound('No se permite borrar pqrsdf ya radicados')
                else:
                    raise NotFound('No se encontró ningún pqrsdf con estos parámetros')
            
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def set_descripcion_auditoria(self, pqrsdf):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf.cod_tipo_PQRSDF).first()

        persona = Personas.objects.filter(id_persona = pqrsdf.id_persona_titular_id).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = pqrsdf.id_medio_solicitud_id).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(pqrsdf.fecha_registro),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data
    
    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_eliminados_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'BO',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data) 

        
########################## Historico Estados ##########################
class HistoricoEstadosCreate(generics.CreateAPIView):
    creador_estados = Estados_PQRCreate()

    def create_historico_estado(self, data_PQRSDF, nombre_estado, id_persona_guarda, fecha_actual):
        data_estado_crear = self.set_data_estado(data_PQRSDF, nombre_estado, id_persona_guarda, fecha_actual)
        self.creador_estados.crear_estado(data_estado_crear)

    def set_data_estado(self, data_PQRSDF, nombre_estado, id_persona_guarda, fecha_actual):
        data_estado = {}
        data_estado['PQRSDF'] = data_PQRSDF['id_PQRSDF']
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['persona_genera_estado'] = None if id_persona_guarda == 0 else id_persona_guarda

        estado = EstadosSolicitudes.objects.filter(nombre=nombre_estado).first()
        data_estado['estado_solicitud'] = estado.id_estado_solicitud

        return data_estado

########################## RADICADOS ##########################
class RadicarPQRSDF(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                id_PQRSDF = request.data['id_PQRSDF']
                id_persona_guarda = request.data['id_persona_guarda']
                isCreateForWeb = request.data['isCreateForWeb']
                data_radicado_pqrsdf = self.radicar_pqrsdf(request, id_PQRSDF, id_persona_guarda, isCreateForWeb)
                return Response({'success':True, 'detail':'Se creo el radicado para el PQRSDF', 'data': data_radicado_pqrsdf['radicado']}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def radicar_pqrsdf(self, request, id_PQRSDF, id_persona_guarda, isCreateForWeb):
        fecha_actual = datetime.now()
        data_PQRSDF_instance = PQRSDF.objects.filter(id_PQRSDF = id_PQRSDF).first()
        previous_instance = copy.copy(data_PQRSDF_instance)
        crear_alerta=AlertasProgramadasCreate()
        #Obtiene los dias para la respuesta del PQRSDF
        tipo_pqr = self.get_tipos_pqr(data_PQRSDF_instance.cod_tipo_PQRSDF)
        dias_respuesta = tipo_pqr.tiempo_respuesta_en_dias
        
        #Crea el radicado
        data_for_create = {}
        data_for_create['fecha_actual'] = fecha_actual
        data_for_create['id_persona'] = id_persona_guarda
        data_for_create['tipo_radicado'] = "E"
        data_for_create['modulo_radica'] = "PQRSDF"
        radicadoCreate = RadicadoCreate()
        data_radicado = radicadoCreate.post(data_for_create)
        data_radicado['asunto'] = data_PQRSDF_instance.asunto
        data_radicado['persona_titular'] = self.set_titular(data_PQRSDF_instance.id_persona_titular_id)

        #Actualiza el estado y la data del radicado al PQRSDF
        PrsdfUpdate = PQRSDFUpdate()
        pqrsdf_dic = model_to_dict(data_PQRSDF_instance)
        data_update_pqrsdf = self.set_data_update_radicado_pqrsdf(pqrsdf_dic, data_radicado, dias_respuesta, fecha_actual)
        data_PQRSDF_creado = PrsdfUpdate.update_pqrsdf(data_PQRSDF_instance, data_update_pqrsdf)

        #Guarda el nuevo estado Radicado en la tabla T255
        historicoEstadosCreate = HistoricoEstadosCreate()
        historicoEstadosCreate.create_historico_estado(data_PQRSDF_creado, 'RADICADO', id_persona_guarda, fecha_actual)

        #Auditoria
        descripciones = self.set_descripcion_auditoria(previous_instance, data_PQRSDF_instance)
        self.auditoria(request, descripciones['descripcion'], isCreateForWeb, descripciones['data_auditoria_update'])
        
        #CRECIACON DE ALERTA
        print("TIEMPO DE RESPUESTA")
        print(data_PQRSDF_instance.dias_para_respuesta)
        cadena = ""
        # if data_PQRSDF_instance.id_radicado:
        #     instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=data_PQRSDF_instance.id_radicado.agno_radicado,cod_tipo_radicado=data_PQRSDF_instance.id_radicado.cod_tipo_radicado).first()
        #     numero_con_ceros = str(data_PQRSDF_instance.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        #     cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
    
       
        fecha_respuesta = fecha_actual + timedelta(days=data_PQRSDF_instance.dias_para_respuesta)
        print(fecha_respuesta)
        data_alerta = {
            'cod_clase_alerta':'Gest_TRPqr',
            'dia_cumplimiento':fecha_respuesta.day,
            'mes_cumplimiento':fecha_respuesta.month,
            'age_cumplimiento':fecha_respuesta.year,
            #'complemento_mensaje':mensaje,
            'id_elemento_implicado':data_PQRSDF_instance.id_PQRSDF,
            #'id_persona_implicada':persona.id_persona,
            "tiene_implicado":False
            }
        
        response_alerta=crear_alerta.crear_alerta_programada(data_alerta)
        if response_alerta.status_code!=status.HTTP_201_CREATED:
            return response_alerta

        #raise ValidationError(data_PQRSDF_instance.dias_para_respuesta)

        return {
            'radicado': data_radicado,
            'pqrsdf': data_PQRSDF_creado
        }
    
    def get_tipos_pqr(self, cod_tipo_PQRSDF):
        tipo_pqr = TiposPQR.objects.filter(cod_tipo_pqr=cod_tipo_PQRSDF).first()
        if tipo_pqr.tiempo_respuesta_en_dias == None:
            raise ValidationError("No se encuentra configurado el numero de dias para la respuesta. La entidad debe configurar todos los días de respuesta para todas las PQRSDF para realizar el proceso creación.")
        return tipo_pqr
    
    def set_data_update_radicado_pqrsdf(self, pqrsdf, data_radicado, dias_respuesta, fecha_actual):
        pqrsdf['id_radicado'] = data_radicado['id_radicado']
        pqrsdf['fecha_radicado'] = data_radicado['fecha_radicado']
        pqrsdf['dias_para_respuesta'] = dias_respuesta

        estado = EstadosSolicitudes.objects.filter(nombre='RADICADO').first()
        pqrsdf['id_estado_actual_solicitud'] = estado.id_estado_solicitud
        pqrsdf['fecha_ini_estado_actual'] = fecha_actual

        return pqrsdf
    
    def set_titular(self, id_persona):
        persona = Personas.objects.filter(id_persona = id_persona).first()
        nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo
    
    def set_descripcion_auditoria(self, previous_pqrsdf, pqrsdf_update):
        descripcion_auditoria_update = {
            'IdRadicado': previous_pqrsdf.id_radicado,
            'FechaRadicado': previous_pqrsdf.fecha_radicado
        }

        data_auditoria_update = {'previous':previous_pqrsdf, 'current':pqrsdf_update}

        data = {
            'descripcion': descripcion_auditoria_update,
            'data_auditoria_update': data_auditoria_update
        }

        return data

    def auditoria(self, request, descripcion, isCreateForWeb, valores_actualizados):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 171 if isCreateForWeb else 162,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

class RadicadoCreate(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    config_radicados = ConfigTiposRadicadoAgnoGenerarN
    
    def post(self, data_radicado):
        try:
            config_tipos_radicado = self.get_config_tipos_radicado(data_radicado)
            radicado_data = self.set_data_radicado(config_tipos_radicado, data_radicado['fecha_actual'], data_radicado['id_persona'], data_radicado['modulo_radica'])
            serializer = self.serializer_class(data=radicado_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer_data = serializer.data
            serializer_data['radicado_nuevo'] = config_tipos_radicado['radicado_nuevo']
            return serializer_data

        except Exception as e:
            raise ValidationError(str(e))


    def get_config_tipos_radicado(self, request):
        data_request = {
            'id_persona': request['id_persona'],
            'cod_tipo_radicado': request['tipo_radicado'],
            'fecha_actual': request['fecha_actual']
        }
        config_tipos_radicados = self.config_radicados.generar_n_radicado(self, data_request)
        config_tipos_radicado_data = config_tipos_radicados.data['data']
        if config_tipos_radicado_data['implementar'] == False:
            raise ValidationError("El sistema requiere que se maneje un radicado de entrada o unico, debe solicitar al administrador del sistema la configuración del radicado")
        else:
            return config_tipos_radicado_data
        
    def set_data_radicado(self, config_tipos_radicado, fecha_actual, id_persona, modulo_radica):
        radicado = {}
        radicado['cod_tipo_radicado'] = config_tipos_radicado['cod_tipo_radicado']
        radicado['prefijo_radicado'] = config_tipos_radicado['prefijo_consecutivo']
        radicado['agno_radicado'] = config_tipos_radicado['agno_radicado']
        radicado['nro_radicado'] = config_tipos_radicado['consecutivo_actual']
        radicado['fecha_radicado'] = fecha_actual
        radicado['id_persona_radica'] = id_persona

        modulo_radica = modulos_radican.objects.filter(nombre=modulo_radica).first()
        radicado['id_modulo_que_radica'] = modulo_radica.id_ModuloQueRadica

        return radicado


########################## DENUNCIAS ##########################
class DenunciasCreate(generics.CreateAPIView):
    serializer_class = InfoDenunciasPQRSDFPostSerializer

    def crear_denuncia(self, data_denuncia, id_PQRSDF):
        try:
            data_denuncia['id_PQRSDF'] = id_PQRSDF
            serializer = self.serializer_class(data=data_denuncia)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
          raise ValidationError(str(e))
        
class DenunciasUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = InfoDenunciasPQRSDFPutSerializer
    queryset = InfoDenuncias_PQRSDF.objects.all()

    def put(self, data_denuncia):
        try:
            denuncia_db = self.queryset.filter(id_info_denuncia_PQRSDF = data_denuncia['id_info_denuncia_PQRSDF']).first()
            if denuncia_db:
                serializer = self.serializer_class(denuncia_db, data=data_denuncia)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return serializer.data
            else:
                raise ValidationError("No se encuentra la denuncia que intenta actualziar")

        except Exception as e:
            raise ValidationError(str(e))   


class DenunciasDelete(generics.RetrieveAPIView):
    serializer_class = InfoDenunciasPQRSDFSerializer
    queryset = InfoDenuncias_PQRSDF.objects.all()

    def delete(self, id_PQRSDF):
        try:
            denuncia = self.queryset.filter(id_PQRSDF = id_PQRSDF).first()
            if denuncia:
                denuncia.delete()
            return True
        except Exception as e:
            raise ValidationError(str(e))



########################## ANEXOS Y ANEXOS PQR ##########################
class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer
    
    def create_anexos_pqrsdf(self, anexos, id_PQRSDF, id_complemento_PQRSDF, isCreateForWeb, fecha_actual):
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        nombres_anexos_auditoria = []
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        for anexo in anexos:
            data_anexo = self.crear_anexo(anexo)

            #Crea la relacion en la tabla T259
            data_anexos_PQR = {}
            data_anexos_PQR['id_PQRSDF'] = id_PQRSDF
            data_anexos_PQR['id_complemento_usu_PQR'] = id_complemento_PQRSDF
            data_anexos_PQR['id_anexo'] = data_anexo['id_anexo']
            anexosPQRCreate = AnexosPQRCreate()
            anexosPQRCreate.crear_anexo_pqr(data_anexos_PQR)

            #Guardar el archivo en la tabla T238
            if anexo['archivo']:
                archivo_creado = self.crear_archivos(anexo['archivo'], fecha_actual)
            else:
                raise ValidationError("No se puede crear anexos sin archivo adjunto")

            #Crea los metadatos del archivo cargado
            data_metadatos = {}
            data_metadatos['metadatos'] = anexo['metadatos']
            data_metadatos['anexo'] = data_anexo
            data_metadatos['isCreateForWeb'] = isCreateForWeb
            data_metadatos['fecha_registro'] = fecha_actual
            data_metadatos['id_archivo_digital'] = archivo_creado.data.get('data').get('id_archivo_digital')
            metadatosPQRCreate = MetadatosPQRCreate()
            metadatosPQRCreate.create_metadatos_pqr(data_metadatos)

            nombres_anexos_auditoria.append({'NombreAnexo': anexo['nombre_anexo']})
        return nombres_anexos_auditoria

    def crear_anexo(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))

    def crear_archivos(self, uploaded_file, fecha_creacion):
        #Valida extensión del archivo
        nombre=uploaded_file.name
            
        extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1][1:] if extension[1].startswith('.') else extension
        if not extension_sin_punto:
            raise ValidationError("No fue posible registrar el archivo")
        
        formatos=FormatosTiposMedio.objects.filter(nombre__iexact=extension_sin_punto,activo=True).first()
        if not formatos:
            raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")

        # Obtiene el año actual para determinar la carpeta de destino
        current_year = fecha_creacion.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", "Anexos_PQR", str(current_year))

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': False,
            'ruta': ruta,
        }
        
        archivos_Digitales = ArchivosDgitalesCreate()
        archivo_creado = archivos_Digitales.crear_archivo(data_archivo, uploaded_file)
        return archivo_creado
    
class AnexosUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = AnexosPutSerializer
    queryset = Anexos.objects.all()

    def put(self, anexos, fecha_actual):
        try:
            nombres_anexos_auditoria = []
            for anexo in anexos:
                anexo_update_db = self.queryset.filter(id_anexo = anexo['id_anexo']).first()
                if anexo_update_db:
                    previous_instancia = copy.copy(anexo_update_db)
                    self.update_anexo(anexo_update_db, anexo)

                    #Actualiza metadatos
                    archivo_editar = anexo['archivo'] if 'archivo' in anexo else None
                    metadatosPQRUpdate = MetadatosPQRUpdate()
                    metadatosPQRUpdate.put(anexo.get('metadatos'), archivo_editar, fecha_actual)

                    descripcion_auditoria = {'NombreAnexo': anexo['nombre_anexo']}
                    nombres_anexos_auditoria.append({'descripcion': descripcion_auditoria, 'previous':previous_instancia, 'current':anexo_update_db})
                    
                else:
                    raise ValidationError("No se encontro el anexo que intenta actualizar")
            return nombres_anexos_auditoria

        except Exception as e:
            raise ValidationError(str(e))
        
    def update_anexo(self, anexo_db, anexo_update):
        serializer = self.serializer_class(anexo_db, data=anexo_update, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
    
class AnexosDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosSerializer
    queryset = Anexos.objects.all()

    @transaction.atomic
    def delete(self, anexos_pqr):
        try:
            nombres_anexos_auditoria = []
            for anexo_pqr in anexos_pqr:
                anexo_delete = self.queryset.filter(id_anexo = anexo_pqr.id_anexo_id).first()
                if anexo_delete:
                    metadatosPQRDelete = MetadatosPQRDelete()
                    anexosPQRDelete = AnexosPQRDelete()
                    metadatosPQRDelete.delete(anexo_delete.id_anexo)
                    anexosPQRDelete.delete(anexo_pqr.id_anexo_PQR)
                    anexo_delete.delete()

                    nombres_anexos_auditoria.append({'NombreAnexo': anexo_delete.nombre_anexo})
                else:
                    raise NotFound('No se encontró ningún anexo con estos parámetros')
            return nombres_anexos_auditoria
            
        except Exception as e:
            raise ValidationError(str(e))

class AnexosPQRCreate(generics.CreateAPIView):
    serializer_class = AnexosPQRSDFPostSerializer
    
    def crear_anexo_pqr(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))
        
class AnexosPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosPQRSDFSerializer
    queryset = Anexos_PQR.objects.all()

    @transaction.atomic
    def delete(self, id_anexo_PQR):
        anexoPqr = self.queryset.filter(id_anexo_PQR = id_anexo_PQR).first()
        if anexoPqr:
            anexoPqr.delete()
            return True
        else:
            raise NotFound('No se encontró ningún anexo pqr asociado al anexo')

########################## METADATOS Y DELETE ARCHIVO ##########################   
class MetadatosPQRCreate(generics.CreateAPIView):
    serializer_class = MetadatosPostSerializer

    def create_metadatos_pqr(self, data_metadatos):
        try:
            data_to_create = self.set_data_metadato(data_metadatos)
            serializer = self.serializer_class(data=data_to_create)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))
        
    def set_data_metadato(self, data_metadatos):
        metadato = {}
        anexo = data_metadatos['anexo']
        data_metadato = {} if not data_metadatos['metadatos'] else data_metadatos['metadatos']

        if data_metadatos['isCreateForWeb']:
            metadato['id_anexo'] = anexo['id_anexo']
            metadato['fecha_creacion_doc'] = data_metadatos['fecha_registro'].date()
            metadato['cod_origen_archivo'] = "E"
            metadato['es_version_original'] = True
            metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']
        else:
            data_metadato['id_anexo'] = anexo['id_anexo']
            data_metadato['fecha_creacion_doc'] = data_metadatos['fecha_registro'].date()
            data_metadato['nro_folios_documento'] = anexo['numero_folios']
            data_metadato['es_version_original'] = True
            data_metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']
            metadato = data_metadato
        
        return metadato
    
class MetadatosPQRUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = MetadatosPutSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    def put(self, metadato_update, archivo, fecha_actual):
        try:
            metadato_db = self.queryset.filter(id_metadatos_anexo_tmp = metadato_update['id_metadatos_anexo_tmp']).first()
            if metadato_db:
                #Si se tiene archivo se borra el actual y se crea el archivo enviado y se asocia al metadato
                if archivo:
                    archivo_actualizado = self.actualizar_archivo(archivo, fecha_actual, metadato_update['id_archivo_sistema'])
                    metadato_update['id_archivo_sistema'] = archivo_actualizado.data.get('data').get('id_archivo_digital')

                serializer = self.serializer_class(metadato_db, data=metadato_update, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return serializer.data
            else:
                raise NotFound('No se encontró el metadato que intenta actualizar')
                
        except Exception as e:
            raise ValidationError(str(e))
    
    def actualizar_archivo(self, archivo, fecha_actual, id_archivo_anterior):
        #Borra archivo anterior del metadato
        archivoDelete = ArchivoDelete()
        archivoDelete.delete(id_archivo_anterior)

        #Crea el nuevo archivo
        archivo_creado = AnexosCreate.crear_archivos(self, archivo, fecha_actual)
        return archivo_creado

class MetadatosPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = MetadatosSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    def delete(self, id_anexo):
        try:
            metadato = self.queryset.filter(id_anexo = id_anexo).first()
            if metadato:
                archivoDelete = ArchivoDelete()
                archivoDelete.delete(metadato.id_archivo_sistema_id)
                metadato.delete()
                return True
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros')
        except Exception as e:
          raise ValidationError(str(e))
        
class ArchivoDelete(generics.RetrieveDestroyAPIView):
    serializer_class = ArchivosSerializer
    queryset = ArchivosDigitales.objects.all()

    def delete(self, id_archivo_digital):
        try:
            archivo = self.queryset.filter(id_archivo_digital = id_archivo_digital).first()
            if archivo:
                archivo.delete()
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros') 
        except Exception as e:
          raise ValidationError(str(e))

############################## UTILS ###########################################################
class Util_PQR:
    # Funcion trasversal para update
    @staticmethod
    def reemplazar_objetos(objeto_existente, nuevo_objeto):
        for propiedad, valor in nuevo_objeto.items():
            if propiedad in list(vars(objeto_existente).keys()):
                setattr(objeto_existente, propiedad, valor)
        return objeto_existente
    
    @staticmethod
    def set_archivo_in_anexo(anexos, archivos, proceso):
        if anexos != None and archivos != None:
            nombre_archivo_proceso = "archivo-" + proceso
            archivos_filter = [
                {"nombre archivo": nombre, "archivo":archivo} for nombre, archivo in archivos.items() if nombre_archivo_proceso in nombre
            ]
            if len(anexos)!= len(archivos_filter) and proceso == "create":
                raise ValidationError("Se debe tener la misma cantidad de archivos y anexos.")
            
            for anexo in anexos:
                nombre_archivo_completo = nombre_archivo_proceso + "-" + anexo['nombre_anexo']
                archivo_filter = [archivo["archivo"] for archivo in archivos_filter if archivo['nombre archivo'] == nombre_archivo_completo]
                if archivo_filter:
                    anexo['archivo'] = archivo_filter[0]
        return anexos
    
       

 ########################## MEDIOS DE SOLICITUD ##########################


#CREAR_MEDIOS_SOLICITUD
class MediosSolicitudCreate(generics.CreateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudCreateSerializer
    permission_classes = [IsAuthenticated]


#BUSCAR_MEDIOS_SOLICITUD
class MediosSolicitudSearch(generics.ListAPIView):
    serializer_class = MediosSolicitudSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_medio_solicitud = self.request.query_params.get('nombre_medio_solicitud', '').strip()
        aplica_para_pqrsdf = self.request.query_params.get('aplica_para_pqrsdf', '').strip()
        aplica_para_tramites = self.request.query_params.get('aplica_para_tramites', '').strip()
        aplica_para_otros = self.request.query_params.get('aplica_para_otros', '').strip()
        activo = self.request.query_params.get('activo', '').strip()

        medios_solicitud = MediosSolicitud.objects.all()

        if nombre_medio_solicitud:
            medios_solicitud = medios_solicitud.filter(nombre__icontains=nombre_medio_solicitud)

        
        if aplica_para_pqrsdf:
            medios_solicitud = medios_solicitud.filter(aplica_para_pqrsdf__icontains=aplica_para_pqrsdf)


        if aplica_para_tramites:
            medios_solicitud = medios_solicitud.filter(aplica_para_tramites__icontains=aplica_para_tramites)

        if aplica_para_otros:
            medios_solicitud = medios_solicitud.filter(descripcion__icontains=aplica_para_otros)

    
        if activo:
            medios_solicitud = medios_solicitud.filter(activo__icontains=activo)
            

        medios_solicitud = medios_solicitud.order_by('id_medio_solicitud')  # Ordenar aquí

        return medios_solicitud

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron medios de solicitud que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes medios de solicitud.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
#BORRAR_MEDIO_SOLICITUD
class MediosSolicitudDelete(generics.DestroyAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudDeleteSerializer 
    lookup_field = 'id_medio_solicitud'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque está precargado (Registro_Precargado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque ya ha sido usado (ItemYaUsado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar el medio de solicitud
        instance.delete()

        return Response({'success': True,"detail": "El medio de solicitud se eliminó con éxito."}, status=status.HTTP_200_OK)
    
#ACTUALIZAR_MEDIO_SOLICITUD
class MediosSolicitudUpdate(generics.UpdateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudUpdateSerializer  
    lookup_field = 'id_medio_solicitud'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False, "detail": "No puedes actualizar este medio de solicitud porque está precargado.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            # Comprobar si 'nombre' está presente en los datos de solicitud
            if 'nombre' in request.data:
                return Response({'success': False, "detail": "No puedes actualizar el campo 'nombre' en este medio de solicitud.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

            # Permitir actualizar otros campos
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Si T253itemYaUsado es FALSE, permitir la actualización completa del medio de solicitud
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

################################################### RESPUESTA A UNA SOLICITUD PQRSDF ###################################################################
    
class RespuestaPQRSDFCreate(generics.CreateAPIView):
    serializer_class = RespuestaPQRSDFPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data_respuesta_pqrsdf = json.loads(request.data.get('respuesta_pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))
                user = request.user

                persona = user.persona

                fecha_actual = datetime.now()
                id_persona_responde = persona
                valores_creados_detalles = []

                if not 'id_tarea_asignada' in data_respuesta_pqrsdf:
                    raise ValidationError('El campo "id_tarea_asignada" es obligatorio.')
                
                
                #Validacion 116
                id_tarea = int(data_respuesta_pqrsdf['id_tarea_asignada'])
               
                tarea = TareasAsignadas.objects.filter(id_tarea_asignada=id_tarea).first()
                if not tarea:
                    raise ValidationError('No se encontró la tarea asignada con el ID especificado.')
              
                

                util_respuesta_PQR = Util_Respuesta_PQR()
                anexos = util_respuesta_PQR.set_archivo_in_anexo(data_respuesta_pqrsdf['anexos'], request.FILES, "create")
                
                # Verificar si la PQRSDF ya tiene respuesta
                pqrsdf_id = data_respuesta_pqrsdf['id_pqrsdf']
                respuesta_existente = RespuestaPQR.objects.filter(id_pqrsdf=pqrsdf_id).exists()

                if respuesta_existente:
                    # Si ya hay una respuesta, retornar un mensaje indicando que la PQRSDF ya tiene respuesta
                    return Response({'success': False, 'detail': 'Esta PQRSDF ya tiene una respuesta generada.'}, status=status.HTTP_400_BAD_REQUEST)

                # Crea la respuesta pqrsdf si no hay respuesta existente
                data_respuesta_PQRSDF_creado = self.create_respuesta_pqrsdf(data_respuesta_pqrsdf, fecha_actual, id_persona_responde)

                # Guarda los anexos en la tabla T258 y la relación entre los anexos y el PQRSDF en la tabla T259 si tiene anexos
                if anexos:
                    anexosCreate = AnexosRespuestaCreate()
                    valores_creados_detalles = anexosCreate.create_anexos_respuesta_pqrsdf(anexos, data_respuesta_PQRSDF_creado['id_respuesta_pqr'], isCreateForWeb, fecha_actual, id_persona_responde)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    if update_requiere_digitalizacion:
                        data_respuesta_PQRSDF_creado = self.update_requiereDigitalizacion_pqrsdf(data_respuesta_PQRSDF_creado)

                # # Auditoria
                # descripcion_auditoria = self.set_descripcion_auditoria(data_respuesta_PQRSDF_creado)
                # self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles)
                        
                ##VALIDACION 116

                ##NOMBRE DE LA PERSONA QUE RESPONDE
                
                nombre_completo_responde = None
                nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                                persona.primer_apellido, persona.segundo_apellido]
                nombre_completo_responde = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_responde = nombre_completo_responde if nombre_completo_responde != "" else None
                nombre_persona = nombre_completo_responde

                tarea.cod_estado_solicitud = 'Re'
                tarea.fecha_respondido =data_respuesta_PQRSDF_creado['fecha_respuesta'] #fecha_respuesta
                tarea.nombre_persona_que_responde = nombre_persona
                tarea.save()
                #SI LA TAREA FUE FRUTO DE UNA REASIGNACION 
                if tarea.id_tarea_asignada_padre_inmediata:
                    tarea_padre = tarea.id_tarea_asignada_padre_inmediata

                    # Iterar a través de las tareas padres hasta encontrar la tarea original
                    while tarea_padre and not tarea_padre.id_asignacion:
                        tarea_padre.fecha_respondido = data_respuesta_PQRSDF_creado['fecha_respuesta']
                        tarea_padre.nombre_persona_que_responde = nombre_persona
                        tarea_padre.ya_respondido_por_un_delegado = True
                        tarea_padre.save()

                        # Ir a la siguiente tarea padre
                        tarea_padre = tarea_padre.id_tarea_asignada_padre_inmediata

                    # Si se encontró la tarea original, actualizarla
                    if tarea_padre:
                        tarea_padre.fecha_respondido = data_respuesta_PQRSDF_creado['fecha_respuesta']
                        tarea_padre.nombre_persona_que_responde = nombre_persona
                        tarea_padre.ya_respondido_por_un_delegado = True
                        tarea_padre.save()
                return Response({'success': True, 'detail': 'Se creó el PQRSDF correctamente', 'data': data_respuesta_PQRSDF_creado}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def create_respuesta_pqrsdf(self, data, fecha_actual, id_persona_responde):
        data_respuesta_pqrsdf = self.set_data_pqrsdf(data, fecha_actual)
        data_respuesta_pqrsdf['id_persona_responde'] = id_persona_responde.id_persona
        serializer = self.serializer_class(data=data_respuesta_pqrsdf)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def update_requiereDigitalizacion_pqrsdf(self, data_respuesta_PQRSDF_creado):
        PrsdfUpdate = RespuestaPQRSDFUpdate()
        pqr_respuesta_instance = RespuestaPQR.objects.filter(id_respuesta_pqr=data_respuesta_PQRSDF_creado['id_respuesta_pqr']).first()
        data_respuesta_pqrsdf_update = copy.deepcopy(data_respuesta_PQRSDF_creado)
        data_respuesta_pqrsdf_update['requiere_digitalizacion'] = False
        pqrsdf_update = PrsdfUpdate.update_respuesta_pqrsdf(pqr_respuesta_instance, data_respuesta_pqrsdf_update)
        return pqrsdf_update

    def set_data_pqrsdf(self, data, fecha_actual):
        data['fecha_respuesta'] = data['fecha_ini_estado_actual'] = fecha_actual
        data['requiere_digitalizacion'] = True if data['cantidad_anexos'] != 0 else False
        return data

    def set_descripcion_auditoria(self, pqrsdf):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf['cod_tipo_PQRSDF']).first()
        persona = Personas.objects.filter(id_persona=pqrsdf['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']
        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud=pqrsdf['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(pqrsdf['fecha_respuesta']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC' if isCreateForWeb else 'CR',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

class RespuestaPQRSDFUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = RespuestaPQRSDFPostSerializer
    queryset = RespuestaPQR.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                #Obtiene los datos enviado en el request
                respuesta_pqrsdf = json.loads(request.data.get('respuesta_pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))

                pqrsdf_db = self.queryset.filter(id_respuesta_pqr=respuesta_pqrsdf['id_respuesta_pqr']).first()
                if pqrsdf_db:
                    anexos = respuesta_pqrsdf['anexos']
                    fecha_actual = datetime.now()


                    #Actualiza los anexos y los metadatos
                    data_auditoria_anexos = self.procesa_anexos(anexos, request.FILES, respuesta_pqrsdf['id_respuesta_pqr'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    RespuestaPQRSDFPostSerializer['requiere_digitalizacion'] = False if update_requiere_digitalizacion else True
                    
                    #Actuaiza pqrsdf
                    pqrsdf_update = self.update_respuesta_pqrsdf(pqrsdf_db, respuesta_pqrsdf)

                    #Auditoria
                    descripcion_auditoria = self.set_descripcion_auditoria(pqrsdf_update)
                    self.auditoria(request, descripcion_auditoria, isCreateForWeb, data_auditoria_anexos)
                    
                    return Response({'success':True, 'detail':'Se editó el PQRSDF correctamente', 'data': pqrsdf_update}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'No se encontró el PQRSDF para actualizar'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update_respuesta_pqrsdf(self, pqrsdf_db, pqrsdf_update):
        try:
            serializer = self.serializer_class(pqrsdf_db, data=pqrsdf_update)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data
        except Exception as e:
            raise ValidationError(str(e))
    

    def procesa_anexos(self, anexos, archivos, id_respuesta_PQR, isCreateForWeb, fecha_actual):
        data_auditoria_create = []
        data_auditoria_update = []
        data_auditoria_delete = []

        anexos = [] if not anexos else anexos
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        anexos_pqr_DB = Anexos_PQR.objects.filter(id_respuesta_PQR = id_respuesta_PQR)
        if anexos_pqr_DB:
            util_respuesta_PQR = Util_Respuesta_PQR()
            data_anexos_create = [anexo for anexo in anexos if anexo['id_anexo'] == None]
            anexos_create = util_respuesta_PQR.set_archivo_in_anexo(data_anexos_create, archivos, "create")
            
            data_anexos_update = [anexo for anexo in anexos if not anexo['id_anexo'] == None]
            anexos_update = util_respuesta_PQR.set_archivo_in_anexo(data_anexos_update, archivos, "update")

            ids_anexos_update = [anexo_update['id_anexo'] for anexo_update in anexos_update]
            anexos_delete = [anexo_pqr for anexo_pqr in anexos_pqr_DB if getattr(anexo_pqr,'id_anexo_id') not in ids_anexos_update]

            anexosCreate = AnexosRespuestaCreate()
            anexosUpdate = AnexosRespuestaUpdate()
            anexosDelete = AnexosRespuestaDelete()

            data_auditoria_create = anexosCreate.create_anexos_respuesta_pqrsdf(anexos_create, id_respuesta_PQR, None, isCreateForWeb, fecha_actual)
            data_auditoria_update = anexosUpdate.put(anexos_update, fecha_actual)
            data_auditoria_delete = anexosDelete.delete(anexos_delete)
            
        else:
            anexosCreate = AnexosRespuestaCreate()
            util_respuesta_PQR = Util_Respuesta_PQR()
            anexos_create = util_respuesta_PQR.set_archivo_in_anexo(anexos, archivos, "create")
            data_auditoria_create = anexosCreate.create_anexos_respuesta_pqrsdf(anexos_create, id_respuesta_PQR, None, isCreateForWeb, fecha_actual)

        return {
            'data_auditoria_create': data_auditoria_create,
            'data_auditoria_update': data_auditoria_update,
            'data_auditoria_delete': data_auditoria_delete
        }
    
    def set_descripcion_auditoria(self, pqrsdf):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf['cod_tipo_PQRSDF']).first()

        persona = Personas.objects.filter(id_persona = pqrsdf['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = pqrsdf['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(pqrsdf['fecha_respuesta']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_detalles['data_auditoria_update'],
            "valores_creados_detalles": valores_detalles['data_auditoria_create'],
            "valores_eliminados_detalles": valores_detalles['data_auditoria_delete']
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

########################## ANEXOS Y ANEXOS PQR RESPUESTAS ##########################
class AnexosRespuestaCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer
    
    def create_anexos_respuesta_pqrsdf(self, anexos, id_respuesta_pqr, isCreateForWeb, fecha_actual, id_persona_responde ):
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        nombres_anexos_auditoria = []
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        for anexo in anexos:
            data_anexo = self.crear_anexo(anexo)

            #Crea la relacion en la tabla T259
            data_anexos_Respuesta_PQR = {}
            data_anexos_Respuesta_PQR['id_respuesta_PQR'] = id_respuesta_pqr
            data_anexos_Respuesta_PQR['id_anexo'] = data_anexo['id_anexo']
            anexosRespuestaPQRCreate = AnexosRespuestaPQRCreate()
            anexosRespuestaPQRCreate.crear_anexo_respuesta_pqr(data_anexos_Respuesta_PQR)

            #Guardar el archivo en la tabla T238
            if anexo['archivo']:
                archivo_creado = self.crear_archivos(anexo['archivo'], fecha_actual)
            else:
                raise ValidationError("No se puede crear anexos sin archivo adjunto")

            #Crea los metadatos del archivo cargado
            data_metadatos = {}
            data_metadatos['metadatos'] = anexo['metadatos']
            data_metadatos['anexo'] = data_anexo
            data_metadatos['isCreateForWeb'] = isCreateForWeb
            data_metadatos['fecha_respuesta'] = fecha_actual
            data_metadatos['id_archivo_digital'] = archivo_creado.data.get('data').get('id_archivo_digital')
            metadatosRespuestaPQRCreate = MetadatosRespuestaPQRCreate()
            metadatosRespuestaPQRCreate.create_metadatos_respuesta_pqr(data_metadatos)

            nombres_anexos_auditoria.append({'NombreAnexo': anexo['nombre_anexo']})
        return nombres_anexos_auditoria

    def crear_anexo(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise ValidationError(str(e))

    def crear_archivos(self, uploaded_file, fecha_creacion):
        #Valida extensión del archivo
        nombre=uploaded_file.name
            
        extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1][1:] if extension[1].startswith('.') else extension
        if not extension_sin_punto:
            raise ValidationError("No fue posible registrar el archivo")
        
        formatos=FormatosTiposMedio.objects.filter(nombre=extension_sin_punto,activo=True).first()
        if not formatos:
            raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")

        # Obtiene el año actual para determinar la carpeta de destino
        current_year = fecha_creacion.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", "Anexos_PQR", str(current_year))

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': False,
            'ruta': ruta,
        }
        
        archivos_Digitales = ArchivosDgitalesCreate()
        archivo_creado = archivos_Digitales.crear_archivo(data_archivo, uploaded_file)
        return archivo_creado
    
class AnexosRespuestaUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = AnexosPutSerializer
    queryset = Anexos.objects.all()

    def put(self, anexos, fecha_actual):
        try:
            nombres_anexos_auditoria = []
            for anexo in anexos:
                anexo_update_db = self.queryset.filter(id_anexo = anexo['id_anexo']).first()
                if anexo_update_db:
                    previous_instancia = copy.copy(anexo_update_db)
                    self.update_anexo(anexo_update_db, anexo)

                    #Actualiza metadatos
                    archivo_editar = anexo['archivo'] if 'archivo' in anexo else None
                    metadatosRespuestaPQRUpdate = MetadatosRespuestaPQRUpdate()
                    metadatosRespuestaPQRUpdate.put(anexo.get('metadatos'), archivo_editar, fecha_actual)

                    descripcion_auditoria = {'NombreAnexo': anexo['nombre_anexo']}
                    nombres_anexos_auditoria.append({'descripcion': descripcion_auditoria, 'previous':previous_instancia, 'current':anexo_update_db})
                    
                else:
                    raise ValidationError("No se encontro el anexo que intenta actualizar")
            return nombres_anexos_auditoria

        except Exception as e:
            raise ValidationError(str(e))
        
    def update_anexo(self, anexo_db, anexo_update):
        serializer = self.serializer_class(anexo_db, data=anexo_update, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
    
class AnexosRespuestaDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosSerializer
    queryset = Anexos.objects.all()

    @transaction.atomic
    def delete(self, anexos_pqr):
        try:
            nombres_anexos_auditoria = []
            for anexo_pqr in anexos_pqr:
                anexo_delete = self.queryset.filter(id_anexo = anexo_pqr.id_anexo_id).first()
                if anexo_delete:
                    metadatosPQRDelete = MetadatosRespuestaPQRDelete()
                    anexosPQRDelete = AnexosRespuestaPQRDelete()
                    metadatosPQRDelete.delete(anexo_delete.id_anexo)
                    anexosPQRDelete.delete(anexo_pqr.id_anexo_PQR)
                    anexo_delete.delete()

                    nombres_anexos_auditoria.append({'NombreAnexo': anexo_delete.nombre_anexo})
                else:
                    raise NotFound('No se encontró ningún anexo con estos parámetros')
            return nombres_anexos_auditoria
            
        except Exception as e:
            raise ValidationError(str(e))

class AnexosRespuestaPQRCreate(generics.CreateAPIView):
    serializer_class = AnexosPQRSDFPostSerializer
    
    def crear_anexo_respuesta_pqr(self, request):
        # try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        # except Exception as e:
        #     raise({'success': False, 'detail': str(e)})
        
class AnexosRespuestaPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosPQRSDFSerializer
    queryset = Anexos_PQR.objects.all()

    @transaction.atomic
    def delete(self, id_anexo_PQR):
        anexoPqr = self.queryset.filter(id_anexo_PQR = id_anexo_PQR).first()
        if anexoPqr:
            anexoPqr.delete()
            return True
        else:
            raise NotFound('No se encontró ningún anexo pqr asociado al anexo')

########################## METADATOS Y DELETE ARCHIVO ##########################   
class MetadatosRespuestaPQRCreate(generics.CreateAPIView):
    serializer_class = MetadatosPostSerializer

    def create_metadatos_respuesta_pqr(self, data_metadatos):
        # try:
            data_to_create = self.set_data_metadato(data_metadatos)
            serializer = self.serializer_class(data=data_to_create)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        # except Exception as e:
        #     raise({'success': False, 'detail': str(e)})
        
    def set_data_metadato(self, data_metadatos):
        metadato = {}
        anexo = data_metadatos['anexo']
        data_metadato = {} if not data_metadatos['metadatos'] else data_metadatos['metadatos']

        if data_metadatos['isCreateForWeb']:
            metadato['id_anexo'] = anexo['id_anexo']
            metadato['fecha_creacion_doc'] = data_metadatos['fecha_respuesta'].date()
            metadato['cod_origen_archivo'] = "E"
            metadato['es_version_original'] = True
            metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']
        else:
            data_metadato['id_anexo'] = anexo['id_anexo']
            data_metadato['fecha_creacion_doc'] = data_metadatos['fecha_respuesta'].date()
            data_metadato['nro_folios_documento'] = anexo['numero_folios']
            data_metadato['es_version_original'] = True
            data_metadato['id_archivo_sistema'] = data_metadatos['id_archivo_digital']
            metadato = data_metadato
        
        return metadato
    
class MetadatosRespuestaPQRUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = MetadatosPutSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    def put(self, metadato_update, archivo, fecha_actual):
        # try:
            metadato_db = self.queryset.filter(id_metadatos_anexo_tmp = metadato_update['id_metadatos_anexo_tmp']).first()
            if metadato_db:
                #Si se tiene archivo se borra el actual y se crea el archivo enviado y se asocia al metadato
                if archivo:
                    archivo_actualizado = self.actualizar_archivo(archivo, fecha_actual, metadato_update['id_archivo_sistema'])
                    metadato_update['id_archivo_sistema'] = archivo_actualizado.data.get('data').get('id_archivo_digital')

                serializer = self.serializer_class(metadato_db, data=metadato_update, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return serializer.data
            else:
                raise NotFound('No se encontró el metadato que intenta actualizar')
                
        # except Exception as e:
        #     raise({'success': False, 'detail': str(e)})
    
    def actualizar_archivo(self, archivo, fecha_actual, id_archivo_anterior):
        #Borra archivo anterior del metadato
        archivoDelete = ArchivoDelete()
        archivoDelete.delete(id_archivo_anterior)

        #Crea el nuevo archivo
        archivo_creado = AnexosCreate.crear_archivos(self, archivo, fecha_actual)
        return archivo_creado

class MetadatosRespuestaPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = MetadatosSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    def delete(self, id_anexo):
        try:
            metadato = self.queryset.filter(id_anexo = id_anexo).first()
            if metadato:
                archivoDelete = ArchivoDelete()
                archivoDelete.delete(metadato.id_archivo_sistema_id)
                metadato.delete()
                return True
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros')
        except Exception as e:
          raise ValidationError(str(e))
        
class ArchivoDelete(generics.RetrieveDestroyAPIView):
    serializer_class = ArchivosSerializer
    queryset = ArchivosDigitales.objects.all()

    def delete(self, id_archivo_digital):
        try:
            archivo = self.queryset.filter(id_archivo_digital = id_archivo_digital).first()
            if archivo:
                archivo.delete()
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros') 
        except Exception as e:
          raise ValidationError(str(e))

############################## UTILS ###########################################################
class Util_Respuesta_PQR:
    # Funcion trasversal para update
    @staticmethod
    def reemplazar_objetos(objeto_existente, nuevo_objeto):
        for propiedad, valor in nuevo_objeto.items():
            if propiedad in list(vars(objeto_existente).keys()):
                setattr(objeto_existente, propiedad, valor)
        return objeto_existente
    
    @staticmethod
    def set_archivo_in_anexo(anexos, archivos, proceso):
        if anexos != None and archivos != None:
            nombre_archivo_proceso = "archivo-" + proceso
            archivos_filter = [
                {"nombre archivo": nombre, "archivo":archivo} for nombre, archivo in archivos.items() if nombre_archivo_proceso in nombre
            ]
            if len(anexos)!= len(archivos_filter) and proceso == "create":
                return Response({"detail": "Se debe tener la misma cantidad de archivos y anexos."}, status=status.HTTP_400_BAD_REQUEST)
                # raise ValidationError("Se debe tener la misma cantidad de archivos y anexos.")
            
            for anexo in anexos:
                nombre_archivo_completo = nombre_archivo_proceso + "-" + anexo['nombre_anexo']
                archivo_filter = [archivo["archivo"] for archivo in archivos_filter if archivo['nombre archivo'] == nombre_archivo_completo]
                if archivo_filter:
                    anexo['archivo'] = archivo_filter[0]
        return anexos
    
# Listar_respuesta_PQRSDF
class GetRespuestaPQRSDFForPanel(generics.RetrieveAPIView):
    serializer_class = RespuestaPQRSDFPanelSerializer
    queryset = RespuestaPQR.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_pqrsdf):
        # try:
            data_pqrsdf = self.queryset.filter(id_pqrsdf = id_pqrsdf).first()
            
            if data_pqrsdf:
                serializador = self.serializer_class(data_pqrsdf, many = False)
                return Response({'success':True, 'detail':'Se encontro La siguiente respuesta a la PQRSDF por el id consultado','data':serializador.data},status=status.HTTP_200_OK)
            else:
                raise NotFound('No Se encontro respuesta a la PQRSDF por el id consultado')
        # except Exception as e:
        #     return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
#REPORTES_PQRSDF
            

def get_tipo_pqrsdf_descripcion(cod_tipo_pqrsdf):
    tipo_mapping = {
        "PG": "Petición General",
        "PD": "Petición De Documentos o Información",
        "PC": "Petición De Consulta",
        "Q": "Queja",
        "R": "Reclamo",
        "S": "Sugerencia",
        "D": "Denuncia",
        "F": "Felicitación",
    }

    return tipo_mapping.get(cod_tipo_pqrsdf, "Tipo Desconocido")
class ReportesPQRSDFSearch(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    def get_tipo_pqrsdf_descripcion(self, cod_tipo_pqrsdf):
        tipo_mapping = {
            "PG": "Petición General",
            "PD": "Petición De Documentos o Información",
            "PC": "Petición De Consulta",
            "Q": "Queja",
            "R": "Reclamo",
            "S": "Sugerencia",
            "D": "Denuncia",
            "F": "Felicitación",
        }

        return tipo_mapping.get(cod_tipo_pqrsdf, "Tipo Desconocido")

    def get_queryset(self):
        estados_pqrsdf = EstadosSolicitudes.objects.filter(
            aplica_para_pqrsdf=True
        ).exclude(nombre__in=[
            'SOLICITUD DE DIGITALIZACION ENVIADA',
            'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
            'SOLICITUD AL USUARIO ENVIADA',
            'SOLICITUD AL USUARIO RESPONDIDA'
        ])

        titular_id = self.request.query_params.get('id_persona_titular')
        titular = get_object_or_404(Personas, id_persona=titular_id) if titular_id else None

        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        id_estado_actual_solicitud = self.request.query_params.get('id_estado_actual_solicitud')
        id_und_org_seccion_asignada = self.request.query_params.get('id_und_org_seccion_asignada')
        tipo_solicitud = self.request.query_params.get('tipo_solicitud')

        queryset = PQRSDF.objects.filter(id_estado_actual_solicitud__in=estados_pqrsdf)

        if titular:
            queryset = queryset.filter(id_persona_titular=titular)

        if fecha_desde:
            queryset = queryset.filter(fecha_registro__gte=fecha_desde)

        if fecha_hasta:
            queryset = queryset.filter(fecha_registro__lte=fecha_hasta)

        if id_estado_actual_solicitud:
            queryset = queryset.filter(id_estado_actual_solicitud=id_estado_actual_solicitud)

        if id_und_org_seccion_asignada:
            queryset = queryset.filter(asignacionpqr__id_und_org_seccion_asignada=id_und_org_seccion_asignada)

        if tipo_solicitud:
            queryset = queryset.filter(cod_tipo_PQRSDF=tipo_solicitud)


        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PQRSDFGetSerializer(queryset, many=True)

        # Modificar el retorno del JSON aquí para incluir la información adicional
        data = []
        for pqrsdf in queryset:
            if pqrsdf.id_radicado:
                try:
                    radicado = T262Radicados.objects.get(id_radicado=pqrsdf.id_radicado.id_radicado)
                    numero_radicado = f'{radicado.prefijo_radicado}-{radicado.agno_radicado}-{radicado.nro_radicado}'
                    fecha_radicado = radicado.fecha_radicado
                except T262Radicados.DoesNotExist:
                    numero_radicado = 'N/A'
                    fecha_radicado = 'N/A'
            else:
                numero_radicado = 'N/A'
                fecha_radicado = 'N/A'

            # Verificar si id_sucursal_recepcion_fisica es None antes de acceder a descripcion_sucursal
            sucursal_recepcion = pqrsdf.id_sucursal_especifica_implicada.descripcion_sucursal if pqrsdf.id_sucursal_especifica_implicada else 'N/A'

            try:
                medio_solicitud_nombre = pqrsdf.id_medio_solicitud.nombre
            except MediosSolicitud.DoesNotExist:
                medio_solicitud_nombre = 'N/A'

            # Obtener el nombre completo de la persona que recibe
            persona_recibe_data = pqrsdf.id_persona_recibe
            if persona_recibe_data:
                nombre_completo = ' '.join(
                    filter(None, [
                        persona_recibe_data.primer_nombre,
                        persona_recibe_data.segundo_nombre,
                        persona_recibe_data.primer_apellido,
                        persona_recibe_data.segundo_apellido,
                    ])
                )
            else:
                nombre_completo = 'N/A'

            data.append({
                'id_pqrsdf': pqrsdf.id_PQRSDF,
                'tipo_pqrsdf': pqrsdf.cod_tipo_PQRSDF,
                'tipo_pqrsdf_descripcion': get_tipo_pqrsdf_descripcion(pqrsdf.cod_tipo_PQRSDF),
                'medio_solicitud': medio_solicitud_nombre,
                'sucursal_recepcion': sucursal_recepcion,
                'numero_radicado': numero_radicado,
                'fecha_radicado': fecha_radicado,
                'persona_recibe': nombre_completo,
                'fecha_solicitud': pqrsdf.fecha_registro
            })

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': data
        }, status=status.HTTP_200_OK)
    

    
class EstadosSolicitudesList(generics.ListAPIView):
    serializer_class = EstadosSolicitudesSerializer

    def get_queryset(self):
        # Filtrar estados por aplicaParaPQRSDF y excluir estados específicos
        excluded_state_names = [
            'SOLICITUD DE DIGITALIZACION ENVIADA',
            'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
            'SOLICITUD AL USUARIO ENVIADA',
            'SOLICITUD AL USUARIO RESPONDIDA',
        ]
        queryset = EstadosSolicitudes.objects.filter(aplica_para_pqrsdf=True).exclude(nombre__in=excluded_state_names)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            raise NotFound('No se encontraron registros que coincidan con los criterios de búsqueda.')

        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


##########################################################################################################################################################################################################
    
#CONSULTA_ESTADO_SOLICITUD_PQRSDF
class ConsultaEstadoPQRSDF(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    permission_classes = [IsAuthenticated]

    def get_tipo_pqrsdf_descripcion(self, cod_tipo_pqrsdf):
        tipo_mapping = {
            "PG": "Petición General",
            "PD": "Petición De Documentos o Información",
            "PC": "Petición De Consulta",
            "Q": "Queja",
            "R": "Reclamo",
            "S": "Sugerencia",
            "D": "Denuncia",
            "F": "Felicitación",
        }

        return tipo_mapping.get(cod_tipo_pqrsdf, "Tipo Desconocido")

    def get_estado_solicitud_nombre(self, id_estado_solicitud, fecha_radicado=None, dias_para_respuesta=None):
        # Verificar si es VENCIDO y ajustar la lógica
        if dias_para_respuesta is not None and fecha_radicado:
            tiempo_respuesta = fecha_radicado + timedelta(days=dias_para_respuesta)
            today = datetime.now()
            
            # Verificar si es VENCIDO
            if today > tiempo_respuesta:
                return 'VENCIDO'

        # Verificar si ya es un objeto de estado o un ID
        if isinstance(id_estado_solicitud, EstadosSolicitudes):
            estado = id_estado_solicitud
        else:
            try:
                estado = EstadosSolicitudes.objects.get(id_estado_solicitud=id_estado_solicitud)
            except EstadosSolicitudes.DoesNotExist:
                return "Estado Desconocido"

        return estado.nombre


    def get_location_info(self, pqrsdf):
        estado_actual = pqrsdf.id_estado_actual_solicitud

        if estado_actual and estado_actual.nombre in ['RADICADO', 'EN VENTANILLA CON PENDIENTES', 'EN VENTANILLA SIN PENDIENTES']:
            return 'EN VENTANILLA'

        elif estado_actual and estado_actual.nombre == 'EN GESTION':
            # Obtener información de la asignación actual
            try:
                asignacion = AsignacionPQR.objects.filter(
                    id_pqrsdf=pqrsdf,
                    cod_estado_asignacion='Ac'
                ).latest('fecha_asignacion')

                # Validar si la asignación ha sido reasignada
                tarea_reasignada = ReasignacionesTareas.objects.filter(
                    id_tarea_asignada=asignacion.id_asignacion_pqr,
                    cod_estado_reasignacion='Ac'
                ).first()

                if tarea_reasignada:
                    # Obtener información de la reasignación
                    if tarea_reasignada.cod_estado_reasignacion == 'Ep':
                        # Reasignación en espera
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Re':
                        # Reasignación rechazada
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Ac':
                        # Reasignación aceptada
                        persona_reasignada = Personas.objects.get(
                            id_persona=tarea_reasignada.id_persona_a_quien_se_reasigna
                        )
                        unidad_reasignada = persona_reasignada.id_unidad_organizacional_actual

                    if unidad_reasignada:
                        if unidad_reasignada.cod_agrupacion_documental == 'SEC':
                            return f'SECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.codigo == 'SUB':
                            return f'SUBSECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.cod_agrupacion_documental is None:
                            return f'{unidad_reasignada.codigo} - {unidad_reasignada.nombre}'

                # Obtener información de la asignación original
                unidad_asignada = asignacion.id_und_org_seccion_asignada
                if unidad_asignada:
                    if unidad_asignada.cod_agrupacion_documental == 'SEC':
                        return f'SECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental == 'SUB':
                        return f'SUBSECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental is None:
                        return f'{unidad_asignada.codigo} - {unidad_asignada.nombre}'

            except AsignacionPQR.DoesNotExist:
                pass


        elif estado_actual and estado_actual.nombre == 'RESPONDIDA':
            # Obtener información de la respuesta
            respuestas = RespuestaPQR.objects.filter(id_pqrsdf=pqrsdf.id_PQRSDF)

            if respuestas.exists():
                # Tomar la primera respuesta para obtener la ubicación
                respuesta = respuestas.first()
                persona_responde = respuesta.id_persona_responde

                # Asegúrate de que el campo exista y tenga el nombre correcto en el modelo 'Personas'
                if hasattr(persona_responde, 'id_unidad_organizacional_actual'):
                    unidad_responde = persona_responde.id_unidad_organizacional_actual

                    # Asegúrate de que los nombres de los campos coincidan con el modelo 'UnidadesOrganizacionales'
                    if unidad_responde.cod_agrupacion_documental == 'SEC':
                        return f'SECCION - {unidad_responde.nombre}'
                    elif unidad_responde.cod_agrupacion_documental == 'SUB':
                        return f'SUBSECCION - {unidad_responde.nombre}'
                    elif unidad_responde.cod_agrupacion_documental is None:
                        return f'{unidad_responde.codigo} - {unidad_responde.nombre}'

        elif estado_actual and estado_actual.nombre == 'VENCIDO':
            # Obtener información de la asignación cuando la PQRSDF está vencida
            try:
                asignacion = AsignacionPQR.objects.filter(
                    T268Id_PQRSDF=pqrsdf.id_PQRSDF,
                    T268codEstadoAsignacion='Ac'
                ).latest('T268FechaAsignacion')

                unidad_asignada = asignacion.id_und_org_seccion_asignada
                if unidad_asignada.cod_agrupacion_documental == 'SEC':
                    return f'SECCION - {unidad_asignada.nombre}'
                elif unidad_asignada.cod_agrupacion_documental == 'SUB':
                    return f'SUBSECCION - {unidad_asignada.nombre}'
                else:
                    return f'{unidad_asignada.codigo} - {unidad_asignada.nombre}'

            except AsignacionPQR.DoesNotExist:
                pass

        return None
    

    def get_documento_info(self, pqrsdf, *args, **kwargs):
        estado_actual_nombre = pqrsdf.id_estado_actual_solicitud.nombre if pqrsdf.id_estado_actual_solicitud else None

        try:
            if estado_actual_nombre == 'RESPONDIDA':
                # Obtener los registros correspondientes en T269
                registros_t269 = RespuestaPQR.objects.filter(id_pqrsdf=pqrsdf.id_PQRSDF)

                if registros_t269.exists():
                    primer_registro_t269 = registros_t269.first()

                    # Obtener el registro en T237DocumentosDeArchivo_Expediente
                    id_doc_archivo_exped = getattr(primer_registro_t269.id_doc_archivo_exp, 'id_documento_de_archivo_exped', None)

                    if id_doc_archivo_exped:
                        # Obtener el registro en T237DocumentosDeArchivo_Expediente
                        registro_t237 = DocumentosDeArchivoExpediente.objects.filter(
                            id_documento_de_archivo_exped=id_doc_archivo_exped
                        ).first()

                        if registro_t237:
                            # Obtener el registro en T238ArchivosDigitales
                            registro_t238 = getattr(registro_t237.id_archivo_sistema, 'id_archivo_digital', None)

                            if registro_t238:
                                try:
                                    registro_t238 = ArchivosDigitales.objects.get(id_archivo_digital=registro_t238)

                                    return {
                                        'tipo': 'HIPERVINCULO',
                                        'valor': 'RESPUESTA',
                                        'archivo': {
                                            'id_archivo_digital': registro_t238.id_archivo_digital,
                                            'nombre_de_Guardado': registro_t238.nombre_de_Guardado,
                                            'formato': registro_t238.formato,
                                            'tamagno_kb': registro_t238.tamagno_kb,
                                            'ruta_archivo': registro_t238.ruta_archivo.url,
                                            'fecha_creacion_doc': registro_t238.fecha_creacion_doc,
                                            'es_Doc_elec_archivo': registro_t238.es_Doc_elec_archivo,
                                        },
                                        'url': f'/api/abrir_archivo/{registro_t238.id_archivo_digital}/',
                                    }

                                except ArchivosDigitales.DoesNotExist:
                                    pass

        except (RespuestaPQR.DoesNotExist, DocumentosDeArchivoExpediente.DoesNotExist, ArchivosDigitales.DoesNotExist):
            pass

        return {'tipo': 'No Aplica', 'valor': 'No Aplica'}


    def get_queryset(self):
        estados_pqrsdf = EstadosSolicitudes.objects.filter(
            aplica_para_pqrsdf=True
        ).exclude(nombre__in=[
            'SOLICITUD DE DIGITALIZACION ENVIADA',
            'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
            'SOLICITUD AL USUARIO ENVIADA',
            'SOLICITUD AL USUARIO RESPONDIDA'
            'GUARDADO'
        ])

        tipo_solicitud = self.request.query_params.get('tipo_solicitud')
        tipo_pqrsdf = self.request.query_params.get('tipo_pqrsdf')
        radicado = self.request.query_params.get('radicado')
        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')
        estado_solicitud = self.request.query_params.get('estado_solicitud')
        id_persona_titular = self.request.query_params.get('id_persona_titular')
        id_persona_interpone = self.request.query_params.get('id_persona_interpone')
        cod_relacion_con_el_titular = self.request.query_params.get('cod_relacion_con_el_titular')
        asunto = self.request.query_params.get('asunto')
        id_medio_solicitud = self.request.query_params.get('id_medio_solicitud')
        id_sucursal_especifica_implicada = self.request.query_params.get('id_sucursal_especifica_implicada')

        queryset = PQRSDF.objects.exclude(id_estado_actual_solicitud__nombre='GUARDADO')

        if tipo_solicitud:
            queryset = queryset.filter(cod_tipo_PQRSDF=tipo_solicitud)
    
        if asunto:
            queryset = queryset.filter(asunto__icontains=asunto)

        if tipo_pqrsdf:
            queryset = queryset.filter(cod_tipo_PQRSDF=tipo_pqrsdf)

        if id_persona_titular:
            queryset = queryset.filter(id_persona_titular=id_persona_titular)

        if id_sucursal_especifica_implicada:
            queryset = queryset.filter(id_sucursal_especifica_implicada=id_sucursal_especifica_implicada)
            # Verificar si id_sucursal_recepciona_fisica es None antes de acceder a descripcion_sucursal
            queryset = queryset.exclude(id_sucursal_especifica_implicada__isnull=True)

        if id_medio_solicitud:
            queryset = queryset.filter(id_medio_solicitud=id_medio_solicitud)

        if id_persona_interpone:
            queryset = queryset.filter(id_persona_interpone=id_persona_interpone)
       
        if cod_relacion_con_el_titular:
                queryset = queryset.filter(cod_relacion_con_el_titular=cod_relacion_con_el_titular)


        if radicado:
            # Filtrar por el radicado en la tabla T262Radicados con flexibilidad
            if '-' in radicado:
                try:
                    prefijo, agno, numero = radicado.split('-')
                except ValueError:
                    # Si no se puede dividir en prefijo, año y número, continuar sin filtrar por radicado
                    pass
                else:
                   queryset = queryset.filter(
                        id_radicado__prefijo_radicado__icontains=prefijo,
                        id_radicado__agno_radicado__icontains=agno,
                        id_radicado__nro_radicado__icontains=numero
                    )
            else:
                # Si no hay guion ('-'), buscar en cualquier parte del radicado
                queryset = queryset.filter(
                    Q(id_radicado__prefijo_radicado__icontains=radicado) |
                    Q(id_radicado__agno_radicado__icontains=radicado) |
                    Q(id_radicado__nro_radicado__icontains=radicado)
                )
    

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)


        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)
        

        if estado_solicitud:
            estado_mapping = {
                'RADICADO': 'RADICADO',
                'EN VENTANILLA CON PENDIENTES': 'EN VENTANILLA CON PENDIENTES',
                'EN VENTANILLA SIN PENDIENTES': 'EN VENTANILLA SIN PENDIENTES',
                'EN GESTION': 'EN GESTION',
                'RESPONDIDA': 'RESPONDIDA',
                'VENCIDO': 'VENCIDO'
            }

            if estado_solicitud == 'VENCIDO':
                # Calcular tiempo de respuesta
                tiempo_respuesta = F('fecha_radicado') + ExpressionWrapper(
                    timedelta(days=1) * F('dias_para_respuesta'),
                    output_field=fields.DurationField()
                )
                
                # Utilizar ExpressionWrapper para calcular la diferencia en días
                dias_faltantes_expression = ExpressionWrapper(
                    ExtractDay(tiempo_respuesta - Now()),
                    output_field=fields.IntegerField()
                )
                
                # Filtrar por PQRSDF en estado 'RADICADO' y 'Tiempo Para Respuesta' <= -1
                queryset = queryset.annotate(dias_faltantes=dias_faltantes_expression)
                queryset = queryset.filter(
                    Q(id_estado_actual_solicitud__nombre='RADICADO') &
                    (Q(fecha_radicado__isnull=True) | Q(dias_faltantes__lte=0))
                ).distinct()
            elif estado_solicitud == 'RADICADO':
                # Calcular tiempo de respuesta
                tiempo_respuesta = F('fecha_radicado') + ExpressionWrapper(
                    timedelta(days=1) * F('dias_para_respuesta'),
                    output_field=fields.DurationField()
                )
                
                # Utilizar ExpressionWrapper para calcular la diferencia en días
                dias_faltantes_expression = ExpressionWrapper(
                    ExtractDay(tiempo_respuesta - Now()),
                    output_field=fields.IntegerField()
                )
                
                # Filtrar por PQRSDF en estado 'RADICADO' y 'Tiempo Para Respuesta' > -1
                queryset = queryset.annotate(dias_faltantes=dias_faltantes_expression)
                queryset = queryset.filter(
                    Q(id_estado_actual_solicitud__nombre='RADICADO') &
                    (Q(fecha_radicado__isnull=True) | Q(dias_faltantes__gt=0))
                ).distinct()
            elif estado_solicitud == 'EN VENTANILLA CON PENDIENTES':
                # Filtrar por PQRSDF en estado 'EN VENTANILLA CON PENDIENTES'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='EN VENTANILLA CON PENDIENTES')

            elif estado_solicitud == 'EN VENTANILLA SIN PENDIENTES':
                # Filtrar por PQRSDF en estado 'EN VENTANILLA SIN PENDIENTES'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='EN VENTANILLA SIN PENDIENTES')

            elif estado_solicitud == 'EN GESTION':
                # Filtrar por PQRSDF en estado 'EN GESTION'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='EN GESTION')

            elif estado_solicitud == 'RESPONDIDA':
                # Filtrar por PQRSDF en estado 'RESPONDIDA'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='RESPONDIDA')

            elif estado_solicitud == 'NOTIFICADA':
                # Filtrar por PQRSDF en estado 'RESPONDIDA'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='NOTIFICADA')

            elif estado_solicitud == 'CERRADA':
                # Filtrar por PQRSDF en estado 'RESPONDIDA'
                queryset = queryset.filter(id_estado_actual_solicitud__nombre='CERRADA')



        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.'
            }, status=status.HTTP_404_NOT_FOUND)

        data = []
        today = datetime.now().date()

        for pqrsdf in queryset:
            # Titular
            if pqrsdf.id_persona_titular:
                titular_data = pqrsdf.id_persona_titular
                if titular_data.tipo_persona == 'N':
                    titular_nombre = f'{titular_data.primer_nombre} {titular_data.segundo_nombre} {titular_data.primer_apellido} {titular_data.segundo_apellido}'
                elif titular_data.tipo_persona == 'J':
                    titular_nombre = titular_data.razon_social
                else:
                    titular_nombre = 'Anónimo'
            else:
                titular_nombre = 'Anónimo'

            # Estado
            estado_nombre = self.get_estado_solicitud_nombre(pqrsdf.id_estado_actual_solicitud)

            # Obtener información de ubicación
            ubicacion_corporacion = self.get_location_info(pqrsdf)

            # Obtener información del documento
            documento_info = self.get_documento_info(pqrsdf)


            # Cálculo de días para respuesta
            if pqrsdf.fecha_radicado and pqrsdf.dias_para_respuesta is not None:
                tiempo_respuesta = pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)
                dias_faltantes = (tiempo_respuesta - datetime.now()).days

                # Determinar el estado VENCIDO
                if dias_faltantes <= -1:
                    estado_nombre = 'VENCIDO'
                else:
                    estado_nombre = self.get_estado_solicitud_nombre(pqrsdf.id_estado_actual_solicitud, pqrsdf.fecha_radicado, pqrsdf.dias_para_respuesta)
            else:
                dias_faltantes = None


            data.append({
                'Id_PQRSDF': pqrsdf.id_PQRSDF,
                'Tipo de Solicitud': 'PQRSDF',
                'Tipo de PQRSDF': pqrsdf.cod_tipo_PQRSDF,
                'tipo_pqrsdf_descripcion': get_tipo_pqrsdf_descripcion(pqrsdf.cod_tipo_PQRSDF),
                'Titular': titular_nombre,
                'Asunto': pqrsdf.asunto,
                'Radicado': f"{pqrsdf.id_radicado.prefijo_radicado}-{pqrsdf.id_radicado.agno_radicado}-{pqrsdf.id_radicado.nro_radicado}" if pqrsdf.id_radicado else 'N/A',
                'Fecha de Radicado': pqrsdf.fecha_radicado,
                'Fecha de registro': pqrsdf.fecha_registro,
                'Persona Que Radicó': f"{pqrsdf.id_radicado.id_persona_radica.primer_nombre} {pqrsdf.id_radicado.id_persona_radica.segundo_nombre} {pqrsdf.id_radicado.id_persona_radica.primer_apellido} {pqrsdf.id_radicado.id_persona_radica.segundo_apellido}" if pqrsdf.id_radicado and pqrsdf.id_radicado.id_persona_radica else 'N/A',
                'Tiempo Para Respuesta': dias_faltantes if dias_faltantes is not None else 'N/A',
                'Id_estado': pqrsdf.id_estado_actual_solicitud.id_estado_solicitud,
                'Estado': estado_nombre,
                'Medio Solicitud': pqrsdf.id_medio_solicitud.nombre,
                'Sucursal Implicada': pqrsdf.id_sucursal_especifica_implicada.descripcion_sucursal,
                'Ubicacion en la corporacion':ubicacion_corporacion,
                'Documento': documento_info['valor'],
                'URL_Documento': documento_info.get('url', None),
                'Archivo': documento_info.get('archivo', {}),
                
            })

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': data
        }, status=status.HTTP_200_OK)
    

##########################################################################################################################################################################################################
    
#CONSULTA_ESTADO_SOLICITUD_WORKFLOW
class ConsultaEstadoWorkFlow(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    permission_classes = [IsAuthenticated]

    def get_tipo_pqrsdf_descripcion(self, cod_tipo_pqrsdf):
        tipo_mapping = {
            "PG": "Petición General",
            "PD": "Petición De Documentos o Información",
            "PC": "Petición De Consulta",
            "Q": "Queja",
            "R": "Reclamo",
            "S": "Sugerencia",
            "D": "Denuncia",
            "F": "Felicitación",
        }

        return tipo_mapping.get(cod_tipo_pqrsdf, "Tipo Desconocido")

    def get_estado_solicitud_nombre(self, id_estado_solicitud, fecha_radicado=None, dias_para_respuesta=None):
        # Verificar si es VENCIDO y ajustar la lógica
        if dias_para_respuesta is not None and fecha_radicado:
            tiempo_respuesta = fecha_radicado + timedelta(days=dias_para_respuesta)
            today = datetime.now()
            
            # Verificar si es VENCIDO
            if today > tiempo_respuesta:
                return 'VENCIDO'

        # Verificar si ya es un objeto de estado o un ID
        if isinstance(id_estado_solicitud, EstadosSolicitudes):
            estado = id_estado_solicitud
        else:
            try:
                estado = EstadosSolicitudes.objects.get(id_estado_solicitud=id_estado_solicitud)
            except EstadosSolicitudes.DoesNotExist:
                return "Estado Desconocido"

        return estado.nombre


    def get_location_info(self, pqrsdf):
        estado_actual = pqrsdf.id_estado_actual_solicitud

        if estado_actual and estado_actual.nombre in ['RADICADO', 'EN VENTANILLA CON PENDIENTES', 'EN VENTANILLA SIN PENDIENTES']:
            return 'EN VENTANILLA'

        elif estado_actual and estado_actual.nombre == 'EN GESTION':
            # Obtener información de la asignación actual
            try:
                asignacion = AsignacionPQR.objects.filter(
                    id_pqrsdf=pqrsdf,
                    cod_estado_asignacion='Ac'
                ).latest('fecha_asignacion')

                # Validar si la asignación ha sido reasignada
                tarea_reasignada = ReasignacionesTareas.objects.filter(
                    id_tarea_asignada=asignacion.id_asignacion_pqr,
                    cod_estado_reasignacion='Ac'
                ).first()

                if tarea_reasignada:
                    # Obtener información de la reasignación
                    if tarea_reasignada.cod_estado_reasignacion == 'Ep':
                        # Reasignación en espera
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Re':
                        # Reasignación rechazada
                        unidad_reasignada = tarea_reasignada.id_und_org_reasignada
                    elif tarea_reasignada.cod_estado_reasignacion == 'Ac':
                        # Reasignación aceptada
                        persona_reasignada = Personas.objects.get(
                            id_persona=tarea_reasignada.id_persona_a_quien_se_reasigna
                        )
                        unidad_reasignada = persona_reasignada.id_unidad_organizacional_actual

                    if unidad_reasignada:
                        if unidad_reasignada.cod_agrupacion_documental == 'SEC':
                            return f'SECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.codigo == 'SUB':
                            return f'SUBSECCION - {unidad_reasignada.codigo} - {unidad_reasignada.nombre}'
                        elif unidad_reasignada.cod_agrupacion_documental is None:
                            return f'{unidad_reasignada.codigo} - {unidad_reasignada.nombre}'

                # Obtener información de la asignación original
                unidad_asignada = asignacion.id_und_org_seccion_asignada
                if unidad_asignada:
                    if unidad_asignada.cod_agrupacion_documental == 'SEC':
                        return f'SECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental == 'SUB':
                        return f'SUBSECCION - {unidad_asignada.codigo} - {unidad_asignada.nombre}'
                    elif unidad_asignada.cod_agrupacion_documental is None:
                        return f'{unidad_asignada.codigo} - {unidad_asignada.nombre}'

            except AsignacionPQR.DoesNotExist:
                pass


        elif estado_actual and estado_actual.nombre == 'RESPONDIDA':
            # Obtener información de la respuesta
            respuestas = RespuestaPQR.objects.filter(id_pqrsdf=pqrsdf.id_PQRSDF)

            if respuestas.exists():
                # Tomar la primera respuesta para obtener la ubicación
                respuesta = respuestas.first()
                persona_responde = respuesta.id_persona_responde

                # Asegúrate de que el campo exista y tenga el nombre correcto en el modelo 'Personas'
                if hasattr(persona_responde, 'id_unidad_organizacional_actual'):
                    unidad_responde = persona_responde.id_unidad_organizacional_actual

                    # Asegúrate de que los nombres de los campos coincidan con el modelo 'UnidadesOrganizacionales'
                    if unidad_responde.cod_agrupacion_documental == 'SEC':
                        return f'SECCION - {unidad_responde.nombre}'
                    elif unidad_responde.cod_agrupacion_documental == 'SUB':
                        return f'SUBSECCION - {unidad_responde.nombre}'
                    elif unidad_responde.cod_agrupacion_documental is None:
                        return f'{unidad_responde.codigo} - {unidad_responde.nombre}'

        elif estado_actual and estado_actual.nombre == 'VENCIDO':
            # Obtener información de la asignación cuando la PQRSDF está vencida
            try:
                asignacion = AsignacionPQR.objects.filter(
                    T268Id_PQRSDF=pqrsdf.id_PQRSDF,
                    T268codEstadoAsignacion='Ac'
                ).latest('T268FechaAsignacion')

                unidad_asignada = asignacion.id_und_org_seccion_asignada
                if unidad_asignada.cod_agrupacion_documental == 'SEC':
                    return f'SECCION - {unidad_asignada.nombre}'
                elif unidad_asignada.cod_agrupacion_documental == 'SUB':
                    return f'SUBSECCION - {unidad_asignada.nombre}'
                else:
                    return f'{unidad_asignada.codigo} - {unidad_asignada.nombre}'

            except AsignacionPQR.DoesNotExist:
                pass

        return None
    

    def get_documento_info(self, pqrsdf, *args, **kwargs):
        estado_actual_nombre = pqrsdf.id_estado_actual_solicitud.nombre if pqrsdf.id_estado_actual_solicitud else None

        try:
            
            if estado_actual_nombre == 'RESPONDIDA':
                # Obtener los registros correspondientes en T269
                registros_t269 = RespuestaPQR.objects.filter(id_pqrsdf=pqrsdf.id_PQRSDF)

                if registros_t269.exists():
                    primer_registro_t269 = registros_t269.first()
                    
                    # Obtener el registro en T237DocumentosDeArchivo_Expediente
                    registros_t237 = DocumentosDeArchivoExpediente.objects.filter(
                        id_documento_de_archivo_exped=primer_registro_t269.id_doc_archivo_exp.id_documento_de_archivo_exped
                    )

                    if registros_t237.exists():
                        registro_t237 = registros_t237.first()

                        # Obtener el registro en T238ArchivosDigitales
                        try:
                            registro_t238 = ArchivosDigitales.objects.get(
                                id_archivo_digital=registro_t237.id_archivo_sistema.id_archivo_digital
                            )

                            return {
                                'tipo': 'HIPERVINCULO',
                                'valor': 'RESPUESTA',
                                'archivo': {
                                    'id_archivo_digital': registro_t238.id_archivo_digital,
                                    'nombre_de_Guardado': registro_t238.nombre_de_Guardado,
                                    'formato': registro_t238.formato,
                                    'tamagno_kb': registro_t238.tamagno_kb,
                                    'ruta_archivo': registro_t238.ruta_archivo.url,
                                    'fecha_creacion_doc': registro_t238.fecha_creacion_doc,
                                    'es_Doc_elec_archivo': registro_t238.es_Doc_elec_archivo,
                                },
                                'url': f'/api/abrir_archivo/{registro_t238.id_archivo_digital}/',
                            }

                        except ArchivosDigitales.DoesNotExist:
                            pass

        except (RespuestaPQR.DoesNotExist, DocumentosDeArchivoExpediente.DoesNotExist, ArchivosDigitales.DoesNotExist):
            pass

        return {'tipo': 'No Aplica', 'valor': 'No Aplica'}



    def get_queryset(self):
        estados_pqrsdf = EstadosSolicitudes.objects.filter(
            aplica_para_pqrsdf=True
        ).exclude(nombre__in=[
            'SOLICITUD DE DIGITALIZACION ENVIADA',
            'SOLICITUD DIGITALIZACIÓN RESPONDIDA',
            'SOLICITUD AL USUARIO ENVIADA',
            'SOLICITUD AL USUARIO RESPONDIDA'
        ])

        tipo_solicitud = self.request.query_params.get('tipo_solicitud')
        tipo_pqrsdf = self.request.query_params.get('tipo_pqrsdf')
        radicado = self.request.query_params.get('radicado')
        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')
        estado_solicitud = self.request.query_params.get('estado_solicitud')
        id_persona_titular = self.request.query_params.get('id_persona_titular')
        id_persona_interpone = self.request.query_params.get('id_persona_interpone')
        cod_relacion_con_el_titular = self.request.query_params.get('cod_relacion_con_el_titular')

        queryset = PQRSDF.objects.filter(id_estado_actual_solicitud__in=estados_pqrsdf)

        if tipo_solicitud:
            queryset = queryset.filter(cod_tipo_PQRSDF=tipo_solicitud)
    

        if tipo_pqrsdf:
            queryset = queryset.filter(cod_tipo_PQRSDF=tipo_pqrsdf)

        if id_persona_titular:
            queryset = queryset.filter(id_persona_titular=id_persona_titular)

        if id_persona_interpone:
            queryset = queryset.filter(id_persona_interpone=id_persona_interpone)
       
        if cod_relacion_con_el_titular:
                queryset = queryset.filter(cod_relacion_con_el_titular=cod_relacion_con_el_titular)

        if radicado:
            try:
                prefijo, agno, numero = radicado.split('-')
            except ValueError:
                raise ValidationError('El campo "Radicado" debe tener el formato correcto: (PREFIJO) - (AGNO) - (NUMERO_RADICADO).')
            
            queryset = queryset.filter(
                id_radicado__prefijo_radicado=prefijo,
                id_radicado__agno_radicado=agno,
                id_radicado__nro_radicado=numero
            )
    

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)


        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)
        

        if estado_solicitud:
            estado_mapping = {
                'RADICADO': 'RADICADO',
                'EN VENTANILLA CON PENDIENTES': 'EN VENTANILLA CON PENDIENTES',
                'EN VENTANILLA SIN PENDIENTES': 'EN VENTANILLA SIN PENDIENTES',
                'EN GESTION': 'EN GESTION',
                'RESPONDIDA': 'RESPONDIDA',
                'VENCIDO': 'VENCIDO'
            }

            if estado_solicitud == 'VENCIDO':
                # Calcular tiempo de respuesta
                tiempo_respuesta = F('fecha_radicado') + ExpressionWrapper(
                    timedelta(days=1) * F('dias_para_respuesta'),
                    output_field=fields.DurationField()
                )
                
                # Utilizar ExpressionWrapper para calcular la diferencia en días
                dias_faltantes_expression = ExpressionWrapper(
                    ExtractDay(tiempo_respuesta - Now()),
                    output_field=fields.IntegerField()
                )
                
                # Filtrar por PQRSDF en estado 'RADICADO' y 'Tiempo Para Respuesta' <= -1
                queryset = queryset.annotate(dias_faltantes=dias_faltantes_expression)
                queryset = queryset.filter(
                    Q(id_estado_actual_solicitud__nombre='RADICADO') &
                    (Q(fecha_radicado__isnull=True) | Q(dias_faltantes__lte=0))
                ).distinct()
            elif estado_solicitud == 'RADICADO':
                # Calcular tiempo de respuesta
                tiempo_respuesta = F('fecha_radicado') + ExpressionWrapper(
                    timedelta(days=1) * F('dias_para_respuesta'),
                    output_field=fields.DurationField()
                )
                
                # Utilizar ExpressionWrapper para calcular la diferencia en días
                dias_faltantes_expression = ExpressionWrapper(
                    ExtractDay(tiempo_respuesta - Now()),
                    output_field=fields.IntegerField()
                )
                
                # Filtrar por PQRSDF en estado 'RADICADO' y 'Tiempo Para Respuesta' > -1
                queryset = queryset.annotate(dias_faltantes=dias_faltantes_expression)
                queryset = queryset.filter(
                    Q(id_estado_actual_solicitud__nombre='RADICADO') &
                    (Q(fecha_radicado__isnull=True) | Q(dias_faltantes__gt=0))
                ).distinct()
            else:
                estado_mapping_value = estado_mapping.get(estado_solicitud, '')
                if estado_mapping_value:
                    queryset = queryset.filter(id_estado_actual_solicitud__nombre=estado_mapping_value)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.'
            }, status=status.HTTP_404_NOT_FOUND)

        data = []
        today = datetime.now().date()

        for pqrsdf in queryset:
            # Titular
            if pqrsdf.id_persona_titular:
                titular_data = pqrsdf.id_persona_titular
                if titular_data.tipo_persona == 'N':
                    titular_nombre = f'{titular_data.primer_nombre} {titular_data.segundo_nombre} {titular_data.primer_apellido} {titular_data.segundo_apellido}'
                elif titular_data.tipo_persona == 'J':
                    titular_nombre = titular_data.razon_social
                else:
                    titular_nombre = 'Anónimo'
            else:
                titular_nombre = 'Anónimo'

            # Estado
            estado_nombre = self.get_estado_solicitud_nombre(pqrsdf.id_estado_actual_solicitud)

            # Obtener información de ubicación
            ubicacion_corporacion = self.get_location_info(pqrsdf)

            # Obtener información del documento
            documento_info = self.get_documento_info(pqrsdf)


            # Cálculo de días para respuesta
            if pqrsdf.fecha_radicado and pqrsdf.dias_para_respuesta is not None:
                tiempo_respuesta = pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)
                dias_faltantes = (tiempo_respuesta - datetime.now()).days

                # Determinar el estado VENCIDO
                if dias_faltantes <= -1:
                    estado_nombre = 'VENCIDO'
                else:
                    estado_nombre = self.get_estado_solicitud_nombre(pqrsdf.id_estado_actual_solicitud, pqrsdf.fecha_radicado, pqrsdf.dias_para_respuesta)
            else:
                dias_faltantes = None


            data.append({
                'Id_PQRSDF': pqrsdf.id_PQRSDF,
                'Tipo de Solicitud': 'PQRSDF',
                'Tipo de PQRSDF': pqrsdf.cod_tipo_PQRSDF,
                'tipo_pqrsdf_descripcion': get_tipo_pqrsdf_descripcion(pqrsdf.cod_tipo_PQRSDF),
                'Titular': titular_nombre,
                'Asunto': pqrsdf.asunto,
                'Radicado': f"{pqrsdf.id_radicado.prefijo_radicado}-{pqrsdf.id_radicado.agno_radicado}-{pqrsdf.id_radicado.nro_radicado}" if pqrsdf.id_radicado else 'N/A',
                'Fecha de Radicado': pqrsdf.fecha_radicado,
                'Persona Que Radicó': f"{pqrsdf.id_radicado.id_persona_radica.primer_nombre} {pqrsdf.id_radicado.id_persona_radica.segundo_nombre} {pqrsdf.id_radicado.id_persona_radica.primer_apellido} {pqrsdf.id_radicado.id_persona_radica.segundo_apellido}" if pqrsdf.id_radicado and pqrsdf.id_radicado.id_persona_radica else 'N/A',
                'Tiempo Para Respuesta': dias_faltantes if dias_faltantes is not None else 'N/A',
                'Estado': estado_nombre,
                'Ubicacion en la corporacion':ubicacion_corporacion,
                'Documento': documento_info['valor'],
                'URL_Documento': documento_info.get('url', None),
                'Archivo': documento_info.get('archivo', {}),
                
            })

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': data
        }, status=status.HTTP_200_OK)
    

#CONSULTA_DE_WORKFLOW
class ListarInformacionArbolWorkflow(generics.ListAPIView):
    def get(self, request, id_PQRSDF):
        try:
            pqrsdf = PQRSDF.objects.get(id_PQRSDF=id_PQRSDF)
        except PQRSDF.DoesNotExist:
            return Response({"error": "PQRSDF no encontrado"}, status=404)

        arbol_solicitudes = []

        #GUARDADO
        if pqrsdf.id_estado_actual_solicitud.nombre == "GUARDADO":
            arbol_solicitudes.append({"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},)
            
        #RADICADO    
        elif pqrsdf.id_estado_actual_solicitud.nombre == "RADICADO":
            arbol_solicitudes.extend([{"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                                      {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado}])

        #EN VENTANILLA CON PENIDENTES
        elif pqrsdf.id_estado_actual_solicitud.nombre == "EN VENTANILLA CON PENDIENTES":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"}
            ])

        #SOLICITUD DE DIGITALIZACION ENVIADA    
        elif pqrsdf.id_estado_actual_solicitud.nombre == "SOLICITUD DE DIGITALIZACION ENVIADA":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                {"solicitud": "SOLICITUD DE DIGITALIZACION ENVIADA"}
            ])

        #SOLICITUD DIGITALIZACIÓN RESPONDIDA  
        elif pqrsdf.id_estado_actual_solicitud.nombre == "SOLICITUD DIGITALIZACIÓN RESPONDIDA":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                {"solicitud": "SOLICITUD DE DIGITALIZACION ENVIADA"},
                {"solicitud": "SOLICITUD DIGITALIZACIÓN RESPONDIDA"},
            ])

        #SOLICITUD AL USUARIO ENVIADA  
        elif pqrsdf.id_estado_actual_solicitud.nombre == "SOLICITUD AL USUARIO ENVIADA":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                {"solicitud": "SOLICITUD AL USUARIO ENVIADA"},
            ])


        #SOLICITUD AL USUARIO RESPONDIDA    
        elif pqrsdf.id_estado_actual_solicitud.nombre == "SOLICITUD AL USUARIO RESPONDIDA":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                {"solicitud": "SOLICITUD AL USUARIO ENVIADA"},
                {"solicitud": "SOLICITUD AL USUARIO RESPONDIDA"},
            ])

        #EN VENTANILLA SIN PENDIENTES
        elif pqrsdf.id_estado_actual_solicitud.nombre == "EN VENTANILLA SIN PENDIENTES":
            arbol_solicitudes.extend([
                {"solicitud": "GUARDADO","fecha_registro": pqrsdf.fecha_registro},
                {"solicitud": "RADICADO","fecha_radicado": pqrsdf.fecha_radicado},
                {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                {"solicitud": "EN VENTANILLA SIN PENDIENTES"}
            ])


        #EN GESTION
        elif pqrsdf.id_estado_actual_solicitud.nombre == "EN GESTION":
            asignacion_en_gestion = AsignacionPQR.objects.filter(id_pqrsdf=pqrsdf).first()

            if asignacion_en_gestion:
                persona_asignada_data = {}
                unidad_asignada_data = {}

                if asignacion_en_gestion.id_persona_asignada:
                    persona_asignada_data = PersonaSerializer(asignacion_en_gestion.id_persona_asignada).data

                if asignacion_en_gestion.id_und_org_seccion_asignada:
                    unidad_asignada_data = UnidadOrganizacionalSerializer(asignacion_en_gestion.id_und_org_seccion_asignada).data

                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION", "persona_asignada": persona_asignada_data, "unidad_asignada": unidad_asignada_data}
                ])
            else:
                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION" ", no se le ha asignado una (persona),ni una (unidad organizacion)"}
        ])
        
        #RESPONDIDA    
        elif pqrsdf.id_estado_actual_solicitud.nombre == "RESPONDIDA":
            asignacion_en_gestion = AsignacionPQR.objects.filter(id_pqrsdf=pqrsdf).first()

            if asignacion_en_gestion:
                persona_asignada_data = {}
                unidad_asignada_data = {}

                if asignacion_en_gestion.id_persona_asignada:
                    persona_asignada_data = PersonaSerializer(asignacion_en_gestion.id_persona_asignada).data

                if asignacion_en_gestion.id_und_org_seccion_asignada:
                    unidad_asignada_data = UnidadOrganizacionalSerializer(asignacion_en_gestion.id_und_org_seccion_asignada).data

                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION", "persona_asignada": persona_asignada_data, "unidad_asignada": unidad_asignada_data},
                    {"solicitud": "RESPONDIDA"}
                ])
            else:
                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION" "no se le ha asignado una (persona),ni una (unidad organizacion)"},
                    {"solicitud": "RESPONDIDA"},
        ])

        #NOTIFICADA
        elif pqrsdf.id_estado_actual_solicitud.nombre == "NOTIFICADA":
            asignacion_en_gestion = AsignacionPQR.objects.filter(id_pqrsdf=pqrsdf).first()

            if asignacion_en_gestion:
                persona_asignada_data = {}
                unidad_asignada_data = {}

                if asignacion_en_gestion.id_persona_asignada:
                    persona_asignada_data = PersonaSerializer(asignacion_en_gestion.id_persona_asignada).data

                if asignacion_en_gestion.id_und_org_seccion_asignada:
                    unidad_asignada_data = UnidadOrganizacionalSerializer(asignacion_en_gestion.id_und_org_seccion_asignada).data

                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION", "persona_asignada": persona_asignada_data, "unidad_asignada": unidad_asignada_data},
                    {"solicitud": "RESPONDIDA"},
                    {"solicitud": "NOTIFICADA"}
                ])
            else:
                arbol_solicitudes.extend([
                    {"solicitud": "GUARDADO", "fecha_registro": pqrsdf.fecha_registro},
                    {"solicitud": "RADICADO", "fecha_radicado": pqrsdf.fecha_radicado},
                    {"solicitud": "EN VENTANILLA CON PENDIENTES"},
                    {"solicitud": "EN VENTANILLA SIN PENDIENTES"},
                    {"solicitud": "EN GESTION" "no se le ha asignado una (persona),ni una (unidad organizacion)"},
                    {"solicitud": "RESPONDIDA"},
                    {"solicitud": "NOTIFICADA"},
        ])

        serializer = PQRSDFSerializer(pqrsdf)
        data = serializer.data
        data["arbol_solicitudes"] = arbol_solicitudes

        return Response(data)
    


#INDICADORES_PQRSDF
    

#PERIOCIDAD
class IndicadorPeriocidad(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF con estado diferente de "guardado"
        queryset = PQRSDF.objects.exclude(id_radicado__isnull=True)

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Obtener indicadores por medio de solicitud
        indicadores = queryset.values('id_medio_solicitud__nombre', 'id_medio_solicitud').annotate(
            cantidad_pqrsdf=Count('id_PQRSDF')
        )

        # Obtener el total de PQRSDF con estado diferente de "guardado"
        total_pqrsdf = queryset.count()

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicadores de PQRSDF por periocidad.',
            'data': {
                'indicadores_por_medio_solicitud': [
                    {
                        'id_medio_solicitud': indicador['id_medio_solicitud'],
                        'nombre_medio_solicitud': indicador['id_medio_solicitud__nombre'],
                        'cantidad_pqrsdf': indicador['cantidad_pqrsdf'],
                    }
                    for indicador in indicadores
                ],
                'total_pqrsdf': total_pqrsdf
            }
        }, status=status.HTTP_200_OK)

#PRIMER_INDICADOR_ATENCION_PQRSDF
class IndicadorAtencionPQRSDF(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF recibidos (excluir los que están en estado 'guardado')
        queryset = PQRSDF.objects.exclude(id_radicado__isnull=True)

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtrar PQRSDF respondidos (en estado 'respondida' o 'notificada')
        queryset_respondidos = queryset.filter(
            id_estado_actual_solicitud__nombre__in=['RESPONDIDA', 'NOTIFICADA', 'CERRADA']
        )

        # Filtrar PQRSDF no respondidos (cualquier estado diferente a 'respondida' o 'notificada')
        queryset_no_respondidos = queryset.exclude(
            id_estado_actual_solicitud__nombre__in=['RESPONDIDA', 'NOTIFICADA', 'CERRADA']
        )

        # Número de PQRSDF recibidos
        num_pqrsdf_recibidos = queryset.count()

        # Número de PQRSDF respondidos
        num_pqrsdf_respondidos = queryset_respondidos.count()

        # Número de PQRSDF no respondidos
        num_pqrsdf_no_respondidos = queryset_no_respondidos.count()

        # Calcular el porcentaje de PQRSDF respondidos y no respondidos
        porcentaje_respondidos = 0
        porcentaje_no_respondidos = 0

        if num_pqrsdf_recibidos > 0:
            porcentaje_respondidos = (num_pqrsdf_respondidos / num_pqrsdf_recibidos) * 100
            porcentaje_no_respondidos = (num_pqrsdf_no_respondidos / num_pqrsdf_recibidos) * 100

        # Calcular el rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_respondidos >= 80 else ('Regular' if 60 <= porcentaje_respondidos <= 79 else 'Deficiente')

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicador de atención a PQRSDF.',
            'data': {
                'num_pqrsdf_recibidos': num_pqrsdf_recibidos,
                'num_pqrsdf_respondidos': num_pqrsdf_respondidos,
                'num_pqrsdf_no_respondidos': num_pqrsdf_no_respondidos,
                'porcentaje_respondidos': porcentaje_respondidos,
                'porcentaje_no_respondidos': porcentaje_no_respondidos,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#SEGUNDO_INDICADOR_PETICIONES_PQRSDF
class IndicadorAtencionDerechosPetecion(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF recibidos de tipo 'PG', 'PD', 'PC' (excluir los que están en estado 'guardado')
        queryset = PQRSDF.objects.filter(
            cod_tipo_PQRSDF__in=['PG', 'PD', 'PC']
        ).exclude(id_radicado__isnull=True)

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtrar PQRSDF de tipo 'PG', 'PD', 'PC' respondidos (en estado 'respondida' o 'notificada')
        queryset_respondidos = queryset.filter(
            id_estado_actual_solicitud__nombre__in=['RESPONDIDA', 'NOTIFICADA', 'CERRADA']
        )

        # Número de PQRSDF recibidos de tipo 'PG', 'PD', 'PC'
        num_peticiones_recibidos = queryset.count()

        # Número de PQRSDF de tipo 'PG', 'PD', 'PC' respondidos
        num_peticiones_respondidos = queryset_respondidos.count()

        # Calcular el porcentaje de PQRSDF respondidos y no respondidos
        porcentaje_respondidos = 0
        porcentaje_no_respondidos = 0

        if num_peticiones_recibidos > 0:
            porcentaje_respondidos = (num_peticiones_respondidos / num_peticiones_recibidos) * 100
            porcentaje_no_respondidos = 100 - porcentaje_respondidos

        # Calcular el indicador de atención
        indicador_atencion = 0
        if num_peticiones_recibidos > 0:
            indicador_atencion = (num_peticiones_respondidos / num_peticiones_recibidos) * 100

        # Calcular el rango de cumplimiento
        rango_cumplimiento = 'Excelente' if indicador_atencion >= 80 else ('Regular' if 60 <= indicador_atencion <= 79 else 'Deficiente')

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicador de atención a Derechos de Petición.',
            'data': {
                'num_peticiones_recibidos': num_peticiones_recibidos,
                'num_peticiones_respondidos': num_peticiones_respondidos,
                'porcentaje_respondidos': porcentaje_respondidos,
                'porcentaje_no_respondidos': porcentaje_no_respondidos,
                'indicador_atencion': indicador_atencion,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#TERCER_INDICADOR_QUEJAS_PQRSDF
class IndicadorAtencionQuejas(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF recibidas de tipo 'Q' (excluir las que están en estado 'guardado')
        queryset = PQRSDF.objects.filter(
            cod_tipo_PQRSDF='Q'
        ).exclude(id_radicado__isnull=True)

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtrar PQRSDF de tipo 'Q' respondidas (en estado 'respondida' o 'notificada')
        queryset_respondidas = queryset.filter(
            id_estado_actual_solicitud__nombre__in=['RESPONDIDA', 'NOTIFICADA', 'CERRADA']
        )

        # Número de PQRSDF recibidas de tipo 'Q'
        num_quejas_recibidas = queryset.count()

        # Número de PQRSDF de tipo 'Q' respondidas
        num_quejas_respondidas = queryset_respondidas.count()

        # Calcular el porcentaje de Quejas respondidas y no respondidas
        porcentaje_respondidas = 0
        porcentaje_no_respondidas = 0

        if num_quejas_recibidas > 0:
            porcentaje_respondidas = (num_quejas_respondidas / num_quejas_recibidas) * 100
            porcentaje_no_respondidas = 100 - porcentaje_respondidas

        # Calcular el indicador de atención
        indicador_atencion = 0
        if num_quejas_recibidas > 0:
            indicador_atencion = (num_quejas_respondidas / num_quejas_recibidas) * 100

        # Calcular el rango de cumplimiento
        rango_cumplimiento = 'Excelente' if indicador_atencion >= 80 else ('Regular' if 60 <= indicador_atencion <= 79 else 'Deficiente')

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicador de atención a Quejas.',
            'data': {
                'num_quejas_recibidas': num_quejas_recibidas,
                'num_quejas_respondidas': num_quejas_respondidas,
                'porcentaje_respondidas': porcentaje_respondidas,
                'porcentaje_no_respondidas': porcentaje_no_respondidas,
                'indicador_atencion': indicador_atencion,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#CUARTO_INDICADOR_RECLAMOS_PQRSDF
class IndicadorAtencionReclamos(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF de tipo 'R' (Reclamos) recibidos (excluir los que están en estado 'guardado')
        queryset = PQRSDF.objects.filter(
            cod_tipo_PQRSDF='R'
        ).exclude(id_radicado__isnull=True)

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filtrar PQRSDF de tipo 'R' respondidos (en estado 'respondida' o 'notificada')
        queryset_respondidos = queryset.filter(
            id_estado_actual_solicitud__nombre__in=['RESPONDIDA', 'NOTIFICADA', 'CERRADA']
        )

        # Número de PQRSDF recibidos de tipo 'R'
        num_reclamos_recibidos = queryset.count()

        # Número de PQRSDF de tipo 'R' respondidos
        num_reclamos_respondidos = queryset_respondidos.count()

        # Calcular el porcentaje de Reclamos respondidos y no respondidos
        porcentaje_respondidos = 0
        porcentaje_no_respondidos = 0

        if num_reclamos_recibidos > 0:
            porcentaje_respondidos = (num_reclamos_respondidos / num_reclamos_recibidos) * 100
            porcentaje_no_respondidos = 100 - porcentaje_respondidos

        # Calcular el indicador de atención
        indicador_atencion = 0
        if num_reclamos_recibidos > 0:
            indicador_atencion = (num_reclamos_respondidos / num_reclamos_recibidos) * 100

        # Calcular el rango de cumplimiento
        rango_cumplimiento = 'Excelente' if indicador_atencion >= 80 else ('Regular' if 60 <= indicador_atencion <= 79 else 'Deficiente')

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicador de atención a Reclamos.',
            'data': {
                'num_reclamos_recibidos': num_reclamos_recibidos,
                'num_reclamos_respondidos': num_reclamos_respondidos,
                'porcentaje_respondidos': porcentaje_respondidos,
                'porcentaje_no_respondidos': porcentaje_no_respondidos,
                'indicador_atencion': indicador_atencion,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#QUINTO_INDICADOR_SUGERENCIAS_PQRSDF
class IndicadorSugerenciasRadicadas(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Usa el serializador proporcionado

    def get_queryset(self):
        # Filtrar PQRSDF radicadas (excluir los que están en estado 'guardado')
        queryset = PQRSDF.objects.all()

        # Filtrar PQRSDF de tipo 'S' (Sugerencia) radicadas (en estado 'radicado')
        queryset_sugerencias = queryset.filter(
            cod_tipo_PQRSDF='S',
        )

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset = queryset.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset = queryset.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset, queryset_sugerencias

    def get(self, request, *args, **kwargs):
        queryset, queryset_sugerencias = self.get_queryset()

        # Número de PQRSDF radicadas
        num_pqrsdf_radicadas = queryset.count()

        # Número total de Sugerencias
        num_sugerencias_total = queryset_sugerencias.count()

        # Número de Sugerencias radicadas
        num_sugerencias_radicadas = queryset_sugerencias.filter(id_radicado__isnull=False).count()

        # Número de Sugerencias no radicadas
        num_sugerencias_no_radicadas = queryset_sugerencias.filter(id_radicado__isnull=True).count()

        # Calcular el porcentaje de Sugerencias radicadas y no radicadas
        porcentaje_sugerencias_radicadas = 0
        porcentaje_sugerencias_no_radicadas = 0

        if num_sugerencias_total > 0:
            porcentaje_sugerencias_radicadas = (num_sugerencias_radicadas / num_sugerencias_total) * 100
            porcentaje_sugerencias_no_radicadas = (num_sugerencias_no_radicadas / num_sugerencias_total) * 100

        # Calcular el rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_sugerencias_radicadas >= 80 else ('Regular' if 60 <= porcentaje_sugerencias_radicadas <= 79 else 'Deficiente')

        # Devolver los resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Sugerencias radicadas.',
            'data': {
                'num_pqrsdf_radicadas': num_pqrsdf_radicadas,
                'num_sugerencias_radicadas': num_sugerencias_radicadas,
                'num_sugerencias_no_radicadas': num_sugerencias_no_radicadas,
                'porcentaje_sugerencias_radicadas': porcentaje_sugerencias_radicadas,
                'porcentaje_sugerencias_no_radicadas': porcentaje_sugerencias_no_radicadas,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    


#OCTAVO_INDICADOR_PQRSDF_CONTESTADOS_OPORTUNAMENTE
class IndicadorPQRSDFContestadosOportunamente(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar PQRSDF recibidos (excluir los que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidos = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True)
        )

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidos = queryset_recibidos.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidos = queryset_recibidos.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidos

    def get(self, request, *args, **kwargs):
        queryset_recibidos = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidos)

        # Filtrar los resultados después de recuperarlos
        queryset_contestadas_oportunamente = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion and
            pqrsdf.id_estado_actual_solicitud.nombre in ['NOTIFICADA', 'CERRADA', 'RESPONDIDA']
        ]

        num_pqrsdf_contestados_dentro_del_termino = len(queryset_contestadas_oportunamente)

        # Número total de PQRSDF recibidos
        num_pqrsdf_recibidos = len(results)

        # Calcular porcentajes
        porcentaje_contestados_dentro_del_termino = (num_pqrsdf_contestados_dentro_del_termino / num_pqrsdf_recibidos) * 100
        porcentaje_no_contestados_dentro_del_termino = 100 - porcentaje_contestados_dentro_del_termino

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_contestados_dentro_del_termino >= 80 else (
            'Regular' if 60 <= porcentaje_contestados_dentro_del_termino <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de PQRSDF contestados oportunamente.',
            'data': {
                'num_pqrsdf_recibidos': num_pqrsdf_recibidos,
                'num_pqrsdf_contestados_oportunamente': num_pqrsdf_contestados_dentro_del_termino,
                'porcentaje_contestados_oportunamente': porcentaje_contestados_dentro_del_termino,
                'porcentaje_contestados_inoportunamente': porcentaje_no_contestados_dentro_del_termino,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#NOVENO_INDICADOR_PETICIONES_CONTESTADOS_OPORTUNAMENTE

class IndicadorPeticionesContestadasOportunamente(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar peticiones recibidas (excluir las que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidas = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True)
        ).filter(cod_tipo_PQRSDF__in=['PG', 'PD', 'PC'])

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidas

    def get(self, request, *args, **kwargs):
        queryset_recibidas = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidas)

        # Filtrar los resultados después de recuperarlos
        queryset_contestadas_oportunamente = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion and
            pqrsdf.id_estado_actual_solicitud.nombre in ['NOTIFICADA', 'CERRADA', 'RESPONDIDA']
        ]

        num_peticiones_contestadas_dentro_del_termino = len(queryset_contestadas_oportunamente)

        # Número total de Peticiones recibidas
        num_peticiones_recibidas = len(results)

        # Calcular porcentajes
        porcentaje_contestadas_dentro_del_termino = (num_peticiones_contestadas_dentro_del_termino / num_peticiones_recibidas) * 100
        porcentaje_no_contestadas_dentro_del_termino = 100 - porcentaje_contestadas_dentro_del_termino

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_contestadas_dentro_del_termino >= 80 else (
            'Regular' if 60 <= porcentaje_contestadas_dentro_del_termino <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Peticiones Contestadas Oportunamente.',
            'data': {
                'num_peticiones_recibidas': num_peticiones_recibidas,
                'num_peticiones_contestadas_oportunamente': num_peticiones_contestadas_dentro_del_termino,
                'porcentaje_contestadas_oportunamente': porcentaje_contestadas_dentro_del_termino,
                'porcentaje_contestadas_inoportunamente': porcentaje_no_contestadas_dentro_del_termino,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    
#DECIMO_INDICADOR_QUEJAS_CONTESTADOS_OPORTUNAMENTE
class IndicadorQuejasContestadasOportunamente(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar quejas recibidas (excluir las que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidas = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True)
        ).filter(cod_tipo_PQRSDF='Q')

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidas

    def get(self, request, *args, **kwargs):
        queryset_recibidas = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidas)

        # Filtrar los resultados después de recuperarlos
        queryset_contestadas_oportunamente = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion and
            pqrsdf.id_estado_actual_solicitud.nombre in ['NOTIFICADA', 'CERRADA', 'RESPONDIDA']
        ]

        num_quejas_contestadas_dentro_del_termino = len(queryset_contestadas_oportunamente)

        # Número total de Quejas recibidas
        num_quejas_recibidas = len(results)

        # Calcular porcentajes con verificación para evitar división por cero
        porcentaje_contestadas_dentro_del_termino = 0 if num_quejas_recibidas == 0 else (num_quejas_contestadas_dentro_del_termino / num_quejas_recibidas) * 100
        porcentaje_no_contestadas_dentro_del_termino = 100 - porcentaje_contestadas_dentro_del_termino if num_quejas_recibidas > 0 else 0

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_contestadas_dentro_del_termino >= 80 else (
            'Regular' if 60 <= porcentaje_contestadas_dentro_del_termino <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Quejas Contestadas Oportunamente.',
            'data': {
                'num_quejas_recibidas': num_quejas_recibidas,
                'num_quejas_contestadas_oportunamente': num_quejas_contestadas_dentro_del_termino,
                'porcentaje_contestadas_oportunamente': porcentaje_contestadas_dentro_del_termino,
                'porcentaje_contestadas_inoportunamente': porcentaje_no_contestadas_dentro_del_termino,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)

#UNDECIMO_INDICADOR_RECLAMOS_CONTESTADOS_OPORTUNAMENTE
class IndicadorReclamosContestadosOportunamente(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar reclamos recibidos (excluir los que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidos = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True)
        ).filter(cod_tipo_PQRSDF='R')

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidos = queryset_recibidos.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidos = queryset_recibidos.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidos

    def get(self, request, *args, **kwargs):
        queryset_recibidos = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidos)

        # Filtrar los resultados después de recuperarlos
        queryset_contestadas_oportunamente = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion and
            pqrsdf.id_estado_actual_solicitud.nombre in ['NOTIFICADA', 'CERRADA', 'RESPONDIDA']
        ]

        num_reclamos_contestados_dentro_del_termino = len(queryset_contestadas_oportunamente)

        # Número total de Reclamos recibidos
        num_reclamos_recibidos = len(results)

        # Calcular porcentajes con verificación para evitar división por cero
        porcentaje_contestados_dentro_del_termino = 0 if num_reclamos_recibidos == 0 else (num_reclamos_contestados_dentro_del_termino / num_reclamos_recibidos) * 100
        porcentaje_no_contestados_dentro_del_termino = 100 - porcentaje_contestados_dentro_del_termino if num_reclamos_recibidos > 0 else 0

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_contestados_dentro_del_termino >= 80 else (
            'Regular' if 60 <= porcentaje_contestados_dentro_del_termino <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Reclamos Contestados Oportunamente.',
            'data': {
                'num_reclamos_recibidos': num_reclamos_recibidos,
                'num_reclamos_contestados_oportunamente': num_reclamos_contestados_dentro_del_termino,
                'porcentaje_contestados_oportunamente': porcentaje_contestados_dentro_del_termino,
                'porcentaje_no_contestados_inoportunamente': porcentaje_no_contestados_dentro_del_termino,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)


#DUODECIMO_INDICADOR_DENUNCIAS_CONTESTADOS_OPORTUNAMENTE
class IndicadorDenunciasContestadasOportunamente(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar denuncias ambientales recibidas (excluir las que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidas = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True) |
            Q(id_estado_actual_solicitud__nombre='GUARDADO')
        ).filter(cod_tipo_PQRSDF='D')

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidas

    def get(self, request, *args, **kwargs):
        queryset_recibidas = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidas)

        # Filtrar los resultados después de recuperarlos
        queryset_contestadas_oportunamente = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion and
            pqrsdf.id_estado_actual_solicitud.nombre in ['NOTIFICADA', 'CERRADA', 'RESPONDIDA']
        ]

        num_denuncias_contestadas_oportunamente = len(queryset_contestadas_oportunamente)

        # Número total de Denuncias Ambientales recibidas
        num_denuncias_recibidas = len(results)

        # Calcular porcentajes con verificación para evitar división por cero
        porcentaje_contestadas_oportunamente = 0 if num_denuncias_recibidas == 0 else (num_denuncias_contestadas_oportunamente / num_denuncias_recibidas) * 100
        porcentaje_no_contestadas_oportunamente = 100 - porcentaje_contestadas_oportunamente if num_denuncias_recibidas > 0 else 0

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_contestadas_oportunamente >= 80 else (
            'Regular' if 60 <= porcentaje_contestadas_oportunamente <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Denuncias Ambientales Contestadas Oportunamente.',
            'data': {
                'num_denuncias_recibidas': num_denuncias_recibidas,
                'num_denuncias_contestadas_oportunamente': num_denuncias_contestadas_oportunamente,
                'porcentaje_contestadas_oportunamente': porcentaje_contestadas_oportunamente,
                'porcentaje_no_contestadas_oportunamente': porcentaje_no_contestadas_oportunamente,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)



#INDICADOR_PQRSDF_VENCIDAS
class IndicadorVencimientoPQRSDF(generics.ListAPIView):
    serializer_class = PQRSDFPostSerializer  # Ajusta el serializador según tus necesidades

    def get_queryset(self):
        # Filtrar PQRSDF recibidas (excluir las que están en estado 'GUARDADO' y sin radicado)
        queryset_recibidas = PQRSDF.objects.exclude(
            Q(id_radicado__isnull=True) |
            Q(id_estado_actual_solicitud__nombre='GUARDADO')
        )

        fecha_radicado_desde = self.request.query_params.get('fecha_radicado_desde')
        fecha_radicado_hasta = self.request.query_params.get('fecha_radicado_hasta')

        if fecha_radicado_desde:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__gte=fecha_radicado_desde)

        if fecha_radicado_hasta:
            queryset_recibidas = queryset_recibidas.filter(fecha_radicado__lte=fecha_radicado_hasta)

        return queryset_recibidas

    def get(self, request, *args, **kwargs):
        queryset_recibidas = self.get_queryset()

        # Obtener todos los resultados de la consulta
        results = list(queryset_recibidas)

        # Filtrar los resultados después de recuperarlos
        queryset_vencidas = [
            pqrsdf for pqrsdf in results
            if pqrsdf.fecha_rta_final_gestion is not None and
            (pqrsdf.fecha_radicado + timedelta(days=pqrsdf.dias_para_respuesta)) - pqrsdf.fecha_rta_final_gestion
        ]

        num_pqrsdf_vencidas = len(queryset_vencidas)

        # Número total de PQRSDF recibidas
        num_pqrsdf_recibidas = len(results)

        # Calcular porcentajes con verificación para evitar división por cero
        porcentaje_vencidas = 0 if num_pqrsdf_recibidas == 0 else (num_pqrsdf_vencidas / num_pqrsdf_recibidas) * 100
        porcentaje_oportunas = 100 - porcentaje_vencidas if num_pqrsdf_recibidas > 0 else 0

        # Calcular rango de cumplimiento
        rango_cumplimiento = 'Excelente' if porcentaje_oportunas >= 80 else (
            'Regular' if 60 <= porcentaje_oportunas <= 79 else 'Deficiente'
        )

        # Retornar resultados
        return Response({
            'success': True,
            'detail': 'Indicador de Vencimiento de PQRSDF.',
            'data': {
                'num_pqrsdf_recibidas': num_pqrsdf_recibidas,
                'num_pqrsdf_vencidas': num_pqrsdf_vencidas,
                'porcentaje_vencidas': porcentaje_vencidas,
                'porcentaje_oportunas': porcentaje_oportunas,
                'rango_cumplimiento': rango_cumplimiento
            }
        }, status=status.HTTP_200_OK)
    

#Radicacion_Email
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# class CustomPageNumberPagination(PageNumberPagination):
#     page_size = 5  
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

class ObtenerCorreosView(generics.ListAPIView):
    # ...

    def save_attachment(self, filename, file_content, save_dir):
        # Crear el directorio si no existe
        os.makedirs(save_dir, exist_ok=True)

        # Calcular el hash MD5 del archivo
        md5_hash = hashlib.md5()
        md5_hash.update(file_content)
        md5_hexdigest = md5_hash.hexdigest()

        # Obtener la extensión del archivo (formato)
        _, file_extension = os.path.splitext(filename)
        formato = file_extension.lower() if file_extension else 'desconocido'

        # Construir el nuevo nombre de archivo con el hash y la extensión
        new_filename = f"{md5_hexdigest}{formato}"

        # Guardar el archivo adjunto en el sistema de archivos local con el nuevo nombre
        file_path = os.path.join(save_dir, new_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Reemplazar barras invertidas con barras diagonales en la ruta del archivo
        file_path = file_path.replace("\\", "/")

        return file_path, md5_hexdigest, formato

    def get(self, request, *args, **kwargs):
        imap_server = imaplib.IMAP4_SSL('imap.gmail.com')

        # Reemplazar con tus credenciales
        imap_server.login('bia@cormacarena.gov.co', 'sbrc bqls wvta jvfm')
        imap_server.select('INBOX')

        current_date = datetime.now()
        current_year = current_date.year

        base_dir = os.path.join("/media", "home", "BIA", "Correos")
        save_dir = os.path.join(base_dir, str(current_year))

        status_email, data = imap_server.search(None, 'ALL')
        email_ids = data[0].split()[::-1]
        total = len(email_ids)

        page = int(self.request.query_params.get('page', 1))
        rango = 5
        lim_final = rango * page
        lim_inicial = lim_final - rango

        lim_final = min(lim_final, total)
        lim_inicial = max(lim_inicial, 0)

        email_ids = email_ids[lim_inicial:lim_final]

        all_emails_info = []

        for email_id in email_ids:
            status_email, email_data = imap_server.fetch(email_id, "(RFC822)")

            raw_email = email_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            subject = decode_header(email_message["Subject"])[0][0]
            sender = decode_header(email_message["From"])[0][0]
            date = email_message["Date"]
            message = ""
            attachments = []

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            message = part.get_payload(decode=True).decode("utf-8")
                        except UnicodeDecodeError:
                            # Manejar errores de decodificación usando otra codificación o estrategia
                            message = part.get_payload(decode=True).decode("latin-1", errors="replace")
                    elif "application" in content_type or "image" in content_type or "audio" in content_type or "video" in content_type:
                        # Archivo adjunto detectado
                        filename = part.get_filename()
                        if filename:
                            decoded_filename, encoding = decode_header(filename)[0]
                            if isinstance(decoded_filename, bytes):
                                try:
                                    decoded_filename = decoded_filename.decode(encoding or 'utf-8')
                                except UnicodeDecodeError:
                                    # Manejar errores de decodificación usando otra codificación o estrategia
                                    decoded_filename = decoded_filename.decode("latin-1", errors="replace")

                            file_content = part.get_payload(decode=True)

                            # Guardar el archivo adjunto con el hash en el nombre y la extensión
                            file_path, md5_hexdigest, formato = self.save_attachment(decoded_filename, file_content, save_dir)

                            attachments.append({
                                'Nombre_archivo': decoded_filename,
                                'ruta': file_path,
                                'md5_hexdigest': md5_hexdigest,
                                'formato': formato
                            })

            all_emails_info.append({
                'ID': email_id,
                'Asunto': subject,
                'Remitente': sender,
                'Fecha': date,
                'Mensaje': message,
                'ArchivosAdjuntos': attachments
            })

        imap_server.logout()

        # Devolver la respuesta con información de paginación
        return Response({
            'success': True,
            'detail': 'BANDEJA DE ENTRADA DE CORREOS ELECTRONICOS.',
            'total_correos': total,
            'página_actual': page,
            'total_páginas': (total + rango - 1) // rango,
            'correos_por_página': rango,
            'data': all_emails_info,
        })
    

#Eliminar_Correo
class EliminarCorreoView(generics.DestroyAPIView):
    
    def delete(self, request, *args, **kwargs):
        try:
            email_id = kwargs.get('email_id')  # Obtén el ID del correo de los parámetros de la URL
            if email_id:
                # Conéctate al servidor IMAP y autentica
                imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
                imap_server.login('bia@cormacarena.gov.co', 'sbrc bqls wvta jvfm')
                imap_server.select('INBOX')

                # Elimina el correo utilizando su ID
                imap_status, _ = imap_server.store(email_id, '+FLAGS', '(\\Deleted)')
                imap_server.expunge()

                # Cierra la conexión
                imap_server.logout()

                if imap_status == 'OK':
                    return Response({'success': True, 'detail': 'Correo eliminado correctamente.'}, status=status.HTTP_200_OK)
                elif imap_status == 'NO':
                    raise ValidationError("No se encontró el correo con el ID proporcionado.")
                else:
                    raise ValidationError("No se pudo eliminar el correo.")
            else:
                raise ValidationError("ID de correo no proporcionado.")
        except Exception as e:
            raise ValidationError(str(e))
        

class ListarMediosParaPQRSDF(generics.ListAPIView):
    serializer_class = MediosSolicitudSerializer
    queryset = MediosSolicitud.objects.all()
    permission_classes = [IsAuthenticated]  # Asegúrate de importar IsAuthenticated de rest_framework.permissions

    def get(self, request):
        medios_pqrsdf = self.queryset.filter(aplica_para_pqrsdf=True)
        serializer = self.serializer_class(medios_pqrsdf, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.','data': serializer.data}, status=status.HTTP_200_OK)



class ListarSucursalesEmpresas(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        return SucursalesEmpresas.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)



class CrearExpedientePQRSDF(generics.CreateAPIView):
    serializer_class = AperturaExpedienteSimpleSerializer
    serializer_class_complejo = AperturaExpedienteComplejoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data

        data_expediente = {}
        request_serializer = {}
        
        # Crear codigo expediente
        tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und=data['id_cat_serie_und_org_ccd_trd_prop']).first()
        
        if not tripleta_trd:
            raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
        
        configuracion_expediente = ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd = tripleta_trd.id_catserie_unidadorg).first()

        if not configuracion_expediente:
            raise ValidationError('No se encontró la configuración de expediente para la tripleta de TRD seleccionada')
        
        cod_unidad = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.codigo
        cod_serie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        cod_subserie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        
        current_date = datetime.now()
        
        
        data_expediente['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie
        data_expediente['codigo_exp_Agno'] = current_date.year
        
        # OBTENER CONSECUTIVO ACTUAL
        codigo_exp_consec_por_agno = None
        
        if configuracion_expediente.cod_tipo_expediente == 'C':
            # LLAMAR CLASE PARA GENERAR CONSECUTIVO
            fecha_actual = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            clase_consec = ConfiguracionTipoExpedienteAgnoGetConsect()
            codigo_exp_consec_por_agno = clase_consec.generar_radicado(
                tripleta_trd.id_catserie_unidadorg,
                request.user.persona.id_persona,
                fecha_actual
            )
            codigo_exp_consec_por_agno = codigo_exp_consec_por_agno.data.get('data').get('consecutivo_actual')
        else:
            expediente = ExpedientesDocumentales.objects.filter(id_cat_serie_und_org_ccd_trd_prop=tripleta_trd.id_catserie_unidadorg, codigo_exp_Agno=current_date.year).first()
        
            if expediente:
                raise ValidationError('Ya existe un expediente simple para este año en la Serie-Subserie-Unidad seleccionada')
            
        data_expediente['titulo_expediente'] = f"Expediente PQRSDF {codigo_exp_und_serie_subserie} {current_date.year}"
        data_expediente['descripcion_expediente'] = f"Expediente PQRSDF para la unidad {codigo_exp_und_serie_subserie} y el año {current_date.year}"
        data_expediente['palabras_clave_expediente'] = f"Expediente|PQRSDF|{codigo_exp_und_serie_subserie}|{current_date.year}"
        data_expediente['id_cat_serie_und_org_ccd_trd_prop'] = tripleta_trd.id_catserie_unidadorg
        data_expediente['id_trd_origen'] = tripleta_trd.id_trd.id_trd
        data_expediente['id_und_seccion_propietaria_serie'] = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional
        data_expediente['id_serie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc
        data_expediente['id_subserie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        data_expediente['codigo_exp_consec_por_agno'] = codigo_exp_consec_por_agno
        data_expediente['estado'] = 'A'
        data_expediente['fecha_apertura_expediente'] = current_date
        data_expediente['fecha_folio_inicial'] = current_date
        data_expediente['cod_etapa_de_archivo_actual_exped'] = 'G'
        data_expediente['tiene_carpeta_fisica'] = False
        data_expediente['ubicacion_fisica_esta_actualizada'] = False
        data_expediente['creado_automaticamente'] = True
        data_expediente['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        data_expediente['id_unidad_org_oficina_respon_original'] = data['id_unidad_org_oficina_respon_original']
        data_expediente['id_und_org_oficina_respon_actual'] = data['id_unidad_org_oficina_respon_original']


        request.data['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        request.data['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie

        
        if configuracion_expediente.cod_tipo_expediente == 'S':
            serializer = self.serializer_class(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        elif configuracion_expediente.cod_tipo_expediente == 'C':
            serializer = self.serializer_class_complejo(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        

        
        # CREAR INDICE - PENDIENTE VALIDAR SI ES CORRECTO REALIZARLO ASÍ
        IndicesElectronicosExp.objects.create(
            id_expediente_doc = expediente_creado,
            fecha_indice_electronico = current_date,
            abierto = True
        )
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(serializer.data.get('codigo_exp_Agno')),
        }
        if codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_modulo" : 188,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
            
        return Response({'success':True, 'detail':'Apertura realizada de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)   

