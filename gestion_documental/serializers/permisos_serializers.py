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
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
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
    id_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_unidad_organizacional.id_unidad_org_actual_admin_series.id_unidad_organizacional', default=None)
    nombre_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_unidad_organizacional.id_unidad_org_actual_admin_series.nombre', default=None)
    codigo_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_unidad_organizacional.id_unidad_org_actual_admin_series.codigo', default=None)
    nombre_unidad_organizacional = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    codigo_unidad_organizacional = serializers.ReadOnlyField(source='id_unidad_organizacional.codigo', default=None)
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_cat_serie_und', 'id_unidad_organizacional', 'id_catalogo_serie', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_subserie_doc', 'nombre_subserie', 'codigo_subserie', 'id_unidad_org_actual_admin_series', 'nombre_unidad_org_actual_admin_series', 'codigo_unidad_org_actual_admin_series']

class PermisosGetSerializer(serializers.ModelSerializer):
    nombre_und_organizacional_actual = serializers.ReadOnlyField(source='id_und_organizacional_actual.nombre', default=None)
    codigo_und_organizacional_actual = serializers.ReadOnlyField(source='id_und_organizacional_actual.codigo', default=None)
    mostrar = serializers.SerializerMethodField()
    
    def get_mostrar(self, obj):
        return True
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        exclude = [
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class DenegacionPermisosGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = [
            'id_permisos_und_org_actual_serie_exp_ccd',
            'id_cat_serie_und_org_ccd',
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class PermisosPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        exclude = [
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class PermisosPutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = [
            'pertenece_seccion_actual_admin_serie',
            'crear_expedientes',
            'crear_documentos_exps_no_propios',
            'anular_documentos_exps_no_propios',
            'borrar_documentos_exps_no_propios',
            'conceder_acceso_documentos_exps_no_propios',
            'conceder_acceso_expedientes_no_propios',
            'consultar_expedientes_no_propios',
            'descargar_expedientes_no_propios',
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class PermisosPostDenegacionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = [
            'id_cat_serie_und_org_ccd',
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class PermisosPutDenegacionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = [
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]

class PermisosPutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = [
            'denegar_anulacion_docs',
            'denegar_borrado_docs',
            'excluir_und_actual_respon_series_doc_restriccion',
            'denegar_conceder_acceso_doc_na_resp_series',
            'denegar_conceder_acceso_exp_na_resp_series'
        ]