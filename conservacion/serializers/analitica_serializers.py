from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.cuarentena_models import CuarentenaMatVegetal, ItemsLevantaCuarentena
from conservacion.models.despachos_models import DistribucionesItemDespachoEntrante
from conservacion.models.incidencias_models import ConsumosIncidenciasMV

from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.siembras_models import CambiosDeEtapa, ConsumosSiembra, Siembras
from conservacion.models.traslados_models import ItemsTrasladoViveros, TrasladosViveros

class GetTableroControlConservacionSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien = serializers.SerializerMethodField()
    tipo_bien = serializers.SerializerMethodField()
    unidad_disponible = serializers.SerializerMethodField()
    cantidad_existente = serializers.SerializerMethodField()
    cantidad_cuarentena = serializers.SerializerMethodField()
    etapa_lote = serializers.SerializerMethodField()
    origen = serializers.SerializerMethodField()
    
    def get_nombre_bien(self,obj):
        if obj.id_bien:
            nombre_bien = obj.id_bien.nombre
        else:
            nombre_bien = obj.id_mezcla.nombre
            
        return nombre_bien

    def get_unidad_disponible(self,obj):
        if obj.id_bien:
            unidad_disponible = obj.id_bien.id_unidad_medida.abreviatura
        else:
            unidad_disponible = obj.id_mezcla.id_unidad_medida.abreviatura
            
        return unidad_disponible
    
    def get_etapa_lote(self,obj):
        desc_etapa_lotes = {'G':'Germinación', 'P':'Producción', 'D':'Distribución'}
        desc_etapa_lote = desc_etapa_lotes[obj.cod_etapa_lote] if obj.cod_etapa_lote else None
        return desc_etapa_lote

    def get_tipo_bien(self, obj):
        if obj.id_bien:
            if obj.id_bien.cod_tipo_elemento_vivero == 'IN':
                tipo_bien = 'Insumo'
            elif obj.id_bien.cod_tipo_elemento_vivero == 'HE':
                tipo_bien = 'Herramienta'
            elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == True:
                tipo_bien = 'Semilla'
            elif obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False:
                tipo_bien = 'Planta'
        else:
            tipo_bien = 'Mezcla'
            
        return tipo_bien
    
    def get_cantidad_existente(self, obj):
        inventario_vivero = InventarioViveros.objects.filter(id_bien=obj.id_bien, id_vivero=obj.id_vivero, agno_lote=obj.agno_lote, nro_lote=obj.nro_lote, cod_etapa_lote=obj.cod_etapa_lote).first()
        
        porc_cuarentena_lote_germinacion = inventario_vivero.porc_cuarentena_lote_germinacion if inventario_vivero.porc_cuarentena_lote_germinacion else 0
        cantidad_entrante = inventario_vivero.cantidad_entrante if inventario_vivero.cantidad_entrante else 0
        cantidad_bajas = inventario_vivero.cantidad_bajas if inventario_vivero.cantidad_bajas else 0
        cantidad_traslados_lote_produccion_distribucion = inventario_vivero.cantidad_traslados_lote_produccion_distribucion if inventario_vivero.cantidad_traslados_lote_produccion_distribucion else 0
        cantidad_salidas = inventario_vivero.cantidad_salidas if inventario_vivero.cantidad_salidas else 0
        cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena if inventario_vivero.cantidad_lote_cuarentena else 0
        cantidad_consumos_internos = inventario_vivero.cantidad_consumos_internos if inventario_vivero.cantidad_consumos_internos else 0
        
        cantidad_existente = 0
        
        if obj.id_bien:
            if obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False:
                if inventario_vivero.cod_etapa_lote == 'G':
                    cantidad_existente = 100 - porc_cuarentena_lote_germinacion
                if inventario_vivero.cod_etapa_lote == 'P':
                    cantidad_existente = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
                if inventario_vivero.cod_etapa_lote == 'D':
                    cantidad_existente = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena
            elif (obj.id_bien.cod_tipo_elemento_vivero == 'IN') or (obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False):
                cantidad_existente = cantidad_entrante - cantidad_bajas - cantidad_consumos_internos - cantidad_salidas
            elif obj.id_bien.cod_tipo_elemento_vivero == 'HE':
                cantidad_existente = cantidad_entrante - cantidad_bajas - cantidad_salidas
        elif obj.id_mezcla:
            cantidad_existente = cantidad_entrante - cantidad_bajas - cantidad_consumos_internos
            
        return cantidad_existente
    
    def get_cantidad_cuarentena(self, obj):
        cuarentena_planta = CuarentenaMatVegetal.objects.filter(id_bien=obj.id_bien, id_vivero=obj.id_vivero, agno_lote=obj.agno_lote, nro_lote=obj.nro_lote, cod_etapa_lote=obj.cod_etapa_lote).first() #id_siembra_lote_germinacion=None
        
        cantidad_cuarentena = 0
        
        if cuarentena_planta:
            cantidad_cuarentena_inv = cuarentena_planta.cantidad_cuarentena if cuarentena_planta.cantidad_cuarentena else 0
            cantidad_bajas = cuarentena_planta.cantidad_bajas if cuarentena_planta.cantidad_bajas else 0
            cantidad_levantada = cuarentena_planta.cantidad_levantada if cuarentena_planta.cantidad_levantada else 0
            
            cantidad_cuarentena = cantidad_cuarentena_inv - cantidad_bajas - cantidad_levantada
        else:
            cantidad_cuarentena = None
            
        return cantidad_cuarentena
    
    def get_origen(self,obj):
        if obj.cod_tipo_entrada_alm_lote:
            origen = obj.cod_tipo_entrada_alm_lote.nombre
        else:
            origen = 'Producción Propia' if obj.es_produccion_propia_lote else 'Compras/No Identificado'
            
        return origen

    class Meta:
        model = InventarioViveros
        fields = (
            'id_inventario_vivero',
            'id_vivero',
            'nombre_vivero',
            'id_bien',
            'id_mezcla',
            'nombre_bien',
            'tipo_bien',
            'unidad_disponible',
            'cantidad_existente',
            'cantidad_cuarentena',
            'cod_etapa_lote',
            'etapa_lote',
            'nro_lote',
            'agno_lote',
            'origen'
        )

class GetBienesMezclasSerializer(serializers.ModelSerializer):
    id_mezcla = serializers.SerializerMethodField()
    tipo_bien = serializers.SerializerMethodField()
    
    def get_id_mezcla(self,obj):
        return None
    
    def get_tipo_bien(self, obj):
        tipo_bien = None
        
        if obj.cod_tipo_elemento_vivero == 'IN':
            tipo_bien = 'Insumo'
        elif obj.cod_tipo_elemento_vivero == 'HE':
            tipo_bien = 'Herramienta'
        elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == True:
            tipo_bien = 'Semilla'
        elif obj.cod_tipo_elemento_vivero == 'MV' and obj.es_semilla_vivero == False:
            tipo_bien = 'Planta'
            
        return tipo_bien
            
    class Meta:
        fields = ['nombre','id_mezcla','id_bien','codigo_bien','tipo_bien','nombre_cientifico']
        model = CatalogoBienes
        
class GetBienesInventarioSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_cientifico = serializers.ReadOnlyField(source='id_bien.nombre_cientifico', default=None)
            
    class Meta:
        fields = ['nombre','id_bien','codigo_bien','nombre_cientifico','agno_lote','nro_lote']
        model = InventarioViveros
        
class ConsumosIncidenciasGetSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    unidad_medida = serializers.SerializerMethodField()
    
    def get_nombre(self,obj):
        if obj.id_bien:
            nombre = obj.id_bien.nombre
        else:
            nombre = obj.id_mezcla.nombre
            
        return nombre

    def get_unidad_medida(self,obj):
        if obj.id_bien:
            unidad_medida = obj.id_bien.id_unidad_medida.abreviatura
        else:
            unidad_medida = obj.id_mezcla.id_unidad_medida.abreviatura
            
        return unidad_medida
            
    class Meta:
        fields = ['nombre','unidad_medida','cantidad_consumida']
        model = ConsumosIncidenciasMV

class HistoricoDistribucionesGetSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    fecha_ingreso = serializers.ReadOnlyField(source='id_item_despacho_entrante.fecha_ingreso', default=None)
    etapa_ingresa = serializers.CharField(source='get_cod_etapa_lote_al_ingresar_display')
    fecha_distribucion = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    id_bien = serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.nombre', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_unidad_medida.abreviatura', default=None)
    numero_despacho = serializers.ReadOnlyField(source='id_item_despacho_entrante.id_despacho_entrante.id_despacho_consumo_alm.numero_despacho_consumo', default=None)
            
    class Meta:
        fields = [
            'id_distribucion_item_despacho_entrante',
            'cantidad_asignada',
            'id_vivero',
            'nombre_vivero',
            'numero_despacho',
            'fecha_distribucion',
            'fecha_ingreso',
            'etapa_ingresa',
            'id_bien',
            'nombre_bien',
            'unidad_medida'
        ]
        model = DistribucionesItemDespachoEntrante

class HistoricoSiembrasBienesConsumidosGetSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.SerializerMethodField()
    unidad_medida = serializers.SerializerMethodField()
    
    def get_nombre_bien(self,obj):
        if obj.id_bien_consumido:
            nombre_bien = obj.id_bien_consumido.nombre
        else:
            nombre_bien = obj.id_mezcla_consumida.nombre
            
        return nombre_bien
    
    def get_unidad_medida(self,obj):
        if obj.id_bien_consumido:
            unidad_medida = obj.id_bien_consumido.id_unidad_medida.abreviatura
        else:
            unidad_medida = obj.id_mezcla_consumida.id_unidad_medida.abreviatura
            
        return unidad_medida
    
    class Meta:
        model = ConsumosSiembra
        fields = (
            'id_consumo_siembra',
            'id_bien_consumido',
            'id_mezcla_consumida',
            'nombre_bien',
            'cantidad',
            'unidad_medida'
        )

class HistoricoSiembrasGetSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien_sembrado.nombre', default=None)
    bienes_consumidos = serializers.SerializerMethodField()
    
    def get_bienes_consumidos(self, obj):
        bienes_consumidos = ConsumosSiembra.objects.filter(id_siembra=obj.id_siembra)
        bienes_consumidos_serializer = HistoricoSiembrasBienesConsumidosGetSerializer(bienes_consumidos, many=True)
        return bienes_consumidos_serializer.data
    
    class Meta:
        model = Siembras
        fields = (
            'id_siembra',
            'fecha_siembra',
            'id_vivero',
            'nombre_vivero',
            'id_bien_sembrado',
            'nombre_bien',
            'distancia_entre_semillas',
            'nro_lote',
            'fecha_registro',
            'bienes_consumidos'
        )
        
class HistoricoCambiosEtapaGetSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    etapa_origen = serializers.CharField(source='get_cod_etapa_lote_origen_display', default=None)
    etapa_destino = serializers.SerializerMethodField()
    
    def get_etapa_destino(self, obj):
        etapa_destino = None
        if obj.cod_etapa_lote_origen == 'G':
            etapa_destino = 'Producción'
        elif obj.cod_etapa_lote_origen == 'P':
            etapa_destino = 'Distribución'
            
        return etapa_destino
    
    class Meta:
        model = CambiosDeEtapa
        fields = (
            'id_cambio_de_etapa',
            'fecha_cambio',
            'id_vivero',
            'nombre_vivero',
            'id_bien',
            'nombre_bien',
            'etapa_origen',
            'etapa_destino',
            'agno_lote',
            'nro_lote',
            'fecha_registro'
        )
        
class HistoricoIngresoCuarentenaGetSerializer(serializers.ModelSerializer):
    nombre_vivero = serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    etapa_lote = serializers.CharField(source='get_cod_etapa_lote_display', default=None)
    
    class Meta:
        model = CuarentenaMatVegetal
        fields = (
            'id_cuarentena_mat_vegetal',
            'fecha_cuarentena',
            'id_vivero',
            'nombre_vivero',
            'id_bien',
            'nombre_bien',
            'cantidad_cuarentena',
            'agno_lote',
            'nro_lote',
            'etapa_lote',
            'fecha_registro'
        )
        
class HistoricoLevantamientoCuarentenaGetSerializer(serializers.ModelSerializer):
    id_vivero = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.id_vivero.id_vivero', default=None)
    nombre_vivero = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.id_vivero.nombre', default=None)
    id_bien = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.id_bien.id_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.id_bien.nombre', default=None)
    agno_lote = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.agno_lote', default=None)
    nro_lote = serializers.ReadOnlyField(source='id_cuarentena_mat_vegetal.nro_lote', default=None)
    etapa_lote = serializers.CharField(source='id_cuarentena_mat_vegetal.get_cod_etapa_lote_display', default=None)
    
    class Meta:
        model = ItemsLevantaCuarentena
        fields = (
            'id_item_levanta_cuarentena',
            'fecha_levantamiento',
            'id_vivero',
            'nombre_vivero',
            'id_bien',
            'nombre_bien',
            'cantidad_a_levantar',
            'agno_lote',
            'nro_lote',
            'etapa_lote',
            'fecha_registro'
        )

class HistoricoTrasladosGetSerializer(serializers.ModelSerializer):
    fecha_traslado = serializers.ReadOnlyField(source='id_traslado.fecha_traslado', default=None)
    id_vivero_origen = serializers.ReadOnlyField(source='id_traslado.id_vivero_origen.id_vivero', default=None)
    nombre_vivero_origen = serializers.ReadOnlyField(source='id_traslado.id_vivero_origen.nombre', default=None)
    id_vivero_destino = serializers.ReadOnlyField(source='id_traslado.id_vivero_destino.id_vivero', default=None)
    nombre_vivero_destino = serializers.ReadOnlyField(source='id_traslado.id_vivero_destino.nombre', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien_origen.nombre', default=None)
    fecha_registro = serializers.ReadOnlyField(source='id_traslado.fecha_registro', default=None)
    
    class Meta:
        model = ItemsTrasladoViveros
        fields = (
            'id_item_traslado_viveros',
            'fecha_traslado',
            'id_bien_origen',
            'nombre_bien',
            'cantidad_a_trasladar',
            'id_vivero_origen',
            'nombre_vivero_origen',
            'agno_lote_origen',
            'nro_lote_origen',
            'id_vivero_destino',
            'nombre_vivero_destino',
            'agno_lote_destino_MV',
            'nro_lote_destino_MV',
            'fecha_registro'
        )