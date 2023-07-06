import copy
import json
from collections import Counter
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta
from seguridad.utils import Util

from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, EvidenciasAvance, ProgramasPORH, ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import ActualizarActividadesSerializers, ActualizarAvanceEvidenciaSerializers, ActualizarProyectosSerializers, AvanceConEvidenciasSerializer, BusquedaAvanzadaSerializers, EliminarActividadesSerializers, EliminarProyectoSerializers, GetActividadesporProyectosSerializers, GetProgramasporPORHSerializers, GetProyectosPORHSerializers, RegistrarAvanceSerializers, RegistroEvidenciaSerializers, RegistroProgramaPORHSerializer,BusquedaAvanzadaAvancesSerializers,ProyectosPORHSerializer,GetAvancesporProyectosSerializers

class RegistroProgramaPORH(generics.CreateAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    permission_classes = [IsAuthenticated]
    queryset = ProgramasPORH.objects.all()
    
    def obtener_repetido(self,lista_archivos):
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None

    def post(self,request):
        try:
            data_in = request.data
            instancia_programa = None
            instancia_proyecto =None
            if not data_in['id_programa']:
                data_in['id_instrumento'] = 1
            


                serializer = self.serializer_class(data=data_in)
                serializer.is_valid(raise_exception=True)
                
                if data_in['fecha_inicio'] > data_in['fecha_fin']:
                    raise ValidationError("La fecha de inicio del programa no puede ser mayor a la fecha final del mismo.")
                
                instancia_programa = serializer.save()

                #AUDITORIA CREAR PROGRAMA

                usuario = request.user.id_usuario
                direccion=Util.get_client_ip(request)
                descripcion = {"IdInstrumentoPORH":instancia_programa.id_instrumento,"Nombre":instancia_programa.nombre}
                #valores_actualizados = {'current': instance, 'previous': instance_previous}
                auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 110,
                    "cod_permiso": "CR",
                    "subsistema": 'RECU',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    #"valores_actualizados": valores_actualizados
                }
                Util.save_auditoria(auditoria_data)

            else:
                instancia_programa = ProgramasPORH.objects.filter(id_programa=data_in['id_programa']).first()
                if not instancia_programa:
                    raise NotFound("El programa ingresado no existe")
            
            #CREACION DE PROYECTOS

            
            
            if 'proyectos' in data_in: 

                nombres_p=data_in['proyectos']
                #print(data_in['proyectos'])
                nombres_proyectos = [proyecto['nombre'] for proyecto in nombres_p]
                #print(nombres_proyectos)

                existen_repetidos=self.obtener_repetido(nombres_proyectos)
                #print(existen_repetidos)
                if existen_repetidos:
                    raise ValidationError("Existe mas de un proyecto con el nombre:"+str(existen_repetidos))
                
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

                        #AUDITORIA PROYECTO
                        usuario = request.user.id_usuario
                        direccion=Util.get_client_ip(request)
                        descripcion = {"IdProgramaPORH":instancia_proyecto.id_programa.id_programa,"Nombre":instancia_proyecto.nombre}
                        #valores_actualizados = {'current': instance, 'previous': instance_previous}
                        auditoria_data = {
                            "id_usuario" : usuario,
                            "id_modulo" : 110,
                            "cod_permiso": "CR",
                            "subsistema": 'RECU',
                            "dirip": direccion,
                            "descripcion": descripcion, 
                            #"valores_actualizados": valores_actualizados
                        }
                        Util.save_auditoria(auditoria_data)
                    else:
                        instancia_proyecto = ProyectosPORH.objects.filter(id_proyecto=proyecto['id_proyecto']).first()
                        if not instancia_programa:
                            raise NotFound("El proyecto ingresado no existe")
                    #if 'proyectos' in data_in and 'actividades' in data_in['proyectos']:
                    if 'actividades' in proyecto:
                    
                        nombres_a=proyecto['actividades']
                        #print(data_in['proyectos'])
                        nombres_actividad = [proyecto['nombre'] for proyecto in nombres_a]

                        
                        existen_repetidos=None
                        existen_repetidos=self.obtener_repetido(nombres_actividad)
                        #print(existen_repetidos)
                        if existen_repetidos:
                            raise ValidationError("Existe mas de una actividad con el nombre: "+str(existen_repetidos))
                    

                        for actividad in proyecto['actividades']:

                            actividades = ActividadesProyectos.objects.create(
                                id_proyecto = instancia_proyecto,
                                nombre = actividad['nombre']
                            )
                            
                            #AUDITORIA ACTIVIDAD
                            usuario = request.user.id_usuario
                            direccion=Util.get_client_ip(request)
                            descripcion = {"IdProyectoPgPORH":actividades.id_proyecto.id_proyecto,"Nombre":actividades.nombre}
                            #valores_actualizados = {'current': instance, 'previous': instance_previous}
                            auditoria_data = {
                                "id_usuario" : usuario,
                                "id_modulo" : 110,
                                "cod_permiso": "CR",
                                "subsistema": 'RECU',
                                "dirip": direccion,
                                "descripcion": descripcion, 
                                #"valores_actualizados": valores_actualizados
                            }
                            Util.save_auditoria(auditoria_data)
                            
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':data_in},status=status.HTTP_201_CREATED)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    

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
            #print(self.queryset)
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
            raise NotFound("El registro del programa que busca no existe")
        
        return Response({'success':True,'detail':"Se encontro el siguiente registro.",'data':serializer.data},status=status.HTTP_200_OK)
    
class GetProyectosporProgramas(generics.ListAPIView):
    serializer_class = GetProyectosPORHSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        proyecto = ProyectosPORH.objects.filter(id_programa=pk)
        serializer = self.serializer_class(proyecto,many=True)
        
        if not proyecto:
            raise NotFound("El registro del Proyecto que busca, no se encuentra registrado")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)
    
class GetActividadesporProyectos(generics.ListAPIView):
    serializer_class = GetActividadesporProyectosSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        actividades = ActividadesProyectos.objects.filter(id_proyecto=pk)
        serializer = self.serializer_class(actividades,many=True)
        
        if not actividades:
            raise NotFound('El registro de Actividades que busca, no se encuentra registrado')
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros de actividades.','data':serializer.data},status=status.HTTP_200_OK)
    

class GetAvanceporProyectos(generics.ListAPIView):
    serializer_class = GetAvancesporProyectosSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        avances = AvancesProyecto.objects.filter(id_proyecto=pk)
        serializer = self.serializer_class(avances,many=True)
        
        if not avances:
            raise NotFound('El registro de avances que busca, no se encuentra registrado')
        
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
                raise NotFound("No se encuentra el Programa que busca para su modificación.")
            
            instance_previous=copy.copy(programa)
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

    
            #AUDITORÍA
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdInstrumentoPORH":programa.id_instrumento.id_instrumento,"Nombre":programa.nombre}
            
            valores_actualizados = {'current': programa, 'previous': instance_previous}
            #print(valores_actualizados)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 110,
                "cod_permiso": "AC",
                "subsistema": 'RECU',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data) 

            

            
            
            return Response({'success':True,'detail':"Se realiza la actualización correctamente"},status=status.HTTP_200_OK)
        
class EliminarPrograma(generics.DestroyAPIView):
    serializer_class = RegistroProgramaPORHSerializer
    queryset = ProgramasPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        programa = ProgramasPORH.objects.filter(id_programa=pk).first()
        proyecto = ProyectosPORH.objects.filter(id_programa=pk).first()
        
        if not programa:
            raise NotFound("No existe el programa que desea eliminar.")
        
        fecha_sistema = datetime.now()        
        
        if fecha_sistema.date() > programa.fecha_fin:
            raise ValidationError("No se puede eliminar el programa si ya finalizo.")
        
        if proyecto:
            raise ValidationError("No se puede eliminar el programa si tiene un proyecto asignado.")
        
        programa.delete()
        #AUDITORIA BORRAR PROGRAMA
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdInstrumentoPORH":programa.id_instrumento.id_instrumento,"Nombre":programa.nombre}
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 110,
                "cod_permiso": "BO",
                "subsistema": 'RECU',
                "dirip": direccion,
                "descripcion": descripcion, 
                
            }
        Util.save_auditoria(auditoria_data) 
        
        
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
            raise NotFound("No se encuentra el Proyecto a modificar.")
        
        instance_previous=copy.copy(proyecto)
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

        #AUDITORÍA ACTUALIZAR PROYECTO
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdProgramaPORH":proyecto.id_programa.id_programa,"Nombre":proyecto.nombre}
            
        valores_actualizados = {'current': proyecto, 'previous': instance_previous}
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 110,
                "cod_permiso": "AC",
                "subsistema": 'RECU',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data) 

        
        return Response({'success':True,'detail':"Se realizo la modificacion del proyecto correctamente."},status=status.HTTP_200_OK)

class EliminarProyecto(generics.DestroyAPIView):
    serializer_class = EliminarProyectoSerializers
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        proyecto = ProyectosPORH.objects.filter(id_proyecto=pk).first()
        actividad = ActividadesProyectos.objects.filter(id_proyecto=pk).first()
        
        if not proyecto:
            raise NotFound("No existe el Proyecto a eliminar")
        
        fecha_sistema = datetime.now()
        
        if fecha_sistema.date() > proyecto.vigencia_final:
            raise ValidationError("No se puede Eliminar un Proyecto que este Vencido.")
        
        if actividad:
            raise ValidationError("No se puede Eliminar un proyecto, si tiene actividades asignadas.")
        
        proyecto.delete()

        #AUDITORIA ELIMINAR PROYECTO
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdProgramaPORH":proyecto.id_programa.id_programa,"Nombre":proyecto.nombre}
            
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 110,
                "cod_permiso": "BO",
                "subsistema": 'RECU',
                "dirip": direccion,
                "descripcion": descripcion, 
                
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True,'detail':'Se elimino el Proyecto seleccionado.'},status=status.HTTP_200_OK)

class ActualizarActividades(generics.UpdateAPIView):
    serializer_class = ActualizarActividadesSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:    
            data = request.data
            actividad = ActividadesProyectos.objects.filter(id_actividades=pk).first()
            
            if not actividad:
                raise NotFound("No se existe la actividad que trata de Actualizar.")
            
            instance_previous=copy.copy(actividad)
            serializer = self.serializer_class(actividad,data=data)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            #AUDITORIA ACTUALIZAR ACTIVIDAD
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdProgramaPgPORH":actividad.id_proyecto.id_proyecto,"Nombre":actividad.nombre}
            valores_actualizados = {'current': actividad, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 110,
                    "cod_permiso": "AC",
                    "subsistema": 'RECU',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente."},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    
        
class EliminarActividades(generics.DestroyAPIView):
    serializer_class = EliminarActividadesSerializers
    queryset = ActividadesProyectos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        actividad = ActividadesProyectos.objects.filter(id_actividades=pk).first()
        
        if not actividad:
            raise NotFound("No existe la Actividad a eliminar.")
        
        fecha_sistema = datetime.now()
        
        if fecha_sistema.date() > actividad.id_proyecto.vigencia_final:
            raise ValidationError("No se puede eliminar una actividad si al proyecto que esta ligado ya vencio.")
        
        actividad.delete()

        #AUDITORIA ELIMINAR ACTIVIDAD 
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdProgramaPgPORH":actividad.id_proyecto.id_proyecto,"Nombre":actividad.nombre}
        
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 110,
                "cod_permiso": "BO",
                "subsistema": 'RECU',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
        Util.save_auditoria(auditoria_data) 
        
        return Response({'success':True,'detail':'Se elimino la Actividad seleccionada.'},status=status.HTTP_200_OK)
    
class RegistroAvance(generics.CreateAPIView):
    serializer_class = RegistrarAvanceSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]
    
    def obtener_archivo_repetido(self,lista_archivos):
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None

    def post(self,request,id_proyecto):
        try:    
            data = request.data
            
            proyecto = ProyectosPORH.objects.filter(id_proyecto=id_proyecto).first()
            
            if not proyecto:
                raise NotFound("No hay proyecto.")
            
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
            repetido=self.obtener_archivo_repetido(nombre_archivos)
            if repetido:
                raise ValidationError("Existe mas de un archivo con el nombre: "+repetido)
            else:

                for i in range(len(archivos)):
                    print("")
                    EvidenciasAvance.objects.create(
                        id_avance = creacion_avance,
                        nombre_archivo = nombre_archivos[i],                
                        id_archivo = i
                    )
    
            return Response({'success':True,'detail':'Se crea el avance del proyecto correctamente.','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)

class BusquedaAvanzadaAvances(generics.ListAPIView):
    #serializer_class = BusquedaAvanzadaAvancesSerializers
    serializer_class = AvanceConEvidenciasSerializer
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
            if key == 'nombre_avances': 
                if value != '':
                    
                    filter['accion__icontains'] = value
        
        programas = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(programas, many=True)
        # avances = self.queryset.filter(**filter).select_related('id_proyecto')
        # serializador = self.serializer_class(avances, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data}, status=status.HTTP_200_OK)

class RegistroEvidencia(generics.CreateAPIView):
    serializer_class = RegistroEvidenciaSerializers
    queryset = EvidenciasAvance.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request,id_evidencia):
        
        data = request.data
        evidencia = AvancesProyecto.objects.filter(id_avance=id_evidencia).first()
        
        if not evidencia:
            return NotFound("No existe el registro al cual se intenta adicionar el registro.")
        
        data['id_avance'] = id_evidencia
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        creacion_evidencia = serializer.save()
        
        return Response({'success':True,'detail':'Se ha creado el registro exitosamente.','data':serializer.data},status=status.HTTP_201_CREATED)

class ActualizarAvanceEvidencia(generics.UpdateAPIView):
    serializer_class = ActualizarAvanceEvidenciaSerializers
    queryset = AvancesProyecto.objects.all()
    permission_classes = [IsAuthenticated]

    def obtener_archivo_repetido(self,lista_archivos):
        contador = Counter(lista_archivos)
        for archivo, cantidad in contador.items():
            if cantidad > 1:
                return archivo
        return None
    
    def put(self,request,pk):
        try:
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



            
            repetido=self.obtener_archivo_repetido(nombre_archivo)
            if repetido:
                 raise ValidationError("Existe mas de un archivo con el nombre: "+repetido)


            #validacion de evidencias existentes
            evidencias_existentes=EvidenciasAvance.objects.filter(id_avance=avance)
            for evidencia in evidencias_existentes:
                for i in range(len(nombre_archivo)):
                    if evidencia.nombre_archivo==nombre_archivo[i]:
                        raise ValidationError("El archivo :``"+str(nombre_archivo[i])+"´´ ya existe en este avance")

            for i in range(len(archivos)):
                EvidenciasAvance.objects.create(
                    id_avance = avance,
                    nombre_archivo = nombre_archivo[i],
                    id_archivo = i
                )
            return Response({'success':True,'detail':'Se ha realizado la actualizacion correctamente.'},status=status.HTTP_200_OK)

        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    
        
        





