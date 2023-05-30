from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, ProgramasPORH, ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import ActualizarActividadesSerializers, ActualizarProyectosSerializers, BusquedaAvanzadaSerializers, EliminarActividadesSerializers, EliminarProyectoSerializers, GetActividadesporProyectosSerializers, GetProgramasporPORHSerializers, GetProyectosPORHSerializers, RegistrarAvanceSerializers, RegistroProgramaPORHSerializer, BusquedaAvanzadaAvancesSerializers


class RegistroProgramaPORH(generics.CreateAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    permission_classes = [IsAuthenticated]
    queryset = ProgramasPORH.objects.all()
    
    def post(self,request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        if data['fecha_inicio'] > data['fecha_fin']:
            raise ValidationError("La fecha de inicio del programa no puede ser mayor a la fecha final del mismo.")
        
        creacion_programa = serializer.save()
        
        #CREACION DE PROYECTOS
        if data['proyectos']:    
                
            for proyecto in data['proyectos']: 
                if proyecto['vigencia_inicial']> proyecto['vigencia_final']:
                    raise ValidationError("La fecha inicial del proyecto no puede superar la fecha final del mismo proyecto.")
                if proyecto['vigencia_inicial'] < data["fecha_inicio"]:
                    raise ValidationError("La fecha de inicio del proyecto no puede ser inferior a la fecha de inicio del programa al que pertenece.")
                if proyecto['vigencia_final'] > data['fecha_fin']:
                    raise ValidationError('La fecha final del proyecto no puede ser mayor que la fecha final del programa.')
                
                proyecto_creado = ProyectosPORH.objects.create(
                    id_programa = creacion_programa,
                    nombre = proyecto['nombre'],
                    vigencia_inicial = proyecto['vigencia_inicial'],
                    vigencia_final = proyecto['vigencia_final'],
                    inversion = proyecto['inversion']                    
                )
                if proyecto['actividades']:
                
                    for actividad in proyecto['actividades']:
                        actividades = ActividadesProyectos.objects.create(
                            id_proyecto = proyecto_creado,
                            nombre = actividad['nombre']
                        )
            
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)

class GetProgramasporPORH(generics.ListAPIView):
    serializer_class = GetProgramasporPORHSerializers
    queryset = ProgramasPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        programa = ProgramasPORH.objects.filter(id_instrumento=pk)
        serializer = self.serializer_class(programa,many=True)
        
        if not programa:
            raise ValidationError("El registro del programa que busca no existe")
        
        return Response({'success':True,'detail':"Se encontro el siguiente registro.",'data':serializer.data},status=status.HTTP_200_OK)
    
class GetProyectosporProgramas(generics.ListAPIView):
    serializer_class = GetProyectosPORHSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        proyecto = ProyectosPORH.objects.filter(id_programa=pk)
        serializer = self.serializer_class(proyecto,many=True)
        
        if not proyecto:
            raise ValidationError("El registro del Proyecto que busca, no se encuentra registrado")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)
    
class GetActividadesporProyectos(generics.ListAPIView):
    serializer_class = GetActividadesporProyectosSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        actividades = ActividadesProyectos.objects.filter(id_proyecto=pk)
        serializer = self.serializer_class(actividades,many=True)
        
        if not actividades:
            raise ValidationError('El registro de Actividades que busca, no se encuentra registrado')
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros de actividades.','data':serializer.data},status=status.HTTP_200_OK)
    
class BusquedaAvanzada(generics.ListAPIView):
    serializer_class = BusquedaAvanzadaSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        
        for key, value in request.query_params.items():
            # if key == 'nombre_porh':
            #     if value !='':
            #         filter['id_programa__id_instrumento__nombre__icontains'] = value
            if key == 'nombre_programa':
                if value !='':
                    filter['id_programa__nombre__icontains'] = value
            if key =='nombre_proyecto':
                if value != '':
                    filter['nombre__icontains'] = value                
                
        programas = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(programas,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        
class ActualizarPrograma(generics.UpdateAPIView):  
        serializer_class = GetProgramasporPORHSerializers
        queryset = ProgramasPORH.objects.all()
        permission_classes = [IsAuthenticated]
        
        def put(self,request,pk):
            data = request.data
            programa = ProgramasPORH.objects.filter(id_programa=pk).first()
            proyecto = ProyectosPORH.objects.filter(id_programa=pk).order_by('vigencia_final').last()
            
            if not programa:
                raise ValidationError("No se encuentra el Programa que busca para su modificación.")
            
            serializer = self.serializer_class(programa,data=data)
            serializer.is_valid(raise_exception=True)
            
            fecha_data_inicio = datetime.strptime(data['fecha_inicio'],'%Y-%m-%d')
            fecha_data_fin = datetime.strptime(data['fecha_fin'],'%Y-%m-%d')
            
            fecha_sistema = datetime.now()
            
            if fecha_sistema.date() > programa.fecha_fin:
                raise ValidationError("No se puede actualizar el programa si ya finalizo.")
            
            if proyecto:
                if fecha_data_fin.date() < proyecto.vigencia_final:
                    raise ValidationError("No se puede actualizar la fecha final del programa, si la fecha fecha final del proyecto al que esta ligada es menor.")
                
                if data['nombre'] != programa.nombre:
                    raise ValidationError("No se puede editar el Nombre del programa si tiene asignado un proyecto.")
            
                if fecha_data_inicio.date() > proyecto.vigencia_inicial:
                    raise ValidationError("No se puede actualizar si la fecha de inicio del programa, si la fecha del proyecto al que esta ligada es mayor.")
            
            serializer.save()
            
            return Response({'success':True,'detail':"Se realiza la actualización correctamente"},status=status.HTTP_200_OK)
        
class EliminarPrograma(generics.DestroyAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    queryset = ProgramasPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        programa = ProgramasPORH.objects.filter(id_programa=pk).first()
        proyecto = ProyectosPORH.objects.filter(id_programa=pk).first()
        
        if not programa:
            raise ValidationError("No existe el programa que desea eliminar.")
        
        fecha_sistema = datetime.now()        
        
        if fecha_sistema.date() > programa.fecha_fin:
            raise ValidationError("No se puede eliminar el programa si ya finalizo.")
        
        if proyecto:
            raise ValidationError("No se puede eliminar el programa si tiene un proyecto asignado.")
        
        programa.delete()
        
        return Response({'success':True,'detail':'Se elimino correctamente el programa seleccionado.'},status=status.HTTP_200_OK)

class ActualizarProyectos(generics.UpdateAPIView):
    serializer_class = ActualizarProyectosSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        
        data = request.data
        proyecto = ProyectosPORH.objects.filter(id_proyecto=pk).order_by('vigencia_final').last()
        actividades = ActividadesProyectos.objects.filter(id_proyecto=pk).first()
        programa = ProyectosPORH.objects.filter(id_programa=pk).first()
        
        if not proyecto:
            raise ValidationError("No se encuentra el Proyecto a modificar.")
        
        serializer = self.serializer_class(proyecto,data=data)
        serializer.is_valid(raise_exception=True)
        
        vigencia_data_inicial = datetime.strptime(data['vigencia_inicial'],'%Y-%m-%d')
        vigencia_data_final = datetime.strptime(data['vigencia_final'],'%Y-%m-%d')
        
        fecha_sistema = datetime.now()
        
        if fecha_sistema.date()>proyecto.vigencia_final:
            raise ValidationError("No se puede actualizar el Proyecto si ya se encuentra finalizado.")
        
        
        if vigencia_data_final.date() > proyecto.id_programa.fecha_fin:
            raise ValidationError("No se puede actualizar la fecha final del proyecto, si supera la fecha final del programa.")
        
        if vigencia_data_inicial.date() < proyecto.id_programa.fecha_inicio:
            raise ValidationError("No se puede actualizar la fecha de Inicio del Proyecto, si la fecha de inicio del programa es mayor.")
        
        if actividades:            
            if data['nombre'] != proyecto.nombre:
                raise ValidationError("No se puede actualizar el nombre del Proyecto, si tiene Actividades ligadas.")
        
        serializer.save()
        
        return Response({'success':True,'detail':"Se realizo la modificacion del proyecto correctamente."},status=status.HTTP_200_OK)

class EliminarProyecto(generics.DestroyAPIView):
    serializer_class = EliminarProyectoSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        proyecto = ProyectosPORH.objects.filter(id_proyecto=pk).first()
        actividad = ActividadesProyectos.objects.filter(id_actividades=pk).first()
        
        if not proyecto:
            raise ValidationError("No existe el Proyecto a eliminar")
        
        fecha_sistema = datetime.now()
        
        if fecha_sistema.date() > proyecto.vigencia_final:
            raise ValidationError("No se puede Eliminar un Proyecto que este Vencido.")
        
        if actividad:
            raise ValidationError("No se puede Eliminar un proyecto, si tiene actividades asignadas.")
        
        proyecto.delete()
        
        return Response({'success':True,'detail':'Se elimino el Proyecto seleccionado.'},status=status.HTTP_200_OK)

class ActualizarActividades(generics.UpdateAPIView):
    serializer_class = ActualizarActividadesSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        data = request.data
        actividad = ActividadesProyectos.objects.filter(id_actividades=pk).first()
        
        if not actividad:
            raise ValidationError("No se existe la actividad que trata de Actualizar.")
        
        serializer = self.serializer_class(actividad,data=data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente."},status=status.HTTP_200_OK)

class EliminarActividades(generics.DestroyAPIView):
    serializer_class = EliminarActividadesSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        actividad = ActividadesProyectos.objects.filter(id_actividades=pk).first()
        
        if not actividad:
            raise ValidationError("No existe la Actividad a eliminar.")
        
        fecha_sistema = datetime.now()
        
        if fecha_sistema.date() > actividad.id_proyecto.vigencia_final:
            raise ValidationError("No se puede eliminar una actividad si al proyecto que esta ligado ya vencio.")
        
        actividad.delete()
        
        return Response({'success':True,'detail':'Se elimino la Actividad seleccionada.'},status=status.HTTP_200_OK)
    
class RegistroAvance(generics.CreateAPIView):
    serializer_class = RegistrarAvanceSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        creacion_avance = serializer.save()
        
        return Response({'success':True,'detail':'Se crea el avance del proyecto correctamente.','data':serializer.data},status=status.HTTP_201_CREATED)
    

class BusquedaAvanzadaAvances(generics.ListAPIView):
    serializer_class = BusquedaAvanzadaAvancesSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key == 'nombre_programa':
                if value != '':
                    filter['id_proyecto__id_programa__nombre__icontains'] = value
            if key == 'nombre_proyecto':
                if value != '':
                    filter['id_proyecto__nombre__icontains'] = value
            if key == 'nombre_avance': 
                if value != '':
                    filter['descripcion__icontains'] = value
        
        programas = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(programas, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data}, status=status.HTTP_200_OK)
