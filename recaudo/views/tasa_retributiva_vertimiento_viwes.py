
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.tasa_retributiva_vertimiento_models import  CaptacionMensualAgua, T0444Formulario, documento_formulario_recuado
from recaudo.serializers.tasa_retributiva_vertimiento_serializers import  T0444FormularioSerializer, documento_formulario_recuados_Getserializer, documento_formulario_recuados_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.views import APIView

from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.views.alertas_views import AlertaEventoInmediadoCreate



class CrearDocumentoFormularioRecuado(generics.CreateAPIView):
    queryset = documento_formulario_recuado.objects.all()
    serializer_class = documento_formulario_recuados_serializer
    archivos_dgitales_create = ArchivosDgitalesCreate()



    def buscar_persona_lider(self,id_unidad):
            ids_personas =[]
            lideres_unidad_orga=LideresUnidadesOrg.objects.filter(id_unidad_organizacional=id_unidad)
            for lider in lideres_unidad_orga:
                ids_personas.append(lider.id_persona.id_persona)
            return ids_personas
    
    def buscar_persona_perfil(self,cod_perfil):
        perfiles_actuales=ConfiguracionEntidad.objects.first()
        if cod_perfil == 'Dire':
            if perfiles_actuales.id_persona_director_actual:
                id_responsable=(perfiles_actuales.id_persona_director_actual.id_persona)
        elif cod_perfil == 'CAlm':
            if perfiles_actuales.id_persona_coord_almacen_actual:
                id_responsable=(perfiles_actuales.id_persona_coord_almacen_actual.id_persona)
        elif cod_perfil == 'RTra':
            if perfiles_actuales.id_persona_respon_transporte_actual:
                id_responsable=(perfiles_actuales.id_persona_respon_transporte_actual.id_persona)
        elif cod_perfil == 'CViv':
            if perfiles_actuales.id_persona_coord_viveros_actual:
                id_responsable=(perfiles_actuales.id_persona_coord_viveros_actual.id_persona)
        elif cod_perfil == 'Alma':
            if perfiles_actuales.id_persona_almacenista:
                id_responsable=(perfiles_actuales.id_persona_almacenista.id_persona)
        return id_responsable

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
                #ENVIO DE DOCUMENTO POR CORREO
                ids=[]

                if 'ids_destinatarios_unidades' in data_in:
                    ids_unidades = vector = json.loads(data_in['ids_destinatarios_unidades'])

                    for id in ids_unidades:
                        ids_persona = self.buscar_persona_lider(id)
                        ids.extend(ids_persona)
                if 'ids_destinatarios_perfiles' in data_in:
                    ids_perfiles = vector = json.loads(data_in['ids_destinatarios_perfiles'])
                    for id in ids_perfiles:
                        id_persona = self.buscar_persona_perfil(id)
                        ids.append(id_persona)
                if 'ids_destinatarios_personas' in data_in:
                    ids_personas  = json.loads(data_in['ids_destinatarios_personas'])
                    ids.extend(ids_personas)
                print("LIDERES DE UNIDAD")

                print(ids)

                raise ValidationError('aaui')
                   



                if 'ids_destinatarios_personas' in data_in:
                    ids_personas = vector = json.loads(data_in['ids_destinatarios_personas'])


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