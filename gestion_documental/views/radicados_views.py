import ast
import copy
from datetime import datetime, date, timedelta
import json
from django.db.models import Q
from django.forms import model_to_dict
import os
from django.db import transaction
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from rest_framework import generics,status
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.models.expedientes_models import ArchivosDigitales
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, EstadosSolicitudes, MediosSolicitud, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR, modulos_radican
from gestion_documental.serializers.radicados_serializers import AnexosPQRSDFPostSerializer, AnexosPQRSDFSerializer, AnexosPostSerializer, AnexosPutSerializer, AnexosSerializer, ArchivosSerializer, MedioSolicitudSerializer, MetadatosPostSerializer, MetadatosPutSerializer, MetadatosSerializer, OTROSPanelSerializer, OTROSSerializer, OtrosPostSerializer, OtrosSerializer, PersonasFilterSerializer, RadicadoPostSerializer, RadicadosImprimirSerializer ,PersonasSerializer
from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from transversal.models.base_models import ApoderadoPersona
from gestion_documental.views.panel_ventanilla_views import Estados_OTROSDelete, Estados_PQRCreate, Estados_PQRDelete
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN





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
    


#LISTAR_SOLICITUD_OTRO_POR_ID_PERSONA_TITULAR
class GetOTROSForStatus(generics.ListAPIView):
    serializer_class = OTROSSerializer
    queryset = Otros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_persona_titular):
        otros = self.queryset.filter(
            Q(id_persona_titular=id_persona_titular) &
            Q(Q(id_radicados=None) | Q(requiere_digitalizacion=True, fecha_digitalizacion_completada=None))
        )
        if otros:
            serializer = self.serializer_class(otros, many=True)
            return Response({'success': True, 'detail': 'Se encontraron OTROS asociados al titular', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron OTROS asociados al titular'}, status=status.HTTP_200_OK)
        
class GetOTROSForPanel(generics.RetrieveAPIView):
    serializer_class = OTROSPanelSerializer
    queryset = Otros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_otros):
        # try:
            data_otros = self.queryset.filter(id_otros = id_otros).first()
            
            if data_otros:
                serializador = self.serializer_class(data_otros, many = False)
                return Response({'success':True, 'detail':'Se encontro el OTROS por el id consultado','data':serializador.data},status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No Se encontro el OTROS por el id consultado'},status=status.HTTP_200_OK)
        # except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)






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
        otros_serializer = OtrosPostSerializer()

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
    


#Filtro_Personas_otros
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
    

#Filtro_Empresas_Otros
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
    
#Filtro_Apoderados_Otros
class GetApoderadosByPoderdanteId(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()

    def get(self, request, id_poderdante, *args, **kwargs):
        apoderados_serializer = []
        apoderados = ApoderadoPersona.objects.filter(
            Q(persona_poderdante=id_poderdante) & Q(
                Q(fecha_cierre__gte=datetime.now()) | Q(fecha_cierre=None)
            )
        )
        if apoderados:
            for apoderado in apoderados:
                apoderado_persona = self.queryset.filter(
                    id_persona=apoderado.persona_apoderada_id
                ).first()
                if apoderado_persona:
                    apoderados_serializer.append(apoderado_persona)
            serializador = self.serializer_class(apoderados_serializer, many=True)
            return Response(
                {"success": True, "detail": "Se encontraron los siguientes apoderados", "data": serializador.data},
                status=status.HTTP_200_OK,
            )
        else:
            raise NotFound("No existen apoderados para el poderdante seleccionado")
        

#CREAR_OTROS
class OtrosCreate(generics.CreateAPIView):
    serializer_class = OtrosPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # try:
            with transaction.atomic():
                data_otros = json.loads(request.data.get('otros', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))
                id_persona_guarda = ast.literal_eval(request.data.get('id_persona_guarda', ''))

                debe_radicar = isCreateForWeb and data_otros['es_anonima']
                fecha_actual = datetime.now()
                valores_creados_detalles = []

                util_Otros = Util_OTROS()
                anexos = util_Otros.set_archivo_in_anexo(data_otros['anexos'], request.FILES, "create")

                #Crea el Otros
                data_OTROS_creado = self.create_otros(data_otros, fecha_actual)

                #Guarda el nuevo estado Guardado en la tabla T255
                historicoEstadosCreate = HistoricoEstadosCreate()
                historicoEstadosCreate.create_historico_estado(data_OTROS_creado, 'GUARDADO', id_persona_guarda, fecha_actual)
                
                #Guarda los anexos en la tabla T258 y la relación entre los anexos y el Otros en la tabla T301 si tiene anexos
                if anexos:
                    anexosCreate = AnexosCreate()
                    valores_creados_detalles = anexosCreate.create_anexos_otros(anexos, data_OTROS_creado['id_otros'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    if update_requiere_digitalizacion:
                        data_OTROS_creado = self.update_requiereDigitalizacion_otros(data_OTROS_creado)

                # #Auditoria
                # descripcion_auditoria = self.set_descripcion_auditoria(data_OTROS_creado)
                # self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles)

                #Si tiene que radicar, crea el radicado
                if debe_radicar:
                    radicarOTROS = RadicarOTROS()
                    data_radicado = radicarOTROS.radicar_otros(request, data_OTROS_creado['id_otros'], id_persona_guarda, isCreateForWeb)
                    data_OTROS_creado = data_radicado['otros']
                
                return Response({'success':True, 'detail':'Se creo OTROS correctamente', 'data':data_OTROS_creado}, status=status.HTTP_201_CREATED)
        
        # except Exception as e:
        #     return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def create_otros(self, data, fecha_actual):
        data_otros = self.set_data_otros(data, fecha_actual)
        serializer = self.serializer_class(data=data_otros)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
    
    def update_requiereDigitalizacion_otros(self, data_OTROS_creado):
        PrsdfUpdate = OTROSUpdate()
        pqr_instance = Otros.objects.filter(id_otros = data_OTROS_creado['id_otros']).first()
        data_otros_update = copy.deepcopy(data_OTROS_creado)
        data_otros_update['requiere_digitalizacion'] = False
        otros_update = PrsdfUpdate.update_otros(pqr_instance, data_otros_update)
        return otros_update

    def set_data_otros(self, data, fecha_actual):
        data['fecha_registro'] = data['fecha_inicial_estado_actual'] = fecha_actual
        data['requiere_digitalizacion'] = True if data['cantidad_anexos'] != 0 else False
    
        estado = EstadosSolicitudes.objects.filter(nombre='GUARDADO').first()
        data['id_estado_actual_solicitud'] = estado.id_estado_solicitud

    
        return data

    def set_descripcion_auditoria(self, otros):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=otros['cod_tipo_PQRSDF']).first() 
        persona = Personas.objects.filter(id_persona = otros['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = otros['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(otros['fecha_registro']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data

class OTROSUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = OtrosPostSerializer
    queryset = Otros.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                #Obtiene los datos enviado en el request
                otros = json.loads(request.data.get('otros', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))

                otros_db = self.queryset.filter(id_otros=otros['id_otros']).first()
                if otros_db:
                    anexos = otros['anexos']
                    fecha_actual = datetime.now()

                    #Actualiza los anexos y los metadatos
                    data_auditoria_anexos = self.procesa_anexos(anexos, request.FILES, otros['id_otros'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    otros['requiere_digitalizacion'] = False if update_requiere_digitalizacion else True
                    
                    #Actuaiza otros
                    otros_update = self.update_otros(otros_db, otros)

                    #Auditoria
                    descripcion_auditoria = self.set_descripcion_auditoria(otros_update)
                    self.auditoria(request, descripcion_auditoria, isCreateForWeb, data_auditoria_anexos)
                    
                    return Response({'success':True, 'detail':'Se editó OTRO correctamente', 'data': otros_update}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'No se encontró el OTRO para actualizar'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update_otros(self, otros_db, otros_update):
        try:
            serializer = self.serializer_class(otros_db, data=otros_update)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data
        except Exception as e:
            raise({'success': False, 'detail': str(e)})
    

    def procesa_anexos(self, anexos, archivos, id_otros, isCreateForWeb, fecha_actual):
        data_auditoria_create = []
        data_auditoria_update = []
        data_auditoria_delete = []

        anexos = [] if not anexos else anexos
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        anexos_pqr_DB = Anexos_PQR.objects.filter(id_otros = id_otros)
        if anexos_pqr_DB:
            Util_OTROS = Util_OTROS()
            data_anexos_create = [anexo for anexo in anexos if anexo['id_anexo'] == None]
            anexos_create = Util_OTROS.set_archivo_in_anexo(data_anexos_create, archivos, "create")
            
            data_anexos_update = [anexo for anexo in anexos if not anexo['id_anexo'] == None]
            anexos_update = Util_OTROS.set_archivo_in_anexo(data_anexos_update, archivos, "update")

            ids_anexos_update = [anexo_update['id_anexo'] for anexo_update in anexos_update]
            anexos_delete = [anexo_pqr for anexo_pqr in anexos_pqr_DB if getattr(anexo_pqr,'id_anexo_id') not in ids_anexos_update]

            anexosCreate = AnexosCreate()
            anexosUpdate = AnexosUpdate()
            anexosDelete = AnexosDelete()

            data_auditoria_create = anexosCreate.create_anexos_otros(anexos_create, id_otros, isCreateForWeb, fecha_actual)
            data_auditoria_update = anexosUpdate.put(anexos_update, fecha_actual)
            data_auditoria_delete = anexosDelete.delete(anexos_delete)
            
        else:
            anexosCreate = AnexosCreate()
            Util_OTROS = Util_OTROS()
            anexos_create = Util_OTROS.set_archivo_in_anexo(anexos, archivos, "create")
            data_auditoria_create = anexosCreate.create_anexos_otros(anexos_create, id_otros, isCreateForWeb, fecha_actual)

        return {
            'data_auditoria_create': data_auditoria_create,
            'data_auditoria_update1': data_auditoria_update,
            'data_auditoria_delete': data_auditoria_delete
        }
    
    def set_descripcion_auditoria(self, otros):
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=otros['cod_tipo_PQRSDF']).first()

        persona = Personas.objects.filter(id_persona = otros['id_persona_titular']).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        medioSolicitud = MediosSolicitud.objects.filter(id_medio_solicitud = otros['id_medio_solicitud']).first()

        data = {
            'TipoPQRSDF': str(tipo_pqrsdf.nombre),
            'NombrePersona': str(nombre_persona_titular),
            'FechaRegistro': str(otros['fecha_registro']),
            'MedioSolicitud': str(medioSolicitud.nombre)
        }

        return data



#UTIL
class Util_OTROS:
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
    


#BORRAR_OTROS
class OTROSDelete(generics.RetrieveDestroyAPIView):
    serializer_class = OTROSSerializer
    borrar_estados = Estados_OTROSDelete
    queryset = Otros.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        # try:
            with transaction.atomic():
                #Parametros para eliminacion
                if request.query_params.get('id_otros')==None or request.query_params.get('isCreateForWeb')==None:
                    raise ValidationError('No se ingresaron parámetros necesarios para eliminar el OTRO')
                id_otros = int(request.query_params.get('id_otros', 0))
                isCreateForWeb = ast.literal_eval(request.query_params.get('isCreateForWeb', False))

                valores_eliminados_detalles = []
                otros_delete = self.queryset.filter(id_otros = id_otros).first()
                if otros_delete:
                    if not otros_delete.id_radicados:
                        #Elimina los anexos, anexos_pqr, metadatos y el archivo adjunto
                        anexos_otros = Anexos_PQR.objects.filter(id_otros = id_otros)
                        if anexos_otros:
                            anexosDelete = AnexosDelete()
                            valores_eliminados_detalles = anexosDelete.delete(anexos_otros)

                        #Elimina el estado creado en el historico
                        self.borrar_estados.delete(self, id_otros)
                        #Elimina el pqrsdf
                        otros_delete.delete()
                        # #Auditoria
                        # descripcion_auditoria = self.set_descripcion_auditoria(otros_delete)
                        # self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_eliminados_detalles)

                        return Response({'success':True, 'detail':'El OTRO ha sido descartado'}, status=status.HTTP_200_OK)
                    else:
                        raise NotFound('No se permite borrar la solicitud otros ya radicados')
                else:
                    raise NotFound('No se encontró ningún otro con estos parámetros')
            
        # except Exception as e:
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
    

########################## Historico Estados ##########################
class HistoricoEstadosCreate(generics.CreateAPIView):
    creador_estados = Estados_PQRCreate()

    def create_historico_estado(self, data_OTROS, nombre_estado, id_persona_guarda, fecha_actual):
        data_estado_crear = self.set_data_estado(data_OTROS, nombre_estado, id_persona_guarda, fecha_actual)
        self.creador_estados.crear_estado(data_estado_crear)

    def set_data_estado(self, data_OTROS, nombre_estado, id_persona_guarda, fecha_actual):
        data_estado = {}
        data_estado['Otros'] = data_OTROS['id_otros']
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['persona_genera_estado'] = None if id_persona_guarda == 0 else id_persona_guarda

        estado = EstadosSolicitudes.objects.filter(nombre=nombre_estado).first()
        data_estado['estado_solicitud'] = estado.id_estado_solicitud

        return data_estado
    

########################## ANEXOS Y ANEXOS PQR ##########################
class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer
    
    def create_anexos_otros(self, anexos, id_otros, isCreateForWeb, fecha_actual):
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        nombres_anexos_auditoria = []
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        for anexo in anexos:
            data_anexo = self.crear_anexo(anexo)

            #Crea la relacion en la tabla T259
            data_anexos_OTROS = {}
            data_anexos_OTROS['id_otros'] = id_otros
            data_anexos_OTROS['id_anexo'] = data_anexo['id_anexo']
            anexosPQRCreate = AnexosPQRCreate()
            anexosPQRCreate.crear_anexo_pqr(data_anexos_OTROS)
            print (anexo)
            #Guardar el archivo en la tabla T238
            if anexo.get('archivo'):
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
        
        formatos=FormatosTiposMedio.objects.filter(nombre__iexact=extension_sin_punto.lower(),activo=True).first()
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
    

class AnexosPQRCreate(generics.CreateAPIView):
    serializer_class = AnexosPQRSDFPostSerializer
    
    def crear_anexo_pqr(self, request):
        # try:
            print(request)
            serializer = self.serializer_class(data=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        # except Exception as e:
        #     raise({'success': False, 'detail': str(e)})
        

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
        # try:
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
            
        # except Exception as e:
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
        # try:
            data_to_create = self.set_data_metadato(data_metadatos)
            serializer = self.serializer_class(data=data_to_create)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        # except Exception as e:
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
    
class ArchivoDelete(generics.RetrieveDestroyAPIView):
    serializer_class = ArchivosSerializer
    queryset = ArchivosDigitales.objects.all()

    def delete(self, id_archivo_digital):
        # try:
            archivo = self.queryset.filter(id_archivo_digital = id_archivo_digital).first()
            if archivo:
                archivo.delete()
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros') 
        # except Exception as e:
        #   raise({'success': False, 'detail': str(e)})
        

class MetadatosPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = MetadatosSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    def delete(self, id_anexo):
        # try:
            metadato = self.queryset.filter(id_anexo = id_anexo).first()
            if metadato:
                archivoDelete = ArchivoDelete()
                archivoDelete.delete(metadato.id_archivo_sistema_id)
                metadato.delete()
                return True
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros')
        # except Exception as e:
        #   raise({'success': False, 'detail': str(e)})
        

####################### RADICADOS ##########################
class RadicarOTROS(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # try:
            with transaction.atomic():
                id_otros = request.data['id_otros']
                id_persona_guarda = request.data['id_persona_guarda']
                isCreateForWeb = request.data['isCreateForWeb']
                data_radicado_otros = self.radicar_otros(request, id_otros, id_persona_guarda, isCreateForWeb)
                return Response({'success':True, 
                                 'detail':'Se creo el radicado para otros', 
                                 'data': data_radicado_otros['radicado']}, status=status.HTTP_201_CREATED)
        
        # except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def radicar_otros(self, request, id_otros, id_persona_guarda, isCreateForWeb):
        fecha_actual = datetime.now()
        data_OTROS_instance = Otros.objects.filter(id_otros = id_otros).first()
        previous_instance = copy.copy(data_OTROS_instance)

        
        #Crea el radicado
        data_for_create = {}
        data_for_create['fecha_actual'] = fecha_actual
        data_for_create['id_usuario'] = id_persona_guarda
        data_for_create['tipo_radicado'] = "E"
        data_for_create['modulo_radica'] = "OTROS"
        radicadoCreate = RadicadoCreate()
        data_radicado = radicadoCreate.post(data_for_create)

        #Actualiza el estado y la data del radicado al OTROS
        OtrosUpdate = OTROSUpdate()
        otros_dic = model_to_dict(data_OTROS_instance)
        data_update_otros= self.set_data_update_radicado_otros(otros_dic, data_radicado, fecha_actual)
        data_OTROS_creado = OtrosUpdate.update_otros(data_OTROS_instance, data_update_otros)

        #Guarda el nuevo estado Radicado en la tabla T255
        historicoEstadosCreate = HistoricoEstadosCreate()
        historicoEstadosCreate.create_historico_estado(data_OTROS_creado, 'RADICADO', id_persona_guarda, fecha_actual)

        # #Auditoria
        # descripciones = self.set_descripcion_auditoria(previous_instance, data_OTROS_instance)
        # self.auditoria(request, descripciones['descripcion'], isCreateForWeb, descripciones['data_auditoria_update'])
        
        return {
            'radicado': data_radicado,
            'otros': data_OTROS_creado
        }
    
    
    def set_data_update_radicado_otros(self, otros, id_radicados, fecha_actual):
        otros['id_radicados'] = id_radicados['id_radicados']
        otros['fecha_radicado'] = id_radicados['fecha_radicado']

        estado = EstadosSolicitudes.objects.filter(nombre='RADICADO').first()
        otros['id_estado_actual_solicitud'] = estado.id_estado_solicitud
        otros['fecha_ini_estado_actual'] = fecha_actual

        return otros
    
    def set_descripcion_auditoria(self, previous_otros, otros_update):
        descripcion_auditoria_update = {
            'IdRadicado': previous_otros.id_radicados,
            'FechaRadicado': previous_otros.fecha_radicado
        }

        data_auditoria_update = {'previous':previous_otros, 'current':otros_update}

        data = {
            'descripcion': descripcion_auditoria_update,
            'data_auditoria_update': data_auditoria_update
        }

        return data
    

class RadicadoCreate(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    config_radicados = ConfigTiposRadicadoAgnoGenerarN
    
    def post(self, data_radicado):
        # try:
            config_tipos_radicado = self.get_config_tipos_radicado(data_radicado)
            radicado_data = self.set_data_radicado(config_tipos_radicado, data_radicado['fecha_actual'], data_radicado['id_usuario'], data_radicado['modulo_radica'])
            serializer = self.serializer_class(data=radicado_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data

        # except Exception as e:
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
