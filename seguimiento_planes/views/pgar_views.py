from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from seguimiento_planes.serializers.pgar_serializers import PlanGestionAmbientalRegionalSerializer, ObjetivoSerializer, LineaEstrategicaSerializer, MetaEstrategicaSerializer, EntidadesSerializer, PgarIndicadorSerializer, ActividadSerializer
from seguimiento_planes.models.pgar_models import PlanGestionAmbientalRegional, Objetivo, LineaEstrategica, MetaEstrategica, Entidades, PgarIndicador, Actividad

# ---------------------------------------- PlanGestionAmbientalRegional ----------------------------------------

# Listar todos los planes de gestion ambiental regional

class PlanGestionAmbientalRegionalList(generics.ListCreateAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        planes = PlanGestionAmbientalRegional.objects.all()
        serializer = PlanGestionAmbientalRegionalSerializer(planes, many=True)
        if not planes.exists():
            return Response({'success': False, 'detail': 'No se encontraron resultados'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'detail': 'Lista de planes de gestion ambiental regional', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un plan de gestion ambiental regional
class PlanGestionAmbientalRegionalCreate(generics.CreateAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'nombre_plan' ya existe
        if PlanGestionAmbientalRegional.objects.filter(nombre_plan=data['nombre_plan']).exists():
            return Response({'success': False, 'detail': 'Ya existe un plan de gestion ambiental regional con ese nombre'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlanGestionAmbientalRegionalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Plan de gestion ambiental regional creado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Actualizar un plan de gestion ambiental regional

class PlanGestionAmbientalRegionalUpdate(generics.UpdateAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            if PlanGestionAmbientalRegional.objects.filter(nombre_plan=data['nombre_plan']).exists():
                return Response({'success': False, 'detail': 'Ya existe un plan de gestion ambiental regional con ese nombre'}, status=status.HTTP_400_BAD_REQUEST)

            plan = PlanGestionAmbientalRegional.objects.get(pk=pk)
        except PlanGestionAmbientalRegional.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un plan de gestion ambiental regional con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlanGestionAmbientalRegionalSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Plan de gestion ambiental regional actualizado correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar un plan de gestion ambiental regional

class PlanGestionAmbientalRegionalDelete(generics.DestroyAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            plan = PlanGestionAmbientalRegional.objects.get(pk=pk)
        except PlanGestionAmbientalRegional.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un plan de gestion ambiental regional con ese id'}, status=status.HTTP_404_NOT_FOUND)
        plan.delete()
        return Response({'success': True, 'detail': 'Plan de gestion ambiental regional eliminado correctamente'}, status=status.HTTP_200_OK)

# Listar un plan de gestion ambiental regional por id

class PlanGestionAmbientalRegionalId(generics.RetrieveAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            plan = PlanGestionAmbientalRegional.objects.get(pk=pk)
        except PlanGestionAmbientalRegional.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un plan de gestion ambiental regional con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlanGestionAmbientalRegionalSerializer(plan)
        return Response({'success': True, 'detail': 'Plan de gestion ambiental regional', 'data': serializer.data}, status=status.HTTP_200_OK)

# Busqueda avanzada por nombre de plan de gestion ambiental regional

class BusquedaAvanzada(generics.ListAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nombre_pgar = request.query_params.get('nombre_pgar', '')

        # Realiza la búsqueda utilizando el campo 'nombre_plan' en el modelo
        queryset = PlanGestionAmbientalRegional.objects.filter(nombre_plan__icontains=nombre_pgar)

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)
  
# ---------------------------------------- Objetivo ----------------------------------------

# Listar todos los objetivos

class ObjetivoList(generics.ListCreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.data
        objetivos = Objetivo.objects.all()
        serializer = ObjetivoSerializer(objetivos, many=True)
        return Response({'success': True, 'detail': 'Lista de objetivos', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un objetivo

class ObjetivoCreate(generics.CreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'descripcion_objetivo' ya existe
        if Objetivo.objects.filter(descripcion_objetivo=data['descripcion_objetivo']).exists():
            return Response({'success': False, 'detail': 'Ya existe un objetivo con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ObjetivoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Objetivo creado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar un objetivo

class ObjetivoUpdate(generics.UpdateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            # Comprobar si el campo 'descripcion_objetivo' ya existe
            if Objetivo.objects.filter(descripcion_objetivo=data['descripcion_objetivo']).exists():
                return Response({'success': False, 'detail': 'Ya existe un objetivo con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
            objetivo = Objetivo.objects.get(pk=pk)
        except Objetivo.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un objetivo con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ObjetivoSerializer(objetivo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Objetivo actualizado correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Eliminar un objetivo

class ObjetivoDelete(generics.DestroyAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            objetivo = Objetivo.objects.get(pk=pk)
        except Objetivo.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un objetivo con ese id'}, status=status.HTTP_404_NOT_FOUND)
        objetivo.delete()
        return Response({'success': True, 'detail': 'Objetivo eliminado correctamente'}, status=status.HTTP_200_OK)
    
# Listar un objetivo por id

class ObjetivoId(generics.RetrieveAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            objetivo = Objetivo.objects.get(pk=pk)
        except Objetivo.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un objetivo con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ObjetivoSerializer(objetivo)
        return Response({'success': True, 'detail': 'Objetivo', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar objetivos por id de plan de gestion ambiental regional

class ObjetivoPgarId(generics.ListAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            objetivos = Objetivo.objects.filter(id_plan=pk)
        except Objetivo.DoesNotExist:
            return Response({'success': False, 'detail': 'No existen objetivos con ese id de plan de gestion ambiental regional'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ObjetivoSerializer(objetivos, many=True)
        return Response({'success': True, 'detail': 'Lista de objetivos', 'data': serializer.data}, status=status.HTTP_200_OK)
# ---------------------------------------- LineaEstrategica ----------------------------------------

# Listar todas las lineas estrategicas

class LineaEstrategicaList(generics.ListCreateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        lineas_estrategicas = LineaEstrategica.objects.all()
        serializer = LineaEstrategicaSerializer(lineas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de lineas estrategicas', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear una linea estrategica

class LineaEstrategicaCreate(generics.CreateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'descripcion_linea_estrategica' ya existe
        if LineaEstrategica.objects.filter(descripcion_linea_estrategica=data['descripcion_linea_estrategica']).exists():
            return Response({'success': False, 'detail': 'Ya existe una linea estrategica con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)    
        serializer = LineaEstrategicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Linea estrategica creada correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una linea estrategica

class LineaEstrategicaUpdate(generics.UpdateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            # Comprobar si el campo 'descripcion_linea_estrategica' ya existe
            if LineaEstrategica.objects.filter(descripcion_linea_estrategica=data['descripcion_linea_estrategica']).exists():
                return Response({'success': False, 'detail': 'Ya existe una linea estrategica con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)    
            linea_estrategica = LineaEstrategica.objects.get(pk=pk)
        except LineaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una linea estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LineaEstrategicaSerializer(linea_estrategica, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Linea estrategica actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar una linea estrategica

class LineaEstrategicaDelete(generics.DestroyAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            linea_estrategica = LineaEstrategica.objects.get(pk=pk)
        except LineaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una linea estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        linea_estrategica.delete()
        return Response({'success': True, 'detail': 'Linea estrategica eliminada correctamente'}, status=status.HTTP_200_OK)

# Listar una linea estrategica por id

class LineaEstrategicaId(generics.RetrieveAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            linea_estrategica = LineaEstrategica.objects.get(pk=pk)
        except LineaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una linea estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LineaEstrategicaSerializer(linea_estrategica)
        return Response({'success': True, 'detail': 'Linea estrategica', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar lineas estrategicas por id de objetivo

class LineaEstrategicaObjetivoId(generics.ListAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            lineas_estrategicas = LineaEstrategica.objects.filter(id_obejtivo=pk)
        except LineaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existen lineas estrategicas con ese id de objetivo'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LineaEstrategicaSerializer(lineas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de lineas estrategicas', 'data': serializer.data}, status=status.HTTP_200_OK)   
# ---------------------------------------- MetaEstrategica ----------------------------------------

# Listar todas las metas estrategicas

class MetaEstrategicaList(generics.ListCreateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        metas_estrategicas = MetaEstrategica.objects.all()
        serializer = MetaEstrategicaSerializer(metas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de metas estrategicas', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear una meta estrategica

class MetaEstrategicaCreate(generics.CreateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'descripcion_meta_estrategica' ya existe
        if MetaEstrategica.objects.filter(descripcion_meta_estrategica=data['descripcion_meta_estrategica']).exists():
            return Response({'success': False, 'detail': 'Ya existe una meta estrategica con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MetaEstrategicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Meta estrategica creada correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una meta estrategica

class MetaEstrategicaUpdate(generics.UpdateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            # Comprobar si el campo 'descripcion_meta_estrategica' ya existe
            if MetaEstrategica.objects.filter(descripcion_meta_estrategica=data['descripcion_meta_estrategica']).exists():
                return Response({'success': False, 'detail': 'Ya existe una meta estrategica con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
            meta_estrategica = MetaEstrategica.objects.get(pk=pk)
        except MetaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una meta estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetaEstrategicaSerializer(meta_estrategica, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Meta estrategica actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Eliminar una meta estrategica

class MetaEstrategicaDelete(generics.DestroyAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            meta_estrategica = MetaEstrategica.objects.get(pk=pk)
        except MetaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una meta estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        meta_estrategica.delete()
        return Response({'success': True, 'detail': 'Meta estrategica eliminada correctamente'}, status=status.HTTP_200_OK)
    
# Listar una meta estrategica por id

class MetaEstrategicaId(generics.RetrieveAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            meta_estrategica = MetaEstrategica.objects.get(pk=pk)
        except MetaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una meta estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetaEstrategicaSerializer(meta_estrategica)
        return Response({'success': True, 'detail': 'Meta estrategica', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar metas estrategicas por id de linea estrategica

class MetaEstrategicaLineaEstrategicaId(generics.ListAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            metas_estrategicas = MetaEstrategica.objects.filter(id_linea_estrategica=pk)
        except MetaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existen metas estrategicas con ese id de linea estrategica'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetaEstrategicaSerializer(metas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de metas estrategicas', 'data': serializer.data}, status=status.HTTP_200_OK) 
# ---------------------------------------- Entidades ----------------------------------------

# Listar todas las entidades

class EntidadesList(generics.ListCreateAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        entidades = Entidades.objects.all()
        serializer = EntidadesSerializer(entidades, many=True)
        return Response({'success': True, 'detail': 'Lista de entidades', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear una entidad

class EntidadesCreate(generics.CreateAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        # Establecer 'activo' en True y determinar 'item_ya_usado' en función de las relaciones
        serializer.save(activo=True, item_ya_usado=self.has_relations(serializer.validated_data))

    def has_relations(self, validated_data):
        # Comprueba si hay relaciones con otras tablas
        if 'pgarindicador' in validated_data:
            # Si se proporciona un valor para 'pgarindicador', se considera que la entidad tiene relaciones
            return True
        return False

    def post(self, request):
        serializer = EntidadesSerializer(data=request.data)
        if serializer.is_valid():
            # Comprobar si el campo 'item_ya_usado' no se establece manualmente
            if 'item_ya_usado' in request.data:
                return Response({'success': False, 'detail': 'No puedes establecer manualmente "item_ya_usado"'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({'success': True, 'detail': 'Entidad creada correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
# Actualizar una entidad

class EntidadesUpdate(generics.UpdateAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            entidad = Entidades.objects.get(pk=pk)
        except Entidades.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una entidad con ese id'}, status=status.HTTP_404_NOT_FOUND)

        if entidad.item_ya_usado:
            return Response({'success': False, 'detail': 'No se puede actualizar una entidad con "item_ya_usado" en True'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EntidadesSerializer(entidad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Entidad actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        
# Eliminar una entidad

class EntidadesDelete(generics.DestroyAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            entidad = Entidades.objects.get(pk=pk)
        except Entidades.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una entidad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        
        if entidad.item_ya_usado or entidad.activo:
            return Response({'success': False, 'detail': 'No se puede eliminar una entidad con "item_ya_usado" o "activo" en True'}, status=status.HTTP_400_BAD_REQUEST)

        entidad.delete()
        return Response({'success': True, 'detail': 'Entidad eliminada correctamente'}, status=status.HTTP_200_OK)
        
# Listar una entidad por id

class EntidadesId(generics.RetrieveAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            entidad = Entidades.objects.get(pk=pk)
        except Entidades.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una entidad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EntidadesSerializer(entidad)
        return Response({'success': True, 'detail': 'Entidad', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- PgarIndicador ----------------------------------------

# Listar todos los indicadores

class PgarIndicadorList(generics.ListCreateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        indicadores = PgarIndicador.objects.all()
        serializer = PgarIndicadorSerializer(indicadores, many=True)
        return Response({'success': True, 'detail': 'Lista de indicadores', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un indicador

class PgarIndicadorCreate(generics.CreateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'descripcion_indicador' ya existe
        if PgarIndicador.objects.filter(descripcion_indicador=data['descripcion_indicador']).exists():
            return Response({'success': False, 'detail': 'Ya existe un indicador con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PgarIndicadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Indicador creado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Actualizar un indicador

class PgarIndicadorUpdate(generics.UpdateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            # Comprobar si el campo 'descripcion_indicador' ya existe
            if PgarIndicador.objects.filter(descripcion_indicador=data['descripcion_indicador']).exists():
                return Response({'success': False, 'detail': 'Ya existe un indicador con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
            indicador = PgarIndicador.objects.get(pk=pk)
        except PgarIndicador.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un indicador con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PgarIndicadorSerializer(indicador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Indicador actualizado correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar un indicador

class PgarIndicadorDelete(generics.DestroyAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            indicador = PgarIndicador.objects.get(pk=pk)
        except PgarIndicador.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un indicador con ese id'}, status=status.HTTP_404_NOT_FOUND)
        indicador.delete()
        return Response({'success': True, 'detail': 'Indicador eliminado correctamente'}, status=status.HTTP_200_OK)

# Listar un indicador por id

class PgarIndicadorId(generics.RetrieveAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            indicador = PgarIndicador.objects.get(pk=pk)
        except PgarIndicador.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un indicador con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PgarIndicadorSerializer(indicador)
        return Response({'success': True, 'detail': 'Indicador', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Actividad ----------------------------------------

# Listar todas las actividades

class ActividadList(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        actividades = Actividad.objects.all()
        serializer = ActividadSerializer(actividades, many=True)
        return Response({'success': True, 'detail': 'Lista de actividades', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear una actividad

class ActividadCreate(generics.CreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        # Comprobar si el campo 'descripcion_linea_base' ya existe
        if Actividad.objects.filter(descripcion_linea_base=data['descripcion_linea_base']).exists():
            return Response({'success': False, 'detail': 'Ya existe una actividad con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActividadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Actividad creada correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una actividad

class ActividadUpdate(generics.UpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            data = request.data
            # Comprobar si el campo 'descripcion_linea_base' ya existe
            if Actividad.objects.filter(descripcion_linea_base=data['descripcion_linea_base']).exists():
                return Response({'success': False, 'detail': 'Ya existe una actividad con esa descripcion'}, status=status.HTTP_400_BAD_REQUEST)

            actividad = Actividad.objects.get(pk=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una actividad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Actividad actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar una actividad

class ActividadDelete(generics.DestroyAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        try:
            actividad = Actividad.objects.get(pk=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una actividad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        actividad.delete()
        return Response({'success': True, 'detail': 'Actividad eliminada correctamente'}, status=status.HTTP_200_OK)

# Listar una actividad por id

class ActividadId(generics.RetrieveAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            actividad = Actividad.objects.get(pk=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una actividad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividad)
        return Response({'success': True, 'detail': 'Actividad', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar actividades por id de meta estrategica

class ActividadMetaEstrategicaId(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            actividades = Actividad.objects.filter(id_meta_estrategica=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existen actividades con ese id de meta estrategica'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividades, many=True)
        return Response({'success': True, 'detail': 'Lista de actividades', 'data': serializer.data}, status=status.HTTP_200_OK)


# Listar actividades por id indicador

class ActividadIndicadorId(generics.ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            actividades = Actividad.objects.filter(id_indicador=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existen actividades con ese id de indicador'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividades, many=True)
        return Response({'success': True, 'detail': 'Lista de actividades', 'data': serializer.data}, status=status.HTTP_200_OK)        

