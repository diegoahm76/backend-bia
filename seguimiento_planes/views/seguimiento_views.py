from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.serializers.expedientes_serializers import ArchivosDigitalesCreateSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguimiento_planes.serializers.seguimiento_serializer import FuenteRecursosPaaSerializerUpdate, FuenteFinanciacionIndicadoresSerializer, SectorSerializer, SectorSerializerUpdate, DetalleInversionCuentasSerializer, ModalidadSerializer, ModalidadSerializerUpdate, UbicacionesSerializer, UbicacionesSerializerUpdate, FuenteRecursosPaaSerializer, IntervaloSerializer, IntervaloSerializerUpdate, EstadoVFSerializer, EstadoVFSerializerUpdate, CodigosUNSPSerializer, CodigosUNSPSerializerUpdate, ConceptoPOAISerializer, FuenteFinanciacionSerializer, BancoProyectoSerializer, PlanAnualAdquisicionesSerializer, PAACodgigoUNSPSerializer, SeguimientoPAISerializer, SeguimientoPAIDocumentosSerializer
from seguimiento_planes.models.seguimiento_models import FuenteFinanciacionIndicadores, Sector, DetalleInversionCuentas, Modalidad, Ubicaciones, FuenteRecursosPaa, Intervalo, EstadoVF, CodigosUNSP, ConceptoPOAI, FuenteFinanciacion, BancoProyecto, PlanAnualAdquisiciones, PAACodgigoUNSP, SeguimientoPAI, SeguimientoPAIDocumentos

# ---------------------------------------- Fuentes de financiacion indicadores ----------------------------------------

# Listar todos los registros de fuentes de financiacion indicadores

class FuenteFinanciacionIndicadoresList(generics.ListAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteFinanciacionIndicadoresSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de financiacion indicadores

class FuenteFinanciacionIndicadoresCreate(generics.CreateAPIView):
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = FuenteFinanciacionIndicadoresSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el registro de fuente de financiación indicadores correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')        
# Actualizar un registro de fuente de financiacion indicadores

class FuenteFinanciacionIndicadoresUpdate(generics.UpdateAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        fuente = self.get_object()
        serializer = self.serializer_class(fuente, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se actualizó el registro de fuente de financiación indicadores correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')       

# Eliminar un registro de fuente de financiacion indicadores

class FuenteFinanciacionIndicadoresDelete(generics.DestroyAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return FuenteFinanciacionIndicadores.objects.get(pk=pk)
        except FuenteFinanciacionIndicadores.DoesNotExist:
            raise NotFound("No se encontró un registro de fuente de financiación indicadores con este ID.")

    def delete(self, request, pk):
        fuente = self.get_object(pk)
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de financiación indicadores correctamente.', 'data': []}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Sectores tabla básica ----------------------------------------

# Listar todos los registros de sectores

class SectorList(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        sectores = self.get_queryset()
        serializer = SectorSerializer(sectores, many=True)
        if not sectores:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de sector

class SectorCreate(generics.CreateAPIView):
    serializer_class = SectorSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = SectorSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de sector correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de sector

class SectorUpdate(generics.UpdateAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        sector = self.queryset.all().filter(id_sector=pk).first()
        if not sector:
            raise NotFound("No se encontró un registro de sector con este ID.")
        if sector.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if sector.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = SectorSerializerUpdate(sector, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de sector correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de sector

class SectorDelete(generics.DestroyAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        sector = self.queryset.all().filter(id_sector=pk).first()
        if not sector:
            raise NotFound("No se encontró un registro de sector con este ID.")
        if sector.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if sector.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        sector.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de sector correctamente.', 'data': []}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Detalle de Inversión Cuentas ----------------------------------------

# Listar todos los registros de detalle de inversión cuentas

class DetalleInversionCuentasList(generics.ListAPIView):
    queryset = DetalleInversionCuentas.objects.all()
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        detalle = self.get_queryset()
        serializer = DetalleInversionCuentasSerializer(detalle, many=True)
        if not detalle:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de detalle de inversión cuentas

class DetalleInversionCuentasCreate(generics.CreateAPIView):
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DetalleInversionCuentasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el registro de detalle de inversión cuentas correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')
    
# Actualizar un registro de detalle de inversión cuentas

class DetalleInversionCuentasUpdate(generics.UpdateAPIView):
    queryset = DetalleInversionCuentas.objects.all()
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        detalle = self.get_object()
        serializer = self.serializer_class(detalle, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de detalle de inversión cuentas correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
# Eliminar un registro de detalle de inversión cuentas

class DetalleInversionCuentasDelete(generics.DestroyAPIView):
    queryset = DetalleInversionCuentas.objects.all()
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return DetalleInversionCuentas.objects.get(pk=pk)
        except DetalleInversionCuentas.DoesNotExist:
            raise NotFound("No se encontró un registro de detalle de inversión cuentas con este ID.")

    def delete(self, request, pk):
        detalle = self.get_object(pk)
        detalle.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de detalle de inversión cuentas correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Modalidades tabla básica ----------------------------------------

# Listar todos los registros de modalidades

class ModalidadList(generics.ListAPIView):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        modalidades = self.get_queryset()
        serializer = ModalidadSerializer(modalidades, many=True)
        if not modalidades:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de modalidad

class ModalidadCreate(generics.CreateAPIView):
    serializer_class = ModalidadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = ModalidadSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de modalidad correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de modalidad

class ModalidadUpdate(generics.UpdateAPIView):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        modalidad = self.queryset.all().filter(id_modalidad=pk).first()
        if not modalidad:
            raise NotFound("No se encontró un registro de modalidad con este ID.")
        if modalidad.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if modalidad.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = ModalidadSerializerUpdate(modalidad, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de modalidad correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de modalidad

class ModalidadDelete(generics.DestroyAPIView):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        modalidad = self.queryset.all().filter(id_modalidad=pk).first()
        if not modalidad:
            raise NotFound("No se encontró un registro de modalidad con este ID.")
        if modalidad.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if modalidad.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        modalidad.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de modalidad correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Ubicaciones tabla básica ----------------------------------------

# Listar todos los registros de ubicaciones

class UbicacionesList(generics.ListAPIView):
    queryset = Ubicaciones.objects.all()
    serializer_class = UbicacionesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        ubicaciones = self.get_queryset()
        serializer = UbicacionesSerializer(ubicaciones, many=True)
        if not ubicaciones:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de ubicacion

class UbicacionesCreate(generics.CreateAPIView):
    serializer_class = UbicacionesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = UbicacionesSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de ubicación correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de ubicacion

class UbicacionesUpdate(generics.UpdateAPIView):
    queryset = Ubicaciones.objects.all()
    serializer_class = UbicacionesSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        ubicacion = self.queryset.all().filter(id_ubicacion=pk).first()
        if not ubicacion:
            raise NotFound("No se encontró un registro de ubicación con este ID.")
        if ubicacion.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if ubicacion.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = UbicacionesSerializerUpdate(ubicacion, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de ubicación correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de ubicacion

class UbicacionesDelete(generics.DestroyAPIView):
    queryset = Ubicaciones.objects.all()
    serializer_class = UbicacionesSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        ubicacion = self.queryset.all().filter(id_ubicacion=pk).first()
        if not ubicacion:
            raise NotFound("No se encontró un registro de ubicación con este ID.")
        if ubicacion.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if ubicacion.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        ubicacion.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de ubicación correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Fuentes de recursos PAA tabla básica----------------------------------------

# Listar todos los registros de fuentes de recursos PAA

class FuenteRecursosPaaList(generics.ListAPIView):
    queryset = FuenteRecursosPaa.objects.all()
    serializer_class = FuenteRecursosPaaSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteRecursosPaaSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de recursos PAA

class FuenteRecursosPaaCreate(generics.CreateAPIView):
    serializer_class = FuenteRecursosPaaSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = FuenteRecursosPaaSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de fuente de recursos PAA correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de fuente de recursos PAA

class FuenteRecursosPaaUpdate(generics.UpdateAPIView):
    queryset = FuenteRecursosPaa.objects.all()
    serializer_class = FuenteRecursosPaaSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        fuente = self.queryset.all().filter(id_fuente=pk).first()
        if not fuente:
            raise NotFound("No se encontró un registro de fuente de recursos PAA con este ID.")
        if fuente.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if fuente.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = FuenteRecursosPaaSerializerUpdate(fuente, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de fuente de recursos PAA correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de fuente de recursos PAA

class FuenteRecursosPaaDelete(generics.DestroyAPIView):
    queryset = FuenteRecursosPaa.objects.all()
    serializer_class = FuenteRecursosPaaSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        fuente = self.queryset.all().filter(id_fuente=pk).first()
        if not fuente:
            raise NotFound("No se encontró un registro de fuente de recursos PAA con este ID.")
        if fuente.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if fuente.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de recursos PAA correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Intervalos tabla básica ----------------------------------------

# Listar todos los registros de intervalos

class IntervaloList(generics.ListAPIView):
    queryset = Intervalo.objects.all()
    serializer_class = IntervaloSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        intervalos = self.get_queryset()
        serializer = IntervaloSerializer(intervalos, many=True)
        if not intervalos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de intervalo

class IntervaloCreate(generics.CreateAPIView):
    serializer_class = IntervaloSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = IntervaloSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de intervalo correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de intervalo

class IntervaloUpdate(generics.UpdateAPIView):
    queryset = Intervalo.objects.all()
    serializer_class = IntervaloSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        intervalo = self.queryset.all().filter(id_intervalo=pk).first()
        if not intervalo:
            raise NotFound("No se encontró un registro de intervalo con este ID.")
        if intervalo.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if intervalo.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = IntervaloSerializerUpdate(intervalo, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de intervalo correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de intervalo

class IntervaloDelete(generics.DestroyAPIView):
    queryset = Intervalo.objects.all()
    serializer_class = IntervaloSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        intervalo = self.queryset.all().filter(id_intervalo=pk).first()
        if not intervalo:
            raise NotFound("No se encontró un registro de intervalo con este ID.")
        if intervalo.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if intervalo.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        intervalo.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de intervalo correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Estados de validación de fuentes tabla básica ----------------------------------------

# Listar todos los registros de estados de validación de fuentes

class EstadoVFList(generics.ListAPIView):
    queryset = EstadoVF.objects.all()
    serializer_class = EstadoVFSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        estados = self.get_queryset()
        serializer = EstadoVFSerializer(estados, many=True)
        if not estados:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de estado de validación de fuentes

class EstadoVFCreate(generics.CreateAPIView):
    serializer_class = EstadoVFSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = EstadoVFSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de estado de validación de fuentes correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de estado de validación de fuentes

class EstadoVFUpdate(generics.UpdateAPIView):
    queryset = EstadoVF.objects.all()
    serializer_class = EstadoVFSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        estado = self.queryset.all().filter(id_estado=pk).first()
        if not estado:
            raise NotFound("No se encontró un registro de estado de validación de fuentes con este ID.")
        if estado.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if estado.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = EstadoVFSerializerUpdate(estado, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de estado de validación de fuentes correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de estado de validación de fuentes

class EstadoVFDelete(generics.DestroyAPIView):
    queryset = EstadoVF.objects.all()
    serializer_class = EstadoVFSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        estado = self.queryset.all().filter(id_estado=pk).first()
        if not estado:
            raise NotFound("No se encontró un registro de estado de validación de fuentes con este ID.")
        if estado.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if estado.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        estado.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de estado de validación de fuentes correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Códigos UNSP tabla básica ----------------------------------------

# Listar todos los registros de códigos UNSP

class CodigosUNSPList(generics.ListAPIView):
    queryset = CodigosUNSP.objects.all()
    serializer_class = CodigosUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        codigos = self.get_queryset()
        serializer = CodigosUNSPSerializer(codigos, many=True)
        if not codigos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de código UNSP

class CodigosUNSPCreate(generics.CreateAPIView):
    serializer_class = CodigosUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_in = request.data
        try:
            data_in['registro_precargado'] = False
            data_in['item_ya_usado'] = False
            data_in['activo'] = True
            serializer = CodigosUNSPSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)
        return Response({'success': True, 'detail': 'Se creó el registro de código UNSP correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Actualizar un registro de código UNSP

class CodigosUNSPUpdate(generics.UpdateAPIView):
    queryset = CodigosUNSP.objects.all()
    serializer_class = CodigosUNSPSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        codigo = self.queryset.all().filter(id_codigo=pk).first()
        if not codigo:
            raise NotFound("No se encontró un registro de código UNSP con este ID.")
        if codigo.item_ya_usado:
            raise ValidationError("No puedes actualizar este registro porque ya ha sido usado.")
        if codigo.registro_precargado:
            raise ValidationError("No puedes actualizar este registro porque es un registro precargado.")
        serializer = CodigosUNSPSerializerUpdate(codigo, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de código UNSP correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de código UNSP

class CodigosUNSPDelete(generics.DestroyAPIView):
    queryset = CodigosUNSP.objects.all()
    serializer_class = CodigosUNSPSerializerUpdate
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        codigo = self.queryset.all().filter(id_codigo=pk).first()
        if not codigo:
            raise NotFound("No se encontró un registro de código UNSP con este ID.")
        if codigo.item_ya_usado:
            raise ValidationError("No puedes eliminar este registro porque ya ha sido usado.")
        if codigo.registro_precargado:
            raise ValidationError("No puedes eliminar este registro porque es un registro precargado.")
        codigo.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de código UNSP correctamente.', 'data': []}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Conceptos POAI ----------------------------------------

# Listar todos los registros de conceptos POAI

class ConceptoPOAIList(generics.ListAPIView):
    queryset = ConceptoPOAI.objects.all()
    serializer_class = ConceptoPOAISerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        conceptos = self.get_queryset()
        serializer = ConceptoPOAISerializer(conceptos, many=True)
        if not conceptos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de concepto POAI

class ConceptoPOAICreate(generics.CreateAPIView):
    serializer_class = ConceptoPOAISerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ConceptoPOAISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el registro de concepto POAI correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# Actualizar un registro de concepto POAI

class ConceptoPOAIUpdate(generics.UpdateAPIView):
    queryset = ConceptoPOAI.objects.all()
    serializer_class = ConceptoPOAISerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        concepto = self.get_object()
        serializer = self.serializer_class(concepto, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de concepto POAI correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de concepto POAI

class ConceptoPOAIDelete(generics.DestroyAPIView):
    queryset = ConceptoPOAI.objects.all()
    serializer_class = ConceptoPOAISerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return ConceptoPOAI.objects.get(pk=pk)
        except ConceptoPOAI.DoesNotExist:
            raise NotFound("No se encontró un registro de concepto POAI con este ID.")

    def delete(self, request, pk):
        concepto = self.get_object(pk)
        concepto.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de concepto POAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Fuentes de financiación ----------------------------------------

# Listar todos los registros de fuentes de financiación

class FuenteFinanciacionList(generics.ListAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteFinanciacionSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de financiación

class FuenteFinanciacionCreate(generics.CreateAPIView):
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = FuenteFinanciacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el registro de fuente de financiación correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# Actualizar un registro de fuente de financiación

class FuenteFinanciacionUpdate(generics.UpdateAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        fuente = self.get_object()
        serializer = self.serializer_class(fuente, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de fuente de financiación correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de fuente de financiación

class FuenteFinanciacionDelete(generics.DestroyAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return FuenteFinanciacion.objects.get(pk=pk)
        except FuenteFinanciacion.DoesNotExist:
            raise NotFound("No se encontró un registro de fuente de financiación con este ID.")

    def delete(self, request, pk):
        fuente = self.get_object(pk)
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de financiación correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Fuentes de financiación  ----------------------------------------

# Listar todos los registros de fuentes de financiación 

class FuenteFinanciacionList(generics.ListAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteFinanciacionSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros de fuentes de financiación:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de financiación

class FuenteFinanciacionCreate(generics.CreateAPIView):
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = FuenteFinanciacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el registro de fuente de financiación correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# Actualizar un registro de fuente de financiación

class FuenteFinanciacionUpdate(generics.UpdateAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        fuente = self.get_object()
        serializer = self.serializer_class(fuente, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el registro de fuente de financiación correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de fuente de financiación

class FuenteFinanciacionDelete(generics.DestroyAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return FuenteFinanciacion.objects.get(pk=pk)
        except FuenteFinanciacion.DoesNotExist:
            raise NotFound("No se encontró un registro de fuente de financiación con este ID.")

    def delete(self, request, pk):
        fuente = self.get_object(pk)
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de financiación correctamente.', 'data': []}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Banco Proyecto ----------------------------------------

# Listar todos los registros de bancos de proyecto

class BancoProyectoList(generics.ListAPIView):
    queryset = BancoProyecto.objects.all()
    serializer_class = BancoProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        bancos = self.get_queryset()
        serializer = BancoProyectoSerializer(bancos, many=True)
        if not bancos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes bancos de proyecto:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de banco de proyecto

class BancoProyectoCreate(generics.CreateAPIView):
    serializer_class = BancoProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = BancoProyectoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el banco de proyecto correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# Actualizar un registro de banco de proyecto

class BancoProyectoUpdate(generics.UpdateAPIView):
    queryset = BancoProyecto.objects.all()
    serializer_class = BancoProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        banco = self.get_object()
        serializer = self.serializer_class(banco, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el banco de proyecto correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de banco de proyecto

class BancoProyectoDelete(generics.DestroyAPIView):
    queryset = BancoProyecto.objects.all()
    serializer_class = BancoProyectoSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return BancoProyecto.objects.get(pk=pk)
        except BancoProyecto.DoesNotExist:
            raise NotFound("No se encontró un banco de proyecto con este ID.")

    def delete(self, request, pk):
        banco = self.get_object(pk)
        banco.delete()
        return Response({'success': True, 'detail': 'Se eliminó el banco de proyecto correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Plan Anual de adquisiciones ----------------------------------------

# Listar todos los registros de planes anuales de adquisiciones

class PlanAnualAdquisicionesList(generics.ListAPIView):
    queryset = PlanAnualAdquisiciones.objects.all()
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        planes = self.get_queryset()
        serializer = PlanAnualAdquisicionesSerializer(planes, many=True)
        if not planes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes planes anuales de adquisiciones:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de plan anual de adquisiciones

class PlanAnualAdquisicionesCreate(generics.CreateAPIView):
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PlanAnualAdquisicionesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el plan anual de adquisiciones correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')
    
# Actualizar un registro de plan anual de adquisiciones

class PlanAnualAdquisicionesUpdate(generics.UpdateAPIView):
    queryset = PlanAnualAdquisiciones.objects.all()
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        plan = self.get_object()
        serializer = self.serializer_class(plan, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el plan anual de adquisiciones correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de plan anual de adquisiciones

class PlanAnualAdquisicionesDelete(generics.DestroyAPIView):
    queryset = PlanAnualAdquisiciones.objects.all()
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return PlanAnualAdquisiciones.objects.get(pk=pk)
        except PlanAnualAdquisiciones.DoesNotExist:
            raise NotFound("No se encontró un plan anual de adquisiciones con este ID.")

    def delete(self, request, pk):
        plan = self.get_object(pk)
        plan.delete()
        return Response({'success': True, 'detail': 'Se eliminó el plan anual de adquisiciones correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- PAA CodgigoUNSP ----------------------------------------

# Listar todos los registros de PAA CodgigoUNSP

class PAACodUNSPList(generics.ListAPIView):
    queryset = PAACodgigoUNSP.objects.all()
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        paas = self.get_queryset()
        serializer = PAACodgigoUNSPSerializer(paas, many=True)
        if not paas:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes PAA CodgigoUNSP:', 'data': serializer.data}, status=status.HTTP_200_OK)


# Crear un registro de PAA CodgigoUNSP

class PAACodUNSPCreate(generics.CreateAPIView):
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PAACodgigoUNSPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el PAA CodgigoUNSP correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')
    
# Actualizar un registro de PAA CodgigoUNSP

class PAACodUNSPUpdate(generics.UpdateAPIView):
    queryset = PAACodgigoUNSP.objects.all()
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        paa = self.get_object()
        serializer = self.serializer_class(paa, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el PAA CodgigoUNSP correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de PAA CodgigoUNSP

class PAACodUNSPDelete(generics.DestroyAPIView):
    queryset = PAACodgigoUNSP.objects.all()
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return PAACodgigoUNSP.objects.get(pk=pk)
        except PAACodgigoUNSP.DoesNotExist:
            raise NotFound("No se encontró un PAA CodgigoUNSP con este ID.")

    def delete(self, request, pk):
        paa = self.get_object(pk)
        paa.delete()
        return Response({'success': True, 'detail': 'Se eliminó el PAA CodgigoUNSP correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Seguimiento PAI ----------------------------------------

# Listar todos los registros de seguimiento PAI

class SeguimientoPAIList(generics.ListAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        seguimientos = self.get_queryset()
        serializer = SeguimientoPAISerializer(seguimientos, many=True)
        if not seguimientos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos PAI:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de seguimiento PAI

class SeguimientoPAICreate(generics.CreateAPIView):
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = SeguimientoPAISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el seguimiento PAI correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# Actualizar un registro de seguimiento PAI

class SeguimientoPAIUpdate(generics.UpdateAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        seguimiento = self.get_object()
        serializer = self.serializer_class(seguimiento, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el seguimiento PAI correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de seguimiento PAI

class SeguimientoPAIDelete(generics.DestroyAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return SeguimientoPAI.objects.get(pk=pk)
        except SeguimientoPAI.DoesNotExist:
            raise NotFound("No se encontró un seguimiento PAI con este ID.")

    def delete(self, request, pk):
        seguimiento = self.get_object(pk)
        seguimiento.delete()
        return Response({'success': True, 'detail': 'Se eliminó el seguimiento PAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Seguimiento PAI ----------------------------------------

# Listar todos los registros de seguimiento PAI

class SeguimientoPAIList(generics.ListAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        seguimientos = self.get_queryset()
        serializer = SeguimientoPAISerializer(seguimientos, many=True)
        if not seguimientos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos PAI:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de seguimiento PAI

class SeguimientoPAICreate(generics.CreateAPIView):
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = SeguimientoPAISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Se creó el seguimiento PAI correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Imprime los errores de validación
            raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')
    
# Actualizar un registro de seguimiento PAI

class SeguimientoPAIUpdate(generics.UpdateAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        seguimiento = self.get_object()
        serializer = self.serializer_class(seguimiento, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el seguimiento PAI correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de seguimiento PAI

class SeguimientoPAIDelete(generics.DestroyAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return SeguimientoPAI.objects.get(pk=pk)
        except SeguimientoPAI.DoesNotExist:
            raise NotFound("No se encontró un seguimiento PAI con este ID.")

    def delete(self, request, pk):
        seguimiento = self.get_object(pk)
        seguimiento.delete()
        return Response({'success': True, 'detail': 'Se eliminó el seguimiento PAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# ---------------------------------------- Seguimiento PAI Documentos ----------------------------------------

# Listar todos los registros de seguimiento PAI documentos

class SeguimientoPAIDocumentosList(generics.ListAPIView):
    queryset = SeguimientoPAIDocumentos.objects.all()
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = (IsAuthenticated,)
    serializer_archivo = ArchivosDigitalesCreateSerializer
    def get(self, request):
        documentos = self.get_queryset()
        data_respuesta=[]
        for documento in documentos:
            archivo = ArchivosDigitales.objects.filter(id_archivo_digital=documento.id_archivo_digital.id_archivo_digital).first()
            serializer_archivo = self.serializer_archivo(archivo)
            data_respuesta.append({'data':self.serializer_class(documento).data,'archivo':serializer_archivo.data})
            
        #serializer = self.serializer_class(documentos, many=True)
        if not documentos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes documentos de seguimiento PAI:', 'data': data_respuesta}, status=status.HTTP_200_OK)

# Crear un registro de seguimiento PAI documentos

class SeguimientoPAIDocumentosCreate(generics.CreateAPIView):
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = (IsAuthenticated,)
    vista_archivos = ArchivosDgitalesCreate()
    def post(self, request):
        data_seguimiento_documentos=[]
        id_seguimiento = request.data['id_seguimiento_pai']
        archivos =request.FILES.getlist('archivo')
        id_archivos=[]
        for archivo in archivos:
            respuesta_archivo=self.vista_archivos.crear_archivo({'es_Doc_elec_archivo':False},archivo)
            
            if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                return respuesta_archivo
            data_archivo = respuesta_archivo.data['data']
            id_archivos.append(data_archivo)
            
        for id_archivo in id_archivos:
            serializer = self.serializer_class(data={'id_seguimiento_pai':id_seguimiento,'id_archivo_digital':id_archivo['id_archivo_digital']})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data_seguimiento_documentos.append({'data':serializer.data,'archivo':id_archivo})


       
        return Response({'success': True, 'detail': 'Se creó el documento de seguimiento PAI correctamente.', 'data': data_seguimiento_documentos}, status=status.HTTP_201_CREATED)
        
# Actualizar un registro de seguimiento PAI documentos

class SeguimientoPAIDocumentosUpdate(generics.UpdateAPIView):
    queryset = SeguimientoPAIDocumentos.objects.all()
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        data = request.data
        documento = self.get_object()
        serializer = self.serializer_class(documento, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail': 'Se actualizó el documento de seguimiento PAI correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# Eliminar un registro de seguimiento PAI documentos

class SeguimientoPAIDocumentosDelete(generics.DestroyAPIView):
    queryset = SeguimientoPAIDocumentos.objects.all()
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return SeguimientoPAIDocumentos.objects.get(pk=pk)
        except SeguimientoPAIDocumentos.DoesNotExist:
            raise NotFound("No se encontró un documento de seguimiento PAI con este ID.")

    def delete(self, request, pk):
        documento = self.get_object(pk)
        documento.delete()
        return Response({'success': True, 'detail': 'Se eliminó el documento de seguimiento PAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Listar Seguimiento PAI documentos por id seguimiento

class SeguimientoPAIDocumentosListIdSeguimiento(generics.ListAPIView):
    queryset = SeguimientoPAIDocumentos.objects.all()
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = (IsAuthenticated,)
    serializer_archivo = ArchivosDigitalesCreateSerializer
    def get(self, request,id_seguimiento):
        documentos = self.get_queryset().filter(id_seguimiento_pai=id_seguimiento)
        data_respuesta=[]
        for documento in documentos:
            archivo = ArchivosDigitales.objects.filter(id_archivo_digital=documento.id_archivo_digital.id_archivo_digital).first()
            serializer_archivo = self.serializer_archivo(archivo)
            data_respuesta.append({'data':self.serializer_class(documento).data,'archivo':serializer_archivo.data})
            
        #serializer = self.serializer_class(documentos, many=True)
        if not documentos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes documentos de seguimiento PAI:', 'data': data_respuesta}, status=status.HTTP_200_OK)