import copy
from datetime import datetime, timedelta
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, Estados_PQR, MetadatosAnexosTmp, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, T262Radicados

from django.db.models import Q
from django.db import transaction
from django.forms import model_to_dict

from gestion_documental.serializers.central_digitalizacion_serializers import SolicitudesAlUsuarioPostSerializer, SolicitudesPendientesSerializer, SolicitudesPostSerializer
from gestion_documental.serializers.pqr_serializers import AnexosPostSerializer, MetadatosPostSerializer, MetadatosPutSerializer, PQRSDFPutSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import ComplementosUsu_PQRPutSerializer
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate
from gestion_documental.views.pqr_views import AnexosCreate, ArchivoDelete, MetadatosPQRDelete

class SolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesPendientesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()

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
    serializer_class = SolicitudesPendientesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    querysetRadicados = T262Radicados.objects.all()

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
                condiciones &= Q(fecha_rta_solicitud__gte=fecha_desde, fecha_rta_solicitud__lte=fecha_hasta)
        else:
            fecha_actual = datetime.now()
            fecha_desde = fecha_actual - timedelta(days=7)
            condiciones &= Q(fecha_rta_solicitud__gte=fecha_desde, fecha_rta_solicitud__lte=fecha_actual)

        condiciones &= Q(Q(digitalizacion_completada = True) or Q(devuelta_sin_completar = True))
        return condiciones
        
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
            # Obtiene los anexos
            anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = pqrsdf.id_PQRSDF)
            ids_anexos = [anexo_pqr.id_anexo_id for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            validate_anexos = self.valida_anexos_filtro_estado(anexos, estado_solicitud)

            if validate_anexos:
                #Obtiene el modelo de solicitud a serializar
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "PQR", pqrsdf.asunto,  pqrsdf.id_persona_titular_id, pqrsdf.cantidad_anexos, radicado, anexos, peticion_estado)
        
        return solicitud_model

    def consulta_anexos_complementos_pqrsdf(self, solicitud_pqr, radicados, estado_solicitud, peticion_estado):
        solicitud_model = None
        complemento_usu_pqrsdf = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR = solicitud_pqr.id_complemento_usu_pqr_id).first()
        radicado = self.get_radicado(radicados, complemento_usu_pqrsdf.id_radicado_id)
        if radicado:
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
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "CDPQR", complemento_usu_pqrsdf.asunto,  pqrsdf.id_persona_titular_id, complemento_usu_pqrsdf.cantidad_anexos, radicado, anexos, peticion_estado)
        
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

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                fecha_actual = datetime.now()
                data_digitalizacion = json.loads(request.data.get('data_digitalizacion', ''))
                #Guardar el archivo en la tabla T238
                archivo_creado = self.create_archivo_adjunto(request.data['archivo'], fecha_actual)
                
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
            archivo_creado = anexosCreate.crear_archivos(self, archivo, fecha_actual)
            return archivo_creado
        else:
            raise ValidationError("No se puede digitalizar anexos sin archivo adjunto")
        
    def set_data_metadato(self, data_metadatos, fecha_actual, id_archivo_digital):
        data_metadatos['fecha_creacion_doc'] = fecha_actual.date()
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
        archivo_creado = AnexosCreate.crear_archivos(self, archivo, fecha_actual)
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

