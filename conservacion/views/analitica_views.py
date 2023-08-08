from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.cuarentena_models import BajasVivero, CuarentenaMatVegetal, ItemsBajasVivero, ItemsLevantaCuarentena
from conservacion.models.despachos_models import DespachoEntrantes, DespachoViveros, DistribucionesItemDespachoEntrante, ItemsDespachoEntrante, ItemsDespachoViveros
from conservacion.models.mezclas_models import Mezclas
from conservacion.models.siembras_models import CambiosDeEtapa, Siembras
from conservacion.models.solicitudes_models import ItemSolicitudViveros, SolicitudesViveros
from conservacion.models.traslados_models import TrasladosViveros
from conservacion.serializers.analitica_serializers import GetBienesMezclasSerializer, GetTableroControlConservacionSerializer
from rest_framework import generics, status
from django.db.models import Q, F, Sum, Count
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated

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
            
            data.update(data_entradas[0])
            
            # Despachos
            # data_despachos = items_despachos.aggregate(
            #     cantidad_total_despachada=Sum('cantidad_despachada')
            # )
            # data['cantidad_total_despachada'] = data_despachos['cantidad_total_despachada']
            
            # data = [data]
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

            # Despachos
            # data_despachos = items_despachos.values(id_vivero=F('id_despacho_viveros__id_vivero')).annotate(
            #     numero_despachos=Count('id_vivero'),
            #     cantidad_total_despachada=Sum('cantidad_despachada')
            # )
            
            # for data_item in data:
            #     data_item['cantidad_total_despachada'] = [data_despacho for data_despacho in data_despachos if data_despacho['id_vivero'] == data_item['id_vivero']]
            #     data_item['cantidad_total_despachada'] = data_item['cantidad_total_despachada'][0]['cantidad_total_despachada'] if data_item['cantidad_total_despachada'] else None
            
        return Response({'success':True,'detail':'Se encontró la siguiente información','data':data}, status=status.HTTP_200_OK)