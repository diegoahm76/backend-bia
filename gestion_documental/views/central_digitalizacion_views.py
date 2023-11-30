import copy
from datetime import datetime
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, MetadatosAnexosTmp, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, T262Radicados

from django.db.models import Q
from django.db import transaction
from django.forms import model_to_dict

from gestion_documental.serializers.central_digitalizacion_serializers import SolicitudesPendientesSerializer, SolicitudesPostSerializer
from gestion_documental.serializers.pqr_serializers import AnexosPostSerializer, MetadatosPostSerializer, MetadatosPutSerializer
from gestion_documental.views.pqr_views import AnexosCreate, ArchivoDelete

class SolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesPendientesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    querysetRadicados = T262Radicados.objects.all()

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            tipo_solicitud = request.query_params.get('tipo_solicitud', None)
            estado_solicitud = request.query_params.get('estado_solicitud', None)
            numero_radicado = request.query_params.get('numero_radicado', None)
            # numero_radicado = int(numero_radicado) if numero_radicado else None

            #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
            condiciones = ~Q(id_pqrsdf=0) and ~Q(id_pqrsdf=None) if tipo_solicitud == 'PQR' else ~Q(id_complemento_usu_pqr=0) and ~Q(id_complemento_usu_pqr=None)
            condiciones &= Q(digitalizacion_completada = False)
            solicitudes_pqr = self.queryset.filter(condiciones)

            #Obtiene los datos de la solicitud y anexos para serializar
            solicitudes_pendientes = self.procesa_solicitudes(solicitudes_pqr, tipo_solicitud, estado_solicitud, numero_radicado)

            # data_to_serializer = self.procesa_radicados_filtrados(solicitudes)
            serializer = self.serializer_class(solicitudes_pendientes, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def procesa_solicitudes(self, solicitudes_pqr, tipo_solicitud, estado_solicitud, numero_radicado):
        #En caso de tener filtro por radicados, obtiene todos los radicados que finalicen por el numero digitado
        radicados = []
        solicitudes_pendientes = []
        if numero_radicado:
            radicados = self.querysetRadicados.filter(nro_radicado__icontains=numero_radicado)
            if len(radicados) == 0:
                raise NotFound("No se encontraron radicados por el numero de radicado ingresado")
        
        for solicitud_pqr in solicitudes_pqr:
            if tipo_solicitud == 'PQR':
                data_anexos_pqrsd = self.consulta_anexos_pqrsdf(solicitud_pqr, radicados, estado_solicitud)
                if data_anexos_pqrsd:
                    solicitudes_pendientes.append(data_anexos_pqrsd)
            else:
                data_anexos_complementos_pqrsd = self.consulta_anexos_complementos_pqrsdf(solicitud_pqr, radicados, estado_solicitud)
                if data_anexos_complementos_pqrsd:
                    solicitudes_pendientes.append(data_anexos_complementos_pqrsd)
        
        return solicitudes_pendientes


    def consulta_anexos_pqrsdf(self, solicitud_pqr, radicados, estado_solicitud):
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
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "PQR", pqrsdf.asunto,  pqrsdf.id_persona_titular_id, pqrsdf.cantidad_anexos, radicado, anexos)
        
        return solicitud_model

    def consulta_anexos_complementos_pqrsdf(self, solicitud_pqr, radicados, estado_solicitud):
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
                solicitud_model = self.set_data_solicitudes(solicitud_pqr, "CDPQR", complemento_usu_pqrsdf.asunto,  pqrsdf.id_persona_titular_id, complemento_usu_pqrsdf.cantidad_anexos, radicado, anexos)
        
        return solicitud_model


    def get_radicado(self, radicados, id_radicado):
        # radicado = None
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
    
    def set_data_solicitudes(self, solicitud, cod_tipo_solicitud, asunto, id_persona_titular, cantidad_anexos, radicado, anexos):
        solicitud_model = {}
        solicitud_model['id_solicitud_de_digitalizacion'] = solicitud.id_solicitud_de_digitalizacion
        solicitud_model['fecha_solicitud'] = solicitud.fecha_solicitud
        solicitud_model['cod_tipo_solicitud'] = cod_tipo_solicitud
        solicitud_model['asunto'] = asunto
        solicitud_model['id_persona_titular'] = id_persona_titular
        solicitud_model['numero_anexos'] = cantidad_anexos
        solicitud_model['radicado'] = radicado
        solicitud_model['anexos'] = anexos

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
