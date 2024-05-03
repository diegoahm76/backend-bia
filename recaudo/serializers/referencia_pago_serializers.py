
from rest_framework import serializers

from recaudo.models.referencia_pago_models import ConfigReferenciaPagoAgno, Referencia


class ConfigTipoRefgnoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigReferenciaPagoAgno
        fields = '__all__'


class ReferenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referencia
        fields ='__all__'

class ConfigTipoRefgnoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigReferenciaPagoAgno
        fields = '__all__'


class ConfigTipoRefgnoGetSerializer(serializers.ModelSerializer):
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad.nombre', default=None)
    persona_configura = serializers.SerializerMethodField()
    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.nombre',default=None) 
    class Meta:
        model = ConfigReferenciaPagoAgno
        fields = '__all__'

    def get_persona_configura(self,obj):
        nombre_completo_responsable = None
        if obj.id_persona_config_implementacion:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_config_implementacion.primer_nombre, obj.id_persona_config_implementacion.segundo_nombre,
                            obj.id_persona_config_implementacion.primer_apellido, obj.id_persona_config_implementacion.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable