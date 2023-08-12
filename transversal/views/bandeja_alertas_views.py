import copy
from rest_framework import generics
from transversal.models.alertas_models import FechaClaseAlerta

from transversal.serializers.alertas_serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class BandejaAlertaPersonaGetByPersona(generics.ListAPIView):

    serializer_class = BandejaAlertaPersonaGetSerializer
    queryset = BandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

           
        bandeja = BandejaAlertaPersona.objects.filter(id_persona=pk)
                
        
        
        if not bandeja:
            raise NotFound("La persona no tiene bandeja de alertas porfavor comunicarse con un administrador.")
        
        serializer = self.serializer_class(bandeja,many=True)
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)

class AlertasBandejaAlertaPersonaGetByBandeja(generics.ListAPIView):

    serializer_class = AlertasBandejaAlertaPersonaGetSerializer
    queryset = AlertasBandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

           
        items = AlertasBandejaAlertaPersona.objects.filter(id_bandeja_alerta_persona=pk)
                
        
        if not items:
            raise NotFound("La bandeja no tiene items de alertas porfavor comunicarse con un administrador.")
        
        serializer = self.serializer_class(items,many=True)
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class AlertasBandejaAlertaPersonaUpdate(generics.UpdateAPIView):
    serializer_class = AlertasBandejaAlertaPersonaPutSerializer
    queryset = AlertasBandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        previus=copy.copy(instance)
        data_in=request.data
        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'El item de bandeja  no existe.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            
            if 'repeticiones_suspendidas' in data_in:
                if previus.repeticiones_suspendidas != instance.repeticiones_suspendidas and instance.repeticiones_suspendidas==True:
                    #print("PRE CONDICION")
                    alerta_programada=AlertasProgramadas.objects.filter(id_alerta_programada=instance.id_alerta_generada.id_alerta_programada_origen).first()
                    if not alerta_programada:
                        raise NotFound('No existe alerta programada')
                    #print("PRE CONDICION")
                    if alerta_programada.agno_cumplimiento:
                        print("CONDICION CON AÑO")
                    else:
                        print("SIN AÑO")


        except ValidationError as e:       
            raise ValidationError(e.detail)


        return Response({'success': True, 'detail': 'Se actualizó la configuración de clase de alerta correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
