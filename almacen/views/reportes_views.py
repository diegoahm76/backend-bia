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
    serializer_class=EntradasInventarioGetSerializer
    queryset=ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['id_bodega','cod_tipo_bien','fecha_desde','fecha_hasta']:
                if key == 'cod_tipo_bien':
                    if value != '':
                        filter['id_bien__cod_tipo_bien']=value
                elif key == 'fecha_desde':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__gte']=value
                elif key == 'fecha_hasta':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__lte']=value
                else:
                    if value != '':
                        filter[key]=value
        
        items_entradas = self.queryset.filter(**filter).filter(id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data
        
        data_output = []
        
        if items_entradas:
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "responsable_bodega"))
                
            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "responsable_bodega")):
                detalles = list(items)
                
                for detalle in detalles:
                    del detalle['id_bodega']
                    del detalle['nombre_bodega']
                    del detalle['id_bien']
                    del detalle['nombre_bien']
                    del detalle['codigo_bien']
                    del detalle['responsable_bodega']
                    
                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "cantidad_ingresada_total": sum(item['cantidad'] for item in detalles),
                    "responsable_bodega": entrada[5],
                    "detalle": detalles
                }
                
                data_output.append(items_data)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output},status=status.HTTP_200_OK)

class MovimientosIncautadosGetView(generics.ListAPIView):
    serializer_class = MovimientosIncautadosGetSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}

        for key, value in request.query_params.items():
            if key in ['fecha_desde', 'fecha_hasta']:
                if key == 'fecha_desde':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__gte'] = value
                elif key == 'fecha_hasta':
                    if value != '':
                        filter['id_entrada_almacen__fecha_entrada__lte'] = value
            elif key == 'categoria':
                if value != '':
                    filter['id_bien__cod_tipo_bien__cod_tipo_activo'] = value
            else:
                if value != '':
                    filter[key] = value

        items_entradas = self.queryset.filter(**filter).filter(id_entrada_almacen__id_tipo_entrada=8, id_bien__nivel_jerarquico=5)
        serializer = self.serializer_class(items_entradas, many=True)
        serializer_data = serializer.data

        data_output = []

        if items_entradas:
            items_entrada_data = sorted(serializer_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "tipo_activo"))

            for entrada, items in itertools.groupby(items_entrada_data, key=operator.itemgetter("id_bodega", "nombre_bodega", "id_bien", "nombre_bien", "codigo_bien", "tipo_activo")):
                items_list = list(items)

                items_data = {
                    "id_bodega": entrada[0],
                    "nombre_bodega": entrada[1],
                    "id_bien": entrada[2],
                    "nombre_bien": entrada[3],
                    "codigo_bien": entrada[4],
                    "tipo_activo": entrada[5],
                    "cantidad_ingresada": sum(item['cantidad'] for item in items_list)
                }

                data_output.append(items_data)

        return Response({'success': True, 'detail': 'Se encontró la siguiente información', 'data': data_output}, status=status.HTTP_200_OK)

class MantenimientosRealizadosGetView(generics.ListAPIView):
    serializer_class=MantenimientosRealizadosGetSerializer
    queryset=RegistroMantenimientos.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['cod_tipo_mantenimiento','id_persona_realiza','fecha_desde','fecha_hasta']:
                if key == 'fecha_desde':
                    if value != '':
                        filter['fecha_ejecutado__gte']=value
                elif key == 'fecha_hasta':
                    if value != '':
                        filter['fecha_ejecutado__lte']=value
                else:
                    if value != '':
                        filter[key]=value
        
        registro_mantenimientos = self.queryset.filter(**filter)
        serializer = self.serializer_class(registro_mantenimientos, many=True)
        serializer_data = serializer.data

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer_data},status=status.HTTP_200_OK)


class BusquedaGeneralInventario(generics.ListAPIView):
    serializer_class = InventarioSerializer

    def get_queryset(self):
        queryset = Inventario.objects.all()

        # Obtener parámetros de consulta
        tipo_movimiento = self.request.query_params.get('tipo_movimiento')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        # Filtrar por tipo de movimiento
        if tipo_movimiento:
            queryset = queryset.filter(tipo_doc_ultimo_movimiento=tipo_movimiento)
        
        # Filtrar por rango de fechas
        if fecha_desde:
            queryset = queryset.filter(fecha_ultimo_movimiento__gte=fecha_desde)
            
        if fecha_hasta:
            queryset = queryset.filter(fecha_ultimo_movimiento__lte=fecha_hasta)

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