import json
from collections import Counter
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.bibliotecas_models import ArchivosInstrumento, CarteraAforos, Cuencas, CuencasInstrumento, DatosRegistroLaboratorio, Instrumentos, ParametrosLaboratorio, Pozos, ResultadosLaboratorio, Secciones,Subsecciones
from recurso_hidrico.serializers.biblioteca_serializers import ActualizarSeccionesSerializer, ArchivosInstrumentoBusquedaAvanzadaSerializer, ArchivosInstrumentoPostSerializer, ArchivosInstrumentoUpdateSerializer, ArchivosInstrumentosGetSerializer, CarteraAforosPostSerializer, CuencasGetByInstrumentoSerializer, CuencasGetSerializer, CuencasInstrumentoDeleteSerializer, CuencasInstrumentoSerializer, CuencasPostSerializer, CuencasUpdateSerializer, DatosRegistroLaboratorioDeleteSerializer, DatosRegistroLaboratorioGetSerializer, DatosRegistroLaboratorioPostSerializer, DatosRegistroLaboratorioUpdateSerializer, EliminarSubseccionSerializer, GetSeccionesSerializer,GetSubseccionesSerializer, InstrumentoBusquedaAvanzadaSerializer, InstrumentoCuencasGetSerializer, InstrumentosPostSerializer, InstrumentosSerializer, InstrumentosUpdateSerializer, ParametrosLaboratorioGetSerializer, ParametrosLaboratorioPostSerializer, ParametrosLaboratorioUpdateSerializer, PozosGetSerializer, PozosPostSerializer, PozosUpdateSerializer,RegistrarSeccionesSerializer,ActualizarSubseccionesSerializer, RegistrarSubSeccionesSerializer, ResultadosLaboratorioGetSerializer, ResultadosLaboratorioPostSerializer, ResultadosLaboratorioUpdateSerializer, SeccionSerializer, SeccionesSerializer, SubseccionBusquedaAvanzadaSerializer, SubseccionContarInstrumentosSerializer,EliminarSeccionSerializer



class GetSecciones(generics.ListAPIView):
    serializer_class = SeccionesSerializer
    queryset = Secciones.objects.all().order_by('-fecha_creacion')
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
    queryset = Subsecciones.objects.all().order_by('-fechaCreacion')
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
    
#CONSULTA BIBLIOTECA 


class SubseccionesContInstrumentosGet(generics.ListAPIView):
    queryset = Subsecciones.objects.all()
    serializer_class = SubseccionContarInstrumentosSerializer


    permission_classes = [IsAuthenticated]
    
    def get(self,request,sec):
        subSeccion = Subsecciones.objects.filter(id_seccion=sec)
        serializer = self.serializer_class(subSeccion,many=True)
        
        if not subSeccion:
            raise NotFound("No se encuentran subsecciones en la seccion suministrada")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)


class InstrumentosSeccionSubseccionGet(generics.ListAPIView):

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
    


class InstrumentoCuencasGet(generics.ListAPIView):

    queryset = Instrumentos.objects.all()
    serializer_class = InstrumentoCuencasGetSerializer
    permission_classes = [IsAuthenticated]
    def get(self,request,sec,sub):
        seccion = sec
        idsubseccion = sub
        
        instrumento_ids = Instrumentos.objects.filter(id_seccion=seccion, id_subseccion=idsubseccion).values_list('id_instrumento', flat=True)
        lista_instrumentos=list(instrumento_ids)

        resultados = CuencasInstrumento.objects.filter(id_instrumento__in=lista_instrumentos)

        serializer = self.serializer_class(resultados,many=True)
        
        if not instrumento_ids:
            raise NotFound("No se encuentran Instrumentos con este requisito.")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)  
    
  
    
class InstrumentosGetById(generics.RetrieveAPIView):
    queryset = Instrumentos.objects.all()
    serializer_class = InstrumentosSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            instrumento = self.get_object()
        except Instrumentos.DoesNotExist:
            raise NotFound("No se encontró instrumento con esta id.")
        
        serializer = self.serializer_class(instrumento)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CuencasInstrumentoGet(generics.ListAPIView):

    queryset = CuencasInstrumento.objects.all()
    serializer_class = InstrumentoCuencasGetSerializer
    permission_classes = [IsAuthenticated]
    def get(self,request,ins):
        id = ins
         
        #cuencas = Instrumentos.objects.filter(id_seccion=seccion, id_subseccion=idsubseccion).values_list('id_instrumento', flat=True)
        cuencas=CuencasInstrumento.objects.filter(id_instrumento=id)


        serializer = self.serializer_class(cuencas,many=True)
        
        if not cuencas:
            raise NotFound("No se encuentran cuentas asociadas a este instrumento.")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)  
    



class ArchivosInstrumentoBusquedaAvanzadaGet(generics.ListAPIView):
    #serializer_class = BusquedaAvanzadaAvancesSerializers
    serializer_class = ArchivosInstrumentoBusquedaAvanzadaSerializer
    queryset = ArchivosInstrumento.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key == 'nombre_seccion':
                if value != '':
                    filter['id_instrumento__id_seccion__nombre__icontains'] = value
            if key == 'nombre_subseccion':
                if value != '':
                    filter['id_instrumento__id_subseccion__nombre__icontains'] = value
            if key == 'nombre_instrumento': 
                if value != '':
                    filter['id_instrumento__nombre__icontains'] = value
            if key == 'nombre_archivo': 
                if value != '':
                    filter['nombre_archivo__icontains'] = value
        
        archivos = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(archivos, many=True)
        # avances = self.queryset.filter(**filter).select_related('id_proyecto')
        # serializador = self.serializer_class(avances, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data}, status=status.HTTP_200_OK)
    



class ArchivosInstrumentoGet(generics.ListAPIView):


    queryset = ArchivosInstrumento.objects.all()
    serializer_class = ArchivosInstrumentosGetSerializer
    permission_classes = [IsAuthenticated]
    def get(self,request,ins):
        id = ins
         
        archivos=ArchivosInstrumento.objects.filter(id_instrumento=id)


        serializer = self.serializer_class(archivos,many=True)
        
        if not archivos:
            raise NotFound("No se encuentran archivos asociadas a este instrumento.")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)  
    



##Registro de Instrumentos en Biblioteca
#configuraciones basicas 


class CuencaCreate(generics.CreateAPIView):
    serializer_class = CuencasPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cuencas.objects.all()
    
    def post(self,request):
        data_in = request.data
        try:
            data_in['registro_precargado']=False
            data_in['item_ya_usado']=False
            data_in['activo']=True
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
    


class CuencaDelete(generics.DestroyAPIView):

    serializer_class = CuencasPostSerializer
    queryset = Cuencas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        cuenca = Cuencas.objects.filter(id_cuenca=pk).first()
        
        if not cuenca:
            raise NotFound("No existe la cuenca a eliminar.")
        


        if cuenca.registro_precargado:
            raise ValidationError("No se puede eliminar una cuenca precargada.")
        
        if cuenca.item_ya_usado:
            raise ValidationError("No se puede eliminar una cuenca que se encuentre en uso.")
    
        cuenca.delete()
        
        return Response({'success':True,'detail':'Se elimino la cuenca seleccionada.'},status=status.HTTP_200_OK)
    

class CeuncaGet(generics.ListAPIView):
    serializer_class = CuencasGetSerializer
    queryset = Cuencas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        estado=False
        for key, value in request.query_params.items():
            if key == 'activo':
                if value != '':
                    if str(value)=='True':
                        estado=True

        if estado:
            cuencas = Cuencas.objects.filter(activo=estado).order_by('id_cuenca')
        else:
            cuencas=Cuencas.objects.all().order_by('id_cuenca')

        serializer = self.serializer_class(cuencas,many=True)
        
        if not cuencas:
            raise NotFound("los registros de cuencas que busca no existen")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    

class CuencaGetById(generics.ListAPIView):

    serializer_class = CuencasGetSerializer
    queryset = Cuencas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        cuencas = Cuencas.objects.filter(id_cuenca=pk)
                
        serializer = self.serializer_class(cuencas,many=True)
        
        if not cuencas:
            raise NotFound("La cuenca no existe.")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    

class CuencaUpdate(generics.UpdateAPIView):

    
    serializer_class = CuencasUpdateSerializer
    queryset = Cuencas.objects.all()
    permission_classes = [IsAuthenticated]
    

    def put(self, request, pk):
        try:
            data = request.data
            cuenca = Cuencas.objects.filter(id_cuenca=pk).first()
        
            if not cuenca:
                raise NotFound("No se existe la cuenca que trata de Actualizar.")
        
            if cuenca.item_ya_usado == False:
                serializer = self.serializer_class(cuenca, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.update(cuenca, serializer.validated_data)
            else:
                raise PermissionDenied('No puedes actualizar una cuenca que haya sido usada')

            return Response({'success': True, 'detail': 'Se actualizaron los registros correctamente', 'data': self.serializer_class(cuenca).data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise ValidationError(e.detail)


 


#POZOS
class PozoCreate(generics.CreateAPIView):
    serializer_class = PozosPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Pozos.objects.all()
    
    def post(self,request):
        data_in = request.data
        try:
            data_in['registro_precargado']=False
            data_in['item_ya_usado']=False
            data_in['activo']=True
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
  

class PozoDelete(generics.DestroyAPIView):

    serializer_class = PozosPostSerializer
    queryset = Pozos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        pozo = Pozos.objects.filter(id_pozo=pk).first()
        
        if not pozo:
            raise NotFound("No existe el pozo a eliminar.")
        


        if pozo.registro_precargado:
            raise ValidationError("No se puede eliminar un pozo precargada.")
        
        if pozo.item_ya_usado:
            raise ValidationError("No se puede eliminar un pozo que se encuentre en uso.")
    
        pozo.delete()
        
        return Response({'success':True,'detail':'Se elimino el pozo seleccionada.'},status=status.HTTP_200_OK)
    

class PozoUpdate(generics.UpdateAPIView):

    
    serializer_class = PozosUpdateSerializer
    queryset = Pozos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):


        try:

            
            data = request.data
            pozo = Pozos.objects.filter(id_pozo=pk).first()
        
            if  not pozo:

                raise NotFound("No se existe el pozo que trata de Actualizar.")
           
            if pozo.item_ya_usado:
                raise PermissionDenied('No puedes actualizar un pozo que haya sido usada')
                
            else:
                serializer = self.serializer_class(pozo, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.update(pozo, serializer.validated_data)
                
                

        except ValidationError as e:       
            raise ValidationError(e.detail)
    
            
        return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':self.serializer_class(pozo).data},status=status.HTTP_200_OK)
    

class PozoGet(generics.ListAPIView):
    serializer_class = PozosGetSerializer
    queryset = Pozos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        estado=None
        for key, value in request.query_params.items():
            if key == 'activo':
                if value != '':
                    if str(value)=='True':
                        estado=True
            if key == 'activo':
                if value != '':
                    if str(value)=='False':
                        estado=False    

        if estado is None:  
            pozos=Pozos.objects.all().order_by('id_pozo')
        else:      

                pozos = Pozos.objects.filter(activo=estado).order_by('id_pozo')
    
    

        serializer = self.serializer_class(pozos,many=True)
        
        if not pozos:
            raise NotFound("los registros de pozos que busca no existen")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
 



class PozoGetById(generics.ListAPIView):

    serializer_class = PozosGetSerializer
    queryset = Pozos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        pozos = Pozos.objects.filter(id_pozo=pk)
                
        serializer = self.serializer_class(pozos,many=True)
        
        if not pozos:
            raise NotFound("El pozo no existe.")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    
#Parametros de laboratorio
class ParametrosLaboratorioCreate(generics.CreateAPIView):
    serializer_class = ParametrosLaboratorioPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = ParametrosLaboratorio.objects.all()
    
    def post(self,request):
        data_in = request.data
        try:
            data_in['registro_precargado']=False
            data_in['item_ya_usado']=False
            data_in['activo']=True
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
  

class ParametrosLaboratorioDelete(generics.DestroyAPIView):

    serializer_class = ParametrosLaboratorioPostSerializer
    queryset = ParametrosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        parametro = ParametrosLaboratorio.objects.filter(id_parametro=pk).first()
        
        if not parametro:
            raise NotFound("No existe el parametro de laboratorio a eliminar.")
        


        if parametro.registro_precargado:
            raise ValidationError("No se puede eliminar un parametro de laboratorio precargada.")
        
        if parametro.item_ya_usado:
            raise ValidationError("No se puede eliminar un parametro de laboratorio que se encuentre en uso.")
    
        parametro.delete()
        
        return Response({'success':True,'detail':'Se elimino el parametro de laboratorio seleccionada.'},status=status.HTTP_200_OK)
    


class ParametrosLaboratorioUpdate(generics.UpdateAPIView):

    
    serializer_class = ParametrosLaboratorioUpdateSerializer
    queryset = ParametrosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):


        try:

            
            data = request.data
            parametro = ParametrosLaboratorio.objects.filter(id_parametro=pk).first()
        
            if  not parametro:

                raise NotFound("No se existe el parametro de laboratorio que trata de Actualizar.")
            #print(parametro.item_ya_usado)
            if parametro.item_ya_usado:
                raise PermissionDenied('No puedes actualizar un parametro de laboratorio que haya sido usada')
                # if 'activo' in data:

                #     if parametro.activo == data['activo']:
                #         raise ValidationError("No se puede actualizar un parametro de laboratorio que se encuentre en uso")
                #     parametro.activo = data['activo']
                #     parametro.save()
                #     return Response({'success':True,'detail':'Se cambio el estado del parametro de laboratorio.','data':self.serializer_class(parametro).data},status=status.HTTP_200_OK)
                # else:
                #     raise ValidationError("Se requiere proporcionar el campo 'activo' para actualizar la parametro de laboratorio.")
   
            else:
                
                serializer = self.serializer_class(parametro, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.update(parametro, serializer.validated_data)

        except ValidationError as e:       
            raise ValidationError(e.detail)
    
            
        return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':self.serializer_class(parametro).data},status=status.HTTP_200_OK)
    

class ParametrosLaboratorioGet(generics.ListAPIView):
    serializer_class = ParametrosLaboratorioGetSerializer
    queryset = ParametrosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        estado=None
        # for key, value in request.query_params.items():
        #     if key == 'activo':
        #         if value != '':
        #             if str(value)=='True':
        #                 estado=True
        #     if key == 'activo':
        #         if value != '':
        #             if str(value)=='False':
        #                 estado=False    
    ##
        filter = {}

        for key, value in request.query_params.items():
            if key == 'cod_tipo_parametro':
                if value != '':
                    filter['cod_tipo_parametro__icontains'] = value
            if key == 'activo':
                if value != '':
                    filter['activo__icontains'] = value
            if key == 'nombre':
                if value != '':
                    filter['nombre__icontains'] = value

        print(filter)
        instrumento = self.queryset.all().filter(**filter)


        serializer = self.serializer_class(instrumento,many=True)
        
        if not instrumento:
            raise NotFound("los registros de parametros que busca no existen")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
 

class ParametrosLaboratorioGetById(generics.ListAPIView):

    serializer_class = ParametrosLaboratorioGetSerializer
    queryset = ParametrosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        parametros = ParametrosLaboratorio.objects.filter(id_parametro=pk)
                
        serializer = self.serializer_class(parametros,many=True)
        
        if not parametros:
            raise NotFound("El parametro de laboratorio  no existe.")
        
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    
#Archivos
class ArchivosInstrumentoCreate(generics.CreateAPIView):
    queryset = ArchivosInstrumento.objects.all()
    serializer_class = ArchivosInstrumentoPostSerializer

    def crear_archivo(self, data):
        serializer = ArchivosInstrumentoPostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def post(self, request, *args, **kwargs):
        data = request.data
        archivo_creado = self.crear_archivo(data)
        return Response(archivo_creado, status=status.HTTP_201_CREATED)


class ArchivosInstrumentoUpdate(generics.UpdateAPIView):
    queryset = ArchivosInstrumento.objects.all()
    serializer_class = ArchivosInstrumentoUpdateSerializer

    def actualizar(self, pk, data):
        instance = ArchivosInstrumento.objects.filter(id_archivo_instrumento=pk).first()
        
        if  not instance:

            raise NotFound("No se existe el archivo  que trata de Actualizar.")
        
        serializer = ArchivosInstrumentoUpdateSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #data actualizada
        archivo = ArchivosInstrumento.objects.filter(id_archivo_instrumento=pk).first()
        serializera = ArchivosInstrumentoUpdateSerializer(archivo)
        return serializera.data

    def put(self, request,pk):
       
        data = request.data
        archivo_actualizado = self.actualizar(pk, data)
        #print(archivo_actualizado)
       # archivo = ArchivosInstrumento.objects.filter(id_archivo_instrumento=pk)
        #data_archivo=ArchivosInstrumentoUpdateSerializer(archivo)
        return Response({'success':True,'detail':'Se actualizaron el archivo correctamente'},status=status.HTTP_200_OK)
class ArchivosInstrumentoGetByInstrumento(generics.ListAPIView):

    serializer_class = ArchivosInstrumentosGetSerializer
    queryset = ArchivosInstrumento.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        archivos = ArchivosInstrumento.objects.filter(id_instrumento=pk)
                
        serializer = self.serializer_class(archivos,many=True)
        
        if not archivos:
            raise NotFound("Este instrumento no cuenta con archivos.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    
#Instrumentos

class InstrumentoCreate(generics.CreateAPIView):
    serializer_class = InstrumentosPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Instrumentos.objects.all()
    

    def obtener_repetido(self,lista_archivos):
        
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None
    def post(self,request):
        
        try:
            data_in = request.data
            data_in._mutable=True
            persona_logueada = request.user.persona.id_persona
            data_in['id_persona_registra']=persona_logueada
            fecha_actual = datetime.now().date()
            
            formato = "%Y-%m-%dT%H:%M:%S"
            fecha_datetime = datetime.strptime(data_in['fecha_creacion_instrumento'], formato).date()
            if(fecha_datetime>fecha_actual):
                raise ValidationError("La fecha de creacion no puese superar la actual.")
            formato_fecha= '%Y-%m-%d'
            if 'fecha_fin_vigencia' in data_in:
                fin_vigencia= datetime.strptime(data_in['fecha_fin_vigencia'], formato_fecha).date()

                if(fin_vigencia<fecha_actual):
                    raise ValidationError("La fecha de fin de vigencia debe ser superor a la actual.")
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()

           #CUENCAS
            cuencas_data=[]
            id_instrumento=serializer.data['id_instrumento']
            ids=[]

            if "id_cuencas" in data_in:

                string_data = request.data.get('id_cuencas')
                integer_list = eval(string_data)
                
       
                cuencas=[]
                for x in integer_list:
                    cuenca={"id_instrumento":id_instrumento,"id_cuenca":x}
                    cuencas.append(cuenca)
            
               

                if cuencas:
                    if self.obtener_repetido(integer_list):
                        raise ValidationError("Intenta insertar la misma cuenca varias veces")

                cuencas_instrumento_serializer = CuencasInstrumentoSerializer(data=cuencas, many=True)
                cuencas_instrumento_serializer.is_valid(raise_exception=True)
                cuencas_instrumento_serializer.save()
                cuencas_data=cuencas_instrumento_serializer.data

            #archivos
            archivos =request.FILES.getlist('archivo')
            nombre_archivos =request.data.getlist('nombre_archivo')
            if len(archivos)!= len(nombre_archivos):
                raise ValidationError("Todos los archivos deben tener nombre.")
             
            archivos_data=[]


            serizalizador_archivos=[]
            for archivo, nombre_archivo in zip(archivos, nombre_archivos):
                archivo_data = {
                        'id_instrumento': id_instrumento,
                        'cod_tipo_de_archivo': 'INS',
                        'nombre_archivo': nombre_archivo,
                        'ruta_archivo': archivo
                    }
                arch=ArchivosInstrumentoCreate()
                serizalizador_archivos.append(arch.crear_archivo(archivo_data))

            
            

        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':{"instrumento":serializer.data,"cuencas":cuencas_data,"archivos":serizalizador_archivos}},status=status.HTTP_201_CREATED)
    

class InstrumentoUpdate(generics.UpdateAPIView):

    serializer_class = InstrumentosUpdateSerializer
    queryset = Instrumentos.objects.all()
    permission_classes = [IsAuthenticated]

    def obtener_repetido(self,lista_archivos):
        
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None    

    
    def put(self,request,pk):
        serializer=None
        try:

            data = request.data
            instrumento = Instrumentos.objects.filter(id_instrumento=pk).first()
        
            if  not instrumento:

                raise NotFound("No se existe el instrumento que trata de Actualizar.")
            
            
            else:
                fecha_actual = datetime.now().date()
                if instrumento.fecha_fin_vigencia:
                    if fecha_actual>instrumento.fecha_fin_vigencia:
                        raise NotFound("No se puede actualizar un instrumento que no se encuentre vigente.")
                serializer = self.serializer_class(instrumento, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.update(instrumento, serializer.validated_data)
                
                cuencas_asociadas = CuencasInstrumento.objects.filter(id_instrumento=pk).values_list('id_cuenca', flat=True)
                lista_id_cuenca = list(cuencas_asociadas)
      
                cuencas_data=[]
                if "id_cuencas" in data:
                    string_data = request.data.get('id_cuencas')
                    data_nueva = eval(string_data)

                    if self.obtener_repetido(data_nueva):
                            raise ValidationError("Intenta insertar la misma cuenca varias veces")
                   

                   #ACTUALIZAR CUENCAS POR INSTRUMENTO
                    elementos_insertar = list(set(data_nueva)-set(lista_id_cuenca))

                    cuencas=[]
                    for x in elementos_insertar:
                        cuenca={"id_instrumento":instrumento.id_instrumento,"id_cuenca":x}
                        cuencas.append(cuenca)
                
                    cuencas_instrumento_serializer = CuencasInstrumentoSerializer(data=cuencas, many=True)
                    cuencas_instrumento_serializer.is_valid(raise_exception=True)
                    cuencas_instrumento_serializer.save()
                    cuencas_data=cuencas_instrumento_serializer.data

                #archivos
            
                archivos =request.FILES.getlist('archivo')
                nombre_archivos =request.data.getlist('nombre_archivo')

                if len(archivos)!= len(nombre_archivos):
                    raise ValidationError("Todos los archivos deben tener nombre.")
                
                serizalizador_archivos=[]
                for archivo, nombre_archivo in zip(archivos, nombre_archivos):
                    archivo_data = {
                            'id_instrumento': instrumento.id_instrumento,
                            'cod_tipo_de_archivo': 'INS',
                            'nombre_archivo': nombre_archivo,
                            'ruta_archivo': archivo
                        }
                    arch=ArchivosInstrumentoCreate()
                    serizalizador_archivos.append(arch.crear_archivo(archivo_data))
                
                actualizar_a=ArchivosInstrumentoUpdate()


                #cambio de nombre a existentes

                if "nombre_actualizar" in data:
                    nombre_actualizar = request.data.get('nombre_actualizar')
                    nombre_actualizar = json.loads(nombre_actualizar)
                    #print(nombre_actualizar)
                    #actualizar(self, pk, data):
                    for nombre_data in nombre_actualizar:
                        archivo_data = {
                            'nombre_archivo':nombre_data['nombre_archivo']
                        }
                        
                        actualizar_a.actualizar(nombre_data['id_archivo'],archivo_data)

                    ##fin archivos
                instrumento = Instrumentos.objects.filter(id_instrumento=pk).first()
                serializer = InstrumentosSerializer(instrumento)
           


                return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':{'instrumento':serializer.data},'cuencas':cuencas_data,'archivos':serizalizador_archivos},status=status.HTTP_200_OK)
    
        except ValidationError as e:       
            raise ValidationError(e.detail)
    
            
class InstrumentoBusquedaAvanzadaGet(generics.ListAPIView):
    #serializer_class = BusquedaAvanzadaAvancesSerializers
    serializer_class = InstrumentoBusquedaAvanzadaSerializer
    queryset = Instrumentos.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key == 'id_seccion__nombre_seccion':
                if value != '':
                    filter['id_seccion__nombre__icontains'] = value
            if key == 'nombre_subseccion':
                if value != '':
                    filter['id_subseccion__nombre__icontains'] = value
            if key == 'nombre_instrumento': 
                if value != '':
                    filter['nombre__icontains'] = value

        
        instrumento = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(instrumento, many=True)

        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data}, status=status.HTTP_200_OK)
         


class CuencasGetByInstrumento(generics.ListAPIView):

    serializer_class = CuencasGetByInstrumentoSerializer
    queryset = CuencasInstrumento.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        cuencas = CuencasInstrumento.objects.filter(id_instrumento=pk)
                
        serializer = self.serializer_class(cuencas,many=True)
        
        if not cuencas:
            raise NotFound("Este instrumento no cuenta con cuencas.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    

##
class SeccionSubseccionBusquedaAvanzadaGet(generics.ListAPIView):
    #serializer_class = BusquedaAvanzadaAvancesSerializers
    serializer_class = SubseccionBusquedaAvanzadaSerializer
    queryset = Subsecciones.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key == 'nombre_seccion':
                if value != '':
                    filter['id_seccion__nombre__icontains'] = value
            if key == 'nombre_subseccion':
                if value != '':
                    filter['nombre__icontains'] = value

        subsecciones = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(subsecciones, many=True)
        # avances = self.queryset.filter(**filter).select_related('id_proyecto')
        # serializador = self.serializer_class(avances, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data}, status=status.HTTP_200_OK)
    
##CUENCAS INSTRUMENTOS
class CuencaInstrumentoDelete(generics.DestroyAPIView):
    serializer_class = CuencasInstrumentoDeleteSerializer
    queryset = CuencasInstrumento.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,cu,ins):
        
        cuenca_instrumento = CuencasInstrumento.objects.filter(id_cuenca=cu,id_instrumento=ins).first()
        
        if not cuenca_instrumento:
            raise NotFound("Esta cuenca no se encuentra vinculado a este instrumento.")
      
        
        cuenca_instrumento.delete()

        
        return Response({'success':True,'detail':'Se elimino la cuenca de este instrumento seleccionada.'},status=status.HTTP_200_OK)
    


##CARTERAS DE AFORO

class CarteraAforosCreate(generics.CreateAPIView):
    serializer_class = CarteraAforosPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = CarteraAforos.objects.all()
    
    def post(self,request):
        data_in = request.data
        

        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
            
        serializer.save()
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)


#RESULTADOS DE LABORATORIO

class ResultadosLaboratorioCreate(generics.CreateAPIView):
    serializer_class = ResultadosLaboratorioPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = ResultadosLaboratorio.objects.all()

    def crear_resultado_laboratorio(self, data):

        try:
            serializer = ResultadosLaboratorioPostSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True,
                            'detail':'Se  registros correctamente',
                            'data':serializer.data},
                            status=status.HTTP_201_CREATED
                            )
        except ValidationError  as e:
           
            raise ValidationError  (e.detail)


    def post(self, request, *args, **kwargs):
        data = request.data
        id_resultado_laboratorio=None
        resultado_laboratorio={}
        datos_laboratorio=[]
        if  not data['id_resultado_laboratorio']:
            
       
            resultado_laboratorio_creado = self.crear_resultado_laboratorio(data)

            if resultado_laboratorio_creado.status_code !=status.HTTP_201_CREATED:
                return resultado_laboratorio_creado
            
           
            id_resultado_laboratorio = resultado_laboratorio_creado.data.get('data', {}).get('id_resultado_laboratorio')
            resultado_laboratorio=resultado_laboratorio_creado.data
            #cracion de datos de laboratorio
            #return resultado_laboratorio_creado
        else:
            resultado=ResultadosLaboratorio.objects.filter(id_resultado_laboratorio=data['id_resultado_laboratorio']).first()
            if not resultado:
                raise NotFound("No existe este registro de laboratorio")
            
            id_resultado_laboratorio=resultado.id_resultado_laboratorio

        
        if 'datos_registro_laboratorio' in data:
            if   data['datos_registro_laboratorio']:
                crear_datos=DatosRegistroLaboratorioCreate()
                for datos in data['datos_registro_laboratorio'] : 
                        datos_lab={
                        "id_registro_laboratorio": id_resultado_laboratorio,
                        "id_parametro": datos['id_parametro'],
                        "metodo":datos['metodo'] ,
                        "resultado": datos['resultado'],
                        "fecha_analisis": datos['fecha_analisis']
                        }
                        response_datos=crear_datos.crear_dato_registro_laboratorio(datos_lab)
                        if response_datos.status_code !=status.HTTP_201_CREATED:
                            return response_datos
                        datos_laboratorio.append(response_datos.data['data'])
                        #print(response_datos)

        return Response({'success':True,'detail':'Se  registros correctamente','data':{
                        'resultados_laboratorio':resultado_laboratorio['data'],
                        'datos_laboratoro':datos_laboratorio
                        }},status=status.HTTP_201_CREATED)

class ResultadosLaboratorioUpdate(generics.UpdateAPIView):
    
    serializer_class = ResultadosLaboratorioUpdateSerializer
    queryset = DatosRegistroLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    

    def obtener_repetido(self,lista_archivos):
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None

    def actualizar_resultados_laboratorio(self,data,pk):
        
        dato = ResultadosLaboratorio.objects.filter(id_resultado_laboratorio=pk).first()

        if not dato:
            raise NotFound("No existe este registro de laboratorio")

        serializer = self.serializer_class(dato, data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.update(dato, serializer.validated_data)
            
            return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':serializer.data},status=status.HTTP_200_OK)
        except ValidationError  as e:
           
            raise ValidationError  (e.detail)
        

    def put(self,request,pk):
    
        data = request.data
      
        response_resultado_lab =self.actualizar_resultados_laboratorio(data,pk)
        response_datos=[]
        response_datos_eliminados=[]
        if response_resultado_lab.status_code !=status.HTTP_200_OK:
            return response_resultado_lab
        
        #actualizar datos
        
        if 'datos_registro_laboratorio' in data:

            if data['datos_registro_laboratorio']:

                crear_dato_registro =DatosRegistroLaboratorioCreate()
                actualizar_dato_registro =DatosRegistroLaboratorioUpdate()
                
                for datos_registro in data['datos_registro_laboratorio']:
                

                    if datos_registro['id_dato_registro_laboratorio']:#si se envia id ,se actualiza
                       
                        datos={
                            
                            "id_registro_laboratorio": datos_registro["id_registro_laboratorio"],
                            "id_parametro": datos_registro["id_parametro"],
                            "metodo": datos_registro["metodo"],
                            "resultado": datos_registro["resultado"],
                            "fecha_analisis": datos_registro["fecha_analisis"]
                        }
                        response_dato=actualizar_dato_registro.actualizar_datos_registro_laboratorio(datos,datos_registro['id_dato_registro_laboratorio'])
                        
                        if response_dato.status_code != status.HTTP_200_OK:
                            return response_dato
                        response_datos.append(response_dato.data['data'])

                    else:
                        datos={
                            "id_registro_laboratorio": pk,
                            "id_registro_laboratorio": datos_registro["id_registro_laboratorio"],
                            "id_parametro": datos_registro["id_parametro"],
                            "metodo": datos_registro["metodo"],
                            "resultado": datos_registro["resultado"],
                            "fecha_analisis": datos_registro["fecha_analisis"]
                        }
                        response_dato=crear_dato_registro.crear_dato_registro_laboratorio(datos)
                        
                        if response_dato.status_code != status.HTTP_201_CREATED:
                            return response_dato
                        response_datos.append(response_dato.data['data'])
        #Eliminar archivos

        if 'datos_registro_eliminar'  in data:
            if data['datos_registro_eliminar']:

                repetido=self.obtener_repetido(data['datos_registro_eliminar'])

                if repetido:
                    raise ValidationError("Intenta eliminar el  mismo dato varias veces.")
                eliminar_datos_registro = DatosRegistroLaboratorioDelete()
                for eliminar in data['datos_registro_eliminar']:
                    
                    response_subseccion=eliminar_datos_registro.delete(request,eliminar)
                    if response_subseccion.status_code == status.HTTP_400_BAD_REQUEST:
                        return response_subseccion
                    response_datos_eliminados.append(response_subseccion.data['data'])


        
        return Response({'success':True,'detail':'Se actualizaron los registros correctamente',
                         'data':{'resultados_laboratorio':response_resultado_lab.data['data'],
                          'datos_registro_laboratorio':response_datos,
                          'datos_registro_laboratorio_eliminados':response_datos_eliminados      
                                 }},
                         status=status.HTTP_200_OK)

class ResultadosLaboratorioGetByInstrumento(generics.ListAPIView):

    serializer_class = ResultadosLaboratorioGetSerializer
    queryset = ResultadosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

        ##

        #filter = {}

        # for key, value in request.query_params.items():
        #     if key == 'id_seccion__nombre_seccion':
        #         if value != '':
        #             filter['id_seccion__nombre__icontains'] = value
        #     if key == 'nombre_subseccion':
        #         if value != '':
        #             filter['id_subseccion__nombre__icontains'] = value
        #     if key == 'nombre_instrumento': 
        #         if value != '':
        #             filter['nombre__icontains'] = value

        
#        instrumento = self.queryset.all().filter(**filter)
       # serializador = self.serializer_class(instrumento, many=True)
        ##            
        resultados = ResultadosLaboratorio.objects.filter(id_instrumento=pk)
                
        serializer = self.serializer_class(resultados,many=True)
        
        if not resultados:
            raise NotFound("Este instrumento no cuenta con resultados.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    

class ResultadosLaboratorioGetById(generics.ListAPIView):

    serializer_class = ResultadosLaboratorioGetSerializer
    queryset = ResultadosLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        resultados = ResultadosLaboratorio.objects.filter(id_resultado_laboratorio=pk)
                
        serializer = self.serializer_class(resultados,many=True)
        
        if not resultados:
            raise NotFound("No se encontraron datos.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
    
#DATOS DE REGISTRO DE LABORATORIO
class DatosRegistroLaboratorioCreate(generics.CreateAPIView):
    serializer_class = DatosRegistroLaboratorioPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatosRegistroLaboratorio.objects.all()

    def crear_dato_registro_laboratorio(self, data):

        try:
            serializer = DatosRegistroLaboratorioPostSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
            return Response({'success':True,'detail':'Se  registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        
        except ValidationError  as e:
           
            raise ValidationError  (e.detail)
        
    def post(self, request, *args, **kwargs):
        data = request.data
        dato_registro_laboratorio_creado = self.crear_dato_registro_laboratorio(data)

        #raise ValidationError(dato_registro_laboratorio_creado.status_code)
        if dato_registro_laboratorio_creado.status_code !=status.HTTP_201_CREATED:
            return dato_registro_laboratorio_creado


        
        return dato_registro_laboratorio_creado
       
    

class DatosRegistroLaboratorioDelete(generics.DestroyAPIView):
    serializer_class = DatosRegistroLaboratorioDeleteSerializer
    queryset = DatosRegistroLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        dato = DatosRegistroLaboratorio.objects.filter(id_dato_registro_laboratorio=pk).first()
      
        
        if not dato:
            raise ValidationError("No existe El dato  a eliminar")
        
        
        serializer = self.serializer_class(dato) 
        dato.delete()


        
        return Response({'success':True,'detail':'Se elimino el Dato seleccionada.','data':serializer.data},status=status.HTTP_200_OK)
    

class DatosRegistroLaboratorioUpdate(generics.UpdateAPIView):
    
    serializer_class = DatosRegistroLaboratorioUpdateSerializer
    queryset = DatosRegistroLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def actualizar_datos_registro_laboratorio(self,data,pk):
        
        dato = DatosRegistroLaboratorio.objects.filter(id_dato_registro_laboratorio=pk).first()

        if not dato:
            raise NotFound("No existe este registro de laboratorio")

        serializer = self.serializer_class(dato, data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.update(dato, serializer.validated_data)
            
            return Response({'success':True,'detail':'Se actualizaron los registros correctamente','data':serializer.data},status=status.HTTP_200_OK)
        except ValidationError  as e:
           
            raise ValidationError  (e.detail)
        

    def put(self,request,pk):
    
        data = request.data
      
        response_subseccion =self.actualizar_datos_registro_laboratorio(data,pk)
       
        if response_subseccion != status.HTTP_200_OK:
            return response_subseccion
        
        return Response(response_subseccion.data,status=status.HTTP_200_OK)
    

class DatosRegistroLaboratorioByResultadosLaboratorioGet(generics.ListAPIView):

    serializer_class = DatosRegistroLaboratorioGetSerializer
    queryset = DatosRegistroLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,lab,par):
        
        if par=="FQ" or par=="MB":
            datos_laboratorio = DatosRegistroLaboratorio.objects.filter(id_registro_laboratorio=lab,id_parametro__cod_tipo_parametro=par).order_by('id_dato_registro_laboratorio')
        else:
            datos_laboratorio = DatosRegistroLaboratorio.objects.filter(id_registro_laboratorio=lab).order_by('id_dato_registro_laboratorio')
        serializer = self.serializer_class(datos_laboratorio,many=True)
        
        if not datos_laboratorio:
            raise NotFound("Este resultado no tiene datos.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class DatosRegistroLaboratorioByIdGet(generics.ListAPIView):

    serializer_class = DatosRegistroLaboratorioGetSerializer
    queryset = DatosRegistroLaboratorio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        datos_laboratorio = DatosRegistroLaboratorio.objects.filter(id_dato_registro_laboratorio=pk)
                
        serializer = self.serializer_class(datos_laboratorio,many=True)
        
        if not datos_laboratorio:
            raise NotFound("Este resultado no tiene datos.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
