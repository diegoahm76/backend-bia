
from seguridad.permissions.permissions_gestor import PermisoActualizarConfiguracionTiemposRespuesta
from seguridad.utils import Util
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from gestion_documental.serializers.configuracion_tiempos_respuesta_serializers import ConfiguracionTiemposRespuestaGetSerializer, ConfiguracionTiemposRespuestaPutSerializer
import copy
class ConfiguracionTiemposRespuestaGet(generics.ListAPIView):
    serializer_class = ConfiguracionTiemposRespuestaGetSerializer
    queryset = ConfiguracionTiemposRespuesta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        queryset=ConfiguracionTiemposRespuesta.objects.all()
        serializador = self.serializer_class(queryset, many=True)
                         
        return Response({'succes':True, 'detail':'Se encontró el siguiente histórico','data':serializador.data}, status=status.HTTP_200_OK)


class ConfiguracionTiemposRespuestaUpdate(generics.UpdateAPIView):

    serializer_class = ConfiguracionTiemposRespuestaPutSerializer
    queryset = ConfiguracionTiemposRespuesta.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarConfiguracionTiemposRespuesta]
    

    def put(self, request, pk):
        try:
            data = request.data
            confi = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=pk).first()
            previus=copy.copy(confi)
            if not confi:
                raise NotFound("No se existe una configuracion asociada a esta id.")
        
        
            serializer = self.serializer_class(confi, data=data,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.update(confi, serializer.validated_data)

            usuario = request.user.id_usuario
            #descripcion = {"Codigo bien": str(nodo.codigo_bien), "Numero elemento bien": str(nodo.nro_elemento_bien)}
            descripcion = {"NombreConfiguracion":instance.nombre_configuracion} 
            direccion = Util.get_client_ip(request)
            valores_actualizados={'previous':previus, 'current':instance}
            auditoria_data = {
                    "id_usuario": usuario,
                    "id_modulo": 163,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion,
                    'valores_actualizados': valores_actualizados
                }
            Util.save_auditoria(auditoria_data)

            return Response({'success': True, 'detail': 'Se actualizaron los registros correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise ValidationError(e.detail)