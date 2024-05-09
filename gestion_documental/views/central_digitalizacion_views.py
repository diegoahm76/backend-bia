import copy
from datetime import datetime, timedelta
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, MetadatosAnexosTmp, Otros, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from seguridad.permissions.permissions_gestor import PermisoActualizarCentralDigitalizacion, PermisoBorrarCentralDigitalizacion, PermisoCrearCentralDigitalizacion
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, SolicitudesTramites
from django.db.models import Q
from django.db import transaction
from django.forms import model_to_dict
from gestion_documental.models.trd_models import TipologiasDoc

from gestion_documental.serializers.central_digitalizacion_serializers import SolicitudesAlUsuarioPostSerializer, SolicitudesPostSerializer, SolicitudesSerializer
from gestion_documental.serializers.pqr_serializers import AnexosPostSerializer, MetadatosPostSerializer, MetadatosPutSerializer, OpasMetadatosPostSerializer, OpasMetadatosPutSerializer, OtrosMetadatosPostSerializer, OtrosMetadatosPutSerializer, PQRSDFPutSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import ComplementosUsu_PQRPutSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate
from gestion_documental.views.pqr_views import AnexosCreate, ArchivoDelete, MetadatosPQRDelete
from seguridad.signals.roles_signals import IsAuthenticated

class SolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            tipo_solicitud = request.query_params.get('tipo_solicitud', None)
            estado_solicitud = request.query_params.get('estado_solicitud', None)
            numero_radicado = request.query_params.get('numero_radicado', None)

            #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
            condiciones = Q()
            if tipo_solicitud:
                condiciones &= ~Q(id_pqrsdf=0) and ~Q(id_pqrsdf=None) if tipo_solicitud == 'PQR' else ~Q(id_complemento_usu_pqr=0) and ~Q(id_complemento_usu_pqr=None)
            condiciones &= Q(digitalizacion_completada = False, devuelta_sin_completar = False)
            solicitudes_pqr = self.queryset.filter(condiciones).order_by('fecha_solicitud')

            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudes = ProcesaSolicitudes()
            solicitudes_pendientes = procesaSolicitudes.procesa_solicitudes(solicitudes_pqr, tipo_solicitud, estado_solicitud, numero_radicado, 'P')

            serializer = self.serializer_class(solicitudes_pendientes, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class SolicitudesRespondidasGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    querysetRadicados = T262Radicados.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            tipo_solicitud = request.query_params.get('tipo_solicitud', None)
            fecha_desde = request.query_params.get('fecha_desde', None)
            fecha_hasta = request.query_params.get('fecha_hasta', None)

            #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
            condiciones = self.set_conditions_filters(tipo_solicitud, fecha_desde, fecha_hasta)
            solicitudes_respondidas_pqr = self.queryset.filter(condiciones).order_by('fecha_rta_solicitud')

            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudes = ProcesaSolicitudes()
            solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitudes_respondidas_pqr, tipo_solicitud, None, None, 'R')

            serializer = self.serializer_class(solicitudes_respondidas, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def set_conditions_filters(self, tipo_solicitud, fecha_desde, fecha_hasta):
        condiciones = Q()
        if tipo_solicitud or (fecha_desde and fecha_hasta):
            if tipo_solicitud:
                condiciones &= ~Q(id_pqrsdf=0) and ~Q(id_pqrsdf=None) if tipo_solicitud == 'PQR' else ~Q(id_complemento_usu_pqr=0) and ~Q(id_complemento_usu_pqr=None)
            if fecha_desde and fecha_hasta:
                condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_hasta)
        else:
            fecha_actual = datetime.now()
            fecha_desde = fecha_actual - timedelta(days=7)
            condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_actual)

        condiciones &= Q(Q(digitalizacion_completada = True) | Q(devuelta_sin_completar = True))
        return condiciones
    
class SolicitudByIdGet(generics.GenericAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    querysetRadicados = T262Radicados.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_solicitud):
        try:
            solicitud = self.queryset.filter(id_solicitud_de_digitalizacion = id_solicitud)
            if solicitud:
                #Obtiene los datos de la solicitud y anexos para serializar
                procesaSolicitudes = ProcesaSolicitudes()
                peticion_estado = "P" if not solicitud.first().devuelta_sin_completar and not solicitud.first().digitalizacion_completada else "R"
                solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitud, None, None, None, peticion_estado)

                serializer = self.serializer_class(solicitudes_respondidas, many=True)
                return Response({'success':True, 'detail':'Se encontro la solicitud por el id asociado', 'data':serializer.data[0]}, status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No se encontro la solicitud por el id asociado'},status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        
class ProcesaSolicitudes:
    querysetRadicados = T262Radicados.objects.all()

    def procesa_solicitudes(self, solicitudes_pqr, tipo_solicitud, estado_solicitud, numero_radicado, peticion_estado):
        #En caso de tener filtro por radicados, obtiene todos los radicados que finalicen por el numero digitado
        radicados = []
        solicitudes = []
        if numero_radicado:
            radicados = self.querysetRadicados.filter(nro_radicado__icontains=numero_radicado)
            if len(radicados) == 0:
                raise NotFound("No se encontraron radicados por el numero de radicado ingresado")
        
        for solicitud_pqr in solicitudes_pqr:
            if tipo_solicitud == 'PQR' or (tipo_solicitud == None and solicitud_pqr.id_pqrsdf_id):
                data_anexos_pqrsd = self.consulta_anexos_pqrsdf(solicitud_pqr, radicados, estado_solicitud, peticion_estado)
                if data_anexos_pqrsd:
                    solicitudes.append(data_anexos_pqrsd)
            else:
                data_anexos_complementos_pqrsd = self.consulta_anexos_complementos_pqrsdf(solicitud_pqr, radicados, estado_solicitud, peticion_estado)
                if data_anexos_complementos_pqrsd:
                    solicitudes.append(data_anexos_complementos_pqrsd)
        
        return solicitudes


    def consulta_anexos_pqrsdf(self, solicitud_pqr, radicados, estado_solicitud, peticion_estado):
        solicitud_model = None
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF = solicitud_pqr.id_pqrsdf_id).first()
        radicado = self.get_radicado(radicados, pqrsdf.id_radicado_id)
        if radicado:
            instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            radicado_nuevo = instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            
            # Obtiene los anexos
            anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = pqrsdf.id_PQRSDF)
            ids_anexos = [anexo_pqr.id_anexo_id for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            validate_anexos = self.valida_anexos_filtro_estado(anexos, estado_solicitud)

            if validate_anexos:
                #Obtiene el modelo de solicitud a serializar
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "PQR", pqrsdf.asunto,  pqrsdf.id_persona_titular_id, pqrsdf.cantidad_anexos, radicado_nuevo, anexos, peticion_estado)
        
        return solicitud_model

    def consulta_anexos_complementos_pqrsdf(self, solicitud_pqr, radicados, estado_solicitud, peticion_estado):
        solicitud_model = None
        complemento_usu_pqrsdf = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR = solicitud_pqr.id_complemento_usu_pqr_id).first()
        radicado = self.get_radicado(radicados, complemento_usu_pqrsdf.id_radicado_id)
        if radicado:
            instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            radicado_nuevo = instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            # Obtiene los anexos
            anexos_pqr = Anexos_PQR.objects.filter(id_complemento_usu_PQR = complemento_usu_pqrsdf.idComplementoUsu_PQR)
            ids_anexos = [anexo_pqr.id_anexo_id for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            validate_anexos = self.valida_anexos_filtro_estado(anexos, estado_solicitud)

            #Obtiene el id del titular para el complemento pqr
            id_PQRSDF = complemento_usu_pqrsdf.id_PQRSDF_id
            if complemento_usu_pqrsdf.id_solicitud_usu_PQR:
                solicitud_usuario = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_solicitud_al_usuario_sobre_pqrsdf = complemento_usu_pqrsdf.id_solicitud_usu_PQR_id).first()
                id_PQRSDF = solicitud_usuario.id_pqrsdf_id

            pqrsdf = PQRSDF.objects.filter(id_PQRSDF = id_PQRSDF).first()


            if validate_anexos:
                #Obtiene el modelo de solicitud a serializar
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "CDPQR", complemento_usu_pqrsdf.asunto,  pqrsdf.id_persona_titular_id, complemento_usu_pqrsdf.cantidad_anexos, radicado_nuevo, anexos, peticion_estado)
        
        return solicitud_model


    def get_radicado(self, radicados, id_radicado):
        if len(radicados) > 0:
            radicado = radicados.filter(id_radicado = id_radicado).first()
        else:
            radicado = self.querysetRadicados.filter(id_radicado = id_radicado).first()
        
        return radicado
    
    def valida_anexos_filtro_estado(self, anexos, estado_solicitud):
        validate_anexos = True
        if estado_solicitud:
            if estado_solicitud == 'SH':
                validate_anexos =  all(not anexo.ya_digitalizado for anexo in anexos)
            else:
                validate_anexos = any(anexo.ya_digitalizado for anexo in anexos)
        
        return validate_anexos
    
    def set_data_solicitudes(self, solicitud, cod_tipo_solicitud, asunto, id_persona_titular, cantidad_anexos, radicado, anexos, peticion_estado):
        solicitud_model = {}
        solicitud_model['id_solicitud_de_digitalizacion'] = solicitud.id_solicitud_de_digitalizacion
        solicitud_model['fecha_solicitud'] = solicitud.fecha_solicitud
        solicitud_model['fecha_rta_solicitud'] = solicitud.fecha_rta_solicitud
        solicitud_model['cod_tipo_solicitud'] = cod_tipo_solicitud
        solicitud_model['asunto'] = asunto
        solicitud_model['id_persona_titular'] = id_persona_titular
        solicitud_model['numero_anexos'] = cantidad_anexos
        solicitud_model['radicado'] = radicado
        solicitud_model['anexos'] = anexos
        solicitud_model['peticion_estado'] = peticion_estado
        solicitud_model['devuelta_sin_completar'] = solicitud.devuelta_sin_completar
        solicitud_model['digitalizacion_completada'] = solicitud.digitalizacion_completada

        return solicitud_model

class DigitalizacionCreate(generics.CreateAPIView):
    serializer_class = MetadatosPostSerializer
    serializer_anexos_class = AnexosPostSerializer
    serializer_solicitud_class = SolicitudesPostSerializer
    permission_classes = [IsAuthenticated, PermisoCrearCentralDigitalizacion]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                fecha_actual = datetime.now()
                data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))

                #Guardar el archivo en la tabla T238
                archivo = request.data.get('archivo', None)
                if archivo:
                    archivo_creado = self.create_archivo_adjunto(archivo, fecha_actual)
                else:
                    raise ValidationError("Se debe tener un archivo para digitalizar el anexo")
                
                #Crea el metadato en la DB
                data_to_create = self.set_data_metadato(data_digitalizacion, fecha_actual, archivo_creado.data.get('data').get('id_archivo_digital'))
                serializer = self.serializer_class(data=data_to_create)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                #Actualiza las tablas de anexos y solicitudes
                self.update_anexo(data_digitalizacion['observacion_digitalizacion'], data_digitalizacion['id_anexo'])
                self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], data_digitalizacion['id_persona_digitalizo'])
                
                return Response({'success':True, 'detail':'Se digitalizo correctamente el anexo', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create_archivo_adjunto(self, archivo, fecha_actual):
        if archivo:
            anexosCreate = AnexosCreate()
            archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
            return archivo_creado
        else:
            raise ValidationError("No se puede digitalizar anexos sin archivo adjunto")
        
    def set_data_metadato(self, data_metadatos, fecha_actual, id_archivo_digital):
        data_metadatos['fecha_creacion_doc'] = fecha_actual
        data_metadatos['es_version_original'] = True
        data_metadatos['id_archivo_sistema'] = id_archivo_digital
        
        return data_metadatos
    
    def update_anexo(self, observacion_digitalizacion, id_anexo):
        anexo_db = Anexos.objects.filter(id_anexo = id_anexo).first()
        anexo_db_instance = copy.copy(anexo_db)
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion
        anexo_update = model_to_dict(anexo_db)
        serializer_anexo = self.serializer_anexos_class(anexo_db_instance, data=anexo_update, many=False)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion = id_solicitud_de_digitalizacion).first()
        solicitud_db_instance = copy.copy(solicitud_db)
        solicitud_db.id_persona_digitalizo_id = id_persona_digitalizo
        solicitud_update = model_to_dict(solicitud_db)
        serializer_solicitud = self.serializer_solicitud_class(solicitud_db_instance, data=solicitud_update, many=False)
        serializer_solicitud.is_valid(raise_exception=True)
        serializer_solicitud.save()
    
class DigitalizacionUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = MetadatosPutSerializer
    serializer_anexos_class = AnexosPostSerializer
    serializer_solicitud_class = SolicitudesPostSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarCentralDigitalizacion]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                fecha_actual = datetime.now()
                data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
                archivo = request.data.get('archivo', None)

                metadato_db = self.queryset.filter(id_metadatos_anexo_tmp = data_digitalizacion['id_metadatos_anexo_tmp']).first()
                if metadato_db:
                    #Guardar el archivo en la tabla T238
                    if archivo:
                        archivo_creado = self.actualizar_archivo(request.data['archivo'], fecha_actual, data_digitalizacion['id_archivo_sistema'])
                        data_digitalizacion['id_archivo_sistema'] = archivo_creado.data.get('data').get('id_archivo_digital')
                    
                    serializer = self.serializer_class(metadato_db, data=data_digitalizacion, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    #Actualiza las tablas de anexos y solicitudes
                    self.update_anexo(data_digitalizacion['observacion_digitalizacion'], data_digitalizacion['id_anexo'])
                    self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], data_digitalizacion['id_persona_digitalizo'])

                    return Response({'success':True, 'detail':'Se edito la digitalización del anexo correctamente', 'data':serializer.data}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró el metadato que intenta actualizar')
                
        except Exception as e:
           return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def actualizar_archivo(self, archivo, fecha_actual, id_archivo_anterior):
        #Borra archivo anterior del metadato
        archivoDelete = ArchivoDelete()
        archivoDelete.delete(id_archivo_anterior)

        #Crea el nuevo archivo
        anexosCreate = AnexosCreate()
        archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
        return archivo_creado
    
    def update_anexo(self, observacion_digitalizacion, id_anexo):
        anexo_db = Anexos.objects.filter(id_anexo = id_anexo).first()
        anexo_db_instance = copy.copy(anexo_db)
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion
        anexo_update = model_to_dict(anexo_db)
        serializer_anexo = self.serializer_anexos_class(anexo_db_instance, data=anexo_update, many=False)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion = id_solicitud_de_digitalizacion).first()
        solicitud_db_instance = copy.copy(solicitud_db)
        solicitud_db.id_persona_digitalizo_id = id_persona_digitalizo
        solicitud_update = model_to_dict(solicitud_db)
        serializer_solicitud = self.serializer_solicitud_class(solicitud_db_instance, data=solicitud_update, many=False)
        serializer_solicitud.is_valid(raise_exception=True)
        serializer_solicitud.save()

class DigitalizacionDelete(generics.RetrieveDestroyAPIView):
    serializer_class = SolicitudesPostSerializer
    serializer_anexos_class = AnexosPostSerializer
    serializer_solicitud_class = SolicitudesPostSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated, PermisoBorrarCentralDigitalizacion]

    @transaction.atomic
    def delete(self, request):
        try:
            with transaction.atomic():
                #Parametros para eliminacion
                if request.query_params.get('id_anexo')==None or request.query_params.get('id_persona_digitalizo')==None or request.query_params.get('id_solicitud_de_digitalizacion')==None:
                    raise ValidationError('No se ingresaron parámetros necesarios para eliminar el PQRSDF')
                id_anexo = int(request.query_params.get('id_anexo', 0))
                id_persona_digitalizo = int(request.query_params.get('id_persona_digitalizo', 0))
                id_solicitud_de_digitalizacion = int(request.query_params.get('id_solicitud_de_digitalizacion', 0))

                #Invoca el metodo de borrado de metadatos que borra el metadato por el id del anexo y a su ves borra el archivo
                metadatosPQRDelete = MetadatosPQRDelete()
                metadatosPQRDelete.delete(id_anexo)
                
                #Actualiza los datos ya_Digitalizado y observacionDigitalizacion del anexo y la persona que borro la digitalizacion en la solicitud
                self.update_anexo(id_anexo)
                self.update_solicitud(id_solicitud_de_digitalizacion, id_persona_digitalizo)

                return Response({'success':True, 'detail':'Se elimino la digitalización del anexo correctamente'}, status=status.HTTP_200_OK)

        except Exception as e:
           return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    def update_anexo(self, id_anexo):
        anexo_db = Anexos.objects.filter(id_anexo = id_anexo).first()
        anexo_db_instance = copy.copy(anexo_db)
        anexo_db.ya_digitalizado = False
        anexo_db.observacion_digitalizacion = None
        anexo_update = model_to_dict(anexo_db)
        serializer_anexo = self.serializer_anexos_class(anexo_db_instance, data=anexo_update, many=False)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion = id_solicitud_de_digitalizacion).first()
        solicitud_db_instance = copy.copy(solicitud_db)
        solicitud_db.id_persona_digitalizo_id = id_persona_digitalizo
        solicitud_update = model_to_dict(solicitud_db)
        serializer_solicitud = self.serializer_solicitud_class(solicitud_db_instance, data=solicitud_update, many=False)
        serializer_solicitud.is_valid(raise_exception=True)
        serializer_solicitud.save()

class ResponderDigitalizacion(generics.RetrieveUpdateAPIView):
    serializer_class = SolicitudesPostSerializer
    serializer_comp_class = ComplementosUsu_PQRPutSerializer
    serializer_solicitudesUsu_class = SolicitudesAlUsuarioPostSerializer
    serializer_pqrsdf_class = PQRSDFPutSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarCentralDigitalizacion]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                fecha_actual = datetime.now()
                id_persona_digitalizo = request.data['id_persona_digitalizo']
                digitalizacion_completada = request.data['digitalizacion_completada']
                solicitud_responder = self.queryset.filter(id_solicitud_de_digitalizacion = request.data['id_solicitud_de_digitalizacion']).first()
                if solicitud_responder:
                    solicitud_db_instance = copy.copy(solicitud_responder)
                    solicitud_responder.fecha_rta_solicitud = fecha_actual
                    solicitud_responder.observacion_digitalizacion = request.data['observacion_digitalizacion']
                    solicitud_responder.digitalizacion_completada = digitalizacion_completada
                    solicitud_responder.devuelta_sin_completar = not solicitud_responder.digitalizacion_completada
                    solicitud_responder.id_persona_digitalizo_id = id_persona_digitalizo
                    solicitud_update = model_to_dict(solicitud_responder)
                    serializer = self.serializer_class(solicitud_db_instance, data=solicitud_update, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    self.crear_historico_estados(solicitud_responder.id_pqrsdf_id, solicitud_responder.id_complemento_usu_pqr_id, fecha_actual, id_persona_digitalizo, digitalizacion_completada)

                    return Response({'success':True, 'detail':'La solicitud ha sido respondida correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró la solicitud que intenta responder')
        
        except Exception as e:
           return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def crear_historico_estados(self, id_pqrsdf, id_complemento_pqrsdf, fecha_actual, id_persona_digitalizo, digitalizacion_completada):
        estado_pqrsdf_inicial = Estados_PQR.objects.filter(Q(PQRSDF=id_pqrsdf, estado_solicitud=3)).first()
        if id_pqrsdf:
            data_estado_crear = self.set_data_estado_pqrsdf(id_pqrsdf, None, fecha_actual, id_persona_digitalizo, estado_pqrsdf_inicial.id_estado_PQR, 10)
            creador_estados = Estados_PQRCreate()
            creador_estados.crear_estado(data_estado_crear)

            sin_pendientes = self.crear_estado_sin_pendientes(id_pqrsdf, fecha_actual, id_persona_digitalizo, estado_pqrsdf_inicial.id_estado_PQR)

            pqrsdf_db = PQRSDF.objects.filter(id_PQRSDF = id_pqrsdf).first()
            pqrsdf_db_instance = copy.copy(pqrsdf_db)
            pqrsdf_db.fecha_envio_definitivo_a_digitalizacion = pqrsdf_db.fecha_envio_definitivo_a_digitalizacion if digitalizacion_completada else None
            pqrsdf_db.fecha_digitalizacion_completada = fecha_actual if digitalizacion_completada else pqrsdf_db.fecha_digitalizacion_completada
            pqrsdf_db.id_estado_actual_solicitud_id = 4 if sin_pendientes else pqrsdf_db.id_estado_actual_solicitud_id
            pqrsdf_db.fecha_ini_estado_actual = fecha_actual if sin_pendientes else pqrsdf_db.fecha_ini_estado_actual
            pqrsdf_update = model_to_dict(pqrsdf_db)
            serializer_pqrsdf = self.serializer_pqrsdf_class(pqrsdf_db_instance, data=pqrsdf_update, many=False)
            serializer_pqrsdf.is_valid(raise_exception=True)
            serializer_pqrsdf.save()

        else:
            data_estado_crear = self.set_data_estado_complemento_pqrsdf(id_complemento_pqrsdf, digitalizacion_completada, fecha_actual, id_persona_digitalizo)

    def crear_estado_sin_pendientes(self, id_pqrsdf, fecha_actual, id_persona_digitalizo, estado_PQR_asociado):
        sin_pendientes = False
        estados_pqrsdf_pendientes = Estados_PQR.objects.filter(Q(PQRSDF=id_pqrsdf, estado_PQR_asociado=estado_PQR_asociado))
        
        #Obtiene todos los tipos de solicitud creadas
        solicitudes_dig_enviadas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=9))
        solicitudes_dig_respondidas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=10))
        solicitudes_usu_enviadas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=11))
        solicitudes_usu_respondidas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=12))

        if solicitudes_dig_enviadas == solicitudes_dig_respondidas and solicitudes_usu_enviadas == solicitudes_usu_respondidas:
            data_estado_crear = self.set_data_estado_pqrsdf(id_pqrsdf, None, fecha_actual, id_persona_digitalizo, None, 4)
            creador_estados = Estados_PQRCreate()
            creador_estados.crear_estado(data_estado_crear)
            sin_pendientes = True
        
        return sin_pendientes 

    def set_data_estado_complemento_pqrsdf(self, id_complemento_pqrsdf, digitalizacion_completada, fecha_actual, id_persona_digitalizo):
        complemento_db = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR = id_complemento_pqrsdf).first()
        complemento_db_instance = copy.copy(complemento_db)
        if complemento_db.id_solicitud_usu_PQR_id:
            estado_PQR_asociado = 8 if digitalizacion_completada else 6
            #TODO: PREGUNTAR POR ESTE CASO 3 YA QUE NO SE SI EL CONSULTAR ESTA BIEN O DEBO ENVIAR DIRECTAMENTE EL NUMERO QUEMADO
            estado_pqrsdf_inicial = Estados_PQR.objects.filter(Q(solicitud_usu_sobre_PQR=complemento_db.id_solicitud_usu_PQR_id, estado_solicitud=estado_PQR_asociado)).first()
            
            data_estado_crear = self.set_data_estado_pqrsdf(None, complemento_db.id_solicitud_usu_PQR_id, fecha_actual, id_persona_digitalizo, estado_pqrsdf_inicial.id_estado_PQR, 10)
            creador_estados = Estados_PQRCreate()
            creador_estados.crear_estado(data_estado_crear)
            if digitalizacion_completada:
                self.update_solicitud_usuario(complemento_db.id_solicitud_usu_PQR_id, fecha_actual)

        complemento_db.fecha_envio_definitivo_digitalizacion = complemento_db.fecha_envio_definitivo_digitalizacion if digitalizacion_completada else None
        complemento_db.fecha_digitalizacion_completada = fecha_actual if digitalizacion_completada else complemento_db.fecha_digitalizacion_completada
        complemento_update = model_to_dict(complemento_db)
        serializer_comp = self.serializer_comp_class(complemento_db_instance, data=complemento_update, many=False)
        serializer_comp.is_valid(raise_exception=True)
        serializer_comp.save()

    def set_data_estado_pqrsdf(self, id_pqrsdf, solicitud_usu_sobre_PQR, fecha_actual, id_persona_digitalizo, estado_PQR_asociado, estado_solicitud):
        data_estado = {}
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['PQRSDF'] = id_pqrsdf if id_pqrsdf else None
        data_estado['solicitud_usu_sobre_PQR'] = solicitud_usu_sobre_PQR if solicitud_usu_sobre_PQR else None
        data_estado['estado_PQR_asociado'] = estado_PQR_asociado
        data_estado['estado_solicitud'] = estado_solicitud
        data_estado['persona_genera_estado'] = id_persona_digitalizo
        return data_estado
    
    def update_solicitud_usuario(self, id_solicitud_usu_PQR, fecha_actual):
        solicitud_usu_db = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_solicitud_al_usuario_sobre_pqrsdf = id_solicitud_usu_PQR).first()
        solicitud_usu_db_instance = copy.copy(solicitud_usu_db)
        solicitud_usu_db.id_estado_actual_solicitud_id = 8
        solicitud_usu_db.fecha_ini_estado_actual = fecha_actual
        solicitud_usu_update = model_to_dict(solicitud_usu_db)
        serializer_solicitud_usu = self.serializer_solicitudesUsu_class(solicitud_usu_db_instance, data=solicitud_usu_update, many=False)
        serializer_solicitud_usu.is_valid(raise_exception=True)
        serializer_solicitud_usu.save()

class ProcesaSolicitudesOtros:
    querysetRadicados = T262Radicados.objects.all()

    def procesa_solicitudes(self, solicitudes_otros, estado_solicitud, peticion_estado):
        solicitudes = []
        for solicitud_otro in solicitudes_otros:
            data_anexos_otros = self.consulta_anexos_otros(solicitud_otro, estado_solicitud, peticion_estado)
            if data_anexos_otros:
                solicitudes.append(data_anexos_otros)
        
        return solicitudes

    def consulta_anexos_otros(self, solicitud_otro, estado_solicitud, peticion_estado):
        solicitud_model = None
        otro = solicitud_otro.id_otro
        radicado = otro.id_radicados
        
        if radicado:
            instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            radicado_nuevo= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            # Obtiene los anexos
            anexos_otros = Anexos_PQR.objects.filter(id_otros = solicitud_otro.id_otro)
            ids_anexos = [anexo_otro.id_anexo.id_anexo for anexo_otro in anexos_otros]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            validate_anexos = self.valida_anexos_filtro_estado(anexos, estado_solicitud)

            if validate_anexos:
                #Obtiene el modelo de solicitud a serializar
                solicitud_model = self.set_data_solicitudes(solicitud_otro, "OTROS", otro.asunto, otro.id_persona_titular.id_persona, otro.cantidad_anexos, radicado_nuevo, anexos, peticion_estado)
        
        return solicitud_model
    
    def valida_anexos_filtro_estado(self, anexos, estado_solicitud):
        validate_anexos = True
        if estado_solicitud:
            if estado_solicitud == 'SH':
                validate_anexos =  all(not anexo.ya_digitalizado for anexo in anexos)
            else:
                validate_anexos = any(anexo.ya_digitalizado for anexo in anexos)
        
        return validate_anexos
    
    def set_data_solicitudes(self, solicitud, cod_tipo_solicitud, asunto, id_persona_titular, cantidad_anexos, radicado, anexos, peticion_estado):
        solicitud_model = {}
        solicitud_model['id_solicitud_de_digitalizacion'] = solicitud.id_solicitud_de_digitalizacion
        solicitud_model['fecha_solicitud'] = solicitud.fecha_solicitud
        solicitud_model['fecha_rta_solicitud'] = solicitud.fecha_rta_solicitud
        solicitud_model['cod_tipo_solicitud'] = cod_tipo_solicitud
        solicitud_model['asunto'] = asunto
        solicitud_model['id_persona_titular'] = id_persona_titular
        solicitud_model['numero_anexos'] = cantidad_anexos
        solicitud_model['radicado'] = radicado
        solicitud_model['anexos'] = anexos
        solicitud_model['peticion_estado'] = peticion_estado
        solicitud_model['devuelta_sin_completar'] = solicitud.devuelta_sin_completar
        solicitud_model['digitalizacion_completada'] = solicitud.digitalizacion_completada

        return solicitud_model

class OtrosSolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            estado_solicitud = request.query_params.get('estado_solicitud', None)
            numero_radicado = request.query_params.get('numero_radicado', None)

            #Filtra las solicitudes que no este completada
            solicitudes_otros = self.queryset.filter(digitalizacion_completada=False, devuelta_sin_completar=False).exclude(id_otro=None).order_by('fecha_solicitud')

            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudesOtros = ProcesaSolicitudesOtros()
            solicitudes_pendientes = procesaSolicitudesOtros.procesa_solicitudes(solicitudes_otros, estado_solicitud, 'P')

            serializer = self.serializer_class(solicitudes_pendientes, many=True)
            serializer_data = serializer.data
            
            if numero_radicado:
                serializer_data = [data for data in serializer_data if numero_radicado.lower() in data['numero_radicado'].lower()]
            
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OtrosDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = OtrosMetadatosPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            if anexo.ya_digitalizado:
                raise PermissionDenied("El anexo ya fue digitalizado antes. No puede volverlo a digitalizar")

            #Guardar el archivo en la tabla T238
            archivo = request.data.get('archivo', None)
            if archivo:
                if data_digitalizacion['cod_origen_archivo'] == 'F':
                    raise ValidationError("Debe descartar el archivo adjunto, se generará uno de referencia")
                
                archivo_creado = self.create_archivo_adjunto(archivo, fecha_actual)
            else:
                if data_digitalizacion['cod_origen_archivo'] == 'F':
                    if data_digitalizacion['nro_folios_documento'] != 1:
                        raise ValidationError("El número de folios debe ser uno porque el archivo que va a generar el sistema solamente es de una hoja")
                    
                    choices_dict_categoria_archivo = dict(tipo_archivo_CHOICES)
                    categoria_archivo = choices_dict_categoria_archivo[data_digitalizacion['cod_categoria_archivo']]
                    tipologia_documental = data_digitalizacion["tipologia_no_creada_TRD"] if data_digitalizacion.get("tipologia_no_creada_TRD") else TipologiasDoc.objects.filter(id_tipologia_documental=data_digitalizacion["id_tipologia_doc"]).first().nombre
                    
                    info_archivo = {
                        "Nombre del Anexo": "Mapa de Proceso",
                        "Medio de Almacenamiento": "Papel",
                        "Asunto": data_digitalizacion["asunto"],
                        "Categoria del Archivo": categoria_archivo,
                        "Tipología Documental": tipologia_documental
                    }
                    archivo_creado =  UtilsGestor.generar_archivo_blanco(info_archivo, "Mapa de Proceso.pdf", "home,BIA,Otros,GDEA,Anexos_PQR")
            
            metadato_db = MetadatosAnexosTmp.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            
            #Crea el metadato en la DB
            data_to_create = self.set_data_metadato(data_digitalizacion, fecha_actual, archivo_creado.data.get('data').get('id_archivo_digital'))
            serializer = self.serializer_class(data=data_to_create) if not metadato_db else self.serializer_class(metadato_db, data=data_to_create, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            id_persona_digitalizo = request.user.persona

            #Actualiza las tablas de anexos y solicitudes
            self.update_anexo(data_digitalizacion['observacion_digitalizacion'], anexo)
            self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], id_persona_digitalizo)
            
            return Response({'success':True, 'detail':'Se digitalizo correctamente el anexo', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        
    def create_archivo_adjunto(self, archivo, fecha_actual):
        # PENDIENTE AÑADIR GENERACIÓN DE DOCUMENTO CUANDO ES FÍSICO
        if archivo:
            anexosCreate = AnexosCreate()
            archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
            return archivo_creado
        else:
            raise ValidationError("No se puede digitalizar anexos sin archivo adjunto")
        
    def set_data_metadato(self, data_metadatos, fecha_actual, id_archivo_digital):
        data_metadatos['fecha_creacion_doc'] = fecha_actual
        data_metadatos['es_version_original'] = True
        data_metadatos['id_archivo_sistema'] = id_archivo_digital
        data_metadatos['nombre_original_archivo'] = None
        data_metadatos['cod_tipologia_doc_Prefijo'] = None
        data_metadatos['cod_tipologia_doc_agno'] = None
        data_metadatos['cod_tipologia_doc_Consecutivo'] = None
        
        # VALIDACIÓN TIPOLOGIA
        if data_metadatos['id_tipologia_doc'] and data_metadatos['tipologia_no_creada_TRD']:
            raise ValidationError('Solo puede elegir la tipologia o ingresar el nombre de la tipología, no las dos cosas')
        elif not data_metadatos['id_tipologia_doc'] and not data_metadatos['tipologia_no_creada_TRD']:
            raise ValidationError('Debe elegir una tipologia o ingresar el nombre de la tipología')
        
        return data_metadatos
    
    def update_anexo(self, observacion_digitalizacion, anexo_db):
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion=id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()
        
class OtrosDigitalizacionUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = OtrosMetadatosPutSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
            archivo = request.data.get('archivo', None)
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            if not anexo.ya_digitalizado:
                raise PermissionDenied("El anexo no ha sido digitalizado aún")

            metadato_db = self.queryset.filter(id_metadatos_anexo_tmp = data_digitalizacion['id_metadatos_anexo_tmp']).first()
            if metadato_db:
                #Guardar el archivo en la tabla T238
                if archivo:
                    #Validar si es un archivo físico
                    if metadato_db.cod_origen_archivo == 'F':
                        raise PermissionDenied("No puede reemplazar el archivo generado para el anexo físico seleccionado")
                    
                    archivo_creado = self.actualizar_archivo(request.data['archivo'], fecha_actual, data_digitalizacion['id_archivo_sistema'])
                    data_digitalizacion['id_archivo_sistema'] = archivo_creado.data.get('data').get('id_archivo_digital')
                
                serializer = self.serializer_class(metadato_db, data=data_digitalizacion, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
                id_persona_digitalizo = request.user.persona
                observacion_digitalizacion = data_digitalizacion.get('observacion_digitalizacion')

                #Actualiza las tablas de anexos y solicitudes
                self.update_anexo(observacion_digitalizacion, anexo)
                self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], id_persona_digitalizo)

                return Response({'success':True, 'detail':'Se edito la digitalización del anexo correctamente', 'data':serializer.data}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró el metadato que intenta actualizar')
    
    def actualizar_archivo(self, archivo, fecha_actual, id_archivo_anterior):
        #Borra archivo anterior del metadato
        archivoDelete = ArchivoDelete()
        archivoDelete.delete(id_archivo_anterior)

        #Crea el nuevo archivo
        anexosCreate = AnexosCreate()
        archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
        return archivo_creado
    
    def update_anexo(self, observacion_digitalizacion, anexo_db):
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion if observacion_digitalizacion else anexo_db.observacion_digitalizacion
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion = id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()

class OtrosDigitalizacionDelete(generics.RetrieveDestroyAPIView):
    serializer_class = SolicitudesPostSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        with transaction.atomic():
            id_anexo = request.query_params.get('id_anexo', 0)
            id_solicitud_de_digitalizacion = request.query_params.get('id_solicitud_de_digitalizacion', 0)
            id_persona_digitalizo = request.user.persona
            
            #Parametros para eliminacion
            if id_anexo == 0 or id_solicitud_de_digitalizacion == 0:
                raise ValidationError('No se ingresaron parámetros necesarios para eliminar la digitalización del anexo')
            
            id_anexo = int(id_anexo)
            id_solicitud_de_digitalizacion = int(id_solicitud_de_digitalizacion)
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=id_anexo).first()
            if not anexo.ya_digitalizado:
                raise PermissionDenied("El anexo no ha sido digitalizado aún")

            #Invoca el metodo de borrado de metadatos que borra el metadato por el id del anexo y a su ves borra el archivo
            metadatosPQRDelete = MetadatosPQRDelete()
            metadatosPQRDelete.delete(id_anexo)
            
            #Actualiza los datos ya_Digitalizado y observacionDigitalizacion del anexo y la persona que borro la digitalizacion en la solicitud
            self.update_anexo(anexo)
            self.update_solicitud(id_solicitud_de_digitalizacion, id_persona_digitalizo)

            return Response({'success':True, 'detail':'Se elimino la digitalización del anexo correctamente'}, status=status.HTTP_200_OK)
    
    def update_anexo(self, anexo_db):
        anexo_db.ya_digitalizado = False
        anexo_db.observacion_digitalizacion = None
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion=id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()
        
class OtrosResponderDigitalizacion(generics.RetrieveUpdateAPIView):
    serializer_class = SolicitudesPostSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            id_persona_digitalizo = request.user.persona
            digitalizacion_completada = request.data['digitalizacion_completada']
            observacion_digitalizacion = request.data['observacion_digitalizacion']
            solicitud_responder = self.queryset.filter(id_solicitud_de_digitalizacion = request.data['id_solicitud_de_digitalizacion']).first()
            if solicitud_responder:
                solicitud_responder.fecha_rta_solicitud = fecha_actual
                solicitud_responder.observacion_digitalizacion = observacion_digitalizacion
                solicitud_responder.digitalizacion_completada = digitalizacion_completada
                solicitud_responder.devuelta_sin_completar = not digitalizacion_completada
                solicitud_responder.id_persona_digitalizo = id_persona_digitalizo
                solicitud_responder.save()
                
                solicitud_responder_serializer = self.serializer_class(solicitud_responder)

                self.crear_historico_estados(solicitud_responder.id_otro, fecha_actual, id_persona_digitalizo, digitalizacion_completada)

                return Response({'success':True, 'detail':'La solicitud ha sido respondida correctamente', 'data': solicitud_responder_serializer.data}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró la solicitud que intenta responder')
        
    def crear_historico_estados(self, id_otro, fecha_actual, id_persona_digitalizo, digitalizacion_completada):
        estado_otro_inicial = Estados_PQR.objects.filter(Q(id_otros=id_otro.id_otros, estado_solicitud=3)).first()
        
        data_estado_crear = self.set_data_estado_otros(id_otro.id_otros, fecha_actual, id_persona_digitalizo, estado_otro_inicial.id_estado_PQR, 10)
        creador_estados = Estados_PQRCreate()
        creador_estados.crear_estado(data_estado_crear)

        sin_pendientes = self.crear_estado_sin_pendientes(id_otro.id_otros, fecha_actual, id_persona_digitalizo, estado_otro_inicial.id_estado_PQR)
        estado_sin_pendientes_instance = EstadosSolicitudes.objects.filter(id_estado_solicitud=4).first()

        otro_db = Otros.objects.filter(id_otros=id_otro.id_otros).first()
        otro_db.fecha_envio_definitivo_digitalizacion = otro_db.fecha_envio_definitivo_digitalizacion if digitalizacion_completada else None
        otro_db.fecha_digitalizacion_completada = fecha_actual if digitalizacion_completada else otro_db.fecha_digitalizacion_completada
        otro_db.id_estado_actual_solicitud = estado_sin_pendientes_instance if sin_pendientes else otro_db.id_estado_actual_solicitud
        otro_db.fecha_inicial_estado_actual = fecha_actual if sin_pendientes else otro_db.fecha_inicial_estado_actual
        otro_db.save()

    def crear_estado_sin_pendientes(self, id_otros, fecha_actual, id_persona_digitalizo, estado_PQR_asociado):
        sin_pendientes = False
        estados_pqrsdf_pendientes = Estados_PQR.objects.filter(Q(id_otros=id_otros, estado_PQR_asociado=estado_PQR_asociado))
        
        #Obtiene todos los tipos de solicitud creadas
        solicitudes_dig_enviadas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=9))
        solicitudes_dig_respondidas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=10))

        if solicitudes_dig_enviadas == solicitudes_dig_respondidas:
            data_estado_crear = self.set_data_estado_otros(id_otros, fecha_actual, id_persona_digitalizo, None, 4)
            creador_estados = Estados_PQRCreate()
            creador_estados.crear_estado(data_estado_crear)
            sin_pendientes = True
        
        return sin_pendientes

    def set_data_estado_otros(self, id_otros, fecha_actual, id_persona_digitalizo, estado_PQR_asociado, estado_solicitud):
        data_estado = {}
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['id_otros'] = id_otros
        data_estado['estado_PQR_asociado'] = estado_PQR_asociado
        data_estado['estado_solicitud'] = estado_solicitud
        data_estado['persona_genera_estado'] = id_persona_digitalizo.id_persona
        
        return data_estado
    
class OtrosSolicitudesRespondidasGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        #Obtiene los filtros de busqueda
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
        condiciones = self.set_conditions_filters(fecha_desde, fecha_hasta)
        solicitudes_respondidas_otros = self.queryset.filter(condiciones).exclude(id_otro=None).order_by('fecha_rta_solicitud')

        #Obtiene los datos de la solicitud y anexos para serializar
        procesaSolicitudes = ProcesaSolicitudesOtros()
        solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitudes_respondidas_otros, None, 'R')

        serializer = self.serializer_class(solicitudes_respondidas, many=True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        
    def set_conditions_filters(self, fecha_desde, fecha_hasta):
        condiciones = Q()
        if fecha_desde and fecha_hasta:
            condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_hasta)
        else:
            fecha_actual = datetime.now()
            fecha_desde = fecha_actual - timedelta(days=7)
            condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_actual)

        condiciones &= Q(Q(digitalizacion_completada = True) | Q(devuelta_sin_completar = True))
        return condiciones

class OtrosSolicitudByIdGet(generics.GenericAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_solicitud):
        solicitud = self.queryset.filter(id_solicitud_de_digitalizacion=id_solicitud)
        if solicitud:
            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudes = ProcesaSolicitudesOtros()
            peticion_estado = "P" if not solicitud.first().devuelta_sin_completar and not solicitud.first().digitalizacion_completada else "R"
            solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitud, None, peticion_estado)

            serializer = self.serializer_class(solicitudes_respondidas, many=True)
            return Response({'success':True, 'detail':'Se encontro la solicitud por el id asociado', 'data':serializer.data[0]}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No se encontro la solicitud por el id asociado'},status=status.HTTP_200_OK)
        



#CENTRAL_DIGITALIZACION_OPAS
class OpasSolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            estado_solicitud = request.query_params.get('estado_solicitud', None)
            numero_radicado = request.query_params.get('numero_radicado', None)

            #Filtra las solicitudes que no este completada
            solicitudes_opas = self.queryset.filter(digitalizacion_completada=False, devuelta_sin_completar=False).exclude(id_tramite=None).order_by('fecha_solicitud')
            opas = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__cod_tipo_permiso_ambiental = 'OP')
            opas_id_list = [opa.id_solicitud_tramite.id_solicitud_tramite for opa in opas]
            solicitudes_opas = solicitudes_opas.filter(id_tramite__in = opas_id_list)

            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudesOpas = ProcesaSolicitudesOpas()
            solicitudes_pendientes = procesaSolicitudesOpas.procesa_solicitudes(solicitudes_opas, estado_solicitud, 'P')

            serializer = self.serializer_class(solicitudes_pendientes, many=True)
            serializer_data = serializer.data
            
            if numero_radicado:
                serializer_data = [data for data in serializer_data if numero_radicado.lower() in data['numero_radicado'].lower()]
            
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class OpasDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = OpasMetadatosPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            if anexo.ya_digitalizado:
                raise PermissionDenied("El anexo ya fue digitalizado antes. No puede volverlo a digitalizar")

            #Guardar el archivo en la tabla T238
            archivo = request.data.get('archivo', None)
            if archivo:
                if data_digitalizacion['cod_origen_archivo'] == 'F':
                    raise ValidationError("Debe descartar el archivo adjunto, se generará uno de referencia")
                
                archivo_creado = self.create_archivo_adjunto(archivo, fecha_actual)
            else:
                if data_digitalizacion['cod_origen_archivo'] == 'F':
                    if data_digitalizacion['nro_folios_documento'] != 1:
                        raise ValidationError("El número de folios debe ser uno porque el archivo que va a generar el sistema solamente es de una hoja")
                    
                    choices_dict_categoria_archivo = dict(tipo_archivo_CHOICES)
                    categoria_archivo = choices_dict_categoria_archivo[data_digitalizacion['cod_categoria_archivo']]
                    tipologia_documental = data_digitalizacion["tipologia_no_creada_TRD"] if data_digitalizacion.get("tipologia_no_creada_TRD") else TipologiasDoc.objects.filter(id_tipologia_documental=data_digitalizacion["id_tipologia_doc"]).first().nombre
                    
                    info_archivo = {
                        "Nombre del Anexo": "Mapa de Proceso",
                        "Medio de Almacenamiento": "Papel",
                        "Asunto": data_digitalizacion["asunto"],
                        "Categoria del Archivo": categoria_archivo,
                        "Tipología Documental": tipologia_documental
                    }
                    archivo_creado =  UtilsGestor.generar_archivo_blanco(info_archivo, "Mapa de Proceso.pdf", "home,BIA,Opas,GDEA,Anexos_PQR")
            
            metadato_db = MetadatosAnexosTmp.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            
            #Crea el metadato en la DB
            data_to_create = self.set_data_metadato(data_digitalizacion, fecha_actual, archivo_creado.data.get('data').get('id_archivo_digital'))
            serializer = self.serializer_class(data=data_to_create) if not metadato_db else self.serializer_class(metadato_db, data=data_to_create, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            id_persona_digitalizo = request.user.persona

            #Actualiza las tablas de anexos y solicitudes
            self.update_anexo(data_digitalizacion['observacion_digitalizacion'], anexo)
            self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], id_persona_digitalizo)
            
            return Response({'success':True, 'detail':'Se digitalizo correctamente el anexo', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        
    def create_archivo_adjunto(self, archivo, fecha_actual):
        # PENDIENTE AÑADIR GENERACIÓN DE DOCUMENTO CUANDO ES FÍSICO
        if archivo:
            anexosCreate = AnexosCreate()
            archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
            return archivo_creado
        else:
            raise ValidationError("No se puede digitalizar anexos sin archivo adjunto")
        
    def set_data_metadato(self, data_metadatos, fecha_actual, id_archivo_digital):
        data_metadatos['fecha_creacion_doc'] = fecha_actual
        data_metadatos['es_version_original'] = True
        data_metadatos['id_archivo_sistema'] = id_archivo_digital
        data_metadatos['nombre_original_archivo'] = None
        data_metadatos['cod_tipologia_doc_Prefijo'] = None
        data_metadatos['cod_tipologia_doc_agno'] = None
        data_metadatos['cod_tipologia_doc_Consecutivo'] = None
        
        # VALIDACIÓN TIPOLOGIA
        if data_metadatos['id_tipologia_doc'] and data_metadatos['tipologia_no_creada_TRD']:
            raise ValidationError('Solo puede elegir la tipologia o ingresar el nombre de la tipología, no las dos cosas')
        elif not data_metadatos['id_tipologia_doc'] and not data_metadatos['tipologia_no_creada_TRD']:
            raise ValidationError('Debe elegir una tipologia o ingresar el nombre de la tipología')
        
        return data_metadatos
    
    def update_anexo(self, observacion_digitalizacion, anexo_db):
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion=id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()


class OpasDigitalizacionUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = OpasMetadatosPutSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
            archivo = request.data.get('archivo', None)
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=data_digitalizacion['id_anexo']).first()
            if not anexo.ya_digitalizado:
                raise PermissionDenied("El anexo no ha sido digitalizado aún")

            metadato_db = self.queryset.filter(id_metadatos_anexo_tmp = data_digitalizacion['id_metadatos_anexo_tmp']).first()
            if metadato_db:
                #Guardar el archivo en la tabla T238
                if archivo:
                    #Validar si es un archivo físico
                    if metadato_db.cod_origen_archivo == 'F':
                        raise PermissionDenied("No puede reemplazar el archivo generado para el anexo físico seleccionado")
                    
                    archivo_creado = self.actualizar_archivo(request.data['archivo'], fecha_actual, data_digitalizacion['id_archivo_sistema'])
                    data_digitalizacion['id_archivo_sistema'] = archivo_creado.data.get('data').get('id_archivo_digital')
                
                serializer = self.serializer_class(metadato_db, data=data_digitalizacion, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
                id_persona_digitalizo = request.user.persona
                observacion_digitalizacion = data_digitalizacion.get('observacion_digitalizacion')

                #Actualiza las tablas de anexos y solicitudes
                self.update_anexo(observacion_digitalizacion, anexo)
                self.update_solicitud(data_digitalizacion['id_solicitud_de_digitalizacion'], id_persona_digitalizo)

                return Response({'success':True, 'detail':'Se edito la digitalización del anexo correctamente', 'data':serializer.data}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró el metadato que intenta actualizar')
    
    def actualizar_archivo(self, archivo, fecha_actual, id_archivo_anterior):
        #Borra archivo anterior del metadato
        archivoDelete = ArchivoDelete()
        archivoDelete.delete(id_archivo_anterior)

        #Crea el nuevo archivo
        anexosCreate = AnexosCreate()
        archivo_creado = anexosCreate.crear_archivos(archivo, fecha_actual)
        return archivo_creado
    
    def update_anexo(self, observacion_digitalizacion, anexo_db):
        anexo_db.ya_digitalizado = True
        anexo_db.observacion_digitalizacion = observacion_digitalizacion if observacion_digitalizacion else anexo_db.observacion_digitalizacion
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion = id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()


class OpasDigitalizacionDelete(generics.RetrieveDestroyAPIView):
    serializer_class = SolicitudesPostSerializer
    queryset = MetadatosAnexosTmp.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        with transaction.atomic():
            id_anexo = request.query_params.get('id_anexo', 0)
            id_solicitud_de_digitalizacion = request.query_params.get('id_solicitud_de_digitalizacion', 0)
            id_persona_digitalizo = request.user.persona
            
            #Parametros para eliminacion
            if id_anexo == 0 or id_solicitud_de_digitalizacion == 0:
                raise ValidationError('No se ingresaron parámetros necesarios para eliminar la digitalización del anexo')
            
            id_anexo = int(id_anexo)
            id_solicitud_de_digitalizacion = int(id_solicitud_de_digitalizacion)
            
            #Validar si ya fue digitalizado
            anexo = Anexos.objects.filter(id_anexo=id_anexo).first()
            if not anexo.ya_digitalizado:
                raise PermissionDenied("El anexo no ha sido digitalizado aún")

            #Invoca el metodo de borrado de metadatos que borra el metadato por el id del anexo y a su ves borra el archivo
            metadatosPQRDelete = MetadatosPQRDelete()
            metadatosPQRDelete.delete(id_anexo)
            
            #Actualiza los datos ya_Digitalizado y observacionDigitalizacion del anexo y la persona que borro la digitalizacion en la solicitud
            self.update_anexo(anexo)
            self.update_solicitud(id_solicitud_de_digitalizacion, id_persona_digitalizo)

            return Response({'success':True, 'detail':'Se elimino la digitalización del anexo correctamente'}, status=status.HTTP_200_OK)
    
    def update_anexo(self, anexo_db):
        anexo_db.ya_digitalizado = False
        anexo_db.observacion_digitalizacion = None
        anexo_db.save()

    def update_solicitud(self, id_solicitud_de_digitalizacion, id_persona_digitalizo):
        solicitud_db = SolicitudDeDigitalizacion.objects.filter(id_solicitud_de_digitalizacion=id_solicitud_de_digitalizacion).first()
        solicitud_db.id_persona_digitalizo = id_persona_digitalizo
        solicitud_db.save()


class OpasResponderDigitalizacion(generics.RetrieveUpdateAPIView):
    serializer_class = SolicitudesPostSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        with transaction.atomic():
            fecha_actual = datetime.now()
            id_persona_digitalizo = request.user.persona
            digitalizacion_completada = request.data['digitalizacion_completada']
            observacion_digitalizacion = request.data['observacion_digitalizacion']
            solicitud_responder = self.queryset.filter(id_solicitud_de_digitalizacion = request.data['id_solicitud_de_digitalizacion']).first()
            if solicitud_responder:
                solicitud_responder.fecha_rta_solicitud = fecha_actual
                solicitud_responder.observacion_digitalizacion = observacion_digitalizacion
                solicitud_responder.digitalizacion_completada = digitalizacion_completada
                solicitud_responder.devuelta_sin_completar = not digitalizacion_completada
                solicitud_responder.id_persona_digitalizo = id_persona_digitalizo
                solicitud_responder.save()
                
                solicitud_responder_serializer = self.serializer_class(solicitud_responder)

                self.crear_historico_estados(solicitud_responder.id_tramite, fecha_actual, id_persona_digitalizo, digitalizacion_completada)

                return Response({'success':True, 'detail':'La solicitud ha sido respondida correctamente', 'data': solicitud_responder_serializer.data}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró la solicitud que intenta responder')
        
    def crear_historico_estados(self, id_tramite, fecha_actual, id_persona_digitalizo, digitalizacion_completada):
        estado_tramite_inicial = Estados_PQR.objects.filter(Q(id_tramite=id_tramite.id_solicitud_tramite, estado_solicitud=3)).first()
        
        data_estado_crear = self.set_data_estado_tramites(id_tramite.id_solicitud_tramite, fecha_actual, id_persona_digitalizo, estado_tramite_inicial.id_estado_PQR, 10)
        creador_estados = Estados_PQRCreate()
        creador_estados.crear_estado(data_estado_crear)

        sin_pendientes = self.crear_estado_sin_pendientes(id_tramite.id_solicitud_tramite, fecha_actual, id_persona_digitalizo, estado_tramite_inicial.id_estado_PQR)
        estado_sin_pendientes_instance = EstadosSolicitudes.objects.filter(id_estado_solicitud=4).first()

        opas_db = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_tramite.id_solicitud_tramite).first()
        opas_db.fecha_envio_definitivo_a_digitalizacion = opas_db.fecha_envio_definitivo_a_digitalizacion if digitalizacion_completada else None
        opas_db.fecha_digitalizacion_completada = fecha_actual if digitalizacion_completada else opas_db.fecha_digitalizacion_completada
        opas_db.id_estado_actual_solicitud = estado_sin_pendientes_instance if sin_pendientes else opas_db.id_estado_actual_solicitud
        opas_db.fecha_ini_estado_actual = fecha_actual if sin_pendientes else opas_db.fecha_ini_estado_actual
        opas_db.save()

    def crear_estado_sin_pendientes(self, id_tramite, fecha_actual, id_persona_digitalizo, estado_PQR_asociado):
        sin_pendientes = False
        estados_pqrsdf_pendientes = Estados_PQR.objects.filter(Q(id_tramite=id_tramite, estado_PQR_asociado=estado_PQR_asociado))
        
        #Obtiene todos los tipos de solicitud creadas
        solicitudes_dig_enviadas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=9))
        solicitudes_dig_respondidas = len(estados_pqrsdf_pendientes.filter(estado_solicitud=10))

        if solicitudes_dig_enviadas == solicitudes_dig_respondidas:
            data_estado_crear = self.set_data_estado_tramites(id_tramite, fecha_actual, id_persona_digitalizo, None, 4)
            creador_estados = Estados_PQRCreate()
            creador_estados.crear_estado(data_estado_crear)
            sin_pendientes = True
        
        return sin_pendientes

    def set_data_estado_tramites(self, id_tramite, fecha_actual, id_persona_digitalizo, estado_PQR_asociado, estado_solicitud):
        data_estado = {}
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['id_tramite'] = id_tramite
        data_estado['estado_PQR_asociado'] = estado_PQR_asociado
        data_estado['estado_solicitud'] = estado_solicitud
        data_estado['persona_genera_estado'] = id_persona_digitalizo.id_persona
        
        return data_estado
    

class ProcesaSolicitudesOpas:
    querysetRadicados = T262Radicados.objects.all()

    def procesa_solicitudes(self, solicitudes_tramites, estado_solicitud, peticion_estado):
        solicitudes = []
        for solicitud_tramite in solicitudes_tramites:
            data_anexos_tramites = self.consulta_anexos_tramites(solicitud_tramite, estado_solicitud, peticion_estado)
            if data_anexos_tramites:
                solicitudes.append(data_anexos_tramites)
        
        return solicitudes

    def consulta_anexos_tramites(self, solicitud_tramite, estado_solicitud, peticion_estado):
        solicitud_model = None
        tramite = solicitud_tramite.id_tramite
        radicado = tramite.id_radicado
        
        instance_config_tipo_radicado =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
        numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        radicado_nuevo= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        if radicado:
            # Obtiene los anexos
            anexos_tramites = AnexosTramite.objects.filter(id_solicitud_tramite = solicitud_tramite.id_tramite.id_solicitud_tramite)
            ids_anexos = [anexo_tramite.id_anexo.id_anexo for anexo_tramite in anexos_tramites]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            validate_anexos = self.valida_anexos_filtro_estado(anexos, estado_solicitud)

            if validate_anexos:
                #Obtiene el modelo de solicitud a serializar
                solicitud_model = self.set_data_solicitudes(solicitud_tramite, "OPAS",None, tramite.id_persona_titular.id_persona, anexos.count(), radicado_nuevo, anexos, peticion_estado)
                
        
        return solicitud_model
    
    def valida_anexos_filtro_estado(self, anexos, estado_solicitud):
        validate_anexos = True
        if estado_solicitud:
            if estado_solicitud == 'SH':
                validate_anexos =  all(not anexo.ya_digitalizado for anexo in anexos)
            else:
                validate_anexos = any(anexo.ya_digitalizado for anexo in anexos)
        
        return validate_anexos
    
    def set_data_solicitudes(self, solicitud, cod_tipo_solicitud, asunto, id_persona_titular, cantidad_anexos, radicado, anexos, peticion_estado):
        solicitud_model = {}
        solicitud_model['id_solicitud_de_digitalizacion'] = solicitud.id_solicitud_de_digitalizacion
        solicitud_model['fecha_solicitud'] = solicitud.fecha_solicitud
        solicitud_model['fecha_rta_solicitud'] = solicitud.fecha_rta_solicitud
        solicitud_model['cod_tipo_solicitud'] = cod_tipo_solicitud
        solicitud_model['asunto'] = asunto
        solicitud_model['id_persona_titular'] = id_persona_titular
        solicitud_model['numero_anexos'] = cantidad_anexos
        solicitud_model['radicado'] = radicado
        solicitud_model['anexos'] = anexos
        solicitud_model['peticion_estado'] = peticion_estado
        solicitud_model['devuelta_sin_completar'] = solicitud.devuelta_sin_completar
        solicitud_model['digitalizacion_completada'] = solicitud.digitalizacion_completada

        return solicitud_model
    

class OpasSolicitudesRespondidasGet(generics.ListAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        #Obtiene los filtros de busqueda
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
        condiciones = self.set_conditions_filters(fecha_desde, fecha_hasta)
        solicitudes_respondidas_tramite = self.queryset.filter(condiciones).exclude(id_tramite=None).order_by('fecha_rta_solicitud')

        print('hola:', condiciones)
        #Obtiene los datos de la solicitud y anexos para serializar
        procesaSolicitudes = ProcesaSolicitudesOpas()
        solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitudes_respondidas_tramite, None, 'R')

        serializer = self.serializer_class(solicitudes_respondidas, many=True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        
    def set_conditions_filters(self, fecha_desde, fecha_hasta):
        condiciones = Q()
        if fecha_desde and fecha_hasta:
            condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_hasta)
        else:
            fecha_actual = datetime.now()
            fecha_desde = fecha_actual - timedelta(days=7)
            condiciones &= Q(fecha_rta_solicitud__date__gte=fecha_desde, fecha_rta_solicitud__date__lte=fecha_actual)

        condiciones &= Q(Q(digitalizacion_completada = True) | Q(devuelta_sin_completar = True))
        return condiciones
    


class OpasSolicitudByIdGet(generics.GenericAPIView):
    serializer_class = SolicitudesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_solicitud):
        solicitud = self.queryset.filter(id_solicitud_de_digitalizacion=id_solicitud)
        if solicitud:
            #Obtiene los datos de la solicitud y anexos para serializar
            procesaSolicitudes = ProcesaSolicitudesOpas()
            peticion_estado = "P" if not solicitud.first().devuelta_sin_completar and not solicitud.first().digitalizacion_completada else "R"
            solicitudes_respondidas = procesaSolicitudes.procesa_solicitudes(solicitud, None, peticion_estado)

            serializer = self.serializer_class(solicitudes_respondidas, many=True)
            return Response({'success':True, 'detail':'Se encontro la solicitud por el id asociado', 'data':serializer.data[0]}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No se encontro la solicitud por el id asociado'},status=status.HTTP_200_OK)
        