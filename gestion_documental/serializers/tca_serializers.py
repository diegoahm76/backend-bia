from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    CatSeriesUnidadOrgCCD_TRD_TCA,
    PermisosCatSeriesUnidadOrgTCA,
    PermisosDetPermisosCatSerieUndOrgTCA
)
from gestion_documental.models.ccd_models import (
    CatalogosSeriesUnidad
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.serializers.ccd_serializers import SubseriesAsignacionesSerializer
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES

class TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = '__all__'

class TCAPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    def validate_id_trd(self, trd):
        if trd.fecha_terminado == None:
            raise serializers.ValidationError('No se puede seleccionar una TRD que no esté terminada')
        if trd.fecha_puesta_produccion:
            raise serializers.ValidationError('No se puede seleccionar una TRD que haya sido puesta en producción')
        if trd.fecha_retiro_produccion:
            raise serializers.ValidationError('No se puede seleccionar una TRD que haya sido retirada de producción')

        return trd

    class Meta:
        model = TablasControlAcceso
        fields = ['id_trd', 'version', 'nombre', 'id_tca']
        extra_kwargs = {
            'id_tca': {'read_only': True},
            'id_trd': {'required': True, 'allow_null':False},
            'version': {'required': True, 'allow_null':False, 'allow_blank':False},
            'nombre': {'required': True, 'allow_null':False, 'allow_blank':False}
        }

class TCAPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    class Meta:
        model = TablasControlAcceso
        fields = ['version', 'nombre']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }

class ClasifSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)

    def validate_ruta_soporte(self, value):
        extension = value.name.split('.')[-1]
        if extension != 'pdf':
            raise serializers.ValidationError('El archivo adjunto debe estar en formato PDF.')
        return value
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'required': True},
            'id_cat_serie_und_ccd_trd': {'required': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True},
        }
        validators = [
           UniqueTogetherValidator(
               queryset=CatSeriesUnidadOrgCCD_TRD_TCA.objects.all(),
               fields = ['id_tca', 'id_cat_serie_und_ccd_trd'],
               message='No puede existir más de una clasificación para el mismo expediente'
           )
        ]     

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)

    def validate_ruta_soporte(self, value):
        extension = value.name.split('.')[-1]
        if extension != 'pdf':
            raise serializers.ValidationError('El archivo adjunto debe estar en formato PDF.')
        return value
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_cat_serie_und': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)

    def validate_ruta_soporte(self, value):
        extension = value.name.split('.')[-1]
        if extension != 'pdf':
            raise serializers.ValidationError('El archivo adjunto debe estar en formato PDF.')
        return value
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_cat_serie_und': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }
        
class ClasifSerieSubseriUnidadTCA_activoSerializer(serializers.ModelSerializer):
    justificacion_cambio = serializers.CharField(max_length=255,min_length=1)
    def validate_ruta_soporte(self, value):
        extension = value.name.split('.')[-1]
        if extension != 'pdf':
            raise serializers.ValidationError('El archivo adjunto debe estar en formato PDF.')
        return value
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = ['cod_clas_expediente','justificacion_cambio','ruta_archivo_cambio']
        extra_kwargs={
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_cat_serie_und': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'required': True,'allow_null':False,'allow_blank':False},
            'ruta_archivo_cambio': {'required': True,'allow_null':False}
        }

class Cargos_Unidad_S_Ss_UndOrg_TCASerializer(serializers.ModelSerializer):
    def validate_ruta_soporte(self, value):
        extension = value.name.split('.')[-1]
        if extension != 'pdf':
            raise serializers.ValidationError('El archivo adjunto debe estar en formato PDF.')
        return value
    class Meta:
        model = PermisosCatSeriesUnidadOrgTCA   
        fields = '__all__'
    
class PermisosCargoUnidadSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    tipo_permiso = serializers.ReadOnlyField(source='cod_permiso.tipo_permiso', default=None)
    class Meta:
        model = PermisosDetPermisosCatSerieUndOrgTCA
        fields = '__all__'

class BusquedaTCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields =['nombre','version','actual','fecha_terminado','fecha_puesta_produccion','fecha_retiro_produccion']

class GetClasifExpedientesSerializer(serializers.ModelSerializer):
    id_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional', default=None)
    nombre_unidad = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_unidad_organizacional.nombre', default=None)
    cod_unidad_org = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_unidad_organizacional.codigo', default=None)
    id_serie_doc = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre', default=None)
    cod_serie = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    cod_subserie = serializers.ReadOnlyField(source='id_cat_serie_und_ccd_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = '__all__'

