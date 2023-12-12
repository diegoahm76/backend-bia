from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import PQRSDF, ComplementosUsu_PQR, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados
from gestion_documental.serializers.radicados_serializers import RadicadosImprimirSerializer ,PersonasSerializer
from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied



class GetRadicadosImprimir(generics.ListAPIView):
    serializer_class = RadicadosImprimirSerializer
    queryset = T262Radicados.objects.all()

    def get(self, request):
        try:
            filter = {}
            for key,value in request.query_params.items():
                if key in ['cod_tipo_radicado','prefijo_radicado','agno_radicado','nro_radicado','fecha_radicado']:
                    if key == "nro_radicado":
                        if value != "":
                            filter[key+'__endswith'] = int(value)
                    elif key == "fecha_radicado":
                        if value != "":
                            filter[key+'__contains'] = value
                    else:
                        if value != "":
                            filter[key] = value

            radicados = self.queryset.filter(**filter)

            data_to_serializer = self.procesa_radicados_filtrados(radicados)
            serializer = self.serializer_class(data_to_serializer, many=True)
            return Response({'success':True, 'detail':'Se encontraron los siguientes radicados que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            raise({'success': False, 'detail': str(e)}) 

    def procesa_radicados_filtrados(self, radicados):
        data_radicados = []
        for radicado in radicados:
            pqrsdf_instance = PQRSDF.objects.all()
            if radicado.id_modulo_que_radica == 1:
                pqrsdf = pqrsdf_instance.filter(id_radicado = radicado.id_radicado).first()
                if pqrsdf:
                    data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular_id, pqrsdf.asunto))

            elif radicado.id_modulo_que_radica == 2:
                solicitud_pqrsdf = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_radicado_salida = radicado.id_radicado).first()
                if solicitud_pqrsdf:
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = solicitud_pqrsdf.id_pqrsdf_id).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular_id, solicitud_pqrsdf.asunto))

            elif radicado.id_modulo_que_radica == 3 or radicado.id_modulo_que_radica == 4:
                complemento_pqrsdf = ComplementosUsu_PQR.objects.filter(id_radicado = radicado.id_radicado).first()
                if complemento_pqrsdf:
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = complemento_pqrsdf.id_PQRSDF_id).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular_id, complemento_pqrsdf.asunto))

            elif radicado.id_modulo_que_radica == 5:
                respuesta_pqrsdf = RespuestaPQR.objects.filter(id_radicado_salida = radicado.id_radicado).first()
                if respuesta_pqrsdf:
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = respuesta_pqrsdf.id_pqrsdf_id).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular_id, respuesta_pqrsdf.asunto))

            #Para las dos ultimas condiciones aun no definen tabla en BD
            elif radicado.id_modulo_que_radica == 6:
                pass

            elif radicado.id_modulo_que_radica == 7:
                pass
        
        return data_radicados
    
    def set_data_to_serializer(self, radicado, id_persona_titular, asunto):
        data = {}
        data['cod_tipo_radicado'] = radicado.cod_tipo_radicado
        data['prefijo_radicado'] = radicado.prefijo_radicado
        data['agno_radicado'] = radicado.agno_radicado
        data['nro_radicado'] = radicado.nro_radicado
        data['fecha_radicado'] = radicado.fecha_radicado
        data['id_persona_titular'] = id_persona_titular
        data['asunto'] = asunto

        return data
    


class FilterPersonasDocumento(generics.ListAPIView):
    serializer_class = PersonasSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        numero_documento = self.request.query_params.get('numero_documento', '').strip()

        # Validación: asegúrate de que el número de documento no esté vacío
        if not numero_documento:
            return Personas.objects.none()

        # Filtrar por atributos específicos referentes a una persona (unión de parámetros)
        queryset = Personas.objects.all()

        if numero_documento:
            queryset = queryset.filter(numero_documento__startswith=numero_documento)

        # Puedes agregar más condiciones de filtro según sea necesario

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            raise NotFound('No se encontraron datos que coincidan con los criterios de búsqueda.')

        serializer = PersonasSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)