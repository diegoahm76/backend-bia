
from gestion_documental.models.consecutivo_unidad_models import Consecutivo
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import  CaptacionMensualAgua, T0444Formulario, T458PrincipalLiquidacion, T459TablaTercerosss, documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import  PrincipalLiquidacionSerializer, T0444FormularioSerializer, T459TablaTercerosssSerializer, documento_formulario_recuados_Getserializer, documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.views import APIView
import json


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
                #ASIGNA EL CONSECUTIVO DEL DOCUMENTO AL DOCUMENTO
                data_in = request.data
                if not 'id_consecutivo' in data_in:
                    raise ValidationError("No se proporcionó el consecutivo del documento.")
                id_consecutivo = data_in['id_consecutivo']

                instance = Consecutivo.objects.filter(id_consecutivo=id_consecutivo).first()

                if not instance:
                    raise ValidationError("No se encontró el consecutivo del documento.")
                
                instance.id_documento_digital = data_archivo_id
                instance.save()

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
        json_informacionFuentesAbastecimiento=json.loads(request.data.get('informacionFuentesAbastecimiento'))
        json_factoresUtilizacion= json.loads(request.data.get('factoresUtilizacion'))
        json_captacionesMensualesAgua=json.loads(request.data.get('captacionesMensualesAgua'))
        # print(type(json_captacionesMensualesAgua))
        # print("###############")
        # print(type(json_factoresUtilizacion))
        # print("###############")

        # print(type(json_informacionFuentesAbastecimiento))
        # print(request.data)
        data_completa=request.data.dict()
        # print(type(data_completa))
        data_completa.pop('captacionesMensualesAgua',None)
        data_completa.pop('factoresUtilizacion',None)
        data_completa.pop('informacionFuentesAbastecimiento',None)
        data_completa.pop('id_archivo_digital', None)
        data_completa["informacionFuentesAbastecimiento"]=json_informacionFuentesAbastecimiento
        data_completa['factoresUtilizacion']=json_factoresUtilizacion
        data_completa['captacionesMensualesAgua']=json_captacionesMensualesAgua 
        vista_archivos = ArchivosDgitalesCreate()
        archivo = request.FILES.get('id_archivo_sistema')
        ruta = "home,BIA,Otros,Recaudo,AutoDeclaracion"
        respuesta_archivo = vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo)
        if respuesta_archivo.status_code != status.HTTP_201_CREATED:
            return respuesta_archivo
        data_archivo = respuesta_archivo.data['data']

        id_archivo =data_archivo['id_archivo_digital']
        # print(data_archivo)
        data_completa.pop('id_archivo_sistema', None)
        data_completa['id_archivo_sistema']=id_archivo
        serializer = T0444FormularioSerializer(data=data_completa)

        if serializer.is_valid():
            serializer.save()
            return   Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class T0444FormularioListView(APIView):
    def get(self, request, *args, **kwargs):
        formularios = T0444Formulario.objects.all()
        serializer = T0444FormularioSerializer(formularios, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class T0444444FormularioPut(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            formulario = T0444Formulario.objects.get(pk=pk)
        except T0444Formulario.DoesNotExist:
            return Response({'detail': 'El formulario no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener el valor del campo aprobado del cuerpo de la solicitud
        aprobado = request.data.get('aprobado', None)

        # Verificar si se proporciona el valor de 'aprobado'
        if aprobado is not None:
            # Actualizar el campo 'aprobado' con el nuevo valor
            formulario.aprobado = aprobado
            formulario.save()

            # Serializar y devolver la respuesta
            serializer = T0444FormularioSerializer(formulario)
            return Response({'success': True, 'detail': 'Campo aprobado actualizado correctamente', 'data': serializer.data})
        else:
            return Response({'detail': 'Se debe proporcionar un valor para el campo aprobado'}, status=status.HTTP_400_BAD_REQUEST)
        


class TipoUsuarioOptionsView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        tipo_usuario_choices = dict(T0444Formulario.TIPO_USUARIO_CHOICES)
        return Response({'tipo_usuario_choices': tipo_usuario_choices})
    

class CaptacionMensualAguaViwes(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        MES_CHOICESs = dict(CaptacionMensualAgua.MES_CHOICES)
        return Response({'meses': MES_CHOICESs})
    



class T458PrincipalLiquidacionPorExpediente(generics.ListAPIView):
    serializer_class = PrincipalLiquidacionSerializer

    def get_queryset(self):
        expediente = self.request.query_params.get('expediente', None)
        nit = self.request.query_params.get('nit', None)
        queryset = T458PrincipalLiquidacion.objects.all()
        
        if expediente:
            queryset = queryset.filter(T458expediente=expediente)
        
        if nit:
            queryset = queryset.filter(T458nit=nit)
        
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)
        except T458PrincipalLiquidacion.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron registros para los parámetros proporcionados'}, status=status.HTTP_404_NOT_FOUND)
        


class viewsT459TablaTercerosssView(generics.ListAPIView):
    serializer_class = T459TablaTercerosssSerializer

    def get_queryset(self):
        nro_documento = self.request.query_params.get('nro_documento', None)
        razon_social = self.request.query_params.get('razon_social', None)
        queryset = T459TablaTercerosss.objects.all()
        
        if nro_documento:
            queryset = queryset.filter(T459nroDocumentoID=nro_documento)
        
        if razon_social:
            queryset = queryset.filter(T459razonSocial__icontains=razon_social)
        
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)
        except T459TablaTercerosss.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron registros para los parámetros proporcionados'}, status=status.HTTP_404_NOT_FOUND)