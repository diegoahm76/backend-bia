from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)

class SerieSubserieUnidadCCDGetSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.codigo', default=None)
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_cat_serie_und', 'id_unidad_organizacional', 'id_catalogo_serie', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_subserie_doc', 'nombre_subserie', 'codigo_subserie']