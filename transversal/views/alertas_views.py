import json
from collections import Counter
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta
from transversal.models.alertas_models import ConfiguracionClaseAlerta, FechaClaseAlerta, PersonasAAlertar

from transversal.serializers.alertas_serializers import ConfiguracionClaseAlertaGetSerializer, ConfiguracionClaseAlertaUpdateSerializer, FechaClaseAlertaDeleteSerializer, FechaClaseAlertaGetSerializer, FechaClaseAlertaPostSerializer, PersonasAAlertarDeleteSerializer, PersonasAAlertarGetSerializer, PersonasAAlertarPostSerializer

class ConfiguracionClaseAlertaUpdate(generics.UpdateAPIView):
    serializer_class = ConfiguracionClaseAlertaUpdateSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()

        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuración de clase de alerta no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'detail': 'Se actualizó la configuración de clase de alerta correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)


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

        if not ('age_cumplimiento' in data_in):
            data_in['age_cumplimiento']=None
        try:
            fechas=FechaClaseAlerta.objects.filter(dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento__isnull=True)
            if fechas:
                raise ValidationError("Ya existe esta fecha en la alerta.")
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



class PersonasAAlertarCreate(generics.CreateAPIView):
    serializer_class = PersonasAAlertarPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = PersonasAAlertar.objects.all()
    
    def post(self,request):
        data_in = request.data
        try:
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)

class PersonasAAlertarDelete(generics.DestroyAPIView):

    serializer_class = PersonasAAlertarDeleteSerializer
    queryset = PersonasAAlertar.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        persona = PersonasAAlertar.objects.filter(id_persona_alertar=pk).first()
        
        if not persona:
            raise NotFound("No existe la persona a eliminar.")
        serializer = self.serializer_class(persona) 
        persona.delete()

        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    
class PersonasAAlertarGetByConfAlerta(generics.ListAPIView):

    serializer_class = PersonasAAlertarGetSerializer
    queryset = PersonasAAlertar.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        alerta = PersonasAAlertar.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            raise NotFound("No existe esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


 

