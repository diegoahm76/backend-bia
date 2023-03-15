from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    SeriesSubseriesUnidadOrg
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)

class SubseriesDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubseriesDoc
        fields = '__all__'
        validators = [
           UniqueTogetherValidator(
               queryset=SubseriesDoc.objects.all(),
               fields = ['id_ccd', 'codigo'],
               message='No puede existir más de una subserie con el mismo código para este CCD'
           ),
           UniqueTogetherValidator(
               queryset=SubseriesDoc.objects.all(),
               fields = ['id_ccd', 'nombre'],
               message='No puede existir más de una subserie con el mismo nombre para este CCD'
           )
        ]

class SubseriesAsignacionesSerializer(serializers.ModelSerializer):
    label = serializers.ReadOnlyField(source='nombre')
    value = serializers.ReadOnlyField(source='id_subserie_doc')
    id_serie_subserie_doc = serializers.IntegerField(default=None)
    clasificacion = serializers.DictField(default=None)
    
    class Meta:
        model = SubseriesDoc
        fields = ['label', 'value', 'codigo', 'id_serie_subserie_doc', 'clasificacion']

class SeriesDocPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeriesDoc
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesDoc.objects.all(),
                fields = ['id_ccd', 'codigo'],
                message='No puede existir más de una serie con el mismo código para este CCD'
            ),
            UniqueTogetherValidator(
                queryset=SeriesDoc.objects.all(),
                fields = ['id_ccd', 'nombre'],
                message='No puede existir más de una serie con el mismo nombre para este CCD'
            )
        ]  

class CCDSerializer(serializers.ModelSerializer):
    series = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    
    def get_series(self,obj):
        series = SeriesDoc.objects.filter(id_ccd=obj.id_ccd)
        serializer_series = SeriesDocPostSerializer(series, many=True)
        return serializer_series.data
    
    def get_subseries(self,obj):
        subseries = SubseriesDoc.objects.filter(id_ccd=obj.id_ccd)
        serializer_subseries = SubseriesDocSerializer(subseries, many=True)
        return serializer_subseries.data
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = (
            'id_ccd',
            'id_organigrama',
            'version',
            'nombre',
            'fecha_terminado',
            'fecha_puesta_produccion',
            'fecha_retiro_produccion',
            'justificacion',
            'ruta_soporte',
            'actual',
            'series',
            'subseries',
        )

class CCDPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='La versión del Cuadro de Clasificación Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='El nombre del Cuadro de Clasificación Documental debe ser único')])
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'id_organigrama', 'version', 'nombre']
        extra_kwargs = {
            'id_organigrama': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }

class CCDPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='La versión del Cuadro de Clasificación Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=CuadrosClasificacionDocumental.objects.all(), message='El nombre del Cuadro de Clasificación Documental debe ser único')])
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['version', 'nombre']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }

class CCDActivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['fecha_terminado']
        extra_kwargs = {
            'fecha_terminado': {'read_only': True}
        }

class SeriesDocSerializer(serializers.ModelSerializer):
    id_ccd = CCDSerializer(read_only=True)
    
    class Meta:
        model = SeriesDoc
        fields = '__all__'

class SeriesSubseriesUnidadOrgSerializer(serializers.ModelSerializer):
    id_ccd = serializers.ReadOnlyField(source='id_serie_doc.id_ccd.id_ccd', default=None)
    seccion = serializers.SerializerMethodField()
    subseccion = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_serie_doc.codigo', default=None)
    id_serie_subserie_doc = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    subseries_nombres = serializers.SerializerMethodField()
    
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
    
    class Meta:
        model = SeriesSubseriesUnidadOrg
        fields = ['id_ccd', 'id_unidad_organizacional', 'seccion', 'subseccion', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_serie_subserie_doc', 'subseries_nombres', 'subseries']
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesSubseriesUnidadOrg.objects.all(),
                fields = ['id_serie_doc', 'id_unidad_organizacional'],
                message='La combinación serie documental y unidad organizacional debe ser única'
            )
        ]

class AsignacionesOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeriesSubseriesUnidadOrg
        fields = '__all__'      
        validators = [
            UniqueTogetherValidator(
                queryset=SeriesSubseriesUnidadOrg.objects.all(),
                fields = ['id_serie_doc', 'id_unidad_organizacional'],
                message='La combinación serie documental y unidad organizacional debe ser única'
            )
        ]  