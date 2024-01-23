
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import  CaptacionMensualAgua, T0444Formulario, documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import  T0444FormularioSerializer, documento_formulario_recuados_Getserializer, documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.views import APIView

from transversal.views.alertas_views import AlertaEventoInmediadoCreate



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

                #GENERA ALERTA DE EVEMTO INMEDIATO 

                vista_alertas_programadas = AlertaEventoInmediadoCreate()
                data_alerta = {}
                data_alerta['cod_clase_alerta'] = 'Rec_GenDoc'
                #data_alerta['id_persona'] = id_persona_asiganada
                data_alerta['id_elemento_implicado'] = data_archivo_id
                

                respuesta_alerta = vista_alertas_programadas.crear_alerta_evento_inmediato(data_alerta)
                if respuesta_alerta.status_code != status.HTTP_200_OK:
                    return respuesta_alerta

                return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                raise ValidationError("No se proporcionó ningún archivo.")
        except ValidationError as e:
            raise ValidationError(e.detail)



class DocumentoFormularioRecaudoGET(generics.ListAPIView):
    queryset = documento_formulario_recuado.objects.all()
    serializer_class = documento_formulario_recuados_Getserializer

    def get(self, request):
        instance = self.get_queryset()
        serializer = self.serializer_class(instance, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)



class T0444444FormularioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = T0444FormularioSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return   Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TipoUsuarioOptionsView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        tipo_usuario_choices = dict(T0444Formulario.TIPO_USUARIO_CHOICES)
        return Response({'tipo_usuario_choices': tipo_usuario_choices})
    

class CaptacionMensualAguaViwes(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        MES_CHOICESs = dict(CaptacionMensualAgua.MES_CHOICES)
        return Response({'meses': MES_CHOICESs})