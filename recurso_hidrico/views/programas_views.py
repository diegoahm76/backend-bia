import json
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta

from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, EvidenciasAvance, ProgramasPORH, ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import ActualizarActividadesSerializers, ActualizarAvanceEvidenciaSerializers, ActualizarProyectosSerializers, BusquedaAvanzadaSerializers, EliminarActividadesSerializers, EliminarProyectoSerializers, GetActividadesporProyectosSerializers, GetProgramasporPORHSerializers, GetProyectosPORHSerializers, RegistrarAvanceSerializers, RegistroEvidenciaSerializers, RegistroProgramaPORHSerializer,BusquedaAvanzadaAvancesSerializers,ProyectosPORHSerializer,GetAvancesporProyectosSerializers

class RegistroProgramaPORH(generics.CreateAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    permission_classes = [IsAuthenticated]
    queryset = ProgramasPORH.objects.all()
    
    def post(self,request):
        data_in = request.data
        instancia_programa = None
        instancia_proyecto =None
        if not data_in['id_programa']:
            data_in['id_instrumento'] = 1
            # data = {
            #     'id_instrumento': 1, 
            #     'nombre': data_in['nombre'],
            #     'fecha_inicio': data_in['fecha_inicio'],
            #     'fecha_fin': data_in['fecha_fin'],
            # }
            #'proyectos': data_in['proyectos']

            # if 'proyectos' in data_in:
            #     data['proyectos'] = data_in['proyectos']

            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            
            if data_in['fecha_inicio'] > data_in['fecha_fin']:
                raise ValidationError("La fecha de inicio del programa no puede ser mayor a la fecha final del mismo.")
            
            instancia_programa = serializer.save()
        else:
            instancia_programa = ProgramasPORH.objects.filter(id_programa=data_in['id_programa']).first()
            if not instancia_programa:
                raise NotFound("El programa ingresado no existe")
        
        #CREACION DE PROYECTOS
        
        if 'proyectos' in data_in: 
                
            for proyecto in data_in['proyectos']: 

                if not proyecto['id_proyecto']:
                    if proyecto['vigencia_inicial']> proyecto['vigencia_final']:
                        raise ValidationError("La fecha inicial del proyecto no puede superar la fecha final del mismo proyecto.")
                    if proyecto['vigencia_inicial'] < data_in["fecha_inicio"]:
                        raise ValidationError("La fecha de inicio del proyecto no puede ser inferior a la fecha de inicio del programa al que pertenece.")
                    if proyecto['vigencia_final'] > data_in['fecha_fin']:
                        raise ValidationError('La fecha final del proyecto no puede ser mayor que la fecha final del programa.')
                    
                    instancia_proyecto = ProyectosPORH.objects.create(
                        id_programa = instancia_programa,
                        nombre = proyecto['nombre'],
                        vigencia_inicial = proyecto['vigencia_inicial'],
                        vigencia_final = proyecto['vigencia_final'],
                        inversion = proyecto['inversion']                    
                    )
                else:
                    instancia_proyecto = ProyectosPORH.objects.filter(id_proyecto=proyecto['id_proyecto']).first()
                    if not instancia_programa:
                        raise NotFound("El proyecto ingresado no existe")
                #if 'proyectos' in data_in and 'actividades' in data_in['proyectos']:
                if 'actividades' in proyecto:
                #if proyecto['actividades']:
                
                    for actividad in proyecto['actividades']:
                        actividades = ActividadesProyectos.objects.create(
                            id_proyecto = instancia_proyecto,
                            nombre = actividad['nombre']
                        )
                          
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':data_in},status=status.HTTP_201_CREATED)

class CreateProgramaPORH(generics.CreateAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    queryset = ProgramasPORH.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        # data = request.data
        data_in = request.data
        data = {
            'id_instrumento': 1, 
            'nombre': data_in['nombre'],
            'fecha_inicio': data_in['fecha_inicio'],
            'fecha_fin': data_in['fecha_fin'],
        }
        serializer = self.serializer_class(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            #print(self.queryset)
            return Response({'success': True, 'detail':'Se creo un programa exitosamente', 'data':serializer.data},status=status.HTTP_200_OK)
        except ValidationError as e:
            raise ValidationError('Error en los datos del formulario')

class CreateProyectosPORH(generics.CreateAPIView):
    serializer_class = ProyectosPORHSerializer
    queryset = ProyectosPORH.objects.all()
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        data = request.data
        # data_in = request.data
        # data = {
        #     'id_instrumento': 1, 
        #     'nombre': data_in['nombre'],
        #     'fecha_inicio': data_in['fecha_inicio'],
        #     'fecha_fin': data_in['fecha_fin'],
        # }
        serializer = self.serializer_class(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(self.queryset)
            return Response({'success': True, 'detail':'Se creo un proyecto exitosamente', 'data':serializer.data},status=status.HTTP_200_OK)
        except ValidationError as e:
            raise ValidationError('Error en los datos del formulario')
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
    

class GetAvanceporProyectos(generics.ListAPIView):
    serializer_class = GetAvancesporProyectosSerializers
    queryset = AvancesProyecto.objects.all()
    #permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        avances = AvancesProyecto.objects.filter(id_proyecto=pk)
        serializer = self.serializer_class(avances,many=True)
        
        if not avances:
            raise ValidationError('El registro de avances que busca, no se encuentra registrado')
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros de avances.','data':serializer.data},status=status.HTTP_200_OK)
  
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
    
    def post(self,request,id_proyecto):
        data = request.data
        
        proyecto = ProyectosPORH.objects.filter(id_proyecto=id_proyecto).first()
        
        if not proyecto:
            raise ValidationError("No hay proyecto.")
        
        archivos =request.FILES.getlist('evidencia')
        
        nombre_archivos =request.data.getlist('nombre_archivo')
        
        if len(archivos)!= len(nombre_archivos):
            raise ValidationError("Todos los archivos deben tener nombre.")

        persona_logueada = request.user.persona.id_persona
        data['id_persona_registra'] = persona_logueada
        
        data['id_proyecto'] = id_proyecto
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
    
        creacion_avance = serializer.save()
        
        for i in range(len(archivos)):
            EvidenciasAvance.objects.create(
                id_avance = creacion_avance,
                nombre_archivo = nombre_archivos[i],                
                id_archivo = i
            )
  
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

class RegistroEvidencia(generics.CreateAPIView):
    serializer_class = RegistroEvidenciaSerializers
    queryset = EvidenciasAvance.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request,id_evidencia):
        
        data = request.data
        evidencia = AvancesProyecto.objects.filter(id_avance=id_evidencia).first()
        
        if not evidencia:
            return ValidationError("No existe el registro al cual se intenta adicionar el registro.")
        
        data['id_avance'] = id_evidencia
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        creacion_evidencia = serializer.save()
        
        return Response({'success':True,'detail':'Se ha creado el registro exitosamente.','data':serializer.data},status=status.HTTP_201_CREATED)

class ActualizarAvanceEvidencia(generics.UpdateAPIView):
    serializer_class = ActualizarAvanceEvidenciaSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        data = request.data
        avance = AvancesProyecto.objects.filter(id_avance=pk).first()
        
        if not avance:
            raise ValidationError("No existe el registro que desea actualizar.")
        
        archivos = request.FILES.getlist('evidencia')
        nombre_archivo = request.data.getlist('nombre_archivo')
        
        # data['id_avance'] = pk
        
        serializer = self.serializer_class(avance,data=data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        nombre_actualizar = request.data.get('nombre_actualizar')
        nombre_actualizar = json.loads(nombre_actualizar)
        # nombre_actualizar_list = [nombre['id_evidencia']for nombre in nombre_actualizar]
        
        for nombre_data in nombre_actualizar:
            evidencia_update = EvidenciasAvance.objects.filter(id_evidencia_avance=nombre_data['id_evidencia_avance']).first()
            if not evidencia_update:
                raise ValidationError('Debe enviar evidencias exitentes')
            if nombre_data['nombre_archivo'] == '':
                raise ValidationError('No puede actualizar el nombre de un archivo a vacío')
            evidencia_update.nombre_archivo = nombre_data['nombre_archivo']
            evidencia_update.save()

        
        for i in range(len(archivos)):
            EvidenciasAvance.objects.create(
                id_avance = avance,
                nombre_archivo = nombre_archivo[i],
                id_archivo = i
            )
        
        return Response({'success':True,'detail':'Se ha realizado la actualizacion correctamente.'},status=status.HTTP_200_OK)
