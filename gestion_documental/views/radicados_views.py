from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import PQRSDF, ComplementosUsu_PQR, MediosSolicitud, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados
from gestion_documental.serializers.radicados_serializers import MedioSolicitudSerializer, OtrosSerializer, PersonasFilterSerializer, RadicadosImprimirSerializer ,PersonasSerializer
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
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = solicitud_pqrsdf.id_pqrsdf).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular, solicitud_pqrsdf.asunto))

            elif radicado.id_modulo_que_radica == 3 or radicado.id_modulo_que_radica == 4:
                complemento_pqrsdf = ComplementosUsu_PQR.objects.filter(id_radicado = radicado.id_radicado).first()
                if complemento_pqrsdf:
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = complemento_pqrsdf.id_PQRSDF).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular, complemento_pqrsdf.asunto))

            elif radicado.id_modulo_que_radica == 5:
                respuesta_pqrsdf = RespuestaPQR.objects.filter(id_radicado_salida = radicado.id_radicado).first()
                if respuesta_pqrsdf:
                    pqrsdf = pqrsdf_instance.filter(id_PQRSDF = respuesta_pqrsdf.id_pqrsdf).first()
                    if pqrsdf:
                        data_radicados.append(self.set_data_to_serializer(radicado, pqrsdf.id_persona_titular, respuesta_pqrsdf.asunto))

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
    

#Creacion_Persona_Titular
class CrearPersonaTitularOtros(generics.CreateAPIView):
    serializer_class = PersonasSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Datos proporcionados en la solicitud POST
                datos = request.data.get('persona_titular', {})
                
                # Crear el serializador con los datos
                serializer = self.get_serializer(data=datos)
                serializer.is_valid(raise_exception=True)

                # Guardar el registro en la base de datos
                persona_titular = serializer.save()

                return Response({
                    'success': True,
                    'detail': 'Persona titular creada correctamente.',
                    'data': serializer.data,
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#LISTAR_MEDIOS_DE_SOLICITUD
class ListarMediosSolicitud(generics.ListAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MedioSolicitudSerializer

    def list(self, request, *args, **kwargs):
        # Obtén el queryset de medios de solicitud
        medios_solicitud = self.get_queryset()

        # Serializa los medios de solicitud
        medios_serializer = self.serializer_class(medios_solicitud, many=True)

        # Obtén la instancia de OtrosSerializer
        otros_serializer = OtrosSerializer()

        # Agrega los medios de solicitud al contexto de OtrosSerializer
        context = {
            'medios_solicitud': medios_serializer.data
        }
        otros_serializer.fields['medios_solicitud'] = MedioSolicitudSerializer(many=True, read_only=True, context=context)

        # Obtén la respuesta predeterminada de ListAPIView
        response = super().list(request, *args, **kwargs)

        # Modifica la respuesta según tus necesidades
        response.data = {
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data':  medios_serializer.data
        }
        return response
    

#FILTRO_PERSONAS
class GetPersonasByFilters(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()

    def get(self,request):
        filter = {}
        
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','primer_apellido','razon_social','nombre_comercial', 'tipo_persona']:
                if key in ['primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                    if value != "":
                        filter[key+'__icontains']=  value
                elif key == "numero_documento":
                    if value != "":
                        filter[key+'__icontains'] = value
                else:
                    if value != "":
                        filter[key] = value
                        
        personas = self.queryset.all().filter(**filter)
        
        serializer = self.serializer_class(personas, many=True)
        return Response({'success':True, 
                         'detail':'Se encontraron las siguientes personas que coinciden con los criterios de búsqueda', 
                         'data':serializer.data}, status=status.HTTP_200_OK)
    


#Filtro_Personas
class GetPersonasByFiltersOtros(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()

    def get(self, request):
        filter_params = {}

        # Obtener parámetros de la solicitud
        tipo_documento = request.query_params.get('tipo_documento', '').upper()
        tipo_persona = request.query_params.get('tipo_persona', '').upper()

        # Validar que el tipo de persona sea proporcionado y sea "Natural" o "Jurídica"
        if tipo_persona not in ['N', 'J']:
            return Response({'success': False, 'detail': 'El tipo de persona es obligatorio y debe ser "Natural" o "Jurídica".'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplicar validaciones para el tipo de documento según el tipo de persona
        if tipo_persona == 'N' and tipo_documento == 'NT':
            return Response({'success': False, 'detail': 'No se permite seleccionar NIT para persona natural.'}, status=status.HTTP_400_BAD_REQUEST)
        elif tipo_persona == 'J' and tipo_documento != 'NT':
            return Response({'success': False, 'detail': 'Solo se permite seleccionar NIT para persona jurídica.'}, status=status.HTTP_400_BAD_REQUEST)

        # Construir diccionario de filtros
        for key, value in request.query_params.items():
            if key in ['tipo_documento', 'numero_documento', 'primer_nombre', 'primer_apellido', 'razon_social', 'nombre_comercial', 'tipo_persona']:
                if value != "":
                    if key in ['primer_nombre', 'primer_apellido', 'razon_social', 'nombre_comercial']:
                        filter_params[key + '__icontains'] = value
                    elif key == 'tipo_documento' and value.upper() == 'N':
                        filter_params['tipo_documento__cod_tipo_documento__in'] = ['TI', 'CC', 'RC', 'NU', 'CE', 'PA', 'PE']
                    elif key == 'tipo_documento' and value.upper() == 'J':
                        filter_params['tipo_documento__cod_tipo_documento'] = 'NT'
                    elif key == 'tipo_persona':
                        filter_params[key] = value
                    else:
                        filter_params[key] = value

        # Aplicar filtros y obtener resultados
        personas = self.queryset.filter(**filter_params)

        # Serializar y devolver respuesta
        serializer = self.serializer_class(personas, many=True)
        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes personas que coinciden con los criterios de búsqueda',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class GetEmpresasByFiltersOtros(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer  # Asegúrate de tener el serializador correcto para empresas
    queryset = Personas.objects.all()  # Asegúrate de tener el modelo correcto para empresas

    def get(self, request):
        filter_params = {}

        # Obtener parámetros de la solicitud
        tipo_documento = request.query_params.get('tipo_documento', '').upper()
        tipo_persona = request.query_params.get('tipo_persona', '').upper()

        # Validar que el tipo de persona sea proporcionado y sea "Jurídica"
        if tipo_persona != 'J':
            return Response({'success': False, 'detail': 'El tipo de persona es obligatorio y debe ser "Jurídica".'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplicar validaciones para el tipo de documento
        if tipo_documento != 'NT':
            return Response({'success': False, 'detail': 'Solo se permite filtrar por NIT para persona jurídica.'}, status=status.HTTP_400_BAD_REQUEST)

        # Construir diccionario de filtros
        for key, value in request.query_params.items():
            if key in ['tipo_documento', 'numero_documento', 'razon_social', 'nombre_comercial', 'tipo_persona']:
                if value != "":
                    if key in ['razon_social', 'nombre_comercial']:
                        filter_params[key + '__icontains'] = value
                    elif key == 'tipo_documento' and value.upper() == 'J':
                        filter_params['tipo_documento__cod_tipo_documento'] = 'NT'
                    elif key == 'tipo_persona':
                        filter_params[key] = value
                    else:
                        filter_params[key] = value

        # Aplicar filtros y obtener resultados
        empresas = self.queryset.filter(**filter_params)

        # Serializar y devolver respuesta
        serializer = self.serializer_class(empresas, many=True)
        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes empresas que coinciden con los criterios de búsqueda',
            'data': serializer.data
        }, status=status.HTTP_200_OK)