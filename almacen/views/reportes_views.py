import datetime
import operator, itertools
from almacen.models.bienes_models import ItemEntradaAlmacen
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Count, Sum
from almacen.models.hoja_de_vida_models import HojaDeVidaVehiculos
from almacen.models.mantenimientos_models import RegistroMantenimientos
from almacen.serializers.reportes_serializers import EntradasInventarioGetSerializer, HojaDeVidaVehiculosSerializer, InventarioReporteSerializer, InventarioSerializer, ItemDespachoConsumoSerializer, MantenimientosRealizadosGetSerializer, MovimientosIncautadosGetSerializer, ViajesAgendadosSerializer
from almacen.models.inventario_models import Inventario
from almacen.models.vehiculos_models import  InspeccionesVehiculosDia, PersonasSolicitudViaje, VehiculosAgendables_Conductor, VehiculosArrendados, Marcas, ViajesAgendados,BitacoraViaje
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible

class EntradasInventarioGetView(generics.ListAPIView):
    serializer_class = EntradasInventarioGetSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key in [
                'id_bodega', 'cod_tipo_bien', 'fecha_desde', 'fecha_hasta',
                'nombre_bien', 'codigo_bien', 'placa_serial', 
                'id_proveedor', 'id_responsable', 'consecutivo', 'cod_tipo_activo', 
            ]:
                if key == 'cod_tipo_bien':
                    if value:
                        filter['id_bien__cod_tipo_bien'] = value
                elif key == 'fecha_desde':
                    if value:
                        filter['id_entrada_almacen__fecha_entrada__gte'] = value
                elif key == 'fecha_hasta':
                    if value:
                        filter['id_entrada_almacen__fecha_entrada__lte'] = value
                elif key == 'nombre_bien':
                    if value:
                        filter['id_bien__nombre__icontains'] = value
                elif key == 'codigo_bien':
                    if value:
                        filter['id_bien__codigo_bien__icontains'] = value
                elif key == 'placa_serial':
                    if value:
                        filter['id_bien__doc_identificador_nro__icontains'] = value
                elif key == 'id_proveedor':
                    if value:
                        filter['id_entrada_almacen__id_proveedor'] = value
                elif key == 'id_responsable':
                    if value:
                        filter['id_entrada_almacen__id_responsable'] = value
                elif key == 'consecutivo':
                    if value:
                        filter['id_bien__nro_elemento_bien'] = value
                elif key == 'cod_tipo_activo':
                    if value:
                        filter['id_bien__cod_tipo_activo'] = value
                else:
                    if value:
                        filter[key] = value
        
        items_entradas = self.queryset.filter(**filter).filter(id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data
        
        data_output = []
        
        if items_entradas:
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter(
                "id_bodega", "nombre_bodega", "id_bien", "nombre_bien", 
                "codigo_bien", "responsable_bodega", "nombre_proveedor",
                "consecutivo", "cod_tipo_activo", "placa_serial","id_responsable","id_proveedor","cod_tipo_bien"
            ))
                
            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter(
                "id_bodega", "nombre_bodega", "id_bien", "nombre_bien", 
                "codigo_bien", "responsable_bodega", "nombre_proveedor",
                "consecutivo", "cod_tipo_activo", "placa_serial","id_responsable","id_proveedor","cod_tipo_bien"
            )):
                detalles = list(items)
                
                for detalle in detalles:
                    del detalle['id_bodega']
                    del detalle['nombre_bodega']
                    del detalle['id_bien']
                    del detalle['nombre_bien']
                    del detalle['codigo_bien']
                    del detalle['responsable_bodega']
                    del detalle['nombre_proveedor']
                    del detalle['consecutivo']
                    del detalle['cod_tipo_activo']
                    del detalle['placa_serial']
                    del detalle['id_responsable']
                    del detalle['id_proveedor']
                    del detalle['cod_tipo_bien']
                    
                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "cantidad_ingresada_total": sum(item['cantidad'] for item in detalles),
                    "responsable_bodega": entrada[5],
                    "nombre_proveedor": entrada[6],
                    "consecutivo": entrada[7],
                    "cod_tipo_activo": entrada[8],
                    "placa_serial": entrada[9],
                    "id_responsable": entrada[10],
                    "id_proveedor": entrada[11],
                    "cod_tipo_bien": entrada[12],
                    "detalle": detalles
                }
                
                data_output.append(items_data)

        return Response({'success': True, 'detail': 'Se encontró la siguiente información', 'data': data_output}, status=status.HTTP_200_OK)

class MovimientosIncautadosGetView(generics.ListAPIView):
    serializer_class = MovimientosIncautadosGetSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key in ['fecha_desde', 'fecha_hasta']:
                if key == 'fecha_desde':
                    if value:
                        filter['id_entrada_almacen__fecha_entrada__gte'] = value
                elif key == 'fecha_hasta':
                    if value:
                        filter['id_entrada_almacen__fecha_entrada__lte'] = value
            elif key == 'categoria':
                if value:
                    filter['id_bien__cod_tipo_bien'] = value
            elif key == 'nombre_bien':
                if value:
                    filter['id_bien__nombre__icontains'] = value
            elif key == 'codigo_bien':
                if value:
                    filter['id_bien__codigo_bien__icontains'] = value
            elif key == 'placa_serial':
                if value:
                    filter['id_bien__doc_identificador_nro__icontains'] = value
            elif key == 'id_proveedor':
                if value:
                    filter['id_entrada_almacen__id_proveedor'] = value
            elif key == 'id_responsable':
                if value:
                    filter['id_entrada_almacen__id_responsable'] = value
            elif key == 'consecutivo':
                if value:
                    filter['id_bien__nro_elemento_bien'] = value
            elif key == 'cod_tipo_activo':
                if value:
                    filter['id_bien__cod_tipo_activo'] = value
            elif key == 'id_bodega':
                if value:
                    filter['id_bodega'] = value
            else:
                if value:
                    filter[key] = value

        items_entradas = self.queryset.filter(**filter).filter(id_entrada_almacen__id_tipo_entrada=8, id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data

        data_output = []

        if items_entradas:
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter(
                "id_bodega", "nombre_bodega", "id_bien", "nombre_bien", 
                "codigo_bien", "tipo_activo", "codigo_activo_nombre", 
                'codigo_activo', "cod_estado", "codigo_estado_nombre", 
                'id_responsable', "responsable_bodega","consecutivo","placa_serial","nombre_marca"
            ))

            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter(
                "id_bodega", "nombre_bodega", "id_bien", "nombre_bien", 
                "codigo_bien", "tipo_activo", "codigo_activo_nombre", 
                'codigo_activo', "cod_estado", "codigo_estado_nombre", 
                'id_responsable', "responsable_bodega","consecutivo","placa_serial","nombre_marca"
            )):
                items_list = list(items)

                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "tipo_activo": entrada[5],
                    "codigo_activo_nombre": entrada[6],
                    "codigo_activo": entrada[7],
                    "codigo_estado": entrada[8],
                    "codigo_estado_nombre": entrada[9],
                    "id_responsable": entrada[10],
                    "responsable_bodega": entrada[11],
                    "consecutivo": entrada[12],
                    "placa_serial": entrada[13],
                    "nombre_marca": entrada[14],
                    "cantidad_ingresada": sum(item['cantidad'] for item in items_list)
                }

                data_output.append(items_data)

        return Response({'success': True, 'detail': 'Se encontró la siguiente información', 'data': data_output}, status=status.HTTP_200_OK)


class MantenimientosRealizadosGetView(generics.ListAPIView):
    serializer_class = MantenimientosRealizadosGetSerializer
    queryset = RegistroMantenimientos.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key in ['cod_tipo_mantenimiento', 'id_persona_realiza', 'fecha_desde', 'fecha_hasta', 'nombre_bien', 'codigo_bien', 'serial_placa','consecutivo','cod_tipo_activo']:
                if key == 'fecha_desde':
                    if value:
                        filter['fecha_ejecutado__gte'] = value
                elif key == 'fecha_hasta':
                    if value:
                        filter['fecha_ejecutado__lte'] = value
                elif key == 'nombre_bien':
                    if value:
                        filter['id_articulo__nombre__icontains'] = value
                elif key == 'codigo_bien':
                    if value:
                        filter['id_articulo__codigo_bien__icontains'] = value
                elif key == 'serial_placa':
                    if value:
                        filter['id_articulo__doc_identificador_nro__icontains'] = value
                elif key == 'consecutivo':
                    if value:
                        filter['id_articulo__nro_elemento_bien'] = value
                elif key == 'cod_tipo_activo':
                    if value:
                        filter['id_articulo__cod_tipo_activo'] = value
                else:
                    if value:
                        filter[key] = value

        registro_mantenimientos = self.queryset.filter(**filter)
        serializer = self.serializer_class(registro_mantenimientos, many=True)
        serializer_data = serializer.data

        return Response({'success': True, 'detail': 'Se encontró la siguiente información', 'data': serializer_data}, status=status.HTTP_200_OK)



class BusquedaGeneralInventario(generics.ListAPIView):
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Inventario.objects.all()

        tipo_movimiento = self.request.query_params.get('tipo_movimiento')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        identificador_bien = self.request.query_params.get('identificador_bien')
        codigo_bien = self.request.query_params.get('codigo_bien')
        nombre_bien = self.request.query_params.get('nombre_bien')
        cod_tipo_activo = self.request.query_params.get('cod_tipo_activo')
        consecutivo = self.request.query_params.get('consecutivo')
        id_bodega = self.request.query_params.get('id_bodega')
        id_persona_origen = self.request.query_params.get('id_persona_origen')
        id_persona_responsable = self.request.query_params.get('id_persona_responsable')

        # Filtrar por tipo de movimiento
        if tipo_movimiento:
            queryset = queryset.filter(tipo_doc_ultimo_movimiento=tipo_movimiento)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_ultimo_movimiento__gte=fecha_desde)
            
        if fecha_hasta:
            queryset = queryset.filter(fecha_ultimo_movimiento__lte=fecha_hasta)
        
        if identificador_bien:
            queryset = queryset.filter(id_bien__doc_identificador_nro__icontains=identificador_bien)
        
        if codigo_bien:
            queryset = queryset.filter(id_bien__codigo_bien__icontains=codigo_bien)
        
        if nombre_bien:
            queryset = queryset.filter(id_bien__nombre__icontains=nombre_bien)

        if cod_tipo_activo:
            queryset = queryset.filter(id_bien__cod_tipo_activo=cod_tipo_activo)
        
        if consecutivo:
            queryset = queryset.filter(id_bien__nro_elemento_bien=consecutivo)
        
        if id_bodega:
            queryset = queryset.filter(id_bodega=id_bodega)
        
        if id_persona_origen:
            queryset = queryset.filter(id_persona_origen=id_persona_origen)
        
        if id_persona_responsable:
            queryset = queryset.filter(id_persona_responsable=id_persona_responsable)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Búsqueda realizada exitosamente.',
            'data': serializer.data
        }
        return Response(data)

    

class BusquedaVehiculos(generics.ListAPIView):
    serializer_class = HojaDeVidaVehiculosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tipo_vehiculo = self.request.query_params.get('tipo_vehiculo')
        marca = self.request.query_params.get('marca')
        placa = self.request.query_params.get('placa')
        contratista = self.request.query_params.get('contratista')
        nombre = self.request.query_params.get('nombre')

        queryset = HojaDeVidaVehiculos.objects.all()

        # Aplicar filtros adicionales si se proporcionan
        if tipo_vehiculo:
            queryset = queryset.filter(cod_tipo_vehiculo=tipo_vehiculo)

        if marca:
            queryset = queryset.filter(Q(id_vehiculo_arrendado__id_marca__nombre__icontains=marca) |
                                       Q(id_articulo__id_marca__nombre__icontains=marca))

        if placa:
            # Validar si es_arrendado es None
            queryset = queryset.filter(Q(es_arrendado=None) & Q(id_articulo__doc_identificador_nro__icontains=placa) |
                                    Q(es_arrendado=False, id_articulo__doc_identificador_nro__icontains=placa) |
                                    Q(es_arrendado=True, id_vehiculo_arrendado__placa__icontains=placa))

        if contratista:
            queryset = queryset.filter(id_vehiculo_arrendado__empresa_contratista__icontains=contratista)

        if nombre:
            queryset = queryset.filter(
                Q(es_arrendado=None, id_articulo__nombre__icontains=nombre) |
                Q(es_arrendado=False, id_articulo__nombre__icontains=nombre) |
                Q(es_arrendado=True, id_vehiculo_arrendado__nombre__icontains=nombre)
            )


        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        # Retornar la respuesta con los datos procesados
        return Response({'success': True, 'detail': 'Vehículos obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)


class BusquedaViajesAgendados(generics.ListAPIView):
    serializer_class = ViajesAgendadosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener el parámetro id_hoja_vida_vehiculo de la URL
        id_hoja_vida_vehiculo = self.kwargs.get('id_hoja_vida_vehiculo')

        # Filtrar las asignaciones de conductor para el vehículo específico
        asignaciones_conductor = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo=id_hoja_vida_vehiculo)

        # Filtrar los viajes agendados autorizados asociados a las asignaciones de conductor
        queryset = []
        for asignacion in asignaciones_conductor:
            viajes_agendados = asignacion.viajesagendados_set.filter(viaje_autorizado=True)
            queryset.extend(viajes_agendados)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Viajes obtenidos exitosamente', 'data': serializer.data})
    


class HistoricoTodosViajesAgendados(generics.ListAPIView):
    serializer_class = ViajesAgendadosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener los parámetros de los filtros adicionales
        tipo_vehiculo = self.request.query_params.get('tipo_vehiculo')
        marca = self.request.query_params.get('marca')
        placa = self.request.query_params.get('placa')
        es_arrendado = self.request.query_params.get('es_arrendado')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        queryset_vehiculos = HojaDeVidaVehiculos.objects.all()

        if tipo_vehiculo:
            queryset_vehiculos = queryset_vehiculos.filter(cod_tipo_vehiculo=tipo_vehiculo)

        if es_arrendado:
            queryset_vehiculos = queryset_vehiculos.filter(es_arrendado=es_arrendado)

        if marca:
            queryset_vehiculos = queryset_vehiculos.filter(Q(id_vehiculo_arrendado__id_marca__nombre__icontains=marca) |
                                                           Q(id_articulo__id_marca__nombre__icontains=marca))

        if placa:
            queryset_vehiculos = queryset_vehiculos.filter(Q(es_arrendado=None, id_articulo__doc_identificador_nro__icontains=placa) |
                                                           Q(es_arrendado=False, id_articulo__doc_identificador_nro__icontains=placa) |
                                                           Q(es_arrendado=True, id_vehiculo_arrendado__placa__icontains=placa))

        # Filtrar las asignaciones de conductor para los vehículos filtrados
        asignaciones_conductor = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo__in=queryset_vehiculos.values('pk'))

        # Filtrar los viajes agendados autorizados asociados a las asignaciones de conductor
        queryset_viajes = []
        for asignacion in asignaciones_conductor:
            viajes_agendados = asignacion.viajesagendados_set.filter(viaje_autorizado=True)

            # Filtrar por fecha desde y fecha hasta
            if fecha_desde:
                viajes_agendados = viajes_agendados.filter(fecha_partida_asignada__gte=datetime.strptime(fecha_desde, '%Y-%m-%d'))
            if fecha_hasta:
                viajes_agendados = viajes_agendados.filter(fecha_retorno_asignada__lte=datetime.strptime(fecha_hasta, '%Y-%m-%d'))

            queryset_viajes.extend(viajes_agendados)

        return queryset_viajes

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Viajes obtenidos exitosamente', 'data': serializer.data})
    


class BusquedaGeneralInventarioActivos(generics.ListAPIView):
    serializer_class = InventarioReporteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Inventario.objects.filter(ubicacion_prestado=True)

        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        cod_tipo_activo = self.request.query_params.get('cod_tipo_activo')

        # Filtrar por código de tipo de activo
        if cod_tipo_activo:
            queryset = queryset.filter(id_bien__cod_tipo_activo=cod_tipo_activo)

        # Filtrar por fecha de último movimiento
        if fecha_desde:
            queryset = queryset.filter(fecha_ultimo_movimiento__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_ultimo_movimiento__lte=fecha_hasta)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        
        return Response({'success': True, 'detail': 'Búsqueda realizada exitosamente.', 'data': serializer.data})



class BusquedaGeneralDespachosConsumo(generics.ListAPIView):
    serializer_class = ItemDespachoConsumoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ItemDespachoConsumo.objects.all()

        # Obtener parámetros de consulta
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        # Filtrar por rango de fechas de despacho
        if fecha_desde:
            queryset = queryset.filter(id_despacho_consumo__fecha_despacho__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(id_despacho_consumo__fecha_despacho__lte=fecha_hasta)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        
        # Retornar la respuesta con los datos procesados
        return Response({'success': True, 'detail': 'Búsqueda realizada exitosamente.', 'data': serializer.data})