
import copy
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import TiposPQR
from rest_framework.response import Response
from gestion_documental.serializers.pqr_serializers import TiposPQRGetSerializer, TiposPQRUpdateSerializer
from seguridad.utils import Util
class TiposPQRGet(generics.ListAPIView):
    serializer_class = TiposPQRGetSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        instance=TiposPQR.objects.all()
        if not instance:
            raise NotFound("No existen tipos de radicado")
        
        serializer = self.serializer_class(instance, many=True)

                         
        return Response({'succes':True, 'detail':'Se encontró los siguientes registross','data':serializer.data}, status=status.HTTP_200_OK)




class TiposPQRUpdate(generics.UpdateAPIView):
    serializer_class = TiposPQRUpdateSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:    
            data = request.data
            instance = TiposPQR.objects.filter(cod_tipo_pqr=pk).first()
            
            if not instance:
                raise NotFound("No se existe un tipo de radicado con este codigo.")
            
            instance_previous=copy.copy(instance)
            serializer = self.serializer_class(instance,data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            #AUDITORIA 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"Nombre":instance.nombre}
            valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 153,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    