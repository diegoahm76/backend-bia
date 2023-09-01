from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.cuarentena_models import BajasVivero, CuarentenaMatVegetal, ItemsBajasVivero, ItemsLevantaCuarentena
from conservacion.models.despachos_models import DespachoEntrantes, DespachoViveros, DistribucionesItemDespachoEntrante, ItemsDespachoEntrante, ItemsDespachoViveros
from conservacion.models.incidencias_models import ConsumosIncidenciasMV, IncidenciasMatVegetal
from conservacion.models.mezclas_models import Mezclas
from conservacion.models.siembras_models import CambiosDeEtapa, Siembras
from conservacion.models.solicitudes_models import ItemSolicitudViveros, SolicitudesViveros
from conservacion.models.traslados_models import ItemsTrasladoViveros, TrasladosViveros
from conservacion.serializers.analitica_serializers import ConsumosIncidenciasGetSerializer, GetBienesInventarioSerializer, GetBienesMezclasSerializer, GetTableroControlConservacionSerializer, HistoricoCambiosEtapaGetSerializer, HistoricoDistribucionesGetSerializer, HistoricoIngresoCuarentenaGetSerializer, HistoricoLevantamientoCuarentenaGetSerializer, HistoricoSiembrasGetSerializer, HistoricoTrasladosGetSerializer
from rest_framework import generics, status
from django.db.models import Q, F, Sum, Count
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated

import operator, itertools

from conservacion.models.inventario_models import (
    InventarioViveros
)

class TableroControlGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        viveros_cuarentena = request.query_params.get('viveros_cuarentena', '')
        viveros_cerrados = request.query_params.get('viveros_cerrados', '')
        
        for key,value in request.query_params.items():
            if key in ['id_vivero','cod_tipo_elemento_vivero','cod_etapa_lote','id_bien','id_mezcla']:
                if key == 'cod_tipo_elemento_vivero':
                    if value != '':
                        if value in ['IN','HE']:
                            filter['id_bien__cod_tipo_elemento_vivero']=value
                        elif value == 'MZ':
                            filter['id_mezcla__isnull']=False
                        elif value == 'SE':
                            filter['id_bien__cod_tipo_elemento_vivero']='MV'
                            filter['id_bien__es_semilla_vivero']=True
                        elif value == 'PL':
                            filter['id_bien__cod_tipo_elemento_vivero']='MV'
                            filter['id_bien__es_semilla_vivero']=False
                else:
                    if value != '':
                        filter[key]=value
        
        inventarios = self.queryset.filter(**filter).filter(id_vivero__activo=True).filter(Q(id_bien__isnull=False) | Q(id_mezcla__isnull=False)).exclude(siembra_lote_cerrada=True).order_by('id_vivero__nombre', 'id_bien__nombre')
        inventarios = inventarios.exclude(id_vivero__vivero_en_cuarentena=True) if viveros_cuarentena == 'false' else inventarios
        inventarios = inventarios.exclude(id_vivero__fecha_cierre_actual__isnull=False) if viveros_cerrados == 'false' else inventarios
        
        serializer = self.serializer_class(inventarios,many=True, context = {'request':request})
        
        resumen = {
            'lotes_germinacion': len([inventario for inventario in inventarios if inventario.cod_etapa_lote=='G' and not inventario.siembra_lote_cerrada]),
            'plantas_produccion': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['cod_etapa_lote']=='P']),
            'plantas_distribucion': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['cod_etapa_lote']=='D']),
            'plantas_cuarentena_produccion': sum([inventario['cantidad_cuarentena'] for inventario in serializer.data if inventario['cantidad_cuarentena'] and inventario['cod_etapa_lote']=='P']),
            'plantas_cuarentena_distribucion': sum([inventario['cantidad_cuarentena'] for inventario in serializer.data if inventario['cantidad_cuarentena'] and inventario['cod_etapa_lote']=='D']),
            'cantidad_herramientas': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['tipo_bien']=='Herramienta']),
            'cantidad_plantas': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['tipo_bien']=='Planta']),
            'tipos_insumos': len(set([inventario['unidad_disponible'] for inventario in serializer.data if inventario['tipo_bien']=='Insumo'])),
            'tipos_semillas': len(set([inventario['unidad_disponible'] for inventario in serializer.data if inventario['tipo_bien']=='Semilla'])),
            'cantidad_donaciones': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['origen']=='Donación']),
            'cantidad_resarcimientos': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['origen']=='Resarcimiento']),
            'cantidad_compensaciones': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['origen']=='Compensación']),
            'cantidad_prod_propia': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['origen']=='Producción Propia']),
            'cantidad_compras_no_identificado': sum([inventario['cantidad_existente'] for inventario in serializer.data if inventario['origen']=='Compras/No Identificado'])
        }
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data, 'resumen': resumen},status=status.HTTP_200_OK)

class BienesMezclasFilterGetView(generics.ListAPIView):
    serializer_class = GetBienesMezclasSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
        filter = {}
        nombre = request.query_params.get('nombre', '')
        codigo_bien = request.query_params.get('codigo_bien', '')
        cod_tipo_elemento_vivero = request.query_params.get('cod_tipo_elemento_vivero', '')
        
        data_response = []
        
        if cod_tipo_elemento_vivero != '':
            if cod_tipo_elemento_vivero == 'MZ':
                if codigo_bien == '':
                    mezclas = Mezclas.objects.filter(item_activo=True, nombre__icontains=nombre).values('nombre','id_mezcla')
                    for item in mezclas:
                        item.update(
                            {
                                'id_bien':None,
                                'codigo_bien':None,
                                'tipo_bien':'Mezcla',
                                'nombre_cientifico':None
                            }
                        )
                    data_response = data_response + list(mezclas)
            else:
                if cod_tipo_elemento_vivero in ['IN','HE']:
                    filter['cod_tipo_elemento_vivero']=cod_tipo_elemento_vivero
                elif cod_tipo_elemento_vivero == 'SE':
                    filter['cod_tipo_elemento_vivero']='MV'
                    filter['es_semilla_vivero']=True
                elif cod_tipo_elemento_vivero == 'PL':
                    filter['cod_tipo_elemento_vivero']='MV'
                    filter['es_semilla_vivero']=False
            
                bienes = self.queryset.filter(**filter).filter(solicitable_vivero=True, nivel_jerarquico=5, nombre__icontains=nombre, codigo_bien__icontains=codigo_bien).exclude(cod_tipo_elemento_vivero=None)
                bienes_serializer = self.serializer_class(bienes, many=True)
                data_response = data_response + bienes_serializer.data
        else:
            if codigo_bien == '':
                mezclas = Mezclas.objects.filter(item_activo=True, nombre__icontains=nombre).values('nombre','id_mezcla')
                for item in mezclas:
                    item.update(
                        {
                            'id_bien':None,
                            'codigo_bien':None,
                            'tipo_bien':'Mezcla',
                            'nombre_cientifico':None
                        }
                    )
                data_response = data_response + list(mezclas)
            
            bienes = self.queryset.filter(solicitable_vivero=True, nivel_jerarquico=5, nombre__icontains=nombre, codigo_bien__icontains=codigo_bien).exclude(cod_tipo_elemento_vivero=None)
            bienes_serializer = self.serializer_class(bienes, many=True)
            data_response = data_response + bienes_serializer.data
        
        return Response({'success':True,'detail':'Se encontraron los siguientes bienes/mezclas','data':data_response},status=status.HTTP_200_OK)

class HistoricoMovimientosGetView(generics.ListAPIView):
    serializer_class = GetBienesMezclasSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        id_vivero = request.query_params.get('id_vivero')
        
        ultimos_movimientos = []
        
        # DISTRIBUCIONES
        distribuciones = DistribucionesItemDespachoEntrante.objects.filter(id_vivero=id_vivero) if id_vivero else DistribucionesItemDespachoEntrante.objects.all()
        distribuciones = distribuciones.annotate(fecha_movimiento=F('fecha_distribucion'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in distribuciones:
            item.update( {"movimiento":"Distribucion de Despacho Entrante"})
        ultimos_movimientos = ultimos_movimientos + distribuciones
            
        # BAJAS
        bajas = BajasVivero.objects.filter(id_vivero=id_vivero, tipo_baja='B') if id_vivero else BajasVivero.objects.filter(tipo_baja='B')
        bajas = bajas.annotate(fecha_movimiento=F('fecha_baja'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in bajas:
            item.update( {"movimiento":"Registro de Baja"})
        ultimos_movimientos = ultimos_movimientos + bajas
            
        # SIEMBRAS
        siembras = Siembras.objects.filter(id_vivero=id_vivero) if id_vivero else Siembras.objects.all()
        siembras = siembras.annotate(fecha_movimiento=F('fecha_siembra'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in siembras:
            item.update( {"movimiento":"Registro de Siembra"})
        ultimos_movimientos = ultimos_movimientos + siembras
            
        # INGRESO A CUARENTENA
        ingreso_cuarentena = CuarentenaMatVegetal.objects.filter(id_vivero=id_vivero) if id_vivero else CuarentenaMatVegetal.objects.all()
        ingreso_cuarentena = ingreso_cuarentena.annotate(fecha_movimiento=F('fecha_cuarentena'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in ingreso_cuarentena:
            item.update( {"movimiento":"Ingreso a Cuarentena"})
        ultimos_movimientos = ultimos_movimientos + ingreso_cuarentena
            
        # LEVANTAMIENTO DE CUARENTENA
        levantamiento_cuarentena = ItemsLevantaCuarentena.objects.filter(id_cuarentena_mat_vegetal__id_vivero=id_vivero) if id_vivero else ItemsLevantaCuarentena.objects.all()
        levantamiento_cuarentena = levantamiento_cuarentena.annotate(fecha_movimiento=F('fecha_levantamiento'), nombre_vivero=F('id_cuarentena_mat_vegetal__id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in levantamiento_cuarentena:
            item.update( {"movimiento":"Levantamiento de Cuarentena"})
        ultimos_movimientos = ultimos_movimientos + levantamiento_cuarentena
            
        # CAMBIO DE ETAPA
        cambio_etapa = CambiosDeEtapa.objects.filter(id_vivero=id_vivero) if id_vivero else CambiosDeEtapa.objects.all()
        cambio_etapa = cambio_etapa.annotate(fecha_movimiento=F('fecha_cambio'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in cambio_etapa:
            item.update( {"movimiento":"Distribucion de Despacho Entrante"})
        ultimos_movimientos = ultimos_movimientos + cambio_etapa
            
        # MORTALIDAD
        mortalidad = BajasVivero.objects.filter(id_vivero=id_vivero, tipo_baja='M') if id_vivero else BajasVivero.objects.filter(tipo_baja='M')
        mortalidad = mortalidad.annotate(fecha_movimiento=F('fecha_baja'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in mortalidad:
            item.update( {"movimiento":"Registro de Mortalidad"})
        ultimos_movimientos = ultimos_movimientos + mortalidad
            
        # SOLICITUDES
        solicitudes = SolicitudesViveros.objects.filter(id_vivero_solicitud=id_vivero) if id_vivero else SolicitudesViveros.objects.all()
        solicitudes = solicitudes.annotate(fecha_movimiento=F('fecha_solicitud'), nombre_vivero=F('id_vivero_solicitud__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in solicitudes:
            item.update( {"movimiento":"Registro de Solicitud"})
        ultimos_movimientos = ultimos_movimientos + solicitudes
            
        # DESPACHOS
        despachos = DespachoViveros.objects.filter(id_vivero=id_vivero) if id_vivero else DespachoViveros.objects.all()
        despachos = despachos.annotate(fecha_movimiento=F('fecha_despacho'), nombre_vivero=F('id_vivero__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in despachos:
            item.update( {"movimiento":"Registro de Despacho"})
        ultimos_movimientos = ultimos_movimientos + despachos
            
        # TRASLADOS
        traslados = TrasladosViveros.objects.filter(id_vivero_origen=id_vivero) if id_vivero else TrasladosViveros.objects.all()
        traslados = traslados.annotate(fecha_movimiento=F('fecha_traslado'), nombre_vivero=F('id_vivero_origen__nombre')).order_by('-fecha_movimiento').values('fecha_movimiento', 'nombre_vivero')[:5][::-1]
        for item in traslados:
            item.update( {"movimiento":"Registro de Traslado"})
        ultimos_movimientos = ultimos_movimientos + traslados
        
        ultimos_movimientos.sort(key=lambda item:item['fecha_movimiento'], reverse=True)
        
        return Response({'success':True,'detail':'Se encontró el siguiente histórico de movimientos','data':ultimos_movimientos[:5]},status=status.HTTP_200_OK)
    
class ReporteMortalidadGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        reporte_consolidado = request.query_params.get('reporte_consolidado', '')
        
        if id_bien == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir un bien y las fechas como filtros')
        
        mortalidades = self.queryset.filter(tipo_baja='M', fecha_baja__gte=fecha_desde, fecha_baja__lte=fecha_hasta)
        mortalidades = mortalidades.filter(id_vivero=id_vivero) if id_vivero != '' else mortalidades
        mortalidades_list = list(mortalidades.values_list('id_baja', flat=True))
        
        items_mortalidades = ItemsBajasVivero.objects.filter(id_baja__in=mortalidades_list, id_bien=id_bien)
        
        data = []
        
        if items_mortalidades:
            if reporte_consolidado == 'true':
                data = {
                    'id_vivero': None,
                    'nombre_vivero': None
                }
                
                data_mortalidad = items_mortalidades.values(unidad_medida_abreviatura=F('id_bien__id_unidad_medida__abreviatura')).annotate(
                    numero_registros=Count('id_baja'),
                    cantidad_mortalidad=Sum('cantidad_baja'),
                    mortalidad_cuarentena=Sum('cantidad_baja', filter=~Q(consec_cuaren_por_lote_etapa=None))
                )
                
                data.update(data_mortalidad[0])
                
                data = [data]
            else:
                data = items_mortalidades.values(id_vivero=F('id_baja__id_vivero__id_vivero'), nombre_vivero=F('id_baja__id_vivero__nombre'), unidad_medida_abreviatura=F('id_bien__id_unidad_medida__abreviatura')).annotate(
                    numero_registros=Count('id_vivero'),
                    cantidad_mortalidad=Sum('cantidad_baja'),
                    mortalidad_cuarentena=Sum('cantidad_baja', filter=~Q(consec_cuaren_por_lote_etapa=None))
                )
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data}, status=status.HTTP_200_OK)
    
class ReporteSolicitudesDespachosGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        reporte_consolidado = request.query_params.get('reporte_consolidado', '')
        
        if id_bien == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir un bien y las fechas como filtros')
        
        solicitudes = self.queryset.filter(fecha_solicitud__gte=fecha_desde, fecha_solicitud__lte=fecha_hasta)
        solicitudes = solicitudes.filter(id_vivero_solicitud=id_vivero) if id_vivero != '' else solicitudes
        solicitudes_list = list(solicitudes.values_list('id_solicitud_vivero', flat=True))
        
        items_solicitudes = ItemSolicitudViveros.objects.filter(id_solicitud_viveros__in=solicitudes_list, id_bien=id_bien)
        
        despachos = DespachoViveros.objects.filter(id_solicitud_a_viveros__in=solicitudes_list)
        despachos_list = list(despachos.values_list('id_despacho_viveros', flat=True))
        
        items_despachos = ItemsDespachoViveros.objects.filter(id_despacho_viveros__in=despachos_list, id_bien=id_bien)
        
        data = []
        
        if items_despachos:
            if reporte_consolidado == 'true':
                data = {
                    'id_vivero': None,
                    'nombre_vivero': None
                }
                
                data_solicitud = items_solicitudes.values(unidad_medida_abreviatura=F('id_bien__id_unidad_medida__abreviatura')).annotate(
                    numero_solicitudes=Count('id_solicitud_viveros'),
                    cantidad_total_solicitada=Sum('cantidad')
                )
                
                data.update(data_solicitud[0])
                
                # Despachos
                data_despachos = items_despachos.aggregate(
                    cantidad_total_despachada=Sum('cantidad_despachada')
                )
                data['cantidad_total_despachada'] = data_despachos['cantidad_total_despachada']
                
                data = [data]
            else:
                data = items_solicitudes.values(id_vivero=F('id_solicitud_viveros__id_vivero_solicitud'), nombre_vivero=F('id_solicitud_viveros__id_vivero_solicitud__nombre'), unidad_medida_abreviatura=F('id_bien__id_unidad_medida__abreviatura')).annotate(
                    numero_solicitudes=Count('id_vivero'),
                    cantidad_total_solicitada=Sum('cantidad')
                )

                # Despachos
                data_despachos = items_despachos.values(id_vivero=F('id_despacho_viveros__id_vivero')).annotate(
                    numero_despachos=Count('id_vivero'),
                    cantidad_total_despachada=Sum('cantidad_despachada')
                )
                
                for data_item in data:
                    data_item['cantidad_total_despachada'] = [data_despacho for data_despacho in data_despachos if data_despacho['id_vivero'] == data_item['id_vivero']]
                    data_item['cantidad_total_despachada'] = data_item['cantidad_total_despachada'][0]['cantidad_total_despachada'] if data_item['cantidad_total_despachada'] else None
            
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data}, status=status.HTTP_200_OK)
    
class ReporteEstadoActividadGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=DespachoEntrantes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        reporte_consolidado = request.query_params.get('reporte_consolidado', '')
        
        if id_bien == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir un bien y las fechas como filtros')
        
        entradas = self.queryset.filter(distribucion_confirmada=True, fecha_confirmacion_distribucion__gte=fecha_desde, fecha_confirmacion_distribucion__lte=fecha_hasta)
        entradas_list = list(entradas.values_list('id_despacho_entrante', flat=True))
        
        items_entradas = ItemsDespachoEntrante.objects.filter(id_despacho_entrante__in=entradas_list, id_bien=id_bien).exclude(id_entrada_alm_del_bien=None)
        items_entradas_list = list(items_entradas.values_list('id_item_despacho_entrante', flat=True))
        
        distribuciones_items_entradas = DistribucionesItemDespachoEntrante.objects.filter(id_item_despacho_entrante__in=items_entradas_list)
        distribuciones_items_entradas = distribuciones_items_entradas.filter(id_vivero=id_vivero) if id_vivero != '' else distribuciones_items_entradas
        
        cantidad_actual = InventarioViveros.objects.filter(id_bien=id_bien)
        cantidad_actual = cantidad_actual.filter(id_vivero=id_vivero) if id_vivero != '' else cantidad_actual
        
        if reporte_consolidado == 'true':
            data = {
                'id_vivero': None,
                'nombre_vivero': None
            }
            
            data_entradas = distribuciones_items_entradas.values(unidad_medida_abreviatura=F('id_item_despacho_entrante__id_bien__id_unidad_medida__abreviatura')).annotate(
                cantidad_donacion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación')),
                cantidad_resarcimiento=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento')),
                cantidad_compensacion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación')),
                cantidad_compras_no_especificado=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación'])),
                cantidad_donacion_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_resarcimiento_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_compensacion_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_compras_no_especificado_produccion=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación']) & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_donacion_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_resarcimiento_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_compensacion_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_compras_no_especificado_distribucion=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación']) & Q(cod_etapa_lote_al_ingresar='D')),
            )
            
            data['entradas'] = data_entradas[0]
            
            # Salidas
            
            # Cantidad Mortalidad
            reporte_mortalidad = ReporteMortalidadGetView()
            response_reporte_mortalidad = reporte_mortalidad.get(request)

            if response_reporte_mortalidad.status_code != status.HTTP_200_OK:
                return response_reporte_mortalidad
            
            # Cantidad Despachos
            reporte_despachos = ReporteSolicitudesDespachosGetView()
            response_reporte_despachos = reporte_despachos.get(request)

            if response_reporte_despachos.status_code != status.HTTP_200_OK:
                return response_reporte_despachos
            
            data['salidas'] = {
                'unidades_despachadas': response_reporte_despachos.data.get('data', [])[0].get('cantidad_total_despachada') if response_reporte_despachos.data.get('data', []) else None,
                'unidades_mortalidad': response_reporte_mortalidad.data.get('data', [])[0].get('cantidad_mortalidad') if response_reporte_mortalidad.data.get('data', []) else None
            }
            
            cantidades_produccion = cantidad_actual.filter(cod_etapa_lote='P').aggregate(
                cantidad_entrante_total=Sum('cantidad_entrante'),
                cantidad_bajas_total=Sum('cantidad_bajas'),
                cantidad_traslados_lote_produccion_distribucion_total=Sum('cantidad_traslados_lote_produccion_distribucion'),
                cantidad_lote_cuarentena_total=Sum('cantidad_lote_cuarentena'),
            )
            
            cantidades_distribucion = cantidad_actual.filter(cod_etapa_lote='D').aggregate(
                cantidad_entrante_total=Sum('cantidad_entrante'),
                cantidad_bajas_total=Sum('cantidad_bajas'),
                cantidad_lote_cuarentena_total=Sum('cantidad_lote_cuarentena'),
            )
            
            cantidad_entrante_total_produccion = cantidades_produccion['cantidad_entrante_total'] if cantidades_produccion['cantidad_entrante_total'] else 0
            cantidad_bajas_total_produccion = cantidades_produccion['cantidad_bajas_total'] if cantidades_produccion['cantidad_bajas_total'] else 0
            cantidad_traslados_lote_produccion_distribucion_total_produccion = cantidades_produccion['cantidad_traslados_lote_produccion_distribucion_total'] if cantidades_produccion['cantidad_traslados_lote_produccion_distribucion_total'] else 0
            cantidad_lote_cuarentena_total = cantidades_produccion['cantidad_lote_cuarentena_total'] if cantidades_produccion['cantidad_lote_cuarentena_total'] else 0
            
            cantidad_entrante_total_distribucion = cantidades_distribucion['cantidad_entrante_total'] if cantidades_distribucion['cantidad_entrante_total'] else 0
            cantidad_bajas_total_distribucion = cantidades_distribucion['cantidad_bajas_total'] if cantidades_distribucion['cantidad_bajas_total'] else 0
            cantidad_lote_cuarentena_total_distribucion = cantidades_distribucion['cantidad_lote_cuarentena_total'] if cantidades_distribucion['cantidad_lote_cuarentena_total'] else 0
            
            data['actualidad'] = {
                'cantidad_produccion': cantidad_entrante_total_produccion - cantidad_bajas_total_produccion - cantidad_traslados_lote_produccion_distribucion_total_produccion - cantidad_lote_cuarentena_total,
                'cantidad_distribucion': cantidad_entrante_total_distribucion - cantidad_bajas_total_distribucion - cantidad_lote_cuarentena_total_distribucion
            }
            
            data = [data]
        else:
            data = distribuciones_items_entradas.values('id_vivero', nombre_vivero=F('id_vivero__nombre'), unidad_medida_abreviatura=F('id_item_despacho_entrante__id_bien__id_unidad_medida__abreviatura')).annotate(
                cantidad_donacion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación')),
                cantidad_resarcimiento=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento')),
                cantidad_compensacion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación')),
                cantidad_compras_no_especificado=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación'])),
                cantidad_donacion_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_resarcimiento_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_compensacion_produccion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación') & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_compras_no_especificado_produccion=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación']) & Q(cod_etapa_lote_al_ingresar='P')),
                cantidad_donacion_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Donación') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_resarcimiento_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Resarcimiento') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_compensacion_distribucion=Sum('cantidad_asignada', filter=Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre='Compensación') & Q(cod_etapa_lote_al_ingresar='D')),
                cantidad_compras_no_especificado_distribucion=Sum('cantidad_asignada', filter=~Q(id_item_despacho_entrante__id_entrada_alm_del_bien__id_tipo_entrada__nombre__in=['Donación','Resarcimiento','Compensación']) & Q(cod_etapa_lote_al_ingresar='D'))
            )
            
            data_response = []
            
            # Cantidad Mortalidad
            reporte_mortalidad = ReporteMortalidadGetView()
            response_reporte_mortalidad = reporte_mortalidad.get(request)

            if response_reporte_mortalidad.status_code != status.HTTP_200_OK:
                return response_reporte_mortalidad
            
            # Cantidad Despachos
            reporte_despachos = ReporteSolicitudesDespachosGetView()
            response_reporte_despachos = reporte_despachos.get(request)

            if response_reporte_despachos.status_code != status.HTTP_200_OK:
                return response_reporte_despachos
            
            for item in data:
                item_entradas = dict(list(item.items())[2:])
                item_data = dict(list(item.items())[:2])
                
                item = item_data
                item['entradas'] = item_entradas
                
                unidades_despachadas = [unidad_despachada['cantidad_total_despachada'] for unidad_despachada in response_reporte_despachos.data.get('data', []) if unidad_despachada['id_vivero']==item['id_vivero']]
                unidades_mortalidad = [unidad_mortalidad['cantidad_mortalidad'] for unidad_mortalidad in response_reporte_mortalidad.data.get('data', []) if unidad_mortalidad['id_vivero']==item['id_vivero']]
                
                item['salidas'] = {
                    'unidades_despachadas': unidades_despachadas[0] if unidades_despachadas else None,
                    'unidades_mortalidad': unidades_mortalidad[0] if unidades_mortalidad else None
                }
                
                cantidades_produccion = cantidad_actual.filter(id_vivero=item['id_vivero'], cod_etapa_lote='P').aggregate(
                    cantidad_entrante_total=Sum('cantidad_entrante'),
                    cantidad_bajas_total=Sum('cantidad_bajas'),
                    cantidad_traslados_lote_produccion_distribucion_total=Sum('cantidad_traslados_lote_produccion_distribucion'),
                    cantidad_lote_cuarentena_total=Sum('cantidad_lote_cuarentena'),
                )
                
                cantidades_distribucion = cantidad_actual.filter(id_vivero=item['id_vivero'], cod_etapa_lote='D').aggregate(
                    cantidad_entrante_total=Sum('cantidad_entrante'),
                    cantidad_bajas_total=Sum('cantidad_bajas'),
                    cantidad_lote_cuarentena_total=Sum('cantidad_lote_cuarentena'),
                )
                
                cantidad_entrante_total_produccion = cantidades_produccion['cantidad_entrante_total'] if cantidades_produccion['cantidad_entrante_total'] else 0
                cantidad_bajas_total_produccion = cantidades_produccion['cantidad_bajas_total'] if cantidades_produccion['cantidad_bajas_total'] else 0
                cantidad_traslados_lote_produccion_distribucion_total_produccion = cantidades_produccion['cantidad_traslados_lote_produccion_distribucion_total'] if cantidades_produccion['cantidad_traslados_lote_produccion_distribucion_total'] else 0
                cantidad_lote_cuarentena_total = cantidades_produccion['cantidad_lote_cuarentena_total'] if cantidades_produccion['cantidad_lote_cuarentena_total'] else 0
                
                cantidad_entrante_total_distribucion = cantidades_distribucion['cantidad_entrante_total'] if cantidades_distribucion['cantidad_entrante_total'] else 0
                cantidad_bajas_total_distribucion = cantidades_distribucion['cantidad_bajas_total'] if cantidades_distribucion['cantidad_bajas_total'] else 0
                cantidad_lote_cuarentena_total_distribucion = cantidades_distribucion['cantidad_lote_cuarentena_total'] if cantidades_distribucion['cantidad_lote_cuarentena_total'] else 0
                
                item['actualidad'] = {
                    'cantidad_produccion': cantidad_entrante_total_produccion - cantidad_bajas_total_produccion - cantidad_traslados_lote_produccion_distribucion_total_produccion - cantidad_lote_cuarentena_total,
                    'cantidad_distribucion': cantidad_entrante_total_distribucion - cantidad_bajas_total_distribucion - cantidad_lote_cuarentena_total_distribucion
                }
                
                data_response.append(item)
                
            data = data_response
            
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data}, status=status.HTTP_200_OK)

class ReporteActividadLoteGetView(generics.ListAPIView):
    serializer_class=ConsumosIncidenciasGetSerializer
    queryset=IncidenciasMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        agno_lote = request.query_params.get('agno_lote', '')
        nro_lote = request.query_params.get('nro_lote', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if id_vivero == '' or id_bien == '' or agno_lote == '' or nro_lote == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir el vivero, una planta, el año del lote, número de lote y las fechas como filtros')
        
        incidencias = self.queryset.filter(id_vivero=id_vivero, id_bien=id_bien, agno_lote=agno_lote, nro_lote=nro_lote, fecha_incidencia__gte=fecha_desde, fecha_incidencia__lte=fecha_hasta)
        incidencias_data = incidencias.values(
            'id_incidencias_mat_vegetal',
            'fecha_incidencia',
            'fecha_registro',
            'nombre_incidencia',
            'cod_tipo_incidencia',
            'descripcion',
            consecutivo=F('consec_por_lote_etapa')
        )
        
        for incidencia in incidencias_data:
            consumos_incidencias = ConsumosIncidenciasMV.objects.filter(id_incidencia_mat_vegetal=incidencia['id_incidencias_mat_vegetal'])
            consumos_incidencias_serializer = self.serializer_class(consumos_incidencias, many=True)

            incidencia['tipo_incidencia'] = 'Seguimiento' if incidencia['cod_tipo_incidencia'] == 'S' else 'Actividad'
            incidencia['bienes_consumidos'] = consumos_incidencias_serializer.data
            
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':incidencias_data}, status=status.HTTP_200_OK)

class BienesInventarioFilterGetView(generics.ListAPIView):
    serializer_class = GetBienesInventarioSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
        filter = {}
        id_vivero = request.query_params.get('id_vivero', '')
        
        if id_vivero == '':
            raise ValidationError('Debe elegir un vivero antes de realizar la búsqueda de plantas')
        
        for key,value in request.query_params.items():
            if key in ['nombre','agno_lote','nro_lote']:
                if key == 'nombre':
                    if value != "":
                        filter['id_bien__'+key+'__icontains'] = value
                else:
                    if value != "":
                        filter[key] = value
            
        bienes = self.queryset.filter(**filter).filter(id_vivero=id_vivero, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).distinct('agno_lote','nro_lote')
        bienes_serializer = self.serializer_class(bienes, many=True)
        
        return Response({'success':True,'detail':'Se encontraron las siguientes plantas','data':bienes_serializer.data},status=status.HTTP_200_OK)

class HistoricoBajasGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        bajas = self.queryset.filter(tipo_baja='B', fecha_baja__gte=fecha_desde, fecha_baja__lte=fecha_hasta, baja_anulado=False)
        bajas = bajas.filter(id_vivero=id_vivero) if id_vivero != '' else bajas
        bajas = bajas.values(
            'id_baja',
            'fecha_baja',
            'fecha_registro',
            'id_vivero',
            'nro_baja_por_tipo',
            nombre_vivero=F('id_vivero__nombre')
        )
        
        for baja in bajas:
            items_bajas = ItemsBajasVivero.objects.filter(id_baja=baja['id_baja'])
            items_bajas = items_bajas.filter(id_bien=id_bien) if id_bien != '' else items_bajas
            items_bajas = items_bajas.filter(
                Q(id_bien__cod_tipo_elemento_vivero='IN') | 
                Q(id_bien__cod_tipo_elemento_vivero='HE') | 
                (Q(id_bien__cod_tipo_elemento_vivero='MV') & Q(id_bien__es_semilla_vivero=True))
            )
            
            baja['bienes_implicados'] = items_bajas.values(
                'id_bien',
                'cantidad_baja',
                nombre_bien=F('id_bien__nombre'),
                unidad_medida=F('id_bien__id_unidad_medida__abreviatura')
            )
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':bajas}, status=status.HTTP_200_OK)

class HistoricoDistribucionesGetView(generics.ListAPIView):
    serializer_class=HistoricoDistribucionesGetSerializer
    queryset=DistribucionesItemDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        distribuciones = self.queryset.filter(fecha_distribucion__gte=fecha_desde, fecha_distribucion__lte=fecha_hasta)
        distribuciones = distribuciones.filter(id_vivero=id_vivero) if id_vivero != '' else distribuciones
        distribuciones = distribuciones.filter(id_item_despacho_entrante__id_bien__id_bien=id_bien) if id_bien else distribuciones
        
        distribuciones_serializer = self.serializer_class(distribuciones, many=True)
        distribuciones = distribuciones_serializer.data
        
        distribuciones_data = sorted(distribuciones, key=operator.itemgetter("fecha_distribucion", "id_vivero", "nombre_vivero", "numero_despacho"))
        data_output = []
        
        for fechas_distribucion, bienes in itertools.groupby(distribuciones_data, key=operator.itemgetter("fecha_distribucion", "id_vivero", "nombre_vivero", "numero_despacho")):
            bienes_distribuidos = list(bienes)
            for bien_distribuido in bienes_distribuidos:
                del bien_distribuido['fecha_distribucion']
                del bien_distribuido['id_vivero']
                del bien_distribuido['nombre_vivero']
                del bien_distribuido['numero_despacho']
                
            items_data = {
                "fecha_distribucion": fechas_distribucion[0],
                "id_vivero": fechas_distribucion[1],
                "nombre_vivero": fechas_distribucion[2],
                "numero_despacho": fechas_distribucion[3],
                "bienes_distribuidos": bienes_distribuidos
            }
            
            data_output.append(items_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data_output}, status=status.HTTP_200_OK)

class HistoricoSiembrasGetView(generics.ListAPIView):
    serializer_class=HistoricoSiembrasGetSerializer
    queryset=Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        siembras = self.queryset.filter(fecha_siembra__gte=fecha_desde, fecha_siembra__lte=fecha_hasta)
        siembras = siembras.filter(id_vivero=id_vivero) if id_vivero != '' else siembras
        siembras = siembras.filter(id_bien_sembrado__id_bien=id_bien) if id_bien else siembras
        
        siembras_serializer = self.serializer_class(siembras, many=True)
        siembras = siembras_serializer.data
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':siembras}, status=status.HTTP_200_OK)

class HistoricoCambiosEtapaGetView(generics.ListAPIView):
    serializer_class=HistoricoCambiosEtapaGetSerializer
    queryset=CambiosDeEtapa.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        cambios_etapa = self.queryset.filter(fecha_cambio__gte=fecha_desde, fecha_cambio__lte=fecha_hasta)
        cambios_etapa = cambios_etapa.filter(id_vivero=id_vivero) if id_vivero != '' else cambios_etapa
        cambios_etapa = cambios_etapa.filter(id_bien=id_bien) if id_bien else cambios_etapa
        
        cambios_etapa_serializer = self.serializer_class(cambios_etapa, many=True)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':cambios_etapa_serializer.data}, status=status.HTTP_200_OK)

class HistoricoIngresoCuarentenaGetView(generics.ListAPIView):
    serializer_class=HistoricoIngresoCuarentenaGetSerializer
    queryset=CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        ingresos_cuarentena = self.queryset.filter(fecha_cuarentena__gte=fecha_desde, fecha_cuarentena__lte=fecha_hasta)
        ingresos_cuarentena = ingresos_cuarentena.filter(id_vivero=id_vivero) if id_vivero != '' else ingresos_cuarentena
        ingresos_cuarentena = ingresos_cuarentena.filter(id_bien=id_bien) if id_bien else ingresos_cuarentena
        
        ingresos_cuarentena_serializer = self.serializer_class(ingresos_cuarentena, many=True)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':ingresos_cuarentena_serializer.data}, status=status.HTTP_200_OK)

class HistoricoLevantamientoCuarentenaGetView(generics.ListAPIView):
    serializer_class=HistoricoLevantamientoCuarentenaGetSerializer
    queryset=ItemsLevantaCuarentena.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        items_levanta_cuarentena = self.queryset.filter(fecha_levantamiento__gte=fecha_desde, fecha_levantamiento__lte=fecha_hasta)
        items_levanta_cuarentena = items_levanta_cuarentena.filter(id_cuarentena_mat_vegetal__id_vivero=id_vivero) if id_vivero != '' else items_levanta_cuarentena
        items_levanta_cuarentena = items_levanta_cuarentena.filter(id_cuarentena_mat_vegetal__id_bien=id_bien) if id_bien else items_levanta_cuarentena
        
        items_levanta_cuarentena_serializer = self.serializer_class(items_levanta_cuarentena, many=True)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':items_levanta_cuarentena_serializer.data}, status=status.HTTP_200_OK)

class HistoricoTrasladosGetView(generics.ListAPIView):
    serializer_class=HistoricoTrasladosGetSerializer
    queryset=ItemsTrasladoViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_vivero = request.query_params.get('id_vivero', '')
        id_bien = request.query_params.get('id_bien', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir las fechas como filtros')
        
        items_traslados = self.queryset.filter(id_traslado__fecha_traslado__gte=fecha_desde, id_traslado__fecha_traslado__lte=fecha_hasta).exclude(id_traslado__traslado_anulado=True)
        items_traslados = items_traslados.filter(Q(id_traslado__id_vivero_destino=id_vivero) | Q(id_traslado__id_vivero_origen=id_vivero)) if id_vivero != '' else items_traslados
        items_traslados = items_traslados.filter(id_bien_origen=id_bien) if id_bien else items_traslados
        
        items_traslados_serializer = self.serializer_class(items_traslados, many=True)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':items_traslados_serializer.data}, status=status.HTTP_200_OK)

class AnaliticaMortalidadTiempoGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_bien = request.query_params.get('id_bien', '')
        id_vivero = request.query_params.get('id_vivero', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if id_vivero == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir viveros y fechas como filtros')
        
        mortalidades = self.queryset.filter(tipo_baja='M', baja_anulado=False, fecha_baja__gte=fecha_desde, fecha_baja__lte=fecha_hasta)
        mortalidades = mortalidades.filter(id_vivero__in=id_vivero.split(',')) if id_vivero else mortalidades
        mortalidades_list = [mortalidad.id_baja for mortalidad in mortalidades]
        
        output_list = []
        
        if mortalidades_list:
            items_mortalidad = ItemsBajasVivero.objects.filter(id_baja__in=mortalidades_list)
            items_mortalidad = items_mortalidad.filter(id_bien=id_bien) if id_bien != '' else items_mortalidad
            
            if id_bien != '':
                items_mortalidad = items_mortalidad.values('id_bien', nombre_bien=F('id_bien__nombre'), id_vivero=F('id_baja__id_vivero__id_vivero'), nombre_vivero=F('id_baja__id_vivero__nombre'), fecha_baja=F('id_baja__fecha_baja__date')).annotate(
                    cantidad = Sum('cantidad_baja')
                )
                
                items_mortalidad_data = sorted(items_mortalidad, key=operator.itemgetter("id_bien", "nombre_bien"))

                for item_mortalidad, cantidades in itertools.groupby(items_mortalidad_data, key=operator.itemgetter("id_bien", "nombre_bien")):
                    cantidades_tiempo = list(cantidades)
                    for cantidad_tiempo in cantidades_tiempo:
                        del cantidad_tiempo['id_bien']
                        del cantidad_tiempo['nombre_bien']
                        
                    items_data = {
                        "id_bien": item_mortalidad[0],
                        "nombre_bien": item_mortalidad[1],
                        "cantidades_tiempo": []
                    }
                    
                    group_viveros_data = sorted(cantidades_tiempo, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                    for vivero, cantidades_vivero in itertools.groupby(group_viveros_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                        fechas_vivero = list(cantidades_vivero)
                        for fecha_vivero in fechas_vivero:
                            del fecha_vivero['id_vivero']
                            del fecha_vivero['nombre_vivero']
                            
                        fechas_vivero_data = {
                            "id_vivero": vivero[0],
                            "nombre_vivero": vivero[1],
                            "fechas": fechas_vivero
                        }
                        
                        items_data['cantidades_tiempo'].append(fechas_vivero_data)
                        
                    output_list = items_data
                
            else:
                items_mortalidad = items_mortalidad.values(id_vivero=F('id_baja__id_vivero__id_vivero'), nombre_vivero=F('id_baja__id_vivero__nombre'), fecha_baja=F('id_baja__fecha_baja__date')).annotate(
                    cantidad = Sum('cantidad_baja')
                )
            
                items_mortalidad_data = sorted(items_mortalidad, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                output_list = {
                    "id_bien": None,
                    "nombre_bien": "Todas las plantas",
                    "cantidades_tiempo": []
                }
                
                for vivero, cantidades_vivero in itertools.groupby(items_mortalidad_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                    fechas_vivero = list(cantidades_vivero)
                    for fecha_vivero in fechas_vivero:
                        del fecha_vivero['id_vivero']
                        del fecha_vivero['nombre_vivero']
                        
                    fechas_vivero_data = {
                        "id_vivero": vivero[0],
                        "nombre_vivero": vivero[1],
                        "fechas": fechas_vivero
                    }
                    
                    output_list['cantidades_tiempo'].append(fechas_vivero_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':output_list}, status=status.HTTP_200_OK)

class AnaliticaBajasTiempoGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=BajasVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        cod_tipo_elemento_vivero = request.query_params.get('cod_tipo_elemento_vivero', '')
        id_vivero = request.query_params.get('id_vivero', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        cod_tipo_elemento_vivero_list = cod_tipo_elemento_vivero.split(',')
        
        if id_vivero == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir viveros y fechas como filtros')
        
        bajas = self.queryset.filter(tipo_baja='B', baja_anulado=False, fecha_baja__gte=fecha_desde, fecha_baja__lte=fecha_hasta)
        bajas = bajas.filter(id_vivero__in=id_vivero.split(',')) if id_vivero else bajas
        bajas_list = [baja.id_baja for baja in bajas]
        
        output_list = []
            
        if bajas_list:
            items_mortalidad = ItemsBajasVivero.objects.filter(id_baja__in=bajas_list)
            if cod_tipo_elemento_vivero != '':
                items_mortalidad_cod_tipo_elementos_vivero = None
                if 'HE' in cod_tipo_elemento_vivero_list:
                    items_mortalidad_he = items_mortalidad.filter(
                        Q(id_bien__cod_tipo_elemento_vivero='HE')
                    )
                    items_mortalidad_cod_tipo_elementos_vivero = items_mortalidad_he
                
                if 'IN' in cod_tipo_elemento_vivero_list:
                    items_mortalidad_in = items_mortalidad.filter(
                        Q(id_bien__cod_tipo_elemento_vivero='IN')
                    )
                    items_mortalidad_cod_tipo_elementos_vivero = items_mortalidad_in if not items_mortalidad_cod_tipo_elementos_vivero else items_mortalidad_cod_tipo_elementos_vivero | items_mortalidad_in
                
                if 'SE' in cod_tipo_elemento_vivero_list:
                    items_mortalidad_se = items_mortalidad.filter(
                        id_bien__cod_tipo_elemento_vivero='MV',
                        id_bien__es_semilla_vivero=True 
                    )
                    items_mortalidad_cod_tipo_elementos_vivero = items_mortalidad_se if not items_mortalidad_cod_tipo_elementos_vivero else items_mortalidad_cod_tipo_elementos_vivero | items_mortalidad_se
                
                if 'PL' in cod_tipo_elemento_vivero_list:
                    items_mortalidad_pl = items_mortalidad.filter(
                        id_bien__cod_tipo_elemento_vivero='MV',
                        id_bien__es_semilla_vivero=False 
                    )
                    items_mortalidad_cod_tipo_elementos_vivero = items_mortalidad_pl if not items_mortalidad_cod_tipo_elementos_vivero else items_mortalidad_cod_tipo_elementos_vivero | items_mortalidad_pl
            
                items_mortalidad = items_mortalidad_cod_tipo_elementos_vivero.values(id_vivero=F('id_baja__id_vivero__id_vivero'), nombre_vivero=F('id_baja__id_vivero__nombre'), fecha_baja=F('id_baja__fecha_baja__date')).annotate(
                    cantidad = Sum('cantidad_baja')
                )
                
            else:
                items_mortalidad = items_mortalidad.values(id_vivero=F('id_baja__id_vivero__id_vivero'), nombre_vivero=F('id_baja__id_vivero__nombre'), fecha_baja=F('id_baja__fecha_baja__date')).annotate(
                    cantidad = Sum('cantidad_baja')
                )
            
            items_mortalidad_data = sorted(items_mortalidad, key=operator.itemgetter("id_vivero", "nombre_vivero"))
            
            for vivero, cantidades_vivero in itertools.groupby(items_mortalidad_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                fechas_vivero = list(cantidades_vivero)
                for fecha_vivero in fechas_vivero:
                    del fecha_vivero['id_vivero']
                    del fecha_vivero['nombre_vivero']
                    
                fechas_vivero_data = {
                    "id_vivero": vivero[0],
                    "nombre_vivero": vivero[1],
                    "fechas": fechas_vivero
                }
                    
                output_list.append(fechas_vivero_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':output_list}, status=status.HTTP_200_OK)

class AnaliticaCuarentenaGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_bien = request.query_params.get('id_bien', '')
        id_vivero = request.query_params.get('id_vivero', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if id_vivero == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir viveros y fechas como filtros')
        
        cuarentenas = self.queryset.filter(cuarentena_anulada=False, fecha_cuarentena__gte=fecha_desde, fecha_cuarentena__lte=fecha_hasta)
        cuarentenas = cuarentenas.filter(id_vivero__in=id_vivero.split(',')) if id_vivero else cuarentenas
        cuarentenas = cuarentenas.filter(id_bien=id_bien) if id_bien != '' else cuarentenas
        
        output_list = []
        
        if cuarentenas:
            if id_bien != '':
                cuarentenas_cantidades = cuarentenas.values('id_bien', 'id_vivero', nombre_bien=F('id_bien__nombre'), nombre_vivero=F('id_vivero__nombre'), fecha_cuarentena_date=F('fecha_cuarentena__date')).annotate(
                    cantidad = Sum('cantidad_cuarentena')
                )
                
                cuarentenas_data = sorted(cuarentenas_cantidades, key=operator.itemgetter("id_bien", "nombre_bien"))

                for item_cuarentena, cantidades in itertools.groupby(cuarentenas_data, key=operator.itemgetter("id_bien", "nombre_bien")):
                    cantidades_tiempo = list(cantidades)
                    for cantidad_tiempo in cantidades_tiempo:
                        del cantidad_tiempo['id_bien']
                        del cantidad_tiempo['nombre_bien']
                        
                    items_data = {
                        "id_bien": item_cuarentena[0],
                        "nombre_bien": item_cuarentena[1],
                        "cantidades_tiempo": []
                    }
                    
                    group_viveros_data = sorted(cantidades_tiempo, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                    for vivero, cantidades_vivero in itertools.groupby(group_viveros_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                        fechas_vivero = list(cantidades_vivero)
                        for fecha_vivero in fechas_vivero:
                            del fecha_vivero['id_vivero']
                            del fecha_vivero['nombre_vivero']
                            
                        fechas_vivero_data = {
                            "id_vivero": vivero[0],
                            "nombre_vivero": vivero[1],
                            "fechas": fechas_vivero
                        }
                        
                        items_data['cantidades_tiempo'].append(fechas_vivero_data)
                        
                    output_list = items_data
            else:
                cuarentenas_cantidades = cuarentenas.values('id_vivero', nombre_vivero=F('id_vivero__nombre'), fecha_cuarentena_date=F('fecha_cuarentena__date')).annotate(
                    cantidad = Sum('cantidad_cuarentena')
                )
                
                cuarentenas_data = sorted(cuarentenas_cantidades, key=operator.itemgetter("id_vivero", "nombre_vivero"))
                
                output_list = {
                    "id_bien": None,
                    "nombre_bien": "Todas las plantas",
                    "cantidades_tiempo": []
                }
                
                for vivero, cantidades_vivero in itertools.groupby(cuarentenas_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                    fechas_vivero = list(cantidades_vivero)
                    for fecha_vivero in fechas_vivero:
                        del fecha_vivero['id_vivero']
                        del fecha_vivero['nombre_vivero']
                        
                    fechas_vivero_data = {
                        "id_vivero": vivero[0],
                        "nombre_vivero": vivero[1],
                        "fechas": fechas_vivero
                    }
                    
                    output_list['cantidades_tiempo'].append(fechas_vivero_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':output_list}, status=status.HTTP_200_OK)

class AnaliticaDespachosGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=DespachoViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_bien = request.query_params.get('id_bien', '')
        id_vivero = request.query_params.get('id_vivero', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if id_vivero == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir viveros y fechas como filtros')
        
        despachos = self.queryset.filter(fecha_despacho__gte=fecha_desde, fecha_despacho__lte=fecha_hasta)
        despachos = despachos.filter(id_vivero__in=id_vivero.split(',')) if id_vivero else despachos
        despachos_list = [despacho.id_despacho_viveros for despacho in despachos]
        
        output_list = []
        
        if despachos_list:
            items_despacho = ItemsDespachoViveros.objects.filter(id_despacho_viveros__in=despachos_list)
            items_despacho = items_despacho.filter(id_bien=id_bien) if id_bien != '' else items_despacho
            
            if id_bien != '':
                items_despacho = items_despacho.values('id_bien', nombre_bien=F('id_bien__nombre'), id_vivero=F('id_despacho_viveros__id_vivero__id_vivero'), nombre_vivero=F('id_despacho_viveros__id_vivero__nombre'), fecha_despacho=F('id_despacho_viveros__fecha_despacho__date')).annotate(
                    cantidad = Sum('cantidad_despachada')
                )
                
                items_despacho_data = sorted(items_despacho, key=operator.itemgetter("id_bien", "nombre_bien"))

                for item_despacho, cantidades in itertools.groupby(items_despacho_data, key=operator.itemgetter("id_bien", "nombre_bien")):
                    cantidades_tiempo = list(cantidades)
                    for cantidad_tiempo in cantidades_tiempo:
                        del cantidad_tiempo['id_bien']
                        del cantidad_tiempo['nombre_bien']
                        
                    items_data = {
                        "id_bien": item_despacho[0],
                        "nombre_bien": item_despacho[1],
                        "cantidades_tiempo": []
                    }
                    
                    group_viveros_data = sorted(cantidades_tiempo, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                    for vivero, cantidades_vivero in itertools.groupby(group_viveros_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                        fechas_vivero = list(cantidades_vivero)
                        for fecha_vivero in fechas_vivero:
                            del fecha_vivero['id_vivero']
                            del fecha_vivero['nombre_vivero']
                            
                        fechas_vivero_data = {
                            "id_vivero": vivero[0],
                            "nombre_vivero": vivero[1],
                            "fechas": fechas_vivero
                        }
                        
                        items_data['cantidades_tiempo'].append(fechas_vivero_data)
                        
                    output_list = items_data
            else:
                items_despacho = items_despacho.values(id_vivero=F('id_despacho_viveros__id_vivero__id_vivero'), nombre_vivero=F('id_despacho_viveros__id_vivero__nombre'), fecha_despacho=F('id_despacho_viveros__fecha_despacho__date')).annotate(
                    cantidad = Sum('cantidad_despachada')
                )
                
                items_despacho_data = sorted(items_despacho, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                output_list = {
                    "id_bien": None,
                    "nombre_bien": "Todas las plantas",
                    "cantidades_tiempo": []
                }
                
                for vivero, cantidades_vivero in itertools.groupby(items_despacho_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                    fechas_vivero = list(cantidades_vivero)
                    for fecha_vivero in fechas_vivero:
                        del fecha_vivero['id_vivero']
                        del fecha_vivero['nombre_vivero']
                        
                    fechas_vivero_data = {
                        "id_vivero": vivero[0],
                        "nombre_vivero": vivero[1],
                        "fechas": fechas_vivero
                    }
                    
                    output_list['cantidades_tiempo'].append(fechas_vivero_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':output_list}, status=status.HTTP_200_OK)

class AnaliticaSolicitudesGetView(generics.ListAPIView):
    serializer_class=GetTableroControlConservacionSerializer
    queryset=SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        id_bien = request.query_params.get('id_bien', '')
        id_vivero = request.query_params.get('id_vivero', '')
        fecha_desde = request.query_params.get('fecha_desde', '')
        fecha_hasta = request.query_params.get('fecha_hasta', '')
        
        if id_vivero == '' or fecha_desde == '' or fecha_hasta == '':
            raise ValidationError('Debe elegir viveros y fechas como filtros')
        
        solicitudes = self.queryset.filter(solicitud_anulada_solicitante=False, fecha_solicitud__gte=fecha_desde, fecha_solicitud__lte=fecha_hasta)
        solicitudes = solicitudes.filter(id_vivero_solicitud__in=id_vivero.split(',')) if id_vivero else solicitudes
        solicitudes_list = [solicitud.id_solicitud_vivero for solicitud in solicitudes]
        
        output_list = []
        
        if solicitudes_list:
            items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros__in=solicitudes_list)
            items_solicitud = items_solicitud.filter(id_bien=id_bien) if id_bien != '' else items_solicitud
            
            if id_bien != '':
                items_solicitud = items_solicitud.values('id_bien', nombre_bien=F('id_bien__nombre'), id_vivero=F('id_solicitud_viveros__id_vivero_solicitud__id_vivero'), nombre_vivero=F('id_solicitud_viveros__id_vivero_solicitud__nombre'), fecha_solicitud=F('id_solicitud_viveros__fecha_solicitud__date')).annotate(
                    cantidad = Count('id_item_solicitud_viveros')
                )
                
                items_solicitud_data = sorted(items_solicitud, key=operator.itemgetter("id_bien", "nombre_bien"))

                for item_solicitud, cantidades in itertools.groupby(items_solicitud_data, key=operator.itemgetter("id_bien", "nombre_bien")):
                    cantidades_tiempo = list(cantidades)
                    for cantidad_tiempo in cantidades_tiempo:
                        del cantidad_tiempo['id_bien']
                        del cantidad_tiempo['nombre_bien']
                        
                    items_data = {
                        "id_bien": item_solicitud[0],
                        "nombre_bien": item_solicitud[1],
                        "cantidades_tiempo": []
                    }
                    
                    group_viveros_data = sorted(cantidades_tiempo, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                    for vivero, cantidades_vivero in itertools.groupby(group_viveros_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                        fechas_vivero = list(cantidades_vivero)
                        for fecha_vivero in fechas_vivero:
                            del fecha_vivero['id_vivero']
                            del fecha_vivero['nombre_vivero']
                            
                        fechas_vivero_data = {
                            "id_vivero": vivero[0],
                            "nombre_vivero": vivero[1],
                            "fechas": fechas_vivero
                        }
                        
                        items_data['cantidades_tiempo'].append(fechas_vivero_data)
                        
                    output_list = items_data
            else:
                items_solicitud = items_solicitud.values(id_vivero=F('id_solicitud_viveros__id_vivero_solicitud__id_vivero'), nombre_vivero=F('id_solicitud_viveros__id_vivero_solicitud__nombre'), fecha_solicitud=F('id_solicitud_viveros__fecha_solicitud__date')).annotate(
                    cantidad = Count('id_item_solicitud_viveros')
                )
                
                items_solicitud_data = sorted(items_solicitud, key=operator.itemgetter("id_vivero", "nombre_vivero"))

                output_list = {
                    "id_bien": None,
                    "nombre_bien": "Todas las plantas",
                    "cantidades_tiempo": []
                }

                for vivero, cantidades_vivero in itertools.groupby(items_solicitud_data, key=operator.itemgetter("id_vivero", "nombre_vivero")):
                    fechas_vivero = list(cantidades_vivero)
                    for fecha_vivero in fechas_vivero:
                        del fecha_vivero['id_vivero']
                        del fecha_vivero['nombre_vivero']
                        
                    fechas_vivero_data = {
                        "id_vivero": vivero[0],
                        "nombre_vivero": vivero[1],
                        "fechas": fechas_vivero
                    }
                    
                    output_list['cantidades_tiempo'].append(fechas_vivero_data)
        
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':output_list}, status=status.HTTP_200_OK)
