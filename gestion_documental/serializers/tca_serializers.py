from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    Clasif_Serie_Subserie_Unidad_TCA,
    Cargos_Unidad_S_Ss_UndOrg_TCA,
    PermisosCargoUnidadSerieSubserieUnidadTCA
)
from gestion_documental.models.ccd_models import (
    SeriesSubseriesUnidadOrg
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
        fields = ['id_tca', 'id_ccd', 'version', 'nombre']
        extra_kwargs = {
            'id_tca': {'read_only': True},
            'id_ccd': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }

class TCAPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='La versión de la Tabla de Control de Acceso debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablasControlAcceso.objects.all(), message='El nombre de la Tabla de Control de Acceso debe ser único')])

    class Meta:
        model = TablasControlAcceso
        fields = ['version', 'nombre', 'ruta_soporte']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }

class ClasifSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'required': True},
            'id_serie_subserie_unidad': {'required': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }
        validators = [
           UniqueTogetherValidator(
               queryset=Clasif_Serie_Subserie_Unidad_TCA.objects.all(),
               fields = ['id_tca', 'id_serie_subserie_unidad'],
               message='El TCA y la serie subserie unidad deben ser una pareja única'
           )
        ]     

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_serie_subserie_unidad': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }

class ClasifSerieSubserieUnidadTCAPutSerializer(serializers.ModelSerializer):
    cod_clas_expediente = serializers.ChoiceField(choices=tipo_clasificacion_CHOICES)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'
        extra_kwargs = {
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_serie_subserie_unidad': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'read_only': True},
            'ruta_archivo_cambio': {'read_only': True}
        }

class ClasifSeriesSubseriesUnidadOrgSerializer(serializers.ModelSerializer):
    seccion = serializers.SerializerMethodField()
    subseccion = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_serie_doc.codigo', default=None)
    id_serie_subserie_doc = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    subseries_nombres = serializers.SerializerMethodField()
    clasificacion = serializers.SerializerMethodField()
    
    def get_seccion(self, obj):
        seccion = UnidadesOrganizacionales.objects.filter(id_organigrama=obj.id_unidad_organizacional.id_organigrama.id_organigrama, cod_agrupacion_documental='SEC').first()
        if not seccion:
            seccion = None
        return seccion.nombre
    
    def get_subseries(self, obj):
        serie_subseries_instances = SeriesSubseriesUnidadOrg.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_serie_doc=obj.id_serie_doc.id_serie_doc).exclude(id_sub_serie_doc=None)
        subseries_instances = [serie_subserie.id_sub_serie_doc for serie_subserie in serie_subseries_instances]
        for subserie in subseries_instances:
            subserie.id_serie_subserie_doc = serie_subseries_instances.filter(id_sub_serie_doc=subserie.id_subserie_doc).first().id_serie_subserie_doc
            clasificacion = serie_subseries_instances.filter(id_sub_serie_doc=subserie.id_subserie_doc).first().clasif_serie_subserie_unidad_tca_set.all().first()
            if clasificacion:
                serializer_clasificacion = ClasifSerieSubserieUnidadTCAGetSerializer(clasificacion)
                subserie.clasificacion = serializer_clasificacion.data
        subseries_instances = [serie_subserie.id_sub_serie_doc for serie_subserie in serie_subseries_instances if serie_subserie.clasif_serie_subserie_unidad_tca_set.all()]
        subseries = SubseriesAsignacionesSerializer(subseries_instances, many=True)
        return subseries.data
    
    def get_subseries_nombres(self, obj):
        subseries_instances = SeriesSubseriesUnidadOrg.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_serie_doc=obj.id_serie_doc.id_serie_doc).exclude(id_sub_serie_doc=None)
        subseries_names = [subserie.id_sub_serie_doc.nombre for subserie in subseries_instances]
        return subseries_names
    
    def get_id_serie_subserie_doc(self, obj):
        subseries_instances = SeriesSubseriesUnidadOrg.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_serie_doc=obj.id_serie_doc.id_serie_doc).exclude(id_sub_serie_doc=None)
        id_serie_subserie_doc = None
        if not subseries_instances:
            id_serie_subserie_doc = obj.id_serie_subserie_doc
        return id_serie_subserie_doc
    
    def get_clasificacion(self, obj):
        id_tca = self.context.get("id_tca")
        subseries_instances = SeriesSubseriesUnidadOrg.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_serie_doc=obj.id_serie_doc.id_serie_doc).exclude(id_sub_serie_doc=None)
        clasificacion = None
        if not subseries_instances:
            clasificaciones_instances = Clasif_Serie_Subserie_Unidad_TCA.objects.filter(id_serie_subserie_unidad=obj.id_serie_subserie_doc, id_tca=id_tca).first()
            clasificacion = ClasifSerieSubserieUnidadTCAGetSerializer(clasificaciones_instances).data
        return clasificacion
    
    class Meta:
        model = SeriesSubseriesUnidadOrg
        fields = ['id_unidad_organizacional', 'seccion', 'subseccion', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_serie_subserie_doc', 'subseries_nombres', 'subseries', 'clasificacion']
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesSubseriesUnidadOrg.objects.all(),
                fields = ['id_serie_doc', 'id_unidad_organizacional'],
                message='La combinación serie documental y unidad organizacional debe ser única'
            )
        ]
        
class ClasifSerieSubserieUnidadTCAGetSerializer(serializers.ModelSerializer):
    id_cargo_persona = serializers.SerializerMethodField()
    nombre_cargo_persona = serializers.SerializerMethodField()
    id_unidad_org_cargo = serializers.SerializerMethodField()
    nombre_unidad_org_cargo = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    
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
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = '__all__'

class ClasifSerieSubseriUnidadTCA_activoSerializer(serializers.ModelSerializer):
    justificacion_cambio = serializers.CharField(max_length=255,min_length=1)
    class Meta:
        model = Clasif_Serie_Subserie_Unidad_TCA
        fields = ['cod_clas_expediente','justificacion_cambio','ruta_archivo_cambio']
        extra_kwargs={
            'id_clasif_serie_subserie_unidad_tca': {'read_only': True},
            'id_tca': {'read_only': True},
            'id_serie_subserie_unidad': {'read_only': True},
            'cod_clas_expediente': {'required': True},
            'fecha_registro': {'read_only': True},
            'justificacion_cambio': {'required': True},
            'ruta_archivo_cambio': {'required': True,'allow_null':False}
        }

class Cargos_Unidad_S_Ss_UndOrg_TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargos_Unidad_S_Ss_UndOrg_TCA   
        fields = '__all__'
    
class PermisosCargoUnidadSerieSubserieUnidadTCASerializer(serializers.ModelSerializer):
    tipo_permiso = serializers.ReadOnlyField(source='cod_permiso.tipo_permiso', default=None)
    class Meta:
        model = PermisosCargoUnidadSerieSubserieUnidadTCA
        fields = '__all__'