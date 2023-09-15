from rest_framework import serializers
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD

class CtrlAccesoGetSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    nombre_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_unidad_organizacional.nombre', default=None)
    codigo_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und_org_ccd.id_unidad_organizacional.codigo', default=None)
    
    class Meta:
        model = CtrlAccesoClasificacionExpCCD
        fields = '__all__'
        
class CtrlAccesoCodClasifPutSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    nombre_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.nombre', default=None)
    codigo_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.codigo', default=None)
    
    class Meta:
        model = CtrlAccesoClasificacionExpCCD
        exclude = ['id_cat_serie_und_org_ccd']
        extra_kwargs = {
            'id_ccd': {'required': True, 'allow_null': False},
            'cod_clasificacion_exp': {'required': True, 'allow_null': False},
            'entidad_entera_consultar': {'required': True, 'allow_null': False},
            'entidad_entera_descargar': {'required': True, 'allow_null': False},
            'seccion_actual_respon_serie_doc_consultar': {'required': True, 'allow_null': False},
            'seccion_actual_respon_serie_doc_descargar': {'required': True, 'allow_null': False},
            'seccion_raiz_organi_actual_consultar': {'required': True, 'allow_null': False},
            'seccion_raiz_organi_actual_descargar': {'required': True, 'allow_null': False},
            'secciones_actuales_mismo_o_sup_nivel_respon_consulta': {'required': True, 'allow_null': False},
            'secciones_actuales_mismo_o_sup_nivel_respon_descargar': {'required': True, 'allow_null': False},
            'secciones_actuales_inf_nivel_respon_consultar': {'required': True, 'allow_null': False},
            'secciones_actuales_inf_nivel_respon_descargar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_inf_nivel_resp_exp_consultar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_inf_nivel_resp_exp_descargar': {'required': True, 'allow_null': False},
        }
        
class CtrlAccesoCatUndPutSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    nombre_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.nombre', default=None)
    codigo_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.codigo', default=None)
    
    class Meta:
        model = CtrlAccesoClasificacionExpCCD
        exclude = ['cod_clasificacion_exp']
        extra_kwargs = {
            'id_ccd': {'required': True, 'allow_null': False},
            'id_cat_serie_und_org_ccd': {'required': True, 'allow_null': False},
            'entidad_entera_consultar': {'required': True, 'allow_null': False},
            'entidad_entera_descargar': {'required': True, 'allow_null': False},
            'seccion_actual_respon_serie_doc_consultar': {'required': True, 'allow_null': False},
            'seccion_actual_respon_serie_doc_descargar': {'required': True, 'allow_null': False},
            'seccion_raiz_organi_actual_consultar': {'required': True, 'allow_null': False},
            'seccion_raiz_organi_actual_descargar': {'required': True, 'allow_null': False},
            'secciones_actuales_mismo_o_sup_nivel_respon_consulta': {'required': True, 'allow_null': False},
            'secciones_actuales_mismo_o_sup_nivel_respon_descargar': {'required': True, 'allow_null': False},
            'secciones_actuales_inf_nivel_respon_consultar': {'required': True, 'allow_null': False},
            'secciones_actuales_inf_nivel_respon_descargar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_inf_nivel_resp_exp_consultar': {'required': True, 'allow_null': False},
            'unds_org_sec_respon_inf_nivel_resp_exp_descargar': {'required': True, 'allow_null': False},
        }