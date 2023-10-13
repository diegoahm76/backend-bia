
from rest_framework import serializers
from gestion_documental.models.ccd_models import CatalogosSeries, CatalogosSeriesUnidad

from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental
from transversal.models.organigrama_models import UnidadesOrganizacionales
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
class ConfiguracionTipoExpedienteAgnoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = '__all__'

class ConfiguracionTipoExpedienteAgnoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = '__all__'

class ConfiguracionTipoExpedienteAgnoHistorialSerializer(serializers.ModelSerializer):
    cod_tipo_expediente_display = serializers.CharField(source='get_cod_tipo_expediente_display', read_only=True)
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = '__all__'

class ConfiguracionTipoExpedienteAgnoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = '__all__'

class SecSubUnidadOrgaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=UnidadesOrganizacionales
        fields=['id_unidad_organizacional','nombre']
#CatalogosSeries
class CatalogosSeriesSecSubGetSerializer(serializers.ModelSerializer):
    nombre_serie_doc=serializers.ReadOnlyField(source='id_serie_doc.nombre',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_subserie_doc.nombre',default=None)
    class Meta:

        model=CatalogosSeries
        fields=['id_catalogo_serie','id_serie_doc','nombre_serie_doc','id_subserie_doc','nombre_subserie_doc']

class XXGetSerializer(serializers.ModelSerializer):
    #accesos_unidades_organizacionales = CatalogosSeriesSecSubGetSerializer(many=True, read_only=True)
    id_serie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre',default=None)
    class Meta:
        model= CatSeriesUnidadOrgCCDTRD
        fields=['id_catserie_unidadorg',
            'id_serie_doc',
            'nombre_serie_doc',
            'id_subserie_doc',
            'nombre_subserie_doc']
    
#CatSeriesUnidadOrgCCDTRD
class XYGetSerializer(serializers.ModelSerializer):
    #accesos_unidades_organizacionales = CatalogosSeriesSecSubGetSerializer(many=True, read_only=True)
    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre',default=None)
    class Meta:
        model= CatalogosSeriesUnidad
        fields='__all__'
    
class ConfiguracionTipoExpedienteAgnoGetSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    persona_ultimo_consecutivo_nombre_completo = serializers.SerializerMethodField()
    cod_tipo_expediente_display = serializers.CharField(source='get_cod_tipo_expediente_display', read_only=True)
    class Meta:
        model=ConfiguracionTipoExpedienteAgno
        fields='__all__'

    def get_nombre_completo(self, obj):
    
        if obj.id_persona_ult_config_implement:
            nombre_completo = None
            nombre_list = [obj.id_persona_ult_config_implement.primer_nombre, obj.id_persona_ult_config_implement.segundo_nombre, obj.id_persona_ult_config_implement.primer_apellido, obj.id_persona_ult_config_implement.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()
    
    def get_persona_ultimo_consecutivo_nombre_completo(self, obj):
    
        if obj.id_persona_consecutivo_actual:
            nombre_completo = None
            nombre_list = [obj.id_persona_consecutivo_actual.primer_nombre, obj.id_persona_consecutivo_actual.segundo_nombre, obj.id_persona_consecutivo_actual.primer_apellido, obj.id_persona_consecutivo_actual.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()


    