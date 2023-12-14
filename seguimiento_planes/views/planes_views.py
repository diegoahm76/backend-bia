from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from seguimiento_planes.serializers.planes_serializer import ObjetivoDesarrolloSostenibleSerializer, Planes, EjeEstractegicoSerializer, ObjetivoSerializer, PlanesSerializer, PlanesSerializerGet, ProgramaSerializer, ProyectoSerializer, ProductosSerializer, ActividadSerializer, EntidadSerializer, MedicionSerializer, TipoEjeSerializer, TipoSerializer, RubroSerializer, IndicadorSerializer, MetasSerializer, SubprogramaSerializer
from seguimiento_planes.models.planes_models import ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma

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
        planes = self.queryset.filter(nombre_plan=data["nombre_plan"]).first()
        print('PLANESSSS', planes)
        if planes:
            return Response({'success': False, 'detail': 'El plan ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
        if planes.nombre_plan != data["nombre_plan"] and self.queryset.filter(nombre_plan=data["nombre_plan"]).exists():
            return Response({'success': False, 'detail': 'El plan ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
    queryset = Planes.objects.all()
    serializer_class = PlanesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_plan = request.query_params.get('nombre_plan', '')

        # Realiza la búsqueda utilizando el campo 'nombre_plan' en el modelo
        queryset = Planes.objects.filter(nombre_plan__icontains=nombre_plan)

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

# Crear un Eje Estratégico    

class EjeEstractegicoCreate(generics.ListCreateAPIView):
    queryset = EjeEstractegico.objects.all()
    serializer_class = EjeEstractegicoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        eje = self.queryset.filter(nombre=data["nombre"]).first()
        print('eje estrategico', eje)
        if eje:
            return Response({'success': False, 'detail': 'El eje estratégico ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
        
# Crear un Objetivo

class ObjetivoCreate(generics.ListCreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        objetivo = self.queryset.filter(nombre_objetivo=data["nombre_objetivo"]).first()
        if objetivo:
            return Response({'success': False, 'detail': 'El objetivo ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
    
# Crear un Programa

class ProgramaCreate(generics.ListCreateAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        programa = self.queryset.filter(nombre_programa=data["nombre_programa"]).first()
        if programa:
            return Response({'success': False, 'detail': 'El programa ya existe'}, status=status.HTTP_403_FORBIDDEN)
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

class ProgramaListIdPlanes(generics.ListAPIView):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        programa = self.queryset.all().filter(id_plan=pk)
        if not programa:
            raise NotFound('No se encontraron resultados.')
        serializer = ProgramaSerializer(programa, many=True)
        return Response({'success': True, 'detail': 'Programa encontrado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

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

# Crear un Proyecto

class ProyectoCreate(generics.ListCreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        proyecto = self.queryset.filter(nombre_proyecto=data["nombre_proyecto"]).first()
        if proyecto:
            return Response({'success': False, 'detail': 'El proyecto ya existe'}, status=status.HTTP_403_FORBIDDEN)
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

# Crear un Producto

class ProductosCreate(generics.ListCreateAPIView):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        producto = self.queryset.filter(nombre_producto=data["nombre_producto"]).first()
        if producto:
            return Response({'success': False, 'detail': 'El producto ya existe'}, status=status.HTTP_403_FORBIDDEN)
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

# Crear un Actividad

class ActividadCreate(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        actividad = self.queryset.filter(nombre_actividad=data["nombre_actividad"]).first()
        if actividad:
            return Response({'success': False, 'detail': 'La actividad ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
        rubro = self.queryset.filter(cod_pre=data["cod_pre"]).first()
        if rubro:
            return Response({'success': False, 'detail': 'Codigo ya existe '}, status=status.HTTP_403_FORBIDDEN)
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
    
# Crear un Indicador

class IndicadorCreate(generics.ListCreateAPIView):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        indicador = self.queryset.filter(nombre_indicador=data["nombre_indicador"]).first()
        if indicador:
            return Response({'success': False, 'detail': 'El indicador ya existe'}, status=status.HTTP_403_FORBIDDEN)
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

# Crear un Meta

class MetaCreate(generics.ListCreateAPIView):
    queryset = Metas.objects.all()
    serializer_class = MetasSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        data = request.data
        meta = self.queryset.filter(nombre_meta=data["nombre_meta"]).first()
        if meta:
            return Response({'success': False, 'detail': 'La meta ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
        subprograma = self.queryset.filter(nombre_subprograma=data["nombre_subprograma"]).first()
        if subprograma:
            return Response({'success': False, 'detail': 'El subprograma ya existe'}, status=status.HTTP_403_FORBIDDEN)
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
    


# CONSULTA TOTAL
class PlanesGetAll(generics.ListAPIView):
    serializer_class = PlanesSerializerGet
    queryset = Planes.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print("HOLAAA")
        planes = Planes.objects.all()
        serializer = self.serializer_class(planes, many=True)
        if not planes:
            raise NotFound('No se encontraron resultados.')
        return Response({'success': True, 'detail': 'Listado de planes.', 'data': serializer.data}, status=status.HTTP_200_OK)
