
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from gestion_documental.models.encuencas_models import EncabezadoEncuesta
from gestion_documental.serializers.encuentas_serializers import EncabezadoEncuestaCreateSerializer

class EncabezadoEncuestaCreate(generics.CreateAPIView):
    serializer_class = EncabezadoEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EncabezadoEncuesta.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.id_usuario
        try:
            data_in['id_persona_ult_config_implement']=usuario
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
           
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
class EncabezadoEncuestaCreate(generics.CreateAPIView):
    serializer_class = EncabezadoEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EncabezadoEncuesta.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.id_usuario
        try:
            data_in['id_persona_ult_config_implement']=usuario
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
           
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)