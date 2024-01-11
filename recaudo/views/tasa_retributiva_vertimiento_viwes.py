
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import CaptacionMensualAgua, CoordenadasSitioCaptacion, FactoresUtilizacion, InformacionFuente, T0444Formulario, documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import CaptacionMensualAguaSerializer, CoordenadasSitioCaptacionSerializer, FactoresUtilizacionSerializer, InformacionFuenteSerializer, T0444FormularioSerializer, documento_formulario_recuados_Getserializer, documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.views import APIView



class CrearDocumentoFormularioRecuado(generics.CreateAPIView):
    queryset = documento_formulario_recuado.objects.all()
    serializer_class = documento_formulario_recuados_serializer
    archivos_dgitales_create = ArchivosDgitalesCreate()

    def create(self, request, *args, **kwargs):
        try:
            respuesta_archivo={}
            archivo = request.FILES.get('archivo')

            if archivo:
                id_archivos = []
                    # Procesar cada archivo y obtener el ID del archivo digital
                respuesta_archivo = self.archivos_dgitales_create.crear_archivo({'es_Doc_elec_archivo': False}, archivo)
                #.data['data']['id_archivo_digital']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED :
                     return respuesta_archivo
                data_archivo = respuesta_archivo.data['data'] 
                data_archivo_id=data_archivo['id_archivo_digital']

                # Puedes manejar múltiples archivos de diferentes maneras, aquí solo se toma el primer archivo
                request.data['id_archivo_sistema'] = data_archivo_id

                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                raise ValidationError("No se proporcionó ningún archivo.")
        except ValidationError as e:
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})



class DocumentoFormularioRecaudoGET(generics.ListAPIView):
    queryset = documento_formulario_recuado.objects.all()
    serializer_class = documento_formulario_recuados_Getserializer

    def get(self, request):
        instance = self.get_queryset()
        serializer = self.serializer_class(instance, many=True)





class T0444444FormularioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = T0444FormularioSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class CrearFormularioView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = CrearFormularioSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# class T0444FormularioCreateView(generics.CreateAPIView):
#     serializer_class = T0444FormularioSerializer

#     def create(self, request, *args, **kwargs):
#         # Deserializar la data recibida
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Crear instancias asociadas utilizando serializadores
#         informacion_fuentes_data = serializer.validated_data.pop('informacionFuentesAbastecimiento')
#         coordenadas_sitio_captacion_data = serializer.validated_data.pop('coordenadasSitioCaptacion')
#         factores_utilizacion_data = serializer.validated_data.pop('factoresUtilizacion')
#         captaciones_mensuales_agua_data = serializer.validated_data.pop('captacionesMensualesAgua')

#         informacion_fuentes_serializer = InformacionFuenteSerializer(data=informacion_fuentes_data, many=True)
#         coordenadas_sitio_captacion_serializer = CoordenadasSitioCaptacionSerializer(data=coordenadas_sitio_captacion_data)
#         factores_utilizacion_serializer = FactoresUtilizacionSerializer(data=factores_utilizacion_data)
#         captaciones_mensuales_agua_serializer = CaptacionMensualAguaSerializer(data=captaciones_mensuales_agua_data, many=True)

#         informacion_fuentes_serializer.is_valid(raise_exception=True)
#         coordenadas_sitio_captacion_serializer.is_valid(raise_exception=True)
#         factores_utilizacion_serializer.is_valid(raise_exception=True)
#         captaciones_mensuales_agua_serializer.is_valid(raise_exception=True)

#         informacion_fuentes = informacion_fuentes_serializer.save()
#         coordenadas_sitio_captacion = coordenadas_sitio_captacion_serializer.save()
#         factores_utilizacion = factores_utilizacion_serializer.save()
#         captaciones_mensuales_agua = captaciones_mensuales_agua_serializer.save()

#         # Asignar las instancias asociadas a la instancia principal
#         serializer.validated_data['informacionFuentesAbastecimiento'] = informacion_fuentes
#         serializer.validated_data['coordenadasSitioCaptacion'] = coordenadas_sitio_captacion
#         serializer.validated_data['factoresUtilizacion'] = factores_utilizacion
#         serializer.validated_data['captacionesMensualesAgua'] = captaciones_mensuales_agua

#         # Crear la instancia principal
#         self.perform_create(serializer)

#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# class T0444FormularioCreateView(generics.CreateAPIView):
#     serializer_class = T0444FormularioSerializer

#     def create(self, request, *args, **kwargs):
#         # Deserializar la data recibida
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Crear las instancias asociadas
#         informacion_fuentes = InformacionFuente.objects.bulk_create(serializer.validated_data['informacionFuentesAbastecimiento'])
#         coordenadas_sitio_captacion = CoordenadasSitioCaptacion.objects.create(**serializer.validated_data['coordenadasSitioCaptacion'])
#         factores_utilizacion = FactoresUtilizacion.objects.create(**serializer.validated_data['factoresUtilizacion'])
#         captaciones_mensuales_agua = CaptacionMensualAgua.objects.bulk_create(serializer.validated_data['captacionesMensualesAgua'])

#         # Asignar las instancias asociadas a la instancia principal
#         serializer.validated_data['informacionFuentesAbastecimiento'] = informacion_fuentes
#         serializer.validated_data['coordenadasSitioCaptacion'] = coordenadas_sitio_captacion
#         serializer.validated_data['factoresUtilizacion'] = factores_utilizacion
#         serializer.validated_data['captacionesMensualesAgua'] = captaciones_mensuales_agua

#         # Crear la instancia principal
#         self.perform_create(serializer)

#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)