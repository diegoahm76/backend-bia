
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import documento_formulario_recuados_Getserializer, documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status



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

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)

