from rest_framework import serializers

from conservacion.models.inventario_models import InventarioViveros
from conservacion.models.siembras_models import CambiosDeEtapa
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES


class InventarioViverosSerializer(serializers.ModelSerializer):
    etapa_lote=serializers.SerializerMethodField()
    cantidad_disponible=serializers.IntegerField(read_only=True,default=None)
    codigo_bien=serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_bien.nombre',default=None)

    def get_etapa_lote(self,obj):
        etapa_lote = None
        if obj.cod_etapa_lote == 'G':
            etapa_lote = 'Germinación'
        else:
            etapa_lote = 'Producción'
            
        return etapa_lote
    
    class Meta:
        model =  InventarioViveros
        fields = ['id_inventario_vivero','id_bien','codigo_bien','nombre','agno_lote','nro_lote','cod_etapa_lote','etapa_lote','cantidad_disponible']

class GuardarCambioEtapaSerializer(serializers.ModelSerializer):
    cod_etapa_lote_origen = serializers.ChoiceField(choices=cod_etapa_lote_CHOICES)
    class Meta:
        model =  CambiosDeEtapa
        fields = ['id_bien', 'id_vivero', 'agno_lote', 'nro_lote', 'cod_etapa_lote_origen', 'fecha_cambio',
                  'cantidad_disponible_al_crear', 'cantidad_movida', 'altura_lote_en_cms', 'observaciones',
                  'id_persona_cambia', 'ruta_archivo_soporte', 'consec_por_lote_etapa']
        extra_kwargs = {
            'id_bien': {'required': True},
            'id_vivero': {'required': True},
            'agno_lote': {'required': True},
            'nro_lote':  {'required': True},
            'cod_etapa_lote_origen': {'required': True},
            'fecha_cambio': {'required': True},
            'cantidad_disponible_al_crear': {'required': True},
            'cantidad_movida': {'required': True},
            'altura_lote_en_cms': {'required': True},
            'observaciones': {'required': True},
            'id_persona_cambia': {'required': True}
        }

class ActualizarCambioEtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CambiosDeEtapa
        fields = ['cantidad_movida', 'altura_lote_en_cms', 'observaciones',
                  'id_persona_cambia', 'ruta_archivo_soporte']
        
class GetCambioEtapasSerializer(serializers.ModelSerializer):
    codigo = serializers.ReadOnlyField(source='id_bien.codigo_bien',default=None)
    nombre = serializers.ReadOnlyField(source='id_bien.nombre',default=None)
    cod_etapa_lote_destino = serializers.SerializerMethodField()
    desc_etapa_lote_origen = serializers.SerializerMethodField()
    desc_etapa_lote_destino = serializers.SerializerMethodField()
    
    def get_cod_etapa_lote_destino(self,obj):
        cod_etapa_lote_destino= 'P' if obj.cod_etapa_lote_origen == 'G' else 'D'
        return cod_etapa_lote_destino
    
    def get_desc_etapa_lote_origen(self,obj):
        desc_etapa_lote_origen= 'Camas de Germinación' if obj.cod_etapa_lote_origen == 'G' else 'Producción'
        return desc_etapa_lote_origen
    
    def get_desc_etapa_lote_destino (self,obj):
        desc_etapa_lote_destino= 'Produccion' if obj.cod_etapa_lote_origen == 'G' else 'Distribución'
        return desc_etapa_lote_destino
    
    class Meta:
        
        model = CambiosDeEtapa
        fields = '__all__'
        
class AnularCambioEtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CambiosDeEtapa
        fields = ['id_persona_anula', 'cambio_anulado', 'fecha_anulacion', 'justificacion_anulacion']
        extra_kwargs = {
            'justificacion_anulacion': {'required': True}
        }
