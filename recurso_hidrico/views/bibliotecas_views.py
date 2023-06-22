import json
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.bibliotecas_models import Secciones,Subsecciones
from recurso_hidrico.serializers.biblioteca_serializers import ActualizarSeccionesSerializer, GetSeccionesSerializer,GetSubseccionesSerializer,RegistrarSeccionesSerializer,ActualizarSubseccionesSerializer, SeccionSerializer, SeccionesSerializer
from recurso_hidrico.serializers.programas_serializers import EliminarSeccionSerializer


class GetSecciones(generics.ListAPIView):
    serializer_class = SeccionesSerializer
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
            data_in['id_persona_creada']=request.user.persona.id_persona
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
                        id_persona_creada=request.user.persona
                    )

                          
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)


class ActualizarSeccion(generics.UpdateAPIView):
    
    serializer_class = ActualizarSeccionesSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        data_in = request.data
        seccion = Secciones.objects.filter(id_seccion=pk).first()
        
        if not seccion:
            raise ValidationError("No se existe la seccion que trata de Actualizar.")
        
        #pendiente validacion de instrumentos
        
        if 'subsecciones' in data_in: 
            if  not data_in['subsecciones']:
                print('')
                #print("NO SUBSECCIONES")
            else:
                for subseccion in data_in['subsecciones']: 
                    #print(subseccion)

                    if subseccion['id_subseccion']:#si existe la actualiza 
                        instancia_subseccion = Subsecciones.objects.filter(id_subseccion=subseccion['id_subseccion']).first()
                        if not instancia_subseccion:
                            raise NotFound("La subseccion con el codigo : "+str(subseccion['id_subseccion']) +" no existe en esta seccion")
                        
                        #REGISTRO DE CAMBIOS
                        
                        instancia_subseccion.nombre=subseccion['nombre']
                        instancia_subseccion.descripcion=subseccion['descripcion']
                        instancia_subseccion.save()
                    else:#si id_subseccion es nula se creada
                    
                        #REGISTRO DE BITACORA
                        instancia_subseccion = Subsecciones.objects.create(
                        id_seccion=seccion,
                        nombre=subseccion['nombre'],
                        descripcion=subseccion["descripcion"],
                        id_persona_creada=request.user.persona
                    )

        if 'subsecciones_eliminar'  in data_in:
            if data_in['subsecciones_eliminar']:
                for eliminar in data_in['subsecciones_eliminar']:
                    instancia_subseccion = Subsecciones.objects.filter(id_subseccion=eliminar).first()
                    if not instancia_subseccion:
                        raise NotFound("La subseccion con el codigo : "+str(subseccion['id_subseccion']) +" no existe en esta seccion")
                    #REGISTRO DE CAMBIOS
                    instancia_subseccion.delete()


        serializer = self.serializer_class(seccion,data=data_in)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'success':True,'detail':"Se actualizo la seccion Correctamente."},status=status.HTTP_200_OK)
    



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
    

class GetSeccionSubseccion(generics.RetrieveAPIView):

    serializer_class = SeccionSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            seccion = self.get_object()
        except Secciones.DoesNotExist:
            return Response({
                'success': False,
                'detail': 'La sección no existe.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(seccion)

        return Response({
            'success': True,
            'detail': 'Se encontró la siguiente sección.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    



class EliminarSeccion(generics.DestroyAPIView):
    serializer_class = EliminarSeccionSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        seccion = Secciones.objects.filter(id_seccion=pk).first()
        subseccion = Subsecciones.objects.filter(id_seccion=pk).first()
        
        if not seccion:
            raise ValidationError("No existe la seccion a eliminar")
        
        if subseccion:
            raise ValidationError("No se puede Eliminar una seccion, si tiene subsecciones asignadas.")
        
        if seccion.registroPrecargado:
            raise ValidationError("No se puede Eliminar una seccion, si fue precargada.")
        
        seccion.delete()
        
        return Response({'success':True,'detail':'Se elimino la Seccion seleccionada.'},status=status.HTTP_200_OK)