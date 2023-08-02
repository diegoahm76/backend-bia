from conservacion.models.cuarentena_models import BajasVivero, CuarentenaMatVegetal, ItemsLevantaCuarentena
from conservacion.models.despachos_models import DespachoEntrantes, DespachoViveros, DistribucionesItemDespachoEntrante
from conservacion.models.siembras_models import CambiosDeEtapa, Siembras
from conservacion.models.solicitudes_models import SolicitudesViveros
from conservacion.models.traslados_models import TrasladosViveros
from conservacion.serializers.analitica_serializers import GetBienesMezclasSerializer, GetTableroControlConservacionSerializer
from rest_framework import generics, status
from django.db.models import Q, F
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
            if key in ['id_vivero','cod_tipo_elemento_vivero','cod_etapa_lote','id_bien']:
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
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
        filter = {}
        nombre = request.query_params.get('nombre', '')
        for key,value in request.query_params.items():
            if key in ['id_vivero','cod_tipo_elemento_vivero','cod_etapa_lote','codigo_bien']:
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
                elif key == 'codigo_bien':
                    if value != '':
                        filter['id_bien__codigo_bien__icontains'] = value
                else:
                    if value != '':
                        filter[key]=value
            
        bienes = self.queryset.filter(**filter).filter(id_vivero__activo=True).filter(Q(id_bien__isnull=False) | Q(id_mezcla__isnull=False)).exclude(siembra_lote_cerrada=True).order_by('id_vivero__nombre', 'id_bien__nombre')
        bienes = bienes.filter(Q(id_bien__nombre__icontains=nombre) | Q(id_mezcla__nombre__icontains=nombre)) if nombre != '' else bienes
        
        serializador = self.serializer_class(bienes, many=True)
        serializador_data = serializador.data
        
        return Response({'success':True,'detail':'Se encontraron los siguientes bienes/mezclas','data':serializador_data},status=status.HTTP_200_OK)

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