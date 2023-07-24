import json
from collections import Counter
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta
from transversal.models.alertas_models import ConfiguracionClaseAlerta, FechaClaseAlerta

from transversal.serializers.alertas_serializers import ConfiguracionClaseAlertaGetSerializer, FechaClaseAlertaDeleteSerializer, FechaClaseAlertaGetSerializer, FechaClaseAlertaPostSerializer


class ConfiguracionClaseAlertaGetByCod(generics.ListAPIView):

    serializer_class = ConfiguracionClaseAlertaGetSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        alerta = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            raise NotFound("No existe esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)



class FechaClaseAlertaCreate(generics.CreateAPIView):
    serializer_class = FechaClaseAlertaPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = FechaClaseAlerta.objects.all()
    
    def post(self,request):
        data_in = request.data
        try:

            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
  
class FechaClaseAlertaDelete(generics.DestroyAPIView):

    serializer_class = FechaClaseAlertaDeleteSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,cod):
        
        fecha = FechaClaseAlerta.objects.filter(id_fecha=cod).first()
        
        if not fecha:
            raise NotFound("No existe la fecha a eliminar.")
        serializer = self.serializer_class(fecha) 
        fecha.delete()

        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    

class FechaClaseAlertaGetByConfiguracion(generics.ListAPIView):

    serializer_class = FechaClaseAlertaGetSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        fechas = FechaClaseAlerta.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(fechas,many=True)
        
        if not fechas:
            raise NotFound("No existe fechas asociadas a esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)




