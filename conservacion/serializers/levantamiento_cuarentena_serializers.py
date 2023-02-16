from rest_framework import serializers
from conservacion.models.cuarentena_models import CuarentenaMatVegetal,ItemsLevantaCuarentena
from conservacion.utils import UtilConservacion

class MaterialVegetalCuarentenaSerializer(serializers.ModelSerializer):
    cantidad_por_levantar = serializers.SerializerMethodField()
    nombre_mat_veg = serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    id_material_vegetal = serializers.ReadOnlyField(source='id_bien.id_bien',default=None)
    
    def get_cantidad_por_levantar(self,obj):
        cantidad_por_levantar = UtilConservacion.get_saldo_por_levantar(obj)
        return cantidad_por_levantar
        
    class Meta:
        model = CuarentenaMatVegetal
        fields = ['id_cuarentena_mat_vegetal','nombre_mat_veg','id_material_vegetal','codigo_bien','consec_cueren_por_lote_etapa','fecha_cuarentena','descrip_corta_diferenciable','cantidad_por_levantar','cod_etapa_lote','agno_lote']
        

class ItemsLevantamientoCuarentenaSerializer(serializers.ModelSerializer):
    realizado_por = serializers.SerializerMethodField()
    
    def get_realizado_por(self,obj):
        
        primer_nombre = obj.id_persona_levanta.primer_nombre
        primer_apellido = obj.id_persona_levanta.primer_apellido
        
        realizado_por = str(primer_nombre)+' '+str(primer_apellido)
        
        return realizado_por
    
    class Meta:
        model = ItemsLevantaCuarentena
        fields = '__all__'

class CuarentenaMaterialVegetalSerializer(serializers.ModelSerializer):
    nombre_material_vegetal = serializers.ReadOnlyField(source = 'id_bien.nombre')
    nombre_vivero = serializers.ReadOnlyField(source = 'id_vivero.nombre')
    
    class Meta:
        model = CuarentenaMatVegetal
        fields = '__all__'

class AnulacionItemsLevantamientoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemsLevantaCuarentena
        fields = ['id_item_levanta_cuarentena','fecha_registro','consec_levan_por_cuaren','cantidad_a_levantar']
        
        
        
class AnulacionGetCuarentenaMaterialVegetalSerializer(serializers.ModelSerializer):
    ultimo_item_levantamiento_cuarentena = serializers.SerializerMethodField()
    codigo = serializers.ReadOnlyField(source = 'id_bien.codigo_bien')
    nombre = serializers.ReadOnlyField(source = 'id_bien.nombre')
    
    def get_ultimo_item_levantamiento_cuarentena (self,obj):
        
        ultimo_item_levantamiento_cuarentena = ItemsLevantaCuarentena.objects.filter(id_cuarentena_mat_vegetal=obj.id_cuarentena_mat_vegetal,levantamiento_anulado = False).last()
        serializador = ItemsLevantamientoCuarentenaSerializer(ultimo_item_levantamiento_cuarentena) if ultimo_item_levantamiento_cuarentena else None
        serializador_data = serializador.data if serializador else None
        return serializador_data
   
    class Meta:
        model = CuarentenaMatVegetal
        fields = ['id_cuarentena_mat_vegetal','codigo','nombre','agno_lote','nro_lote','cod_etapa_lote','ultimo_item_levantamiento_cuarentena']

