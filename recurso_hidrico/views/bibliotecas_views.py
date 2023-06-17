import json
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.bibliotecas_models import Secciones,Subsecciones
from recurso_hidrico.serializers.biblioteca_serializers import GetSeccionesSerializer,GetSubseccionesSerializer,RegistrarSeccionesSerializer,ActualizarSubseccionesSerializer


class GetSecciones(generics.ListAPIView):
    serializer_class = GetSeccionesSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class GetSubseccionesPorSecciones(generics.ListAPIView):
    serializer_class = GetSubseccionesSerializer
    queryset = Subsecciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        subSeccion = Subsecciones.objects.filter(id_seccion=pk)
        serializer = self.serializer_class(subSeccion,many=True)
        
        if not subSeccion:
            raise ValidationError("El registro del seccion que busca, no se encuentra subsecciones")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)
    

class RegistroSeccion(generics.CreateAPIView):
    serializer_class = RegistrarSeccionesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Secciones.objects.all()
    
    def post(self,request):
        data_in = request.data
        instancia_seccion = None
        instancia_subseccion =None
        if not data_in['id_seccion']:
            data_in['registroPrecargado']=False
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            
            instancia_seccion = serializer.save()
        else:
            instancia_seccion = Secciones.objects.filter(id_seccion=data_in['id_seccion']).first()
            serializer = self.serializer_class(instance=instancia_seccion)
            if not instancia_seccion:
                raise NotFound("La seccion ingresada no existe")
        
        #CREACION DE Subsecciones
        
        if 'subsecciones' in data_in and  data_in['subsecciones'] : 

                
            for subseccion in data_in['subsecciones'] : 

  
                    instancia_subseccion = Subsecciones.objects.create(
                        id_seccion=instancia_seccion,
                        nombre=subseccion['nombre'],
                        descripcion=subseccion["descripcion"],
                        fechaCreacion=timezone.now(),
                        id_PersonaCrea=request.user.persona
                    )

                          
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)


class ActualizarSubsecciones(generics.UpdateAPIView):
    serializer_class = ActualizarSubseccionesSerializer
    queryset = Subsecciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        data = request.data
        subseccion = Subsecciones.objects.filter(id_subseccion=pk).first()
        
        if not subseccion:
            raise ValidationError("No se existe la subseccion que trata de Actualizar.")
        
        #pendiente validacion de instrumentos
        serializer = self.serializer_class(subseccion,data=data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'success':True,'detail':"Se actualizo la subseccion Correctamente."},status=status.HTTP_200_OK)