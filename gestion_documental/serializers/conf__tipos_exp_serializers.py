
from rest_framework import serializers
from gestion_documental.models.ccd_models import CatalogosSeries, CatalogosSeriesUnidad

from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental
from transversal.models.organigrama_models import UnidadesOrganizacionales

class ConfiguracionTipoExpedienteAgnoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = '__all__'

class ConfiguracionTipoExpedienteAgnoCreateSerializer(serializers.ModelSerializer):
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
    accesos_unidades_organizacionales = CatalogosSeriesSecSubGetSerializer(many=True, read_only=True)
    id_serie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre',default=None)
    class Meta:
        model= CatSeriesUnidadOrgCCDTRD
        fields='__all__'
    

class XYGetSerializer(serializers.ModelSerializer):
    #accesos_unidades_organizacionales = CatalogosSeriesSecSubGetSerializer(many=True, read_only=True)
    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre',default=None)
    class Meta:
        model= CatalogosSeriesUnidad
        fields='__all__'
    

