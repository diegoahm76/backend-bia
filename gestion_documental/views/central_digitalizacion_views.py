from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, SolicitudDeDigitalizacion, T262Radicados

from django.db.models import Q

from gestion_documental.serializers.central_digitalizacion_serializeers import SolicitudesPendientesSerializer

class SolicitudesPendientesGet(generics.ListAPIView):
    serializer_class = SolicitudesPendientesSerializer
    queryset = SolicitudDeDigitalizacion.objects.all()
    querysetRadicados = T262Radicados.objects.all()

    def get(self, request):
        try:
            #Obtiene los filtros de busqueda
            tipo_solicitud = self.request.query_params.get('tipo_solicitud', None)
            estado_solicitud = self.request.query_params.get('estado_solicitud', None)
            numero_radicado = self.request.query_params.get('numero_radicado', None)

            #Filtra las solicitudes de la T263 que coincidan con el tipo de solicitud y que no este completada
            condiciones = ~Q(id_pqrsdf=0) if tipo_solicitud == 'PQR' else ~Q(id_complemento_usu_pqr=0)
            condiciones &= Q(digitalizacion_completada = False)
            solicitudes_pqr = self.queryset.filter(condiciones)

            #Obtiene los datos de la solicitud y anexos para serializar
            solicitudes_pendientes = self.procesa_solicitudes(solicitudes_pqr, estado_solicitud, numero_radicado)

            # data_to_serializer = self.procesa_radicados_filtrados(solicitudes)
            serializer = self.serializer_class(solicitudes_pendientes, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes solicitudes pendientes que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            raise({'success': False, 'detail': str(e)})
    
    def procesa_solicitudes(self, solicitudes_pqr, tipo_solicitud, estado_solicitud, numero_radicado):
        #En caso de tener filtro por radicados, obtiene todos los radicados que finalicen por el numero digitado
        radicados = []
        solicitudes_pendientes = []
        if numero_radicado:
            radicados = self.querysetRadicados.filter({'nro_radicado__endswith': int(numero_radicado)})
            if ~Q(radicados and len(radicados) > 0):
                raise NotFound("No se encontraron radicados por el numero de radicado ingresado")
        
        for solicitud_pqr in solicitudes_pqr:
            if tipo_solicitud == 'PQR':
                data_anexos_pqrsd = self.consulta_anexos_pqrsdf(solicitud_pqr, radicados)
                if data_anexos_pqrsd:
                    solicitudes_pendientes.append(data_anexos_pqrsd)
            else:
                data_anexos_complementos_pqrsd = self.consulta_anexos_complementos_pqrsdf(solicitud_pqr, radicados)
                if data_anexos_complementos_pqrsd:
                    solicitudes_pendientes.append(data_anexos_complementos_pqrsd)
        
        return solicitudes_pendientes


    def consulta_anexos_pqrsdf(self, solicitud_pqr, radicados):
        solicitud_model = None
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF = solicitud_pqr.id_pqrsdf).first()
        radicado = self.get_radicado(radicados, pqrsdf.id_radicado)
        if radicado:
            anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = pqrsdf.id_PQRSDF)
            ids_anexos = [anexo_pqr['id_anexo'] for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            solicitud_model = self.set_data_solicitudes(solicitud_pqr.fecha_solicitud, "PQR", pqrsdf.asunto,  pqrsdf.id_persona_titular, pqrsdf.cantidad_anexos, radicado, anexos)
        
        return solicitud_model
        


    def consulta_anexos_complementos_pqrsdf(self, idComplementoUsu_PQR, radicados):
        solicitud_model = None
        # pqrsdf = PQRSDF.objects.filter(id_PQRSDF = solicitud_pqr.id_pqrsdf).first()
        # radicado = self.get_radicado(radicados, pqrsdf.id_radicado)
        # if radicado:
        #     anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = pqrsdf.id_PQRSDF)
        #     ids_anexos = [anexo_pqr['id_anexo'] for anexo_pqr in anexos_pqr]
        #     anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
        #     solicitud_model = self.set_data_solicitudes(solicitud_pqr.fecha_solicitud, "PQR", pqrsdf.asunto,  pqrsdf.id_persona_titular, pqrsdf.cantidad_anexos, radicado, anexos)
        
        return solicitud_model


    def get_radicado(self, radicados, id_radicado):
        # radicado = None
        if len(radicados) > 0:
            radicado = radicados.filter(id_radicado = id_radicado).first()
        else:
            radicado = self.querysetRadicados.objects.filter(id_radicado = id_radicado).first()
        
        return radicado
    
    def set_data_solicitudes(self, fecha_solicitud, cod_tipo_solicitud, asunto, id_persona_titular, cantidad_anexos, radicado, anexos):
        solicitud_model = {}
        solicitud_model['fecha_solicitud'] = fecha_solicitud
        solicitud_model['cod_tipo_solicitud'] = cod_tipo_solicitud
        solicitud_model['asunto'] = asunto
        solicitud_model['id_persona_titular'] = id_persona_titular
        solicitud_model['numero_anexos'] = cantidad_anexos
        solicitud_model['radicado'] = radicado
        solicitud_model['anexos'] = anexos

        return solicitud_model

