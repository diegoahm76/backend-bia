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

    class Meta:
        model = TablasControlAcceso
        fields = ['id_tca', 'id_trd', 'version', 'nombre']
        extra_kwargs = {
            'id_tca': {'read_only': True},
            'id_trd': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
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
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'required': True},
            'id_cat_serie_und': {'required': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }
        validators = [
           UniqueTogetherValidator(
               queryset=CatSeriesUnidadOrgCCD_TRD_TCA.objects.all(),
               fields = ['id_tca', 'id_cat_serie_und'],
               message='No puede existir más de una clasificación para el mismo expediente'
           )
        ]     

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
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

class CatalogosSeriesUnidadClasifSerializer(serializers.ModelSerializer):
    seccion = serializers.SerializerMethodField()
    subseccion = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    id_serie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_cat_serie_und = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    subseries_nombres = serializers.SerializerMethodField()
    clasificacion = serializers.SerializerMethodField()
    
    def get_seccion(self, obj):
        seccion = UnidadesOrganizacionales.objects.filter(id_organigrama=obj.id_unidad_organizacional.id_organigrama.id_organigrama, cod_agrupacion_documental='SEC').first()
        if not seccion:
            seccion = None
        return seccion.nombre
    
    def get_subseries(self, obj):
        serie_subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances]
        for subserie in subseries_instances:
            subserie.id_cat_serie_und = serie_subseries_instances.filter(id_sub_serie_doc=subserie.id_subserie_doc).first().id_cat_serie_und
            clasificacion = serie_subseries_instances.filter(id_subserie_doc=subserie.id_subserie_doc).first().clasif_serie_subserie_unidad_tca_set.all().first()
            if clasificacion:
                serializer_clasificacion = ClasifExpedientesSerializer(clasificacion)
                subserie.clasificacion = serializer_clasificacion.data
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances if serie_subserie.clasif_serie_subserie_unidad_tca_set.all()]
        subseries = SubseriesAsignacionesSerializer(subseries_instances, many=True)
        return subseries.data
    
    def get_subseries_nombres(self, obj):
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        subseries_names = [subserie.id_catalogo_serie.id_subserie_doc.nombre for subserie in subseries_instances]
        return subseries_names
    
    def get_id_cat_serie_und(self, obj):
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        id_cat_serie_und = None
        if not subseries_instances:
            id_cat_serie_und = obj.id_cat_serie_und
        return id_cat_serie_und
    
    def get_clasificacion(self, obj):
        id_tca = self.context.get("id_tca")
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        clasificacion = None
        if not subseries_instances:
            clasificaciones_instances = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_und=obj.id_cat_serie_und, id_tca=id_tca).first()
            clasificacion = ClasifExpedientesSerializer(clasificaciones_instances).data
        return clasificacion
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_unidad_organizacional', 'seccion', 'subseccion', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_cat_serie_und', 'subseries_nombres', 'subseries', 'clasificacion']
        validators = [
            UniqueTogetherValidator(
                queryset=CatalogosSeriesUnidad.objects.all(),
                fields = ['id_unidad_organizacional', 'id_catalogo_serie'],
                message='La combinación del catalogo y la unidad organizacional debe ser única'
            )
        ]

class ClasifExpedientesSerializer(serializers.ModelSerializer):
    clas_expediente = serializers.SerializerMethodField()
    
    def get_clas_expediente(self, obj):
        clas_expediente = None
        if obj.cod_clas_expediente == 'P':
            clas_expediente = 'Público'
        elif obj.cod_clas_expediente == 'C':
            clas_expediente = 'Controlado'
        elif obj.cod_clas_expediente == 'R':
            clas_expediente = 'Rerservado'
        return clas_expediente
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = [
            'id_cat_serie_unidad_org_ccd_trd_tca',
            'cod_clas_expediente',
            'clas_expediente',
            'fecha_registro',
            'justificacion_cambio',
            'ruta_archivo_cambio'
        ]

class CatalogosSeriesUnidadClasifPermisosSerializer(serializers.ModelSerializer):
    seccion = serializers.SerializerMethodField()
    subseccion = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    id_serie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_cat_serie_und = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    subseries_nombres = serializers.SerializerMethodField()
    clasificacion = serializers.SerializerMethodField()
    
    def get_seccion(self, obj):
        seccion = UnidadesOrganizacionales.objects.filter(id_organigrama=obj.id_unidad_organizacional.id_organigrama.id_organigrama, cod_agrupacion_documental='SEC').first()
        if not seccion:
            seccion = None
        return seccion.nombre
    
    def get_subseries(self, obj):
        serie_subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances]
        for subserie in subseries_instances:
            subserie.id_cat_serie_und = serie_subseries_instances.filter(id_sub_serie_doc=subserie.id_subserie_doc).first().id_cat_serie_und
            clasificacion = serie_subseries_instances.filter(id_subserie_doc=subserie.id_subserie_doc).first().clasif_serie_subserie_unidad_tca_set.all().first()
            if clasificacion:
                serializer_clasificacion = ClasifExpedientesSerializer(clasificacion)
                subserie.clasificacion = serializer_clasificacion.data
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances if serie_subserie.clasif_serie_subserie_unidad_tca_set.all()]
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances if serie_subserie.clasif_serie_subserie_unidad_tca_set.all().first().cargos_unidad_s_ss_undorg_tca_set.all()]
        subseries = SubseriesAsignacionesSerializer(subseries_instances, many=True)
        return subseries.data
    
    def get_subseries_nombres(self, obj):
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        subseries_names = [subserie.id_catalogo_serie.id_subserie_doc.nombre for subserie in subseries_instances]
        return subseries_names
    
    def get_id_cat_serie_und(self, obj):
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        id_cat_serie_und = None
        if not subseries_instances:
            id_cat_serie_und = obj.id_cat_serie_und
        return id_cat_serie_und
    
    def get_clasificacion(self, obj):
        id_tca = self.context.get("id_tca")
        subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        clasificacion = None
        if not subseries_instances:
            clasificaciones_instances = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_und=obj.id_cat_serie_und, id_tca=id_tca).first()
            clasificacion = ClasifExpedientesSerializer(clasificaciones_instances).data
        return clasificacion
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_unidad_organizacional', 'seccion', 'subseccion', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_cat_serie_und', 'subseries_nombres', 'subseries', 'clasificacion']
        validators = [
            UniqueTogetherValidator(
                queryset=CatalogosSeriesUnidad.objects.all(),
                fields = ['id_unidad_organizacional', 'id_catalogo_serie'],
                message='La combinación del catalogo y la unidad organizacional debe ser única'
            )
        ]

class ClasifCargoUnidadPermisosSerializer(ClasifExpedientesSerializer):
    id_cargo_persona = serializers.SerializerMethodField()
    nombre_cargo_persona = serializers.SerializerMethodField()
    id_unidad_org_cargo = serializers.SerializerMethodField()
    nombre_unidad_org_cargo = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    
    def get_clas_expediente(self, obj):
        clas_expediente = None
        if obj.cod_clas_expediente == 'P':
            clas_expediente = 'Público'
        elif obj.cod_clas_expediente == 'C':
            clas_expediente = 'Controlado'
        elif obj.cod_clas_expediente == 'R':
            clas_expediente = 'Rerservado'
        return clas_expediente
    
    def get_id_cargo_persona(self, obj):
        cargo_unidad = obj.cargos_unidad_s_ss_undorg_tca_set.all().first()
        id_cargo_persona = None
        if cargo_unidad:
            id_cargo_persona = cargo_unidad.id_cargo_persona.id_cargo
        return id_cargo_persona
    
    def get_nombre_cargo_persona(self, obj):
        cargo_unidad = obj.cargos_unidad_s_ss_undorg_tca_set.all().first()
        nombre_cargo_persona = None
        if cargo_unidad:
            nombre_cargo_persona = cargo_unidad.id_cargo_persona.nombre
        return nombre_cargo_persona
    
    def get_id_unidad_org_cargo(self, obj):
        cargo_unidad = obj.cargos_unidad_s_ss_undorg_tca_set.all().first()
        id_unidad_org_cargo = None
        if cargo_unidad:
            id_unidad_org_cargo = cargo_unidad.id_unidad_org_cargo.id_unidad_organizacional
        return id_unidad_org_cargo
    
    def get_nombre_unidad_org_cargo(self, obj):
        cargo_unidad = obj.cargos_unidad_s_ss_undorg_tca_set.all().first()
        nombre_unidad_org_cargo = None
        if cargo_unidad:
            nombre_unidad_org_cargo = cargo_unidad.id_unidad_org_cargo.nombre
        return nombre_unidad_org_cargo
    
    def get_permisos(self, obj):
        cargo_unidad = obj.cargos_unidad_s_ss_undorg_tca_set.all().first()
        permisos = []
        if cargo_unidad:
            permisos_instances = cargo_unidad.permisoscargounidadseriesubserieunidadtca_set.all()
            serializer_permisos = PermisosCargoUnidadSerieSubserieUnidadTCASerializer(permisos_instances, many=True)
            permisos = serializer_permisos.data
        return permisos
    
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = ClasifExpedientesSerializer.Meta.fields + ['id_cargo_persona', 'nombre_cargo_persona', 'id_unidad_org_cargo', 'nombre_unidad_org_cargo', 'permisos']

class ClasifSerieSubseriUnidadTCA_activoSerializer(serializers.ModelSerializer):
    justificacion_cambio = serializers.CharField(max_length=255,min_length=1)
    class Meta:
        model = CatSeriesUnidadOrgCCD_TRD_TCA
        fields = ['cod_clas_expediente','justificacion_cambio','ruta_archivo_cambio']
        extra_kwargs={
            'id_cat_serie_unidad_org_ccd_trd_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_cat_serie_und': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'required': True},
            'ruta_archivo_cambio': {'required': True,'allow_null':False}
        }

class Cargos_Unidad_S_Ss_UndOrg_TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisosCatSeriesUnidadOrgTCA   
        fields = '__all__'
    
class PermisosCargoUnidadSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    tipo_permiso = serializers.ReadOnlyField(source='cod_permiso.tipo_permiso', default=None)
    class Meta:
        model = PermisosDetPermisosCatSerieUndOrgTCA
        fields = '__all__'