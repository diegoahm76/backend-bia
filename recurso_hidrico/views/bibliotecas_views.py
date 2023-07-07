import json
from collections import Counter
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.bibliotecas_models import Instrumentos, Secciones,Subsecciones
from recurso_hidrico.serializers.biblioteca_serializers import ActualizarSeccionesSerializer, EliminarSubseccionSerializer, GetSeccionesSerializer,GetSubseccionesSerializer, InstrumentosSerializer,RegistrarSeccionesSerializer,ActualizarSubseccionesSerializer, RegistrarSubSeccionesSerializer, SeccionSerializer, SeccionesSerializer, SubseccionContarInstrumentosSerializer,EliminarSeccionSerializer



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
            raise NotFound("El registro del seccion que busca, no se encuentra subsecciones")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)
    



class RegistroSeccion(generics.CreateAPIView):
    serializer_class = RegistrarSeccionesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Secciones.objects.all()
    
    def post(self,request):
        data_in = request.data
        
       
        data_in['registroPrecargado']=False
        data_in['id_persona_creada']=request.user.persona.id_persona
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
            
        serializer.save()
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
    
class RegistroSubSeccion(generics.CreateAPIView):
    serializer_class = RegistrarSubSeccionesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subsecciones.objects.all()
    
    def crear_subseccion(self,request,data):
        instancia_seccion = None
        #data['id_subseccion']=instancia_seccion.id_seccion
        try:
            data['id_persona_creada']=request.user.persona.id_persona
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializador =serializer.save()

            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)   


    def post(self,request):
        data_in = request.data
        instancia_seccion = None

        instancia_seccion = Secciones.objects.filter(id_seccion=data_in['id_seccion']).first()
    
        if not instancia_seccion:
            raise NotFound("La seccion ingresada no existe")
        
        data_in['id_subseccion']=instancia_seccion.id_seccion
        #data_in['id_persona_creada']=request.user.persona.id_persona

        self.crear_subseccion(request,data_in)
        
        #return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)


class RegistroSeccionSubseccionx(generics.CreateAPIView):
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


#PRUEBAS MODULAR DE REGISTRO DE SUBSECCION


class RegistroSeccionSubseccion(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RegistrarSeccionesSerializer
    queryset = Secciones.objects.all()

    def post(self, request):
        try:
            response_data=[]
            data_in = request.data
            id_seccion=''
            # Creación de la sección
            instancia_seccion=''
            seccion = Secciones.objects.filter(id_seccion=data_in['id_seccion']).first()
            serializer=None
            
            if not seccion:
    
                registro_seccion = RegistroSeccion()
                response_seccion = registro_seccion.post(request)

                if response_seccion.status_code != status.HTTP_201_CREATED:
                    return response_seccion

                response_data.append(response_seccion.data.get('data', {}))
                id_seccion = response_seccion.data.get('data', {}).get('id_seccion')
            
            else:
                id_seccion=seccion.id_seccion
               
            
            # Creación de las subsecciones
            subsecciones = data_in.get('subsecciones', [])

            if subsecciones:
                for subseccion in subsecciones:
                    subseccion_data = {
                        'id_seccion': id_seccion,
                        'nombre': subseccion['nombre'],
                        'descripcion': subseccion['descripcion'],
                        'id_persona_creada': request.user.persona.id_persona
                    }
                    registro_subseccion = RegistroSubSeccion()
                    response_subseccion = registro_subseccion.crear_subseccion(request,subseccion_data)
                    if response_subseccion.status_code != status.HTTP_201_CREATED:
                        return response_subseccion
                    response_data.append(response_subseccion.data)
            serializador=self.get_serializer()

            return Response({'success': True, 'detail': 'Se crearon los registros correctamente', 'data':  response_data}, status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)





class ActualizarSeccionSubseccion(generics.UpdateAPIView):
    
    serializer_class = ActualizarSeccionesSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]

    def obtener_repetido(self,lista_archivos):
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None
    
    def put(self,request,pk):
        operaciones=[]
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

                # nombres_s=data_in['subsecciones']
                
                # nombre_subsecciones = [subseccion['nombre'] for subseccion in nombres_s if 'nombre' in subseccion]
                # existen_repetidos=self.obtener_repetido(nombre_subsecciones)
                # #verifica si en los que se van a crear existen repetidos
                # if existen_repetidos:
                #     raise ValidationError("Existe mas de una subseccion  con el nombre: "+str(existen_repetidos))
                
                # #verifica si los nombres de las subsecciones que van a crear no existan en la base de datos
                # subsecciones_existentes=Subsecciones.objects.filter(id_seccion=seccion.id_seccion).values_list('nombre', flat=True)
                

                # if subsecciones_existentes:
                #     elementos_comunes = list(set(list(subsecciones_existentes)) & set(nombre_subsecciones))
                    
                #     print(len(elementos_comunes))
                #     if len(elementos_comunes)>0:
                        
                #         raise ValidationError(f"Ya existe una subseccion con estos nombres: {', '.join(str(x) for x in elementos_comunes)}")

                for subseccion in data_in['subsecciones']: 
                    #print(subseccion)

                    if subseccion['id_subseccion']:#si existe la actualiza 

                        subseccion_data = {
                            'id_seccion': seccion.id_seccion,
                            'nombre': subseccion['nombre'],
                            'descripcion': subseccion['descripcion'],
                            'id_persona_creada': request.user.persona.id_persona
                        }
                        registro_subseccion = ActualizarSubsecciones()
                        response_subseccion = registro_subseccion.actualizar_subseccion(subseccion_data,subseccion['id_subseccion'])
                        if response_subseccion.status_code != status.HTTP_200_OK:
                            return response_subseccion

                        # instancia_subseccion = Subsecciones.objects.filter(id_subseccion=subseccion['id_subseccion']).first()
                        # if not instancia_subseccion:
                        #     raise NotFound("La subseccion con el codigo : "+str(subseccion['id_subseccion']) +" no existe.")
                        # instancia_subseccion.nombre=subseccion['nombre']
                        # instancia_subseccion.descripcion=subseccion['descripcion']
                        # instancia_subseccion.save()
                    else:#si id_subseccion es nula se creada
                    
                        subseccion_data = {
                            'id_seccion': seccion.id_seccion,
                            'nombre': subseccion['nombre'],
                            'descripcion': subseccion['descripcion'],
                            'id_persona_creada': request.user.persona.id_persona
                        }
                        registro_subseccion = RegistroSubSeccion()
                        response_subseccion = registro_subseccion.crear_subseccion(request,subseccion_data)
                        if response_subseccion.status_code != status.HTTP_201_CREATED:
                            return response_subseccion

                        # instancia_subseccion = Subsecciones.objects.create(
                        # id_seccion=seccion,
                        # nombre=subseccion['nombre'],
                        # descripcion=subseccion["descripcion"],
                        # id_persona_creada=request.user.persona
                    # )

        if 'subsecciones_eliminar'  in data_in:
            if data_in['subsecciones_eliminar']:
                for eliminar in data_in['subsecciones_eliminar']:

                    eliminarSubseccion = EliminarSubseccion()
                    
                    response_subseccion=eliminarSubseccion.delete(request,eliminar)
                    if response_subseccion.status_code == status.HTTP_400_BAD_REQUEST:
                        return response_subseccion



        serializer = self.serializer_class(seccion,data=data_in)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'success':True,'detail':"Se actualizo la seccion Correctamente."},status=status.HTTP_200_OK)
    


class ActualizarSecciones(generics.UpdateAPIView):
    
    serializer_class = ActualizarSeccionesSerializer
    queryset = Secciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def actualizar_seccion(self,data,seccion):
        

        serializer = self.serializer_class(seccion, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(seccion, serializer.validated_data)

        return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        

    def put(self,request,pk):
    
        data = request.data
        Seccione = Secciones.objects.filter(id_seccion=pk).first()
        
        if  not Seccione:
            #print('HOLAA')
            raise NotFound("No se existe la seccion que trata de Actualizar.")

        self.actualizar_seccion(data,Seccione)
        
        return Response({'success':True,'detail':"Se actualizo la seccion Correctamente."},status=status.HTTP_200_OK)



class ActualizarSubsecciones(generics.UpdateAPIView):
    
    serializer_class = ActualizarSubseccionesSerializer
    queryset = Subsecciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def actualizar_subseccion(self,data,pk):
        instancia_seccion = None
        subseccion = Subsecciones.objects.filter(id_subseccion=pk).first()
        nombre_existente = Subsecciones.objects.filter(id_seccion=subseccion.id_seccion,nombre=data['nombre']).first()

        #print(nombre_existente)
        serializer = self.serializer_class(subseccion, data=data)

      
        
        if not subseccion:
            raise NotFound("No  existe la subseccion que trata de Actualizar.")
        
        if nombre_existente  :
            if str(nombre_existente.id_subseccion)!= str(pk):
       
                raise ValidationError("Ya existe una subseccion con este nombre")

        try:
            serializer.is_valid(raise_exception=True)
            serializer.update(subseccion, serializer.validated_data)

        except ValidationError  as e:
           
            raise ValidationError  (e.detail)
        
        return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':serializer.data},status=status.HTTP_200_OK)
        

    def put(self,request,pk):
    
        data = request.data
        subseccion = Subsecciones.objects.filter(id_subseccion=pk).first()
        
        if not subseccion:
            raise NotFound("No  existe la subseccion que trata de Actualizar.")
        
        #pendiente validacion de instrumentos

        response_subseccion =self.actualizar_subseccion(data,pk)
       
        if response_subseccion != status.HTTP_200_OK:
            return response_subseccion
        
        return Response(response_subseccion.data,status=status.HTTP_200_OK)
    

class EliminarSubseccion(generics.DestroyAPIView):
    serializer_class = EliminarSubseccionSerializer
    queryset = Subsecciones.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        subseccion = Subsecciones.objects.filter(id_subseccion=pk).first()
        Instrumento = Instrumentos.objects.filter(id_subseccion=pk).first()
        
        if not subseccion:
            raise ValidationError("No existe la Subseccion a eliminar")
        
        if Instrumento:
            raise ValidationError("No se puede Eliminar una subseccion, si tiene instrumentos asignados.")
        

        subseccion.delete()
        
        return Response({'success':True,'detail':'Se elimino la Subseccion seleccionada.'},status=status.HTTP_200_OK)

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
    

class GetSubseccionesContInstrumentos(generics.ListAPIView):
    queryset = Subsecciones.objects.all()
    serializer_class = SubseccionContarInstrumentosSerializer


    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        subSeccion = Subsecciones.objects.filter(id_seccion=pk)
        serializer = self.serializer_class(subSeccion,many=True)
        
        if not subSeccion:
            raise NotFound("No se encuentran subsecciones en la seccion suministrada")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)


class GetInstrumentosPorSeccionSubseccion(generics.ListAPIView):

    queryset = Instrumentos.objects.all()
    serializer_class = InstrumentosSerializer
    permission_classes = [IsAuthenticated]
    def get(self,request,pk,sub):
        seccion = pk
        idsubseccion = sub
        subSeccion = Instrumentos.objects.filter(id_seccion=seccion,id_subseccion=idsubseccion)
        serializer = self.serializer_class(subSeccion,many=True)
        
        if not subSeccion:
            raise NotFound("No se encuentran Instrumentos con este requisito.")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)  