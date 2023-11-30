
import ast
import copy
from datetime import datetime
import json
import os
from django.forms import model_to_dict
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MediosSolicitud, MetadatosAnexosTmp, T262Radicados, TiposPQR, modulos_radican
from rest_framework.response import Response
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.serializers.pqr_serializers import AnexosPQRSDFPostSerializer, AnexosPQRSDFSerializer, AnexosPostSerializer, AnexosPutSerializer, AnexosSerializer, ArchivosSerializer, InfoDenunciasPQRSDFPostSerializer, InfoDenunciasPQRSDFPutSerializer, InfoDenunciasPQRSDFSerializer, MediosSolicitudCreateSerializer, MediosSolicitudDeleteSerializer, MediosSolicitudSearchSerializer, MediosSolicitudUpdateSerializer, MetadatosPostSerializer, MetadatosPutSerializer, MetadatosSerializer, PQRSDFPanelSerializer, PQRSDFPostSerializer, PQRSDFPutSerializer, PQRSDFSerializer, RadicadoPostSerializer, TiposPQRGetSerializer, TiposPQRUpdateSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate, Estados_PQRDelete
from seguridad.utils import Util

from django.db.models import Q
from django.db import transaction

from transversal.models.personas_models import Personas
from transversal.serializers.personas_serializers import PersonasFilterSerializer
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
                    valores_creados_detalles = anexosCreate.create_anexos_pqrsdf(anexos, data_PQRSDF_creado['id_PQRSDF'], isCreateForWeb, fecha_actual)
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
        data_pqrsdf_update['requiereDigitalizacion'] = False
        pqrsdf_update = PrsdfUpdate.update_pqrsdf(pqr_instance, data_pqrsdf_update)
        return pqrsdf_update

    def set_data_pqrsdf(self, data, fecha_actual):
        data['fecha_registro'] = data['fecha_ini_estado_actual'] = fecha_actual
        data['requiereDigitalizacion'] = True if data['cantidad_anexos'] != 0 else False
    
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
            raise({'success': False, 'detail': str(e)})
    
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
            data_anexos_create = [anexo for anexo in anexos if 'id_anexo' not in list(anexo.keys())]
            anexos_create = util_PQR.set_archivo_in_anexo(data_anexos_create, archivos, "create")
            
            data_anexos_update = [anexo for anexo in anexos if 'id_anexo' in list(anexo.keys())]
            anexos_update = util_PQR.set_archivo_in_anexo(data_anexos_update, archivos, "update")

            ids_anexos_update = [anexo_update['id_anexo'] for anexo_update in anexos_update]
            anexos_delete = [anexo_pqr for anexo_pqr in anexos_pqr_DB if getattr(anexo_pqr,'id_anexo_id') not in ids_anexos_update]

            anexosCreate = AnexosCreate()
            anexosUpdate = AnexosUpdate()
            anexosDelete = AnexosDelete()

            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos_create, id_PQRSDF, isCreateForWeb, fecha_actual)
            data_auditoria_update = anexosUpdate.put(anexos_update, fecha_actual)
            data_auditoria_delete = anexosDelete.delete(anexos_delete)
            
        else:
            anexosCreate = AnexosCreate()
            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos, id_PQRSDF, isCreateForWeb, fecha_actual)

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

        #Obtiene los dias para la respuesta del PQRSDF
        tipo_pqr = self.get_tipos_pqr(data_PQRSDF_instance.cod_tipo_PQRSDF)
        dias_respuesta = tipo_pqr.tiempo_respuesta_en_dias
        
        #Crea el radicado
        data_for_create = {}
        data_for_create['fecha_actual'] = fecha_actual
        data_for_create['id_usuario'] = id_persona_guarda
        data_for_create['tipo_radicado'] = "E"
        data_for_create['modulo_radica'] = "PQRSDF"
        radicadoCreate = RadicadoCreate()
        data_radicado = radicadoCreate.post(data_for_create)

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
            radicado_data = self.set_data_radicado(config_tipos_radicado, data_radicado['fecha_actual'], data_radicado['id_usuario'], data_radicado['modulo_radica'])
            serializer = self.serializer_class(data=radicado_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise({'success': False, 'detail': str(e)})


    def get_config_tipos_radicado(self, request):
        data_request = {
            'id_persona': request['id_usuario'],
            'cod_tipo_radicado': request['tipo_radicado'],
            'fecha_actual': request['fecha_actual']
        }
        config_tipos_radicados = self.config_radicados.generar_n_radicado(self, data_request)
        config_tipos_radicado_data = config_tipos_radicados.data['data']
        if config_tipos_radicado_data['implementar'] == False:
            raise ValidationError("El sistema requiere que se maneje un radicado de entrada o unico, debe solicitar al administrador del sistema la configuración del radicado")
        else:
            return config_tipos_radicado_data
        
    def set_data_radicado(self, config_tipos_radicado, fecha_actual, id_usuario, modulo_radica):
        radicado = {}
        radicado['cod_tipo_radicado'] = config_tipos_radicado['cod_tipo_radicado']
        radicado['prefijo_radicado'] = config_tipos_radicado['prefijo_consecutivo']
        radicado['agno_radicado'] = config_tipos_radicado['agno_radicado']
        radicado['nro_radicado'] = config_tipos_radicado['consecutivo_actual']
        radicado['fecha_radicado'] = fecha_actual
        radicado['id_persona_radica'] = id_usuario

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
          raise ({'success': False, 'detail': str(e)})
        
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
            raise({'success': False, 'detail': str(e)})   


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
            raise({'success': False, 'detail': str(e)})



########################## ANEXOS Y ANEXOS PQR ##########################
class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer
    
    def create_anexos_pqrsdf(self, anexos, id_PQRSDF, isCreateForWeb, fecha_actual):
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
            raise({'success': False, 'detail': str(e)})

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
            raise({'success': False, 'detail': str(e)})
        
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
            raise({'success': False, 'detail': str(e)})

class AnexosPQRCreate(generics.CreateAPIView):
    serializer_class = AnexosPQRSDFPostSerializer
    
    def crear_anexo_pqr(self, request):
        try:
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        except Exception as e:
            raise({'success': False, 'detail': str(e)})
        
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
            raise({'success': False, 'detail': str(e)})
        
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
            raise({'success': False, 'detail': str(e)})
    
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
          raise({'success': False, 'detail': str(e)})
        
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
          raise({'success': False, 'detail': str(e)})

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