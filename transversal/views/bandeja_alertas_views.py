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
