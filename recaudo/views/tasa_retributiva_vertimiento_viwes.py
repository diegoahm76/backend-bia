
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status



class CrearDocumentoFormularioRecuado(generics.CreateAPIView):
    queryset = documento_formulario_recuado.objects.all()
    serializer_class = documento_formulario_recuados_serializer
    archivos_dgitales_create = ArchivosDgitalesCreate()

    def create(self, request, *args, **kwargs):
        try:
            archivos = request.FILES.getlist('archivo')

            if archivos:
                id_archivos = []

                for archivo in archivos:
                    # Procesar cada archivo y obtener el ID del archivo digital
                    archivo_digital_id = self.archivos_dgitales_create.crear_archivo({'es_Doc_elec_archivo': False}, archivo).data['data']['id_archivo_digital']
                    id_archivos.append(archivo_digital_id)

                # Puedes manejar múltiples archivos de diferentes maneras, aquí solo se toma el primer archivo
                request.data['id_archivo_sistema'] = id_archivos[0]

                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                raise ValidationError("No se proporcionó ningún archivo.")
        except ValidationError as e:
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})


