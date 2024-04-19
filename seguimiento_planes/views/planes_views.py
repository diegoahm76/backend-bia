from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from seguimiento_planes.serializers.planes_serializer import LineasBasePGARSerializer, MetasPGARSerializer, ObjetivoDesarrolloSostenibleSerializer, Planes, EjeEstractegicoSerializer, ObjetivoSerializer, PlanesSerializer, PlanesSerializerGet, ProgramaSerializer, ProyectoSerializer, ProductosSerializer, ActividadSerializer, EntidadSerializer, MedicionSerializer, TipoEjeSerializer, TipoSerializer, RubroSerializer, IndicadorSerializer, MetasSerializer, SubprogramaSerializer
from seguimiento_planes.models.planes_models import LineasBasePGAR, MetasEjePGAR, ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma

# ---------------------------------------- Objetivos Desarrollo Sostenible Tabla Básica ----------------------------------------

# Listar todos los Objetivos Desarrollo Sostenible

class ObjetivoDesarrolloSostenibleList(generics.ListCreateAPIView):
    queryset = ObjetivoDesarrolloSostenible.objects.all()
    serializer_class = ObjetivoDesarrolloSostenibleSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        objetivos = ObjetivoDesarrolloSostenible.objects.all()
        serializer = ObjetivoDesarrolloSostenibleSerializer(objetivos, many=True)
        if not objetivos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Objetivos Desarrollo Sostenible.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un Objetivo Desarrollo Sostenible

class ObjetivoDesarrolloSostenibleCreate(generics.ListCreateAPIView):
    queryset = ObjetivoDesarrolloSostenible.objects.all()
    serializer_class = ObjetivoDesarrolloSostenibleSerializer
    permission_classes = (IsAuthenticated,)

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
        return Response({'success': True, 'detail': 'Objetivo Desarrollo Sostenible creado correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un Objetivo Desarrollo Sostenible

class ObjetivoDesarrolloSostenibleUpdate(generics.RetrieveUpdateAPIView):
    queryset = ObjetivoDesarrolloSostenible.objects.all()
    serializer_class = ObjetivoDesarrolloSostenibleSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            return Response({'success': False, 'detail': 'El Objetivo Desarrollo Sostenible ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if objetivo.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Objetivo Desarrollo Sostenible ya ha sido usado en un Planes, por lo tanto no puede ser modificado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ObjetivoDesarrolloSostenibleSerializer(objetivo, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Objetivo Desarrollo Sostenible actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Eliminar un Objetivo Desarrollo Sostenible

class ObjetivoDesarrolloSostenibleDelete(generics.RetrieveUpdateAPIView):
    queryset = ObjetivoDesarrolloSostenible.objects.all()
    serializer_class = ObjetivoDesarrolloSostenibleSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            return Response({'success': False, 'detail': 'El Objetivo Desarrollo Sostenible ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if objetivo.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Objetivo Desarrollo Sostenible ya ha sido usado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        if objetivo.registro_precargado:
            return Response({'success': False, 'detail': 'El Objetivo Desarrollo Sostenible es un registro precargado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        objetivo.delete()
        return Response({'success': True, 'detail': 'Objetivo Desarrollo Sostenible eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Objetivo Desarrollo Sostenible por id

class ObjetivoDesarrolloSostenibleDetail(generics.RetrieveAPIView):
    queryset = ObjetivoDesarrolloSostenible.objects.all()
    serializer_class = ObjetivoDesarrolloSostenibleSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            raise NotFound('No se encontraron resultados.')
        serializer = ObjetivoDesarrolloSostenibleSerializer(objetivo)
        return Response({'success': True, 'detail': 'Objetivo Desarrollo Sostenible encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- PLANES ----------------------------------------

# Listar Planes Nacionales de Desarrollo

class ConsultarPlanes(generics.ListAPIView):
    serializer_class = PlanesSerializer
    queryset = Planes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        planes = self.queryset.all()
        serializador = self.serializer_class(planes, many=True)
        if not planes:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Se encontraron los siguientes planes', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer Planes
class CrearPlanes(generics.CreateAPIView):
    serializer_class = PlanesSerializer
    queryset = Planes.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el plan de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualziar Planes
class ActualizarPlanes(generics.UpdateAPIView):
    serializer_class = PlanesSerializer
    queryset = Planes.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        planes = self.get_object()
        serializador = self.serializer_class(planes, data=data, partial=True)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el plan de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK) 
# Eliminar Planes

class EliminarPlanes(generics.DestroyAPIView):
    serializer_class = PlanesSerializer
    queryset = Planes.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        plan_nacional_desarrollo = self.queryset.all().filter(id_plan=pk).first()

        if not plan_nacional_desarrollo:
            raise NotFound('El planes ingresado no existe.')
        plan_nacional_desarrollo.delete()
        return Response({'success': True, 'detail': 'Se elimino el planes de manera exitosa'}, status=status.HTTP_200_OK)
    
# Listar plan de desarrollo por id

class ConsultarPlanesId(generics.ListAPIView):
    serializer_class = PlanesSerializer
    queryset = Planes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        plan_nacional_desarrollo = self.queryset.all().filter(id_plan=pk).first()
        if not plan_nacional_desarrollo:
            raise NotFound('No se encontraron resultados.')
        serializador = self.serializer_class(plan_nacional_desarrollo)
        return Response({'success': True, 'detail': 'Se encontro el plan', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Busqueda Avanzada Planes Nacionales de Desarrollo

class BusquedaAvanzadaPlanes(generics.ListAPIView):
    serializer_class = PlanesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Planes.objects.all()
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_sigla_plan = request.query_params.get('nombre_sigla_plan', '')

        # Realiza la búsqueda utilizando el campo 'nombre_plan' en el modelo
        if nombre_plan != '':
            queryset = Planes.objects.filter(nombre_plan__icontains=nombre_plan)

        if nombre_sigla_plan != '':
            queryset = Planes.objects.filter(sigla_plan__icontains=nombre_sigla_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Ejes Estratégicos ----------------------------------------

# Listar todos los Ejes Estratégicos

class EjeEstractegicoList(generics.ListCreateAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ejes = EjeEstractegico.objects.all()
        serializer = EjeEstractegicoSerializer(ejes, many=True)
        if not ejes:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Ejes Estratégicos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada eje por nombre plan, y nombre

class BusquedaAvanzadaEjes(generics.ListAPIView):
    serializer_class = EjeEstractegicoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = EjeEstractegico.objects.all()
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_objetivo = request.query_params.get('nombre_objetivo', '')
        nombre_eje = request.query_params.get('nombre_eje', '')

        # Realiza la búsqueda utilizando el campo 'nombre_eje' en el modelo
        if nombre_plan != '':
            queryset = EjeEstractegico.objects.filter(id_plan__nombre_plan__icontains=nombre_plan)
        
        if nombre_objetivo != '':
            queryset = EjeEstractegico.objects.filter(id_objetivo__nombre_objetivo__icontains=nombre_objetivo)

        if nombre_eje != '':
            queryset = EjeEstractegico.objects.filter(nombre__icontains=nombre_eje)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Eje Estratégico    

class EjeEstractegicoCreate(generics.ListCreateAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Eje Estratégico creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualizar un Eje Estratégico

class EjeEstractegicoUpdate(generics.RetrieveUpdateAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        eje = self.queryset.all().filter(id_eje_estrategico=pk).first()
        if not eje:
            return Response({'success': False, 'detail': 'El Eje Estratégico ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EjeEstractegicoSerializer(eje, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Eje Estratégico actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Eje Estratégico

class EjeEstractegicoDelete(generics.RetrieveUpdateAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        eje = self.queryset.all().filter(id_eje_estrategico=pk).first()
        if not eje:
            return Response({'success': False, 'detail': 'El Eje Estratégico ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        eje.delete()
        return Response({'success': True, 'detail': 'Eje Estratégico eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Eje Estratégico por id

class EjeEstractegicoDetail(generics.RetrieveAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        eje = self.queryset.all().filter(id_eje_estrategico=pk).first()        
        if not eje:
            raise NotFound('No se encontraron resultados.')
        serializer = EjeEstractegicoSerializer(eje)
        return Response({'success': True, 'detail': 'Eje Estratégico encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar eje estrategico por id planes

class EjeEstractegicoListIdPlanes(generics.ListAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        eje = self.queryset.all().filter(id_plan=pk)
        if not eje:
            raise NotFound('No se encontraron resultados.')
        serializer = EjeEstractegicoSerializer(eje, many=True)
        return Response({'success': True, 'detail': 'Eje Estratégico encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class EjeEstractegicoListIdObjetivo(generics.ListAPIView):
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        queryset = EjeEstractegico.objects.all()
        queryset = queryset.filter(id_objetivo=pk)
        if not queryset:
            raise NotFound('No se encontraron resultados.')
        serializer = EjeEstractegicoSerializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Eje Estratégico encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

# ---------------------------------------- Objetivos ----------------------------------------

# Listar todos los Objetivos

class ObjetivoList(generics.ListCreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        objetivos = Objetivo.objects.all()
        serializer = ObjetivoSerializer(objetivos, many=True)
        if not objetivos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Objetivos.', 'data': serializer.data}, status=status.HTTP_200_OK)
        
# Busqueda Avanzada objetivo por nombre plan y nombre_objetivo

class BusquedaAvanzadaObjetivos(generics.ListAPIView):
    serializer_class = ObjetivoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Objetivo.objects.all()
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_objetivo = request.query_params.get('nombre_objetivo', '')

        # Realiza la búsqueda utilizando el campo 'nombre_objetivo' en el modelo
        if nombre_plan != '':
            queryset = Objetivo.objects.filter(id_plan__nombre_plan__icontains=nombre_plan)

        if nombre_objetivo != '':
            queryset = Objetivo.objects.filter(nombre_objetivo__icontains=nombre_objetivo)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Objetivo

class ObjetivoCreate(generics.ListCreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Objetivo creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Objetivo

class ObjetivoUpdate(generics.RetrieveUpdateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            return Response({'success': False, 'detail': 'El Objetivo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ObjetivoSerializer(objetivo, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Objetivo actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Objetivo

class ObjetivoDelete(generics.RetrieveUpdateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            return Response({'success': False, 'detail': 'El Objetivo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        objetivo.delete()
        return Response({'success': True, 'detail': 'Objetivo eliminado correctamente.'}, status=status.HTTP_200_OK)
    
# listar un Objetivo por id

class ObjetivoDetail(generics.RetrieveAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        objetivo = self.queryset.all().filter(id_objetivo=pk).first()
        if not objetivo:
            raise NotFound('No se encontraron resultados.')
        serializer = ObjetivoSerializer(objetivo)
        return Response({'success': True, 'detail': 'Objetivo encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar objetivo por id eje estrategico

class ObjetivoListIdEjeEstrategico(generics.ListAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        objetivo = self.queryset.all().filter(id_eje=pk)
        if not objetivo:
            raise NotFound('No se encontraron resultados.')
        serializer = ObjetivoSerializer(objetivo, many=True)
        return Response({'success': True, 'detail': 'Objetivo encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Listar Objetivo por id planes

class ObjetivoListIdPlanes(generics.ListAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        objetivo = self.queryset.all().filter(id_plan=pk)
        if not objetivo:
            raise NotFound('No se encontraron resultados.')
        serializer = ObjetivoSerializer(objetivo, many=True)
        return Response({'success': True, 'detail': 'Objetivo encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

# ---------------------------------------- Programas ----------------------------------------

# Listar todos los Programas

class ProgramaList(generics.ListCreateAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        programas = Programa.objects.all()
        serializer = ProgramaSerializer(programas, many=True)
        if not programas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Programas.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class ProgramaListPeriodoTiempo(generics.ListAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        programas = Programa.objects.filter(fecha_creacion__range=[data['fecha_inicio'], data['fecha_fin']], id_plan=data['id_plan'])
        serializer = ProgramaSerializer(programas, many=True)
        if not programas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Programas.', 'data': serializer.data}, status=status.HTTP_200_OK)    
# Crear un Programa

class ProgramaCreate(generics.ListCreateAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Programa creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Programa

class ProgramaUpdate(generics.RetrieveUpdateAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        programa = self.queryset.all().filter(id_programa=pk).first()
        if not programa:
            return Response({'success': False, 'detail': 'El Programa ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProgramaSerializer(programa, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Programa actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Eliminar un Programa

class ProgramaDelete(generics.RetrieveUpdateAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        programa = self.queryset.all().filter(id_programa=pk).first()
        if not programa:
            return Response({'success': False, 'detail': 'El Programa ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        programa.delete()
        return Response({'success': True, 'detail': 'Programa eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Programa por id

class ProgramaDetail(generics.RetrieveAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        programa = self.queryset.all().filter(id_programa=pk).first()
        if not programa:
            raise NotFound('No se encontraron resultados.')
        serializer = ProgramaSerializer(programa)
        return Response({'success': True, 'detail': 'Programa encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Programa por id planes

class ProgramaListIdEjeEstrategico(generics.ListAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        programa = self.queryset.all().filter(id_eje_estrategico=pk)
        if not programa:
            raise NotFound('No se encontraron resultados.')
        serializer = ProgramaSerializer(programa, many=True)
        return Response({'success': True, 'detail': 'Programa encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada Programas por nombre programa y nombre plan

class BusquedaAvanzadaProgramas(generics.ListAPIView):
    serializer_class = ProgramaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Programa.objects.all()
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_eje = request.query_params.get('nombre_eje', '')

        # Realiza la búsqueda utilizando el campo 'nombre_programa' en el modelo
        if nombre_programa != '':
            queryset = Programa.objects.filter(nombre_programa__icontains=nombre_programa)
        if nombre_eje != '':
            queryset = Programa.objects.filter(id_eje_estrategico__nombre__icontains=nombre_eje)
        

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------- Proyectos ----------------------------------------

# Listar todos los Proyectos

class ProyectoList(generics.ListCreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        proyectos = Proyecto.objects.all()
        serializer = ProyectoSerializer(proyectos, many=True)
        if not proyectos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Proyectos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class ProyectoListPeriodoTiempo(generics.ListAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        print(data, 'data')
        proyectos = Proyecto.objects.filter(fecha_creacion__range=[data['fecha_inicio'], data['fecha_fin']], id_plan=data['id_plan'])
        serializer = ProyectoSerializer(proyectos, many=True)
        if not proyectos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Proyectos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Proyecto

class ProyectoCreate(generics.ListCreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Proyecto creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Proyecto

class ProyectoUpdate(generics.RetrieveUpdateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        proyecto = self.queryset.all().filter(id_proyecto=pk).first()
        if not proyecto:
            return Response({'success': False, 'detail': 'El Proyecto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProyectoSerializer(proyecto, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Proyecto actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Proyecto

class ProyectoDelete(generics.RetrieveUpdateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        proyecto = self.queryset.all().filter(id_proyecto=pk).first()
        if not proyecto:
            return Response({'success': False, 'detail': 'El Proyecto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        proyecto.delete()
        return Response({'success': True, 'detail': 'Proyecto eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Proyecto por id

class ProyectoDetail(generics.RetrieveAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        proyecto = self.queryset.all().filter(id_proyecto=pk).first()
        if not proyecto:
            raise NotFound('No se encontraron resultados.')
        serializer = ProyectoSerializer(proyecto)
        return Response({'success': True, 'detail': 'Proyecto encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Proyecto por id programas

class ProyectoListIdProgramas(generics.ListAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        proyecto = self.queryset.all().filter(id_programa=pk)
        if not proyecto:
            raise NotFound('No se encontraron resultados.')
        serializer = ProyectoSerializer(proyecto, many=True)
        return Response({'success': True, 'detail': 'Proyecto encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada proyectos por nombre plan, nombre programa y nombre proyecto

class BusquedaAvanzadaProyectos(generics.ListAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')

        # Realiza la búsqueda utilizando el campo 'nombre_proyecto' en el modelo
        queryset = Proyecto.objects.filter(nombre_proyecto__icontains=nombre_proyecto, id_programa__nombre_programa__icontains=nombre_programa, id_plan__nombre_plan__icontains=nombre_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------- Productos ----------------------------------------

# Listar todos los Productos

class ProductosList(generics.ListCreateAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        productos = Productos.objects.all()
        serializer = ProductosSerializer(productos, many=True)
        if not productos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Productos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class ProductosListPeriodoTiempo(generics.ListAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        productos = Productos.objects.filter(fecha_creacion__range=[data['fecha_inicio'], data['fecha_fin']], id_plan=data['id_plan'])
        serializer = ProductosSerializer(productos, many=True)
        if not productos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Productos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Producto

class ProductosCreate(generics.ListCreateAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Producto creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Producto

class ProductosUpdate(generics.RetrieveUpdateAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        producto = self.queryset.all().filter(id_producto=pk).first()
        if not producto:
            return Response({'success': False, 'detail': 'El Producto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductosSerializer(producto, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Producto actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Producto

class ProductosDelete(generics.RetrieveUpdateAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        producto = self.queryset.all().filter(id_producto=pk).first()
        if not producto:
            return Response({'success': False, 'detail': 'El Producto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        producto.delete()
        return Response({'success': True, 'detail': 'Producto eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Producto por id

class ProductosDetail(generics.RetrieveAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        producto = self.queryset.all().filter(id_producto=pk).first()
        if not producto:
            raise NotFound('No se encontraron resultados.')
        serializer = ProductosSerializer(producto)
        return Response({'success': True, 'detail': 'Producto encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Producto por id proyectos

class ProductosListIdProyectos(generics.ListAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        producto = self.queryset.all().filter(id_proyecto=pk)
        if not producto:
            raise NotFound('No se encontraron resultados.')
        serializer = ProductosSerializer(producto, many=True)
        return Response({'success': True, 'detail': 'Producto encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada Productos por nombre plan, nombre programa, nombre proyecto y nombre producto
    
class BusquedaAvanzadaProductos(generics.ListAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')
        nombre_producto = request.query_params.get('nombre_producto', '')

        # Realiza la búsqueda utilizando el campo 'nombre_producto' en el modelo
        queryset = Productos.objects.filter(nombre_producto__icontains=nombre_producto, id_proyecto__nombre_proyecto__icontains=nombre_proyecto, id_proyecto__id_programa__nombre_programa__icontains=nombre_programa, id_proyecto__id_plan__nombre_plan__icontains=nombre_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Actividades ----------------------------------------

# Listar todos los Actividades

class ActividadList(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        actividades = Actividad.objects.all()
        serializer = ActividadSerializer(actividades, many=True)
        if not actividades:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Actividades.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class ActividadListPeriodoTiempo(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        actividades = Actividad.objects.filter(fecha_creacion__range=[data['fecha_inicio'], data['fecha_fin']], id_plan=data['id_plan'])
        serializer = ActividadSerializer(actividades, many=True)
        if not actividades:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Actividades.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Actividad

class ActividadCreate(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Actividad creada correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Actividad

class ActividadUpdate(generics.RetrieveUpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        actividad = self.queryset.all().filter(id_actividad=pk).first()
        if not actividad:
            return Response({'success': False, 'detail': 'La Actividad ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividad, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Actividad actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Actividad

class ActividadDelete(generics.RetrieveUpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        actividad = self.queryset.all().filter(id_actividad=pk).first()
        if not actividad:
            return Response({'success': False, 'detail': 'La Actividad ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        actividad.delete()
        return Response({'success': True, 'detail': 'Actividad eliminada correctamente.'}, status=status.HTTP_200_OK)

# listar un Actividad por id

class ActividadDetail(generics.RetrieveAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        actividad = self.queryset.all().filter(id_actividad=pk).first()
        if not actividad:
            raise NotFound('No se encontraron resultados.')
        serializer = ActividadSerializer(actividad)
        return Response({'success': True, 'detail': 'Actividad encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Actividad por id productos

class ActividadListIdProductos(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        actividad = self.queryset.all().filter(id_producto=pk)
        if not actividad:
            raise NotFound('No se encontraron resultados.')
        serializer = ActividadSerializer(actividad, many=True)
        return Response({'success': True, 'detail': 'Actividad encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Actividad por id planes

class ActividadListIdPlanes(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        actividad = self.queryset.all().filter(id_plan=pk)
        if not actividad:
            raise NotFound('No se encontraron resultados.')
        serializer = ActividadSerializer(actividad, many=True)
        return Response({'success': True, 'detail': 'Actividad encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada Actividades por nombre plan, nombre programa, nombre proyecto, nombre producto y nombre actividad
    
class BusquedaAvanzadaActividades(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')
        nombre_producto = request.query_params.get('nombre_producto', '')
        nombre_actividad = request.query_params.get('nombre_actividad', '')

        # Realiza la búsqueda utilizando el campo 'nombre_actividad' en el modelo
        queryset = Actividad.objects.filter(nombre_actividad__icontains=nombre_actividad, id_producto__nombre_producto__icontains=nombre_producto, id_producto__id_proyecto__nombre_proyecto__icontains=nombre_proyecto, id_producto__id_proyecto__id_programa__nombre_programa__icontains=nombre_programa, id_producto__id_proyecto__id_plan__nombre_plan__icontains=nombre_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Entidades Tabla Básica ----------------------------------------

# Listar todas las Entidades

class EntidadList(generics.ListCreateAPIView):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        entidades = Entidad.objects.all()
        serializer = EntidadSerializer(entidades, many=True)
        if not entidades:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Entidades.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear una Entidad

class EntidadCreate(generics.ListCreateAPIView):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer
    permission_classes = (IsAuthenticated,)

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
        return Response({'success': True, 'detail': 'Entidad creada correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar una Entidad

class EntidadUpdate(generics.RetrieveUpdateAPIView):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        entidad = self.queryset.all().filter(id_entidad=pk).first()
        if not entidad:
            return Response({'success': False, 'detail': 'La Entidad ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        if entidad.item_ya_usado == True:
            return Response({'success': False, 'detail': 'La Entidad ya ha sido usado en un Plan, por lo tanto no puede ser modificado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = EntidadSerializer(entidad, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Entidad actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar una Entidad

class EntidadDelete(generics.RetrieveUpdateAPIView):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        entidad = self.queryset.all().filter(id_entidad=pk).first()
        if not entidad:
            return Response({'success': False, 'detail': 'La Entidad ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        if entidad.item_ya_usado == True:
            return Response({'success': False, 'detail': 'La Entidad ya ha sido usado en un Plan, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        if entidad.registro_precargado:
            return Response({'success': False, 'detail': 'La Entidad es un registro precargado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        entidad.delete()
        return Response({'success': True, 'detail': 'Entidad eliminada correctamente.'}, status=status.HTTP_200_OK)

# listar una Entidad por id

class EntidadDetail(generics.RetrieveAPIView):
    queryset = Entidad.objects.all()
    serializer_class = EntidadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        entidad = self.queryset.all().filter(id_entidad=pk).first()
        if not entidad:
            raise NotFound('No se encontraron resultados.')
        serializer = EntidadSerializer(entidad)
        return Response({'success': True, 'detail': 'Entidad encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Medicion Tabla Básica ----------------------------------------

# Listar todas las Mediciones

class MedicionList(generics.ListCreateAPIView):
    queryset = Medicion.objects.all()
    serializer_class = MedicionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        mediciones = Medicion.objects.all()
        serializer = MedicionSerializer(mediciones, many=True)
        if not mediciones:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Mediciones.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear una Medicion

class MedicionCreate(generics.ListCreateAPIView):
    queryset = Medicion.objects.all()
    serializer_class = MedicionSerializer
    permission_classes = (IsAuthenticated,)

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
        return Response({'success': True, 'detail': 'Medicion creada correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar una Medicion

class MedicionUpdate(generics.RetrieveUpdateAPIView):
    queryset = Medicion.objects.all()
    serializer_class = MedicionSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        medicion = self.queryset.all().filter(id_medicion=pk).first()
        if not medicion:
            return Response({'success': False, 'detail': 'La Medicion ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        if medicion.item_ya_usado == True:
            return Response({'success': False, 'detail': 'La Medicion ya ha sido usado en un Plan, por lo tanto no puede ser modificado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MedicionSerializer(medicion, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Medicion actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar una Medicion

class MedicionDelete(generics.RetrieveUpdateAPIView):
    queryset = Medicion.objects.all()
    serializer_class = MedicionSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        medicion = self.queryset.all().filter(id_medicion=pk).first()
        if not medicion:
            return Response({'success': False, 'detail': 'La Medicion ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        if medicion.item_ya_usado == True:
            return Response({'success': False, 'detail': 'La Medicion ya ha sido usado en un Plan, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        if medicion.registro_precargado:
            return Response({'success': False, 'detail': 'La Medicion es un registro precargado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        medicion.delete()
        return Response({'success': True, 'detail': 'Medicion eliminada correctamente.'}, status=status.HTTP_200_OK)

# listar una Medicion por id

class MedicionDetail(generics.RetrieveAPIView):
    queryset = Medicion.objects.all()
    serializer_class = MedicionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        medicion = self.queryset.all().filter(id_medicion=pk).first()
        if not medicion:
            raise NotFound('No se encontraron resultados.')
        serializer = MedicionSerializer(medicion)
        return Response({'success': True, 'detail': 'Medicion encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Tipo Tabla Básica ----------------------------------------

# Listar todos los Tipos

class TipoList(generics.ListCreateAPIView):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tipos = Tipo.objects.all()
        serializer = TipoSerializer(tipos, many=True)
        if not tipos:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Tipos.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Tipo

class TipoCreate(generics.ListCreateAPIView):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    permission_classes = (IsAuthenticated,)

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
        return Response({'success': True, 'detail': 'Tipo creado correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un Tipo

class TipoUpdate(generics.RetrieveUpdateAPIView):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        tipo = self.queryset.all().filter(id_tipo=pk).first()
        if not tipo:
            return Response({'success': False, 'detail': 'El Tipo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if tipo.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Tipo ya ha sido usado en un Plan, por lo tanto no puede ser modificado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TipoSerializer(tipo, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Tipo actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Tipo

class TipoDelete(generics.RetrieveUpdateAPIView):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        tipo = self.queryset.all().filter(id_tipo=pk).first()
        if not tipo:
            return Response({'success': False, 'detail': 'El Tipo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if tipo.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Tipo ya ha sido usado en un Plan, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        if tipo.registro_precargado:
            return Response({'success': False, 'detail': 'El Tipo es un registro precargado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        tipo.delete()
        return Response({'success': True, 'detail': 'Tipo eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Tipo por id

class TipoDetail(generics.RetrieveAPIView):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        tipo = self.queryset.all().filter(id_tipo=pk).first()
        if not tipo:
            raise NotFound('No se encontraron resultados.')
        serializer = TipoSerializer(tipo)
        return Response({'success': True, 'detail': 'Tipo encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Rubro ----------------------------------------

# Listar todos los Rubros

class RubroList(generics.ListCreateAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        rubros = Rubro.objects.all()
        serializer = RubroSerializer(rubros, many=True)
        if not rubros:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de rubros.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Rubro

class RubroCreate(generics.ListCreateAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'rubro creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Rubro

class RubroUpdate(generics.RetrieveUpdateAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        rubro = self.queryset.all().filter(id_rubro=pk).first()
        if not rubro:
            return Response({'success': False, 'detail': 'El Rubro ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RubroSerializer(rubro, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Rubro actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Rubro

class RubroDelete(generics.RetrieveUpdateAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        rubro = self.queryset.all().filter(id_rubro=pk).first()
        if not rubro:
            return Response({'success': False, 'detail': 'El rubro ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        rubro.delete()
        return Response({'success': True, 'detail': 'Rubro eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Rubro por id

class RubroDetail(generics.RetrieveAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        rubro = self.queryset.all().filter(id_rubro=pk).first()
        if not rubro:
            raise NotFound('No se encontraron resultados.')
        serializer = RubroSerializer(rubro)
        return Response({'success': True, 'detail': 'Rubro encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada rubros por cod_pre, cuenta, nombre programa, nombre proyecto, nombre producto, nombre actividad, nombre indicador

class BusquedaAvanzadaRubros(generics.ListAPIView):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cod_pre = request.query_params.get('cod_pre', '')
        cuenta = request.query_params.get('cuenta', '')
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')
        nombre_producto = request.query_params.get('nombre_producto', '')
        nombre_actividad = request.query_params.get('nombre_actividad', '')
        nombre_indicador = request.query_params.get('nombre_indicador', '')

        # Realiza la búsqueda utilizando el campo 'nombre_rubro' en el modelo
        queryset = Rubro.objects.filter(cod_pre__icontains=cod_pre, cuenta__icontains=cuenta, id_actividad__nombre_actividad__icontains=nombre_actividad, id_actividad__id_producto__nombre_producto__icontains=nombre_producto, id_actividad__id_producto__id_proyecto__nombre_proyecto__icontains=nombre_proyecto, id_actividad__id_producto__id_proyecto__id_programa__nombre_programa__icontains=nombre_programa, id_actividad__id_producto__id_proyecto__id_plan__nombre_plan__icontains=nombre_plan, id_actividad__id_producto__id_proyecto__id_plan__id_indicador__nombre_indicador__icontains=nombre_indicador)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Indicador ----------------------------------------

# Listar todos los Indicadores

class IndicadorList(generics.ListCreateAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        indicadores = Indicador.objects.all()
        serializer = IndicadorSerializer(indicadores, many=True)
        if not indicadores:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Indicadores.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class IndicadorListPeriodoTiempo(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        indicadores = Indicador.objects.filter(fecha_creacion__range=[data['fecha_inicio'], data['fecha_fin']], id_plan=data['id_plan'])
        serializer = IndicadorSerializer(indicadores, many=True)
        if not indicadores:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Indicadores.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un Indicador

class IndicadorCreate(generics.ListCreateAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Indicador creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Indicador

class IndicadorUpdate(generics.RetrieveUpdateAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        indicador = self.queryset.all().filter(id_indicador=pk).first()
        if not indicador:
            return Response({'success': False, 'detail': 'El Indicador ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = IndicadorSerializer(indicador, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Indicador actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Indicador

class IndicadorDelete(generics.RetrieveUpdateAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        indicador = self.queryset.all().filter(id_indicador=pk).first()
        if not indicador:
            return Response({'success': False, 'detail': 'El Indicador ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        indicador.delete()
        return Response({'success': True, 'detail': 'Indicador eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Indicador por id

class IndicadorDetail(generics.RetrieveAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_indicador=pk).first()
        if not indicador:
            raise NotFound('No se encontraron resultados.')
        serializer = IndicadorSerializer(indicador)
        return Response({'success': True, 'detail': 'Indicador encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Indicador por id planes

class IndicadorListIdPlanes(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_plan=pk)
        if not indicador:
            raise NotFound('No se encontraron resultados.')
        serializer = IndicadorSerializer(indicador, many=True)
        return Response({'success': True, 'detail': 'Indicador encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Indicador por id actividad

class IndicadorListIdActividad(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_actividad=pk)
        if not indicador:
            raise NotFound('No se encontraron resultados.')
        serializer = IndicadorSerializer(indicador, many=True)
        return Response({'success': True, 'detail': 'Indicador encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Indicador por id producto

class IndicadorListIdProducto(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_producto=pk)
        if not indicador:
            raise NotFound('No se encontraron resultados.')
        serializer = IndicadorSerializer(indicador, many=True)
        return Response({'success': True, 'detail': 'Indicador encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Indicador por id Rubro

class IndicadorListIdRubro(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_rubro=pk)
        if not indicador:
            raise NotFound('No se encontraron resultados.')
        serializer = IndicadorSerializer(indicador, many=True)
        return Response({'success': True, 'detail': 'Indicador encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada Actividades por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad y nombre indicador
    
class BusquedaAvanzadaIndicadores(generics.ListAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')
        nombre_producto = request.query_params.get('nombre_producto', '')
        nombre_actividad = request.query_params.get('nombre_actividad', '')
        nombre_indicador = request.query_params.get('nombre_indicador', '')

        # Realiza la búsqueda utilizando el campo 'nombre_indicador' en el modelo
        queryset = Indicador.objects.filter(nombre_indicador__icontains=nombre_indicador, id_actividad__nombre_actividad__icontains=nombre_actividad, id_actividad__id_producto__nombre_producto__icontains=nombre_producto, id_actividad__id_producto__id_proyecto__nombre_proyecto__icontains=nombre_proyecto, id_actividad__id_producto__id_proyecto__id_programa__nombre_programa__icontains=nombre_programa, id_actividad__id_producto__id_proyecto__id_plan__nombre_plan__icontains=nombre_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Metas ----------------------------------------

# Listar todos los Metas

class MetaList(generics.ListCreateAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        metas = Metas.objects.all()
        serializer = MetasSerializer(metas, many=True)
        if not metas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Metas.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final
    
class MetaListPeriodoTiempo(generics.ListAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        metas = Metas.objects.all().filter(fecha_creacion_meta__range=[data["fecha_inicio"], data["fecha_fin"]])
        serializer = MetasSerializer(metas, many=True)
        if not metas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Metas.', 'data': serializer.data}, status=status.HTTP_200_OK)

# # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id_indicador
    
class MetaListPeriodoTiempoPorIndicador(generics.ListAPIView):
        queryset = Metas.objects.all()
        serializer_class = MetasSerializer
        permission_classes = (IsAuthenticated,)

        def get(self, request):
            data = request.query_params
            metas = Metas.objects.all().filter(fecha_creacion_meta__range=[data["fecha_inicio"], data["fecha_fin"]], id_indicador=data["id_indicador"])
            serializer = MetasSerializer(metas, many=True)
            if not metas:
                raise NotFound('No se encontraron resultados.')
            return Response({'success': True, 'detail': 'Listado de Metas.', 'data': serializer.data}, status=status.HTTP_200_OK)
        
# Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 

class MetaListPeriodoTiempoPorPlan(generics.ListAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        metas = Metas.objects.all().filter(fecha_creacion_meta__range=[data["fecha_inicio"], data["fecha_fin"]], id_plan=data["id_plan"])
        serializer = MetasSerializer(metas, many=True)
        if not metas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Metas.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Meta

class MetaCreate(generics.ListCreateAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Meta creada correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Meta

class MetaUpdate(generics.RetrieveUpdateAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        meta = self.queryset.all().filter(id_meta=pk).first()
        if not meta:
            return Response({'success': False, 'detail': 'La Meta ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetasSerializer(meta, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Meta actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Meta

class MetaDelete(generics.RetrieveUpdateAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        meta = self.queryset.all().filter(id_meta=pk).first()
        if not meta:
            return Response({'success': False, 'detail': 'La Meta ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        meta.delete()
        return Response({'success': True, 'detail': 'Meta eliminada correctamente.'}, status=status.HTTP_200_OK)

# listar un Meta por id

class MetaDetail(generics.RetrieveAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        meta = self.queryset.all().filter(id_meta=pk).first()
        if not meta:
            raise NotFound('No se encontraron resultados.')
        serializer = MetasSerializer(meta)
        return Response({'success': True, 'detail': 'Meta encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Listar Metas por id indicador

class MetaListIdIndicador(generics.ListAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        meta = self.queryset.all().filter(id_indicador=pk)
        if not meta:
            raise NotFound('No se encontraron resultados.')
        serializer = MetasSerializer(meta, many=True)
        return Response({'success': True, 'detail': 'Meta encontrada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda Avanzada Actividades por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad, nombre indicador y nombre meta

class BusquedaAvanzadaMetas(generics.ListAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_plan = request.query_params.get('nombre_plan', '')
        nombre_proyecto = request.query_params.get('nombre_proyecto', '')
        nombre_producto = request.query_params.get('nombre_producto', '')
        nombre_actividad = request.query_params.get('nombre_actividad', '')
        nombre_indicador = request.query_params.get('nombre_indicador', '')
        nombre_meta = request.query_params.get('nombre_meta', '')

        # Realiza la búsqueda utilizando el campo 'nombre_meta' en el modelo
        queryset = Metas.objects.filter(nombre_meta__icontains=nombre_meta, id_indicador__nombre_indicador__icontains=nombre_indicador, id_indicador__id_actividad__nombre_actividad__icontains=nombre_actividad, id_indicador__id_actividad__id_producto__nombre_producto__icontains=nombre_producto, id_indicador__id_actividad__id_producto__id_proyecto__nombre_proyecto__icontains=nombre_proyecto, id_indicador__id_actividad__id_producto__id_proyecto__id_programa__nombre_programa__icontains=nombre_programa, id_indicador__id_actividad__id_producto__id_proyecto__id_plan__nombre_plan__icontains=nombre_plan)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)


# ---------------------------------------- Tipo Eje Tabla Básica ----------------------------------------

# Listar todos los Tipos Eje

class TipoEjeList(generics.ListCreateAPIView):
    queryset = TipoEje.objects.all()
    serializer_class = TipoEjeSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tipos_eje = TipoEje.objects.all()
        serializer = TipoEjeSerializer(tipos_eje, many=True)
        if not tipos_eje:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Tipos Eje.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Tipo Eje

class TipoEjeCreate(generics.ListCreateAPIView):
    queryset = TipoEje.objects.all()
    serializer_class = TipoEjeSerializer
    permission_classes = (IsAuthenticated,)

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
        return Response({'success': True, 'detail': 'Tipo Eje creado correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un Tipo Eje

class TipoEjeUpdate(generics.RetrieveUpdateAPIView):
    queryset = TipoEje.objects.all()
    serializer_class = TipoEjeSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        tipo_eje = self.queryset.all().filter(id_tipo_eje=pk).first()
        if not tipo_eje:
            return Response({'success': False, 'detail': 'El Tipo Eje ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if tipo_eje.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Tipo Eje ya ha sido usado en un Plan, por lo tanto no puede ser modificado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TipoEjeSerializer(tipo_eje, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Tipo Eje actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Tipo Eje

class TipoEjeDelete(generics.RetrieveUpdateAPIView):
    queryset = TipoEje.objects.all()
    serializer_class = TipoEjeSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        tipo_eje = self.queryset.all().filter(id_tipo_eje=pk).first()
        if not tipo_eje:
            return Response({'success': False, 'detail': 'El Tipo Eje ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        if tipo_eje.item_ya_usado == True:
            return Response({'success': False, 'detail': 'El Tipo Eje ya ha sido usado en un Plan, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        if tipo_eje.registro_precargado:
            return Response({'success': False, 'detail': 'El Tipo Eje es un registro precargado, por lo tanto no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
        tipo_eje.delete()
        return Response({'success': True, 'detail': 'Tipo Eje eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Tipo Eje por id

class TipoEjeDetail(generics.RetrieveAPIView):
    queryset = TipoEje.objects.all()
    serializer_class = TipoEjeSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        tipo_eje = self.queryset.all().filter(id_tipo_eje=pk).first()
        if not tipo_eje:
            raise NotFound('No se encontraron resultados.')
        serializer = TipoEjeSerializer(tipo_eje)
        return Response({'success': True, 'detail': 'Tipo Eje encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Subprograma ----------------------------------------

# Listar todos los Subprogramas

class SubprogramaList(generics.ListCreateAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        subprogramas = Subprograma.objects.all()
        serializer = SubprogramaSerializer(subprogramas, many=True)
        if not subprogramas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Subprogramas.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un Subprograma

class SubprogramaCreate(generics.ListCreateAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Subprograma creado correctamente.', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualizar un Subprograma

class SubprogramaUpdate(generics.RetrieveUpdateAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        subprograma = self.queryset.all().filter(id_subprograma=pk).first()
        if not subprograma:
            return Response({'success': False, 'detail': 'El Subprograma ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubprogramaSerializer(subprograma, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Subprograma actualizado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un Subprograma

class SubprogramaDelete(generics.RetrieveUpdateAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        subprograma = self.queryset.all().filter(id_subprograma=pk).first()
        if not subprograma:
            return Response({'success': False, 'detail': 'El Subprograma ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        subprograma.delete()
        return Response({'success': True, 'detail': 'Subprograma eliminado correctamente.'}, status=status.HTTP_200_OK)

# listar un Subprograma por id

class SubprogramaDetail(generics.RetrieveAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        subprograma = self.queryset.all().filter(id_subprograma=pk).first()
        if not subprograma:
            raise NotFound('No se encontraron resultados.')
        serializer = SubprogramaSerializer(subprograma)
        return Response({'success': True, 'detail': 'Subprograma encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar Subprograma por id programa

class SubprogramaListIdPrograma(generics.ListAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        subprograma = self.queryset.all().filter(id_programa=pk)
        if not subprograma:
            raise NotFound('No se encontraron resultados.')
        serializer = SubprogramaSerializer(subprograma, many=True)
        return Response({'success': True, 'detail': 'Subprograma encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Busqueda Avanzada subprogramas por nombre programa y nombre subprograma
    
class BusquedaAvanzadaSubprogramas(generics.ListAPIView):
    queryset = Subprograma.objects.all()
    serializer_class = SubprogramaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_programa = request.query_params.get('nombre_programa', '')
        nombre_subprograma = request.query_params.get('nombre_subprograma', '')

        # Realiza la búsqueda utilizando el campo 'nombre_subprograma' en el modelo
        queryset = Subprograma.objects.filter(nombre_subprograma__icontains=nombre_subprograma, id_programa__nombre_programa__icontains=nombre_programa)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

# CONSULTA TOTAL
class PlanesGetAll(generics.ListAPIView):
    serializer_class = PlanesSerializerGet
    queryset = Planes.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        planes = Planes.objects.all()
        serializer = self.serializer_class(planes, many=True)
        if not planes:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de planes.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# CONSULTA POR ID PLAN

class PlanesGetId(generics.ListAPIView):
    serializer_class = PlanesSerializerGet
    queryset = Planes.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        planes = Planes.objects.all().filter(id_plan=pk)
        serializer = self.serializer_class(planes, many=True)
        if not planes:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de planes.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

#PGAR
#Metas PGAR
class MetasPGARListByIdEjeEstrategico(generics.ListAPIView):
    serializer_class = MetasPGARSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        metas = MetasEjePGAR.objects.filter(id_eje_estrategico=pk)
        serializer = self.serializer_class(metas, many=True)
        if not metas:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de Metas PGAR.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class MetasPGARList(generics.ListAPIView):
    serializer_class = MetasPGARSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        metas = MetasEjePGAR.objects.all()
        nombre_meta = request.query_params.get('nombre_meta', '')
        nombre_eje_estrategico = request.query_params.get('nombre_eje_estrategico', '')
        nombre_objetivo = request.query_params.get('nombre_objetivo', '')
        if nombre_meta != '':
            metas = metas.filter(nombre_meta__icontains=nombre_meta)
        if nombre_eje_estrategico != '':
            metas = metas.filter(id_eje_estrategico__nombre__icontains=nombre_eje_estrategico)
        if nombre_objetivo != '':
            metas = metas.filter(id_objetivo__nombre_objetivo__icontains=nombre_objetivo)

        if not metas:
            raise NotFound('No se encontraron resultados.')
        
        serializer = self.serializer_class(metas, many=True)
        return Response({'success': True, 'detail': 'Listado de Metas PGAR.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class MetasPGARCreate(generics.CreateAPIView):
    serializer_class = MetasPGARSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Meta PGAR creada correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class MetasPGARUpdate(generics.UpdateAPIView):
    serializer_class = MetasPGARSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        meta = MetasEjePGAR.objects.filter(id_meta_eje=pk).first()
        if not meta:
            return Response({'success': False, 'detail': 'La Meta PGAR ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetasPGARSerializer(meta, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Meta PGAR actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

#Linea Base
class LineaBaseListByIdMeta(generics.ListAPIView):
    serializer_class = LineasBasePGARSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        lineas_base = LineasBasePGAR.objects.filter(id_meta_eje=pk)
        if not lineas_base:
            raise NotFound('No se encontraron resultados.')
        
        serializer = self.serializer_class(lineas_base, many=True)
        return Response({'success': True, 'detail': 'Listado de Lineas Base.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class LineaBaseCreate(generics.CreateAPIView):
    serializer_class = LineasBasePGARSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Linea Base creada correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class LineaBaseUpdate(generics.UpdateAPIView):
    serializer_class = LineasBasePGARSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        linea_base = LineasBasePGAR.objects.filter(id_linea_base=pk).first()
        if not linea_base:
            return Response({'success': False, 'detail': 'La Linea Base ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LineasBasePGARSerializer(linea_base, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Linea Base actualizada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
