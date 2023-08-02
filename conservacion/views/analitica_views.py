from conservacion.serializers.analitica_serializers import GetBienesMezclasSerializer, GetTableroControlConservacionSerializer
from rest_framework import generics, status
from django.db.models import Q, Count, Sum
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