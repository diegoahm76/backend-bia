from rest_framework import serializers
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad

from gestion_documental.models.expedientes_models import ExpedientesDocumentales
from transversal.models.entidades_models import SucursalesEmpresas
from transversal.models.organigrama_models import UnidadesOrganizacionales

class ReporteIndicesTodosGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpedientesDocumentales
        fields = '__all__'
class UnidadesGetSerializer(serializers.ModelSerializer):

  
    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional','codigo','nombre']

class SucursalesEmpresasSerializer(serializers.ModelSerializer):
    class Meta:
        model = SucursalesEmpresas
        fields = '__all__'


class CatalogosSeriesUnidadGetSerializer(serializers.ModelSerializer):


    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre',default=None)
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_cat_serie_und','id_serie_doc','cod_serie_doc','nombre_serie_doc','id_subserie_doc','cod_subserie_doc','nombre_subserie_doc']
