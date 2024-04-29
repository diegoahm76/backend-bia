from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.serializers.expedientes_serializers import ArchivosDigitalesCreateSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguimiento_planes.models.planes_models import Sector
from seguimiento_planes.serializers.seguimiento_serializer import FuenteRecursosPaaSerializerUpdate, FuenteFinanciacionIndicadoresSerializer, SectorSerializer, SectorSerializerUpdate, DetalleInversionCuentasSerializer, ModalidadSerializer, ModalidadSerializerUpdate, UbicacionesSerializer, UbicacionesSerializerUpdate, FuenteRecursosPaaSerializer, IntervaloSerializer, IntervaloSerializerUpdate, EstadoVFSerializer, EstadoVFSerializerUpdate, CodigosUNSPSerializer, CodigosUNSPSerializerUpdate, ConceptoPOAISerializer, FuenteFinanciacionSerializer, BancoProyectoSerializer, PlanAnualAdquisicionesSerializer, PAACodgigoUNSPSerializer, SeguimientoPAISerializer, SeguimientoPAIDocumentosSerializer
from seguimiento_planes.models.seguimiento_models import FuenteFinanciacionIndicadores, DetalleInversionCuentas, Modalidad, Ubicaciones, FuenteRecursosPaa, Intervalo, EstadoVF, CodigosUNSP, ConceptoPOAI, FuenteFinanciacion, BancoProyecto, PlanAnualAdquisiciones, PAACodgigoUNSP, SeguimientoPAI, SeguimientoPAIDocumentos
from seguimiento_planes.models.planes_models import Metas, Rubro
from seguridad.permissions.permissions_planes import PermisoActualizarBancoProyectos, PermisoActualizarCodigosUnspsc, PermisoActualizarConceptoPOAI, PermisoActualizarDetalleInversionCuentas, PermisoActualizarEstadosVigenciaFutura, PermisoActualizarFuenteFinanciacionPOAI, PermisoActualizarFuentesFinanciacionIndicadores, PermisoActualizarFuentesFinanciacionPAA, PermisoActualizarIntervalos, PermisoActualizarModalidades, PermisoActualizarPlanAnualAdquisiciones, PermisoActualizarSector, PermisoActualizarSeguimientoTecnicoPAI, PermisoActualizarUbicaciones, PermisoBorrarCodigosUnspsc, PermisoBorrarEstadosVigenciaFutura, PermisoBorrarFuentesFinanciacionPAA, PermisoBorrarIntervalos, PermisoBorrarModalidades, PermisoBorrarSector, PermisoBorrarUbicaciones, PermisoCrearBancoProyectos, PermisoCrearCodigosUnspsc, PermisoCrearConceptoPOAI, PermisoCrearDetalleInversionCuentas, PermisoCrearEstadosVigenciaFutura, PermisoCrearFuenteFinanciacionPOAI, PermisoCrearFuentesFinanciacionIndicadores, PermisoCrearFuentesFinanciacionPAA, PermisoCrearIntervalos, PermisoCrearModalidades, PermisoCrearPlanAnualAdquisiciones, PermisoCrearSector, PermisoCrearSeguimientoTecnicoPAI, PermisoCrearUbicaciones, PermisoCrearSeguimientoPOAI, PermisoActualizarSeguimientoPOAI

# ---------------------------------------- Fuentes de financiacion indicadores ----------------------------------------

# Listar todos los registros de fuentes de financiacion indicadores

class FuenteFinanciacionIndicadoresList(generics.ListAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        fuentes = self.get_queryset().filter(id_meta=pk)
        serializer = FuenteFinanciacionIndicadoresSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de financiacion indicadores

class FuenteFinanciacionIndicadoresCreate(generics.CreateAPIView):
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = [IsAuthenticated, PermisoCrearFuentesFinanciacionIndicadores]

    def post(self, request):
        fuentes = FuenteFinanciacionIndicadores.objects.filter(id_meta=request.data['id_meta'])
        meta = Metas.objects.filter(id_meta=request.data['id_meta']).first()

        if meta == None:
            raise ValidationError("No se encontró una meta con este ID.")

        valor_fuentes = 0
        valor_total = 0
        for fuente in fuentes:
            valor_fuentes = valor_fuentes + fuente.valor_total
        valor_total = valor_fuentes + request.data['valor_total']
        

        if valor_total > int(meta.valor_meta):
            raise ValidationError("El valor total de las fuentes de financiación no puede ser mayor al valor de la meta.")


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
    permission_classes = [IsAuthenticated, PermisoActualizarFuentesFinanciacionIndicadores]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FuenteFinanciacionIndicadores.objects.get(pk=pk)
        except FuenteFinanciacionIndicadores.DoesNotExist:
            raise NotFound("No se encontró un registro de fuente de financiación indicadores con este ID.")

    def delete(self, request, pk):
        fuente = self.get_object(pk)
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de financiación indicadores correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Busqueda avanzada de fuentes de financiacion indicadores por nombre fuente, nombre proyecto, nombre producto, nombre actividad, nombre indicador
    
class BusquedaAvanzadaFuentesFinanciacionIndicadores(generics.ListAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nombre_fuente = request.GET.get('nombre_fuente')
        nombre_proyecto = request.GET.get('nombre_proyecto')
        nombre_producto = request.GET.get('nombre_producto')
        nombre_actividad = request.GET.get('nombre_actividad')
        nombre_indicador = request.GET.get('nombre_indicador')
        if nombre_fuente:
            fuentes = self.queryset.filter(nombre_fuente__icontains=nombre_fuente)
        elif nombre_proyecto:
            fuentes = self.queryset.filter(nombre_proyecto__icontains=nombre_proyecto)
        elif nombre_producto:
            fuentes = self.queryset.filter(nombre_producto__icontains=nombre_producto)
        elif nombre_actividad:
            fuentes = self.queryset.filter(nombre_actividad__icontains=nombre_actividad)
        elif nombre_indicador:
            fuentes = self.queryset.filter(nombre_indicador__icontains=nombre_indicador)
        else:
            fuentes = self.queryset.all()
        serializer = FuenteFinanciacionIndicadoresSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar todos los registros de fuentes de financiacion indicadores por id_indicador

class FuenteFinanciacionIndicadoresPorIndicadorList(generics.ListAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_indicador = request.GET.get('id_indicador')
        if id_indicador:
            fuentes = self.queryset.filter(id_indicador=id_indicador)
        else:
            raise ValidationError("No se proporcionó el ID del indicador.")
        serializer = FuenteFinanciacionIndicadoresSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Listar todos los registros de fuentes de financiacion indicadores por id_meta

class FuenteFinanciacionIndicadoresPorMetaList(generics.ListAPIView):
    queryset = FuenteFinanciacionIndicadores.objects.all()
    serializer_class = FuenteFinanciacionIndicadoresSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_meta = request.GET.get('id_meta')
        if id_meta:
            fuentes = self.queryset.filter(id_meta=id_meta)
        else:
            raise ValidationError("No se proporcionó el ID de la meta.")
        serializer = FuenteFinanciacionIndicadoresSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Sectores tabla básica ----------------------------------------

# Listar todos los registros de sectores

class SectorList(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sectores = self.get_queryset()
        serializer = SectorSerializer(sectores, many=True)
        if not sectores:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de sector

class SectorCreate(generics.CreateAPIView):
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSector]

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
    permission_classes = [IsAuthenticated, PermisoActualizarSector]

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
    permission_classes = [IsAuthenticated, PermisoBorrarSector]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        detalle = self.get_queryset()
        serializer = DetalleInversionCuentasSerializer(detalle, many=True)
        if not detalle:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de detalle de inversión cuentas

class DetalleInversionCuentasCreate(generics.CreateAPIView):
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = [IsAuthenticated, PermisoCrearDetalleInversionCuentas]

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
    permission_classes = [IsAuthenticated, PermisoActualizarDetalleInversionCuentas]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return DetalleInversionCuentas.objects.get(pk=pk)
        except DetalleInversionCuentas.DoesNotExist:
            raise NotFound("No se encontró un registro de detalle de inversión cuentas con este ID.")

    def delete(self, request, pk):
        detalle = self.get_object(pk)
        detalle.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de detalle de inversión cuentas correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Busqueda avanzada de detalle de inversión cuentas por cuenta, nombre programa, nombre subprograma, nombre proyecto, nombre actividad, nombre indicador

class BusquedaAvanzadaDetalleInversionCuentas(generics.ListAPIView):
    queryset = DetalleInversionCuentas.objects.all()
    serializer_class = DetalleInversionCuentasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuenta = request.GET.get('cuenta')
        nombre_programa = request.GET.get('nombre_programa')
        nombre_subprograma = request.GET.get('nombre_subprograma')
        nombre_proyecto = request.GET.get('nombre_proyecto')
        nombre_actividad = request.GET.get('nombre_actividad')
        nombre_indicador = request.GET.get('nombre_indicador')
        if cuenta:
            detalle = self.queryset.filter(cuenta__icontains=cuenta)
        elif nombre_programa:
            detalle = self.queryset.filter(nombre_programa__icontains=nombre_programa)
        elif nombre_subprograma:
            detalle = self.queryset.filter(nombre_subprograma__icontains=nombre_subprograma)
        elif nombre_proyecto:
            detalle = self.queryset.filter(nombre_proyecto__icontains=nombre_proyecto)
        elif nombre_actividad:
            detalle = self.queryset.filter(nombre_actividad__icontains=nombre_actividad)
        elif nombre_indicador:
            detalle = self.queryset.filter(nombre_indicador__icontains=nombre_indicador)
        else:
            detalle = self.queryset.all()
        serializer = DetalleInversionCuentasSerializer(detalle, many=True)
        if not detalle:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Modalidades tabla básica ----------------------------------------

# Listar todos los registros de modalidades

class ModalidadList(generics.ListAPIView):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        modalidades = self.get_queryset()
        serializer = ModalidadSerializer(modalidades, many=True)
        if not modalidades:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de modalidad

class ModalidadCreate(generics.CreateAPIView):
    serializer_class = ModalidadSerializer
    permission_classes = [IsAuthenticated, PermisoCrearModalidades]

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
    permission_classes = [IsAuthenticated, PermisoActualizarModalidades]

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
    permission_classes = [IsAuthenticated, PermisoBorrarModalidades]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ubicaciones = self.get_queryset()
        serializer = UbicacionesSerializer(ubicaciones, many=True)
        if not ubicaciones:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de ubicacion

class UbicacionesCreate(generics.CreateAPIView):
    serializer_class = UbicacionesSerializer
    permission_classes = [IsAuthenticated, PermisoCrearUbicaciones]

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
    permission_classes = [IsAuthenticated, PermisoActualizarUbicaciones]

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
    permission_classes = [IsAuthenticated, PermisoBorrarUbicaciones]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteRecursosPaaSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de recursos PAA

class FuenteRecursosPaaCreate(generics.CreateAPIView):
    serializer_class = FuenteRecursosPaaSerializer
    permission_classes = [IsAuthenticated, PermisoCrearFuentesFinanciacionPAA]

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
    permission_classes = [IsAuthenticated, PermisoActualizarFuentesFinanciacionPAA]

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
    permission_classes = [IsAuthenticated, PermisoBorrarFuentesFinanciacionPAA]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        intervalos = self.get_queryset()
        serializer = IntervaloSerializer(intervalos, many=True)
        if not intervalos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de intervalo

class IntervaloCreate(generics.CreateAPIView):
    serializer_class = IntervaloSerializer
    permission_classes = [IsAuthenticated, PermisoCrearIntervalos]

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
    permission_classes = [IsAuthenticated, PermisoActualizarIntervalos]

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
    permission_classes = [IsAuthenticated, PermisoBorrarIntervalos]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estados = self.get_queryset()
        serializer = EstadoVFSerializer(estados, many=True)
        if not estados:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de estado de validación de fuentes

class EstadoVFCreate(generics.CreateAPIView):
    serializer_class = EstadoVFSerializer
    permission_classes = [IsAuthenticated, PermisoCrearEstadosVigenciaFutura]

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
    permission_classes = [IsAuthenticated, PermisoActualizarEstadosVigenciaFutura]

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
    permission_classes = [IsAuthenticated, PermisoBorrarEstadosVigenciaFutura]

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

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class CodigosUNSPList(generics.ListAPIView):
    serializer_class = CodigosUNSPSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        codigos = CodigosUNSP.objects.all()
        nombre = request.query_params.get('nombre')
        codigo = request.query_params.get('codigo')
        if codigo:
            codigos = CodigosUNSP.objects.filter(codigo_unsp__icontains = codigo)
        if nombre:
            codigos = CodigosUNSP.objects.filter(nombre_producto_unsp__icontains = nombre)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(codigos, request)
        if page is not None:
            serializer = CodigosUNSPSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CodigosUNSPSerializer(codigos, many=True)
        return Response(serializer.data)
    
# Crear un registro de código UNSP

class CodigosUNSPCreate(generics.CreateAPIView):
    serializer_class = CodigosUNSPSerializer
    permission_classes = [IsAuthenticated, PermisoCrearCodigosUnspsc]

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
    permission_classes = [IsAuthenticated, PermisoActualizarCodigosUnspsc]

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
    permission_classes = [IsAuthenticated, PermisoBorrarCodigosUnspsc]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conceptos = self.get_queryset()
        serializer = ConceptoPOAISerializer(conceptos, many=True)
        if not conceptos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de concepto POAI

class ConceptoPOAICreate(generics.CreateAPIView):
    serializer_class = ConceptoPOAISerializer
    permission_classes = [IsAuthenticated, PermisoCrearConceptoPOAI]

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
    permission_classes = [IsAuthenticated, PermisoActualizarConceptoPOAI]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ConceptoPOAI.objects.get(pk=pk)
        except ConceptoPOAI.DoesNotExist:
            raise NotFound("No se encontró un registro de concepto POAI con este ID.")

    def delete(self, request, pk):
        concepto = self.get_object(pk)
        concepto.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de concepto POAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# busqueda avanzada de conceptos POAI por concepto, nombre y nombre indicador

class BusquedaAvanzadaConceptoPOAI(generics.ListAPIView):
    queryset = ConceptoPOAI.objects.all()
    serializer_class = ConceptoPOAISerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        concepto = request.GET.get('concepto')
        nombre = request.GET.get('nombre')
        nombre_indicador = request.GET.get('nombre_indicador')
        if concepto:
            conceptos = self.queryset.filter(concepto__icontains=concepto)
        elif nombre:
            conceptos = self.queryset.filter(nombre__icontains=nombre)
        elif nombre_indicador:
            conceptos = self.queryset.filter(nombre_indicador__icontains=nombre_indicador)
        else:
            conceptos = self.queryset.all()
        serializer = ConceptoPOAISerializer(conceptos, many=True)
        if not conceptos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros de conceptos POAI:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Fuentes de financiación ----------------------------------------

# Listar todos los registros de fuentes de financiación

class FuenteFinanciacionList(generics.ListAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fuentes = self.get_queryset()
        serializer = FuenteFinanciacionSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de fuente de financiación

class FuenteFinanciacionCreate(generics.CreateAPIView):
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = [IsAuthenticated, PermisoCrearFuenteFinanciacionPOAI]

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
    permission_classes = [IsAuthenticated, PermisoActualizarFuenteFinanciacionPOAI]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FuenteFinanciacion.objects.get(pk=pk)
        except FuenteFinanciacion.DoesNotExist:
            raise NotFound("No se encontró un registro de fuente de financiación con este ID.")

    def delete(self, request, pk):
        fuente = self.get_object(pk)
        fuente.delete()
        return Response({'success': True, 'detail': 'Se eliminó el registro de fuente de financiación correctamente.', 'data': []}, status=status.HTTP_200_OK)

#Busqueda Avanzada de fuentes de financiación por nombre_fuente, concepto

class BusquedaAvanzadaFuenteFinanciacion(generics.ListAPIView):
    queryset = FuenteFinanciacion.objects.all()
    serializer_class = FuenteFinanciacionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nombre_fuente = request.GET.get('nombre_fuente')
        concepto = request.GET.get('concepto')
        if nombre_fuente:
            fuentes = self.queryset.filter(nombre_fuente__icontains=nombre_fuente)
        elif concepto:
            fuentes = self.queryset.filter(concepto__icontains=concepto)
        else:
            fuentes = self.queryset.all()
        serializer = FuenteFinanciacionSerializer(fuentes, many=True)
        if not fuentes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros de fuentes de financiación:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# ---------------------------------------- Banco Proyecto ----------------------------------------

# Listar todos los registros de bancos de proyecto

class BancoProyectoList(generics.ListAPIView):
    queryset = BancoProyecto.objects.all()
    serializer_class = BancoProyectoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        bancos = self.get_queryset().filter(id_meta=pk)
        serializer = BancoProyectoSerializer(bancos, many=True)
        if not bancos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes bancos de proyecto:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Crear un registro de banco de proyecto

class BancoProyectoCreate(generics.CreateAPIView):
    serializer_class = BancoProyectoSerializer
    permission_classes = [IsAuthenticated, PermisoCrearBancoProyectos]

    def post(self, request):
        rubro = Rubro.objects.get(id_rubro=request.data['id_rubro'])

        if request.data['banco_valor'] > rubro.valcuenta:
            raise ValidationError('El valor del banco de proyecto no puede ser mayor al valor de la cuenta del rubro.')

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
    permission_classes = [IsAuthenticated, PermisoActualizarBancoProyectos]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return BancoProyecto.objects.get(pk=pk)
        except BancoProyecto.DoesNotExist:
            raise NotFound("No se encontró un banco de proyecto con este ID.")

    def delete(self, request, pk):
        banco = self.get_object(pk)
        banco.delete()
        return Response({'success': True, 'detail': 'Se eliminó el banco de proyecto correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Busqueda avanzada banco proyecto por objeto_contrato, nombre_proyecto, nombre_actividad, nombre_indicador y nombre_meta
    
class BusquedaAvanzadaBancoProyecto(generics.ListAPIView):
    queryset = BancoProyecto.objects.all()
    serializer_class = BancoProyectoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        objeto_contrato = request.GET.get('objeto_contrato')
        nombre_proyecto = request.GET.get('nombre_proyecto')
        nombre_actividad = request.GET.get('nombre_actividad')
        nombre_indicador = request.GET.get('nombre_indicador')
        nombre_meta = request.GET.get('nombre_meta')
        if objeto_contrato:
            bancos = self.queryset.filter(objeto_contrato__icontains=objeto_contrato)
        elif nombre_proyecto:
            bancos = self.queryset.filter(nombre_proyecto__icontains=nombre_proyecto)
        elif nombre_actividad:
            bancos = self.queryset.filter(nombre_actividad__icontains=nombre_actividad)
        elif nombre_indicador:
            bancos = self.queryset.filter(nombre_indicador__icontains=nombre_indicador)
        elif nombre_meta:
            bancos = self.queryset.filter(nombre_meta__icontains=nombre_meta)
        else:
            bancos = self.queryset.all()
        serializer = BancoProyectoSerializer(bancos, many=True)
        if not bancos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes bancos de proyecto:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Plan Anual de adquisiciones ----------------------------------------

# Listar todos los registros de planes anuales de adquisiciones

class PlanAnualAdquisicionesList(generics.ListAPIView):
    queryset = PlanAnualAdquisiciones.objects.all()
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        planes = self.get_queryset()
        serializer = PlanAnualAdquisicionesSerializer(planes, many=True)
        if not planes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes planes anuales de adquisiciones:', 'data': serializer.data}, status=status.HTTP_200_OK)

# Crear un registro de plan anual de adquisiciones

class PlanAnualAdquisicionesCreate(generics.CreateAPIView):
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = [IsAuthenticated, PermisoCrearPlanAnualAdquisiciones]

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
    permission_classes = [IsAuthenticated, PermisoActualizarPlanAnualAdquisiciones]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return PlanAnualAdquisiciones.objects.get(pk=pk)
        except PlanAnualAdquisiciones.DoesNotExist:
            raise NotFound("No se encontró un plan anual de adquisiciones con este ID.")

    def delete(self, request, pk):
        plan = self.get_object(pk)
        plan.delete()
        return Response({'success': True, 'detail': 'Se eliminó el plan anual de adquisiciones correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Busqueda avanzada de planes anuales de adquisiciones por descripcion, nombre_plan, nombre_modalidad, nombre_fuente, nombre_unidad

class BusquedaAvanzadaPlanAnualAdquisiciones(generics.ListAPIView):
    queryset = PlanAnualAdquisiciones.objects.all()
    serializer_class = PlanAnualAdquisicionesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        descripcion = request.GET.get('descripcion')
        nombre_plan = request.GET.get('nombre_plan')
        nombre_modalidad = request.GET.get('nombre_modalidad')
        nombre_fuente = request.GET.get('nombre_fuente')
        nombre_unidad = request.GET.get('nombre_unidad')
        if descripcion:
            planes = self.queryset.filter(descripcion__icontains=descripcion)
        elif nombre_plan:
            planes = self.queryset.filter(nombre_plan__icontains=nombre_plan)
        elif nombre_modalidad:
            planes = self.queryset.filter(nombre_modalidad__icontains=nombre_modalidad)
        elif nombre_fuente:
            planes = self.queryset.filter(nombre_fuente__icontains=nombre_fuente)
        elif nombre_unidad:
            planes = self.queryset.filter(nombre_unidad__icontains=nombre_unidad)
        else:
            planes = self.queryset.all()
        serializer = PlanAnualAdquisicionesSerializer(planes, many=True)
        if not planes:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes planes anuales de adquisiciones:', 'data': serializer.data}, status=status.HTTP_200_OK)
# ---------------------------------------- PAA CodgigoUNSP ----------------------------------------

# Listar todos los registros de PAA CodgigoUNSP

class PAACodUNSPList(generics.ListAPIView):
    queryset = PAACodgigoUNSP.objects.all()
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paas = self.get_queryset().values('id_plan', 'codigo_unsp', 'descripcion', 'unidad_medida', 'cantidad', 'valor_unitario', 'valor_total', 'fuente', 'estado', 'observaciones')
        serializer = PAACodgigoUNSPSerializer(paas, many=True)
        if not paas:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes PAA CodgigoUNSP:', 'data': serializer.data}, status=status.HTTP_200_OK)


# Crear un registro de PAA CodgigoUNSP

class PAACodUNSPCreate(generics.CreateAPIView):
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return PAACodgigoUNSP.objects.get(pk=pk)
        except PAACodgigoUNSP.DoesNotExist:
            raise NotFound("No se encontró un PAA CodgigoUNSP con este ID.")

    def delete(self, request, pk):
        paa = self.get_object(pk)
        paa.delete()
        return Response({'success': True, 'detail': 'Se eliminó el PAA CodgigoUNSP correctamente.', 'data': []}, status=status.HTTP_200_OK)
    
# Listar registros de PAA CodgigoUNSP por ID de PAA

class PAACodUNSPListIdPAA(generics.ListAPIView):
    queryset = PAACodgigoUNSP.objects.all()
    serializer_class = PAACodgigoUNSPSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        paas = self.get_queryset().filter(id_plan=pk)
        serializer = PAACodgigoUNSPSerializer(paas, many=True)
        if not paas:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes PAA CodgigoUNSP:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Seguimiento PAI ----------------------------------------

# Listar todos los registros de seguimiento PAI

class SeguimientoPAIList(generics.ListAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seguimientos = self.get_queryset()
        serializer = SeguimientoPAISerializer(seguimientos, many=True)
        if not seguimientos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos PAI:', 'data': serializer.data}, status=status.HTTP_200_OK)
    
# Listar por periodo de tiempo

class SeguimientoPAIListPeriodo(generics.ListAPIView):
    serializer_class = SeguimientoPAISerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        queryset = SeguimientoPAI.objects.all()

        if fecha_inicio is not None and fecha_fin is not None:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio, fecha_creacion__lte=fecha_fin)

        return queryset

    def get(self, request, *args, **kwargs):
        seguimientos = self.get_queryset()
        serializer = SeguimientoPAISerializer(seguimientos, many=True)
        if not seguimientos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos PAI:', 'data': serializer.data}, status=status.HTTP_200_OK)
# Crear un registro de seguimiento PAI

class SeguimientoPAICreate(generics.CreateAPIView):
    serializer_class = SeguimientoPAISerializer
    permission_classes = [IsAuthenticated, PermisoCrearSeguimientoTecnicoPAI]

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
    permission_classes = [IsAuthenticated, PermisoActualizarSeguimientoTecnicoPAI]

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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SeguimientoPAI.objects.get(pk=pk)
        except SeguimientoPAI.DoesNotExist:
            raise NotFound("No se encontró un seguimiento PAI con este ID.")

    def delete(self, request, pk):
        seguimiento = self.get_object(pk)
        seguimiento.delete()
        return Response({'success': True, 'detail': 'Se eliminó el seguimiento PAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# Busqueda avanzada de seguimiento PAI
    
class BusquedaAvanzadaSeguimientoPAI(generics.ListAPIView):
    queryset = SeguimientoPAI.objects.all()
    serializer_class = SeguimientoPAISerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nombre_programa = request.GET.get('nombre_programa')
        nombre_proyecto = request.GET.get('nombre_proyecto')
        nombre_producto = request.GET.get('nombre_producto')
        nombre_actividad = request.GET.get('nombre_actividad')
        nombre_unidad = request.GET.get('nombre_unidad')
        nombre_indicador = request.GET.get('nombre_indicador')
        nombre_meta = request.GET.get('nombre_meta')
        if nombre_programa:
            seguimientos = self.queryset.filter(id_programa__nombre_programa__icontains=nombre_programa)
        elif nombre_proyecto:
            seguimientos = self.queryset.filter(id_proyecto__nombre_proyecto__icontains=nombre_proyecto)
        elif nombre_producto:
            seguimientos = self.queryset.filter(id_producto__nombre_producto__icontains=nombre_producto)
        elif nombre_actividad:
            seguimientos = self.queryset.filter(id_actividad__nombre_actividad__icontains=nombre_actividad)
        elif nombre_unidad:
            seguimientos = self.queryset.filter(id_unidad_organizacional__nombre__icontains=nombre_unidad)
        elif nombre_indicador:
            seguimientos = self.queryset.filter(id_indicador__nombre_indicador__icontains=nombre_indicador)
        elif nombre_meta:
            seguimientos = self.queryset.filter(id_meta__nombre_meta__icontains=nombre_meta)
        else:
            seguimientos = self.queryset.all()
        serializer = SeguimientoPAISerializer(seguimientos, many=True)
        if not seguimientos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos PAI:', 'data': serializer.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Seguimiento PAI Documentos ----------------------------------------

# Listar todos los registros de seguimiento PAI documentos

class SeguimientoPAIDocumentosList(generics.ListAPIView):
    queryset = SeguimientoPAIDocumentos.objects.all()
    serializer_class = SeguimientoPAIDocumentosSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    serializer_archivo = ArchivosDigitalesCreateSerializer
    def get(self, request, pk):
        documentos = self.get_queryset().filter(id_seguimiento_pai=pk)
        data_respuesta=[]
        for documento in documentos:
            archivo = ArchivosDigitales.objects.filter(id_archivo_digital=documento.id_archivo_digital.id_archivo_digital).first()
            serializer_archivo = self.serializer_archivo(archivo)
            data_respuesta.append({'data':self.serializer_class(documento).data,'archivo':serializer_archivo.data})
            
        if not documentos:
            raise NotFound("No se encontraron resultados para esta consulta.")
        return Response({'success': True, 'detail': 'Se encontraron los siguientes documentos de seguimiento PAI:', 'data': data_respuesta}, status=status.HTTP_200_OK)
    
# # ---------------------------------------- Seguimiento POAI ----------------------------------------

# # Listar todos los registros de seguimiento POAI

# class SeguimientoPOAIList(generics.ListAPIView):
#     queryset = SeguimientoPOAI.objects.all()
#     serializer_class = SeguimientoPOAISerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         seguimientos = self.get_queryset()
#         serializer = SeguimientoPOAISerializer(seguimientos, many=True)
#         if not seguimientos:
#             raise NotFound("No se encontraron resultados para esta consulta.")
#         return Response({'success': True, 'detail': 'Se encontraron los siguientes seguimientos POAI:', 'data': serializer.data}, status=status.HTTP_200_OK)

# # Crear un registro de seguimiento POAI

# class SeguimientoPOAICreate(generics.CreateAPIView):
#     serializer_class = SeguimientoPOAISerializer
#     permission_classes = [IsAuthenticated, PermisoCrearSeguimientoPOAI]

#     def post(self, request):
#         serializer = SeguimientoPOAISerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'success': True, 'detail': 'Se creó el seguimiento POAI correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
#         else:
#             print(serializer.errors)  # Imprime los errores de validación
#             raise ValidationError('Los datos proporcionados no son válidos. Por favor, revisa los datos e intenta de nuevo.')

# # Actualizar un registro de seguimiento POAI

# class SeguimientoPOAIUpdate(generics.UpdateAPIView):
#     queryset = SeguimientoPOAI.objects.all()
#     serializer_class = SeguimientoPOAISerializer
#     permission_classes = [IsAuthenticated, PermisoActualizarSeguimientoPOAI]

#     def put(self, request, pk):
#         data = request.data
#         seguimiento = self.get_object()
#         serializer = self.serializer_class(seguimiento, data=data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'success': True, 'detail': 'Se actualizó el seguimiento POAI correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

# # Eliminar un registro de seguimiento POAI
    
# class SeguimientoPOAIDelete(generics.DestroyAPIView):
#     queryset = SeguimientoPOAI.objects.all()
#     serializer_class = SeguimientoPOAISerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             return SeguimientoPOAI.objects.get(pk=pk)
#         except SeguimientoPOAI.DoesNotExist:
#             raise NotFound("No se encontró un seguimiento POAI con este ID.")

#     def delete(self, request, pk):
#         seguimiento = self.get_object(pk)
#         seguimiento.delete()
#         return Response({'success': True, 'detail': 'Se eliminó el seguimiento POAI correctamente.', 'data': []}, status=status.HTTP_200_OK)

# # Busqueda avanzada de seguimiento POAI por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad, nombre indicador, nombre meta, nombre, concepto, cuenta, objeto_contrato, codigo_modalidad, 

# class BusquedaAvanzadaSeguimientoPOAI(generics.ListAPIView):
#     queryset = SeguimientoPOAI.objects.all()
#     serializer_class = SeguimientoPOAISerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         nombre_plan = request.GET.get('nombre_plan')
#         nombre_programa = request.GET.get('nombre_programa')
#         nombre_proyecto = request.GET.get('nombre_proyecto')
#         nombre_producto = request.GET.get('nombre_producto')
#         nombre_actividad = request.GET.get('nombre_actividad')
#         nombre_indicador = request.GET.get('nombre_indicador')
#         nombre_meta = request.GET.get('nombre_meta')
#         nombre = request.GET.get('nombre')
#         concepto = request.GET.get('concepto')
#         cuenta = request.GET.get('cuenta')
#         objeto_contrato = request.GET.get('objeto_contrato')
#         codigo_modalidad = request.GET.get('codigo_modalidad')
#         if nombre_plan:
#             seguimientos = self.queryset.filter(id_plan__nombre_plan__icontains=nombre_plan)
#         elif nombre_programa:
#             seguimientos = self.queryset.filter(id_programa__nombre_programa__icontains=nombre_programa)
#         elif nombre_proyecto:
#             seguimientos = self.queryset.filter(id_proyecto__nombre_proyecto__icontains=nombre_proyecto)
#         elif nombre_producto:
#             seguimientos = self.queryset.filter(id_producto__nombre_producto__icontains=nombre_producto)
#         elif nombre_actividad:
#             seguimientos = self.queryset.filter(id_actividad__nombre_actividad__icontains=nombre_actividad)
#         elif nombre_indicador:
#             seguimientos = self.queryset.filter(id_indicador__nombre_indicador__icontains=nombre_indicador)
#         elif nombre_meta:
#             seguimientos = self.queryset.filter(id_meta__nombre_meta__icontains=nombre_meta)
#         elif nombre:
#             seguimientos = self.queryset.filter(id_concepto__nombre__icontains=nombre)
#         elif concepto:
#             seguimientos = self.queryset.filter(id_concepto__concepto__icontains=concepto)
#         elif cuenta:
#             seguimientos = self.queryset.filter(id_concepto__cuenta__icontains=cuenta)
#         elif objeto_contrato:
#             seguimientos = self.queryset.filter(id_concepto__objeto_contrato__icontains=objeto_contrato)
#         elif codigo_modalidad:
#             seguimientos = self.queryset.filter(id_concepto__codigo_modalidad__icontains=codigo_modalidad)
#         else:
#             seguimientos = self.queryset.all()
#         serializer = SeguimientoPOAISerializer(seguimientos, many=True)
#         if not seguimientos:
#             raise NotFound("No se encontraron resultados para esta consulta.")
#         return Response( {'success': True, 'detail': 'Se encontraron los siguientes seguimientos POAI:', 'data': serializer.data}, status=status.HTTP_200_OK)