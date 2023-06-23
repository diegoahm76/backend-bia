from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.models.solicitudes_models import SolicitudesViveros, ItemSolicitudViveros
from conservacion.models.despachos_models import DespachoViveros, ItemsDespachoViveros
from conservacion.models.inventario_models import InventarioViveros

class DespachosEntrantesSerializer(serializers.ModelSerializer):
    numero_despacho_consumo = serializers.ReadOnlyField(source='id_despacho_consumo_alm.numero_despacho_consumo', default=None)
    
    class Meta:
        model = DespachoEntrantes
        fields = '__all__'
        
class ItemsDespachosEntrantesSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.id_tipo_entrada.nombre', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_entrada_alm_del_bien.numero_entrada_almacen', default=None)
    cantidad_restante = serializers.IntegerField(read_only=True, default=None)
    class Meta:
        model = ItemsDespachoEntrante
        fields = '__all__'
        
class DistribucionesItemDespachoEntranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistribucionesItemDespachoEntrante
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=DistribucionesItemDespachoEntrante.objects.all(),
                fields=['id_item_despacho_entrante', 'id_vivero'],
                message='El item despacho entrante y el vivero deben ser una pareja única'
            )
        ]
        
class DistribucionesItemPreDistribuidoSerializer(serializers.ModelSerializer):
    vivero_nombre=serializers.ReadOnlyField(source='id_vivero.nombre', default=None)
    nombre_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.nombre', default=None)
    codigo_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.codigo_bien', default=None)
    unidad_medida=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_unidad_medida.abreviatura', default=None)
    id_bien=serializers.ReadOnlyField(source='id_item_despacho_entrante.id_bien.id_bien', default=None)
    
    class Meta:
        model = DistribucionesItemDespachoEntrante
        fields = ['id_distribucion_item_despacho_entrante','id_vivero','id_bien','cantidad_asignada','cod_etapa_lote_al_ingresar','id_item_despacho_entrante','vivero_nombre','unidad_medida','codigo_bien','nombre_bien']

class SolicitudesParaDespachoSerializer(serializers.ModelSerializer):
    persona_solicita = serializers.SerializerMethodField()
    persona_responsable = serializers.SerializerMethodField()
    nombre_unidad_organizacional_destino = serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre', default=None)
    
    def get_persona_solicita(self, obj):
        nombre_completo_solicita = None
        nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                        obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
        nombre_completo_solicita = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_solicita = nombre_completo_solicita if nombre_completo_solicita != "" else None
        return nombre_completo_solicita
    
    def get_persona_responsable(self, obj):
        nombre_completo_responsable = None
        nombre_list = [obj.id_funcionario_responsable_und_destino.primer_nombre, obj.id_funcionario_responsable_und_destino.segundo_nombre,
                        obj.id_funcionario_responsable_und_destino.primer_apellido, obj.id_funcionario_responsable_und_destino.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'

class DespachosParaDespachoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DespachoViveros
        fields = '__all__'

class ItemsSolicitudVieroParaDespachoSerializer(serializers.ModelSerializer):
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None)
    unidad_medida = serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura', default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    tipo_bien = serializers.SerializerMethodField()
    
    def get_tipo_bien(self, obj):
        tipo_bien = None
        if obj.id_bien.cod_tipo_elemento_vivero == 'IN':
            tipo_bien = 'Insumo'
        if obj.id_bien.cod_tipo_elemento_vivero == 'MV' and obj.id_bien.es_semilla_vivero == False:
            tipo_bien = 'Planta'
        return tipo_bien
    
    class Meta:
        model = ItemSolicitudViveros
        fields = ['codigo_bien', 'nombre', 'cantidad', 'observaciones', 'unidad_medida', 'tipo_bien']
        
        
class DespachosViveroSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DespachoViveros
        fields = '__all__'
    
class ItemsDespachoViveroSerializer(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre_bien=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    unidad_medida= serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura',default=None)
    cod_tipo_elemento_vivero= serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero',default=None)
    
    class Meta:
        model = ItemsDespachoViveros
        fields = '__all__'

class GetInsumoSerializer(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    cod_tipo_elemento_vivero=serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero',default=None)
    cantidad_disponible = serializers.IntegerField(read_only=True, default=None)
    disponible= serializers.BooleanField(read_only=True,default=None)
    unidad_medida= serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura',default=None)
    
    class Meta:
        model=InventarioViveros
        fields=('id_inventario_vivero', 'id_bien', 'codigo_bien', 'nombre', 'cod_tipo_elemento_vivero', 'cantidad_disponible','disponible','unidad_medida')


class GetPlantaSerializer(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    cod_tipo_elemento_vivero=serializers.ReadOnlyField(source='id_bien.cod_tipo_elemento_vivero',default=None)
    cantidad_disponible = serializers.IntegerField(read_only=True, default=None)
    disponible= serializers.BooleanField(read_only=True,default=None)
    unidad_medida= serializers.ReadOnlyField(source='id_bien.id_unidad_medida.abreviatura')
    
    class Meta:
        model=InventarioViveros
        fields=('id_inventario_vivero', 'id_bien', 'codigo_bien', 'nombre', 'cod_tipo_elemento_vivero', 'agno_lote', 'nro_lote', 'cantidad_disponible', 'es_produccion_propia_lote', 'disponible','unidad_medida', 'cod_tipo_entrada_alm_lote', 'nro_entrada_alm_lote')

