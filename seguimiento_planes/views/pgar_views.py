from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
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
        return Response({'success': True, 'detail': 'Lista de planes de gestion ambiental regional', 'planes': serializer.data}, status=status.HTTP_200_OK)
    

# Crear un plan de gestion ambiental regional

class PlanGestionAmbientalRegionalCreate(generics.CreateAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PlanGestionAmbientalRegionalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Plan de gestion ambiental regional creado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Actualizar un plan de gestion ambiental regional

class PlanGestionAmbientalRegionalUpdate(generics.UpdateAPIView):
    queryset = PlanGestionAmbientalRegional.objects.all()
    serializer_class = PlanGestionAmbientalRegionalSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            plan = PlanGestionAmbientalRegional.objects.get(pk=pk)
        except PlanGestionAmbientalRegional.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un plan de gestion ambiental regional con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlanGestionAmbientalRegionalSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Plan de gestion ambiental regional actualizado correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Plan de gestion ambiental regional', 'planes': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Objetivo ----------------------------------------

# Listar todos los objetivos

class ObjetivoList(generics.ListCreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        objetivos = Objetivo.objects.all()
        serializer = ObjetivoSerializer(objetivos, many=True)
        return Response({'success': True, 'detail': 'Lista de objetivos', 'objetivos': serializer.data}, status=status.HTTP_200_OK)

# Crear un objetivo

class ObjetivoCreate(generics.CreateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ObjetivoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Objetivo creado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar un objetivo

class ObjetivoUpdate(generics.UpdateAPIView):
    queryset = Objetivo.objects.all()
    serializer_class = ObjetivoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            objetivo = Objetivo.objects.get(pk=pk)
        except Objetivo.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un objetivo con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ObjetivoSerializer(objetivo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Objetivo actualizado correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Objetivo', 'objetivos': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- LineaEstrategica ----------------------------------------

# Listar todas las lineas estrategicas

class LineaEstrategicaList(generics.ListCreateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        lineas_estrategicas = LineaEstrategica.objects.all()
        serializer = LineaEstrategicaSerializer(lineas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de lineas estrategicas', 'lineas_estrategicas': serializer.data}, status=status.HTTP_200_OK)
    
# Crear una linea estrategica

class LineaEstrategicaCreate(generics.CreateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LineaEstrategicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Linea estrategica creada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una linea estrategica

class LineaEstrategicaUpdate(generics.UpdateAPIView):
    queryset = LineaEstrategica.objects.all()
    serializer_class = LineaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            linea_estrategica = LineaEstrategica.objects.get(pk=pk)
        except LineaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una linea estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LineaEstrategicaSerializer(linea_estrategica, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Linea estrategica actualizada correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Linea estrategica', 'lineas_estrategicas': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- MetaEstrategica ----------------------------------------

# Listar todas las metas estrategicas

class MetaEstrategicaList(generics.ListCreateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        metas_estrategicas = MetaEstrategica.objects.all()
        serializer = MetaEstrategicaSerializer(metas_estrategicas, many=True)
        return Response({'success': True, 'detail': 'Lista de metas estrategicas', 'metas_estrategicas': serializer.data}, status=status.HTTP_200_OK)
    
# Crear una meta estrategica

class MetaEstrategicaCreate(generics.CreateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = MetaEstrategicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Meta estrategica creada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una meta estrategica

class MetaEstrategicaUpdate(generics.UpdateAPIView):
    queryset = MetaEstrategica.objects.all()
    serializer_class = MetaEstrategicaSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            meta_estrategica = MetaEstrategica.objects.get(pk=pk)
        except MetaEstrategica.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una meta estrategica con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MetaEstrategicaSerializer(meta_estrategica, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Meta estrategica actualizada correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Meta estrategica', 'metas_estrategicas': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Entidades ----------------------------------------

# Listar todas las entidades

class EntidadesList(generics.ListCreateAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        entidades = Entidades.objects.all()
        serializer = EntidadesSerializer(entidades, many=True)
        return Response({'success': True, 'detail': 'Lista de entidades', 'entidades': serializer.data}, status=status.HTTP_200_OK)

# Crear una entidad

class EntidadesCreate(generics.CreateAPIView):
    queryset = Entidades.objects.all()
    serializer_class = EntidadesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = EntidadesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Entidad creada correctamente'}, status=status.HTTP_201_CREATED)
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
        serializer = EntidadesSerializer(entidad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Entidad actualizada correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'success': True, 'detail': 'Entidad', 'entidades': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- PgarIndicador ----------------------------------------

# Listar todos los indicadores

class PgarIndicadorList(generics.ListCreateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        indicadores = PgarIndicador.objects.all()
        serializer = PgarIndicadorSerializer(indicadores, many=True)
        return Response({'success': True, 'detail': 'Lista de indicadores', 'indicadores': serializer.data}, status=status.HTTP_200_OK)

# Crear un indicador

class PgarIndicadorCreate(generics.CreateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PgarIndicadorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Indicador creado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Actualizar un indicador

class PgarIndicadorUpdate(generics.UpdateAPIView):
    queryset = PgarIndicador.objects.all()
    serializer_class = PgarIndicadorSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            indicador = PgarIndicador.objects.get(pk=pk)
        except PgarIndicador.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe un indicador con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PgarIndicadorSerializer(indicador, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Indicador actualizado correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Indicador', 'indicadores': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Actividad ----------------------------------------

# Listar todas las actividades

class ActividadList(generics.ListCreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        actividades = Actividad.objects.all()
        serializer = ActividadSerializer(actividades, many=True)
        return Response({'success': True, 'detail': 'Lista de actividades', 'actividades': serializer.data}, status=status.HTTP_200_OK)

# Crear una actividad

class ActividadCreate(generics.CreateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ActividadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Actividad creada correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar una actividad

class ActividadUpdate(generics.UpdateAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        try:
            actividad = Actividad.objects.get(pk=pk)
        except Actividad.DoesNotExist:
            return Response({'success': False, 'detail': 'No existe una actividad con ese id'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ActividadSerializer(actividad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Actividad actualizada correctamente'}, status=status.HTTP_200_OK)
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
        return Response({'success': True, 'detail': 'Actividad', 'actividades': serializer.data}, status=status.HTTP_200_OK)