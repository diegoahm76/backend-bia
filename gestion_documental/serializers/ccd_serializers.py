from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad,
    UnidadesSeccionPersistenteTemporal,
    AgrupacionesDocumentalesPersistenteTemporal,
    UnidadesSeccionResponsableTemporal
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

class SubseriesAsignacionesSerializer(serializers.ModelSerializer):
    label = serializers.ReadOnlyField(source='nombre')
    value = serializers.ReadOnlyField(source='id_subserie_doc')
    id_cat_serie_und = serializers.IntegerField(default=None)
    clasificacion = serializers.DictField(default=None)
    
    class Meta:
        model = SubseriesDoc
        fields = ['label', 'value', 'codigo', 'id_cat_serie_und', 'clasificacion']

class SeriesDocPostSerializer(serializers.ModelSerializer):
    existe_catalogo = serializers.SerializerMethodField()
    tiene_subseries = serializers.SerializerMethodField()
    
    def get_existe_catalogo(self, obj):
        existe_catalogo = True if obj.catalogosseries_set.all() else False
        return existe_catalogo
    
    def get_tiene_subseries(self, obj):
        tiene_subseries = True if obj.subseriesdoc_set.all() else False
        return tiene_subseries
    
    class Meta:
        model = SeriesDoc
        fields = '__all__'
        extra_kwargs = {
            'id_serie_doc': {'read_only': True}
        }
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

class SeriesDocPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeriesDoc
        fields = '__all__' # SE PUEDE ACTUALIZAR EL CODIGO?
        extra_kwargs = {
            'id_serie_doc': {'read_only': True},
            'codigo': {'read_only': True},
            'id_ccd': {'read_only': True}
        }
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

class SubseriesDocPostSerializer(serializers.ModelSerializer):
    id_ccd = serializers.ReadOnlyField(source='id_serie_doc.id_ccd.id_ccd', default=None)
    
    def validate_id_serie_doc(self, value):
        if value.id_ccd.actual:
            raise serializers.ValidationError('No puede crear subseries a un CCD actual')
        elif value.id_ccd.fecha_terminado:
            raise serializers.ValidationError('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif value.id_ccd.fecha_retiro_produccion:
            raise serializers.ValidationError('No puede realizar esta acción a un CCD retirado de producción')
        return value
    
    def validate_nombre(self, value):
        serie = SeriesDoc.objects.filter(id_serie_doc=self.initial_data['id_serie_doc']).first()
        subseries = SubseriesDoc.objects.filter(nombre=value, id_serie_doc__id_ccd=serie.id_ccd.id_ccd)
        if subseries:
            raise serializers.ValidationError('No puede existir más de una subserie con el mismo nombre para este CCD')
        return value
    
    class Meta:
        model = SubseriesDoc
        fields = '__all__'
        extra_kwargs = {
            'id_subserie_doc': {'read_only': True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=SubseriesDoc.objects.all(),
                fields = ['id_serie_doc', 'codigo'],
                message='No puede existir más de una subserie con el mismo código para esta serie'
            ),
            UniqueTogetherValidator(
                queryset=SubseriesDoc.objects.all(),
                fields = ['id_serie_doc', 'nombre'],
                message='No puede existir más de una subserie con el mismo nombre para esta serie'
            )
        ]  

class SubseriesDocPutSerializer(serializers.ModelSerializer):
    id_ccd = serializers.ReadOnlyField(source='id_serie_doc.id_ccd.id_ccd', default=None)
    
    def validate_nombre(self, value):
        subseries = SubseriesDoc.objects.filter(nombre=value).exclude(id_subserie_doc=self.instance.id_subserie_doc)
        if subseries:
            raise serializers.ValidationError('No puede existir más de una subserie con el mismo nombre para este CCD')
        return value
    
    class Meta:
        model = SubseriesDoc
        fields = '__all__' # SE PUEDE ACTUALIZAR EL CODIGO?
        extra_kwargs = {
            'id_subserie_doc': {'read_only': True},
            'codigo': {'read_only': True},
            'id_serie_doc': {'read_only': True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=SubseriesDoc.objects.all(),
                fields = ['id_serie_doc', 'codigo'],
                message='No puede existir más de una subserie con el mismo código para esta serie'
            ),
            UniqueTogetherValidator(
                queryset=SubseriesDoc.objects.all(),
                fields = ['id_serie_doc', 'nombre'],
                message='No puede existir más de una subserie con el mismo nombre para esta serie'
            )
        ]  

class CCDSerializer(serializers.ModelSerializer):
    # series = serializers.SerializerMethodField()
    # subseries = serializers.SerializerMethodField()
    usado = serializers.SerializerMethodField()
    
    # def get_series(self,obj):
    #     series = SeriesDoc.objects.filter(id_ccd=obj.id_ccd)
    #     serializer_series = SeriesDocPostSerializer(series, many=True)
    #     return serializer_series.data
    
    # def get_subseries(self,obj):
    #     subseries = SubseriesDoc.objects.filter(id_serie_doc__id_ccd=obj.id_ccd)
    #     serializer_subseries = SeriesDocPostSerializer(subseries, many=True)
    #     return serializer_subseries.data
    
    def get_usado(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd)
        usado = True if trd else False
        
        return usado
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = (
            'id_ccd',
            'id_organigrama',
            'version',
            'nombre',
            'fecha_terminado',
            'usado',
            'fecha_puesta_produccion',
            'fecha_retiro_produccion',
            'justificacion',
            'ruta_soporte',
            'actual'
            # 'series',
            # 'subseries',
        )
        
class CCDPosiblesSerializer(serializers.ModelSerializer):
    trd = serializers.SerializerMethodField()
    tca = serializers.SerializerMethodField()
    
    def get_trd(self,ccd):
        trd = ccd.tablaretenciondocumental
        trd_data = {
            'nombre': trd.nombre,
            'version': trd.version
        }
        return trd_data
    
    def get_tca(self,ccd):
        trd = ccd.tablaretenciondocumental
        tca = trd.tablascontrolacceso
        tca_data = {
            'nombre': tca.nombre,
            'version': tca.version
        }
        return tca_data
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = (
            'id_ccd',
            'nombre',
            'version',
            'trd',
            'tca'
        )

class CCDPostSerializer(serializers.ModelSerializer):
    def validate_valor_aumento_serie(self, value):
        valores_aumento = [1,2,5,10]
        if value not in valores_aumento:
            raise serializers.ValidationError('Debe elegir un valor de aumento entre el rango establecido (1,2,5,10)')
        return value
    
    def validate_valor_aumento_subserie(self, value):
        valores_aumento = [1,2,5,10]
        if value not in valores_aumento:
            raise serializers.ValidationError('Debe elegir un valor de aumento entre el rango establecido (1,2,5,10)')
        return value
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'id_organigrama', 'version', 'nombre', 'valor_aumento_serie', 'valor_aumento_subserie', 'ruta_soporte']
        extra_kwargs = {
            'id_organigrama': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True},
            'valor_aumento_serie': {'required': True},
            'valor_aumento_subserie': {'required': True}
        }

class CCDPutSerializer(serializers.ModelSerializer):
    def validate_valor_aumento_serie(self, value):
        valores_aumento = [1,2,5,10]
        if self.instance:
            if value and int(value) not in valores_aumento:
                raise serializers.ValidationError('Debe elegir un valor de aumento entre el rango establecido (1,2,5,10)')
            
            series = self.instance.seriesdoc_set.all()
            
            if value and int(value) != self.instance.valor_aumento_serie:
                if len(series) > 1:
                    raise serializers.ValidationError('No puede cambiar el valor de aumento de las series porque ya ha creado más de una serie')
            
        return value
    
    def validate_valor_aumento_subserie(self, value):
        valores_aumento = [1,2,5,10]
        if self.instance:
            if value and int(value) not in valores_aumento:
                raise serializers.ValidationError('Debe elegir un valor de aumento entre el rango establecido (1,2,5,10)')
        
            series = self.instance.seriesdoc_set.all()
            
            if value and int(value) != self.instance.valor_aumento_subserie:
                for serie in series:
                    subseries = serie.subseriesdoc_set.all()
                    if len(subseries) > 1:
                        raise serializers.ValidationError('No puede cambiar el valor de aumento de las subseries porque ya ha creado más de una subserie')
        
        return value
        
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'id_organigrama', 'version', 'nombre', 'valor_aumento_serie', 'valor_aumento_subserie', 'ruta_soporte']
        extra_kwargs = {
            'id_ccd': {'read_only': True},
            'id_organigrama': {'read_only': True},
            'version': {'required': True},
            'nombre': {'required': True},
            'valor_aumento_serie': {'required': True},
            'valor_aumento_subserie': {'required': True}
        }

class CCDActivarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['fecha_terminado']
        extra_kwargs = {
            'fecha_terminado': {'read_only': True}
        }

class CatalogosSeriesUnidadSerializer(serializers.ModelSerializer):
    id_ccd = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_ccd.id_ccd', default=None)
    seccion = serializers.SerializerMethodField()
    subseccion = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    id_serie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_cat_serie_und = serializers.SerializerMethodField()
    subseries = serializers.SerializerMethodField()
    subseries_nombres = serializers.SerializerMethodField()
    
    def get_seccion(self, obj):
        seccion = UnidadesOrganizacionales.objects.filter(id_organigrama=obj.id_unidad_organizacional.id_organigrama.id_organigrama, cod_agrupacion_documental='SEC').first()
        if not seccion:
            seccion = None
        return seccion.nombre
    
    def get_subseries(self, obj):
        serie_subseries_instances = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=obj.id_unidad_organizacional.id_unidad_organizacional, id_catalogo_serie__id_serie_doc=obj.id_catalogo_serie.id_serie_doc.id_serie_doc).exclude(id_catalogo_serie__id_subserie_doc=None)
        subseries_instances = [serie_subserie.id_catalogo_serie.id_subserie_doc for serie_subserie in serie_subseries_instances]
        for subserie in subseries_instances:
            subserie.id_cat_serie_und = serie_subseries_instances.filter(id_subserie_doc=subserie.id_subserie_doc).first().id_cat_serie_und
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
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_ccd', 'id_unidad_organizacional', 'seccion', 'subseccion', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_cat_serie_und', 'subseries_nombres', 'subseries']
        validators = [
            UniqueTogetherValidator(
                queryset=CatalogosSeriesUnidad.objects.all(),
                fields = ['id_unidad_organizacional', 'id_catalogo_serie'],
                message='La combinación del catalogo y la unidad organizacional debe ser única'
            )
        ]

class AsignacionesCatalogosOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogosSeriesUnidad
        fields = '__all__'      
        validators = [
            UniqueTogetherValidator(
                queryset=CatalogosSeriesUnidad.objects.all(),
                fields = ['id_unidad_organizacional', 'id_catalogo_serie'],
                message='La combinación del catalogo y la unidad organizacional debe ser única'
            )
        ]
 
class CatalogoSerieSubserieSerializer(serializers.ModelSerializer):
    nombre_serie = serializers.ReadOnlyField(source='id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_serie_doc.codigo', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_subserie_doc.codigo', default=None)
    
    def validate_id_serie_doc(self, value):
        # VALIDACIONES CCD
        if value.id_ccd.fecha_terminado and not value.id_ccd.actual:
            raise serializers.ValidationError('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif value.id_ccd.fecha_retiro_produccion:
            raise serializers.ValidationError('No puede realizar esta acción a un CCD retirado de producción')
        
        # VALIDACION NO EXISTA EN CATALOGO
        if value.catalogosseries_set.all().filter(id_subserie_doc=None):
            raise serializers.ValidationError('No puede relacionar la misma serie más de una vez en el catalogo')
        
        return value
    
    class Meta:
        model = CatalogosSeries
        fields = ['id_catalogo_serie', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_subserie_doc', 'nombre_subserie', 'codigo_subserie']
        extra_kwargs = {
            'id_catalogo_serie': {'read_only':True},
            'id_subserie_doc': {'read_only':True}
        }
        
class CatalogosSeriesUnidadSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.codigo', default=None)
    
    def validate_id_catalogo_serie(self, value):
        # VALIDACIONES CCD
        if value.id_serie_doc.id_ccd.fecha_terminado and not value.id_serie_doc.id_ccd.actual:
            raise serializers.ValidationError('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif value.id_serie_doc.id_ccd.fecha_retiro_produccion:
            raise serializers.ValidationError('No puede realizar esta acción a un CCD retirado de producción')
        
        return value
    
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_cat_serie_und', 'id_unidad_organizacional', 'id_catalogo_serie', 'id_serie_doc', 'nombre_serie', 'codigo_serie', 'id_subserie_doc', 'nombre_subserie', 'codigo_subserie']
        extra_kwargs = {
            'id_cat_serie_und': {'read_only':True}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=CatalogosSeriesUnidad.objects.all(),
                fields = ['id_unidad_organizacional', 'id_catalogo_serie'],
                message='No puede relacionar el mismo item de catalogo de serie y subserie más de una vez'
            )
        ]

class BusquedaCCDSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd)
        usado = True if trd else False
        
        return usado
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields ='__all__'

class BusquedaCCDHomologacionSerializer(serializers.ModelSerializer):
    id_organigrama = serializers.ReadOnlyField(source='id_organigrama.id_organigrama',default=None)
    nombre_organigrama = serializers.ReadOnlyField(source='id_organigrama.nombre',default=None)
    version_organigrama = serializers.ReadOnlyField(source='id_organigrama.version',default=None)
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd)
        usado = True if trd else False
        return usado

    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'nombre', 'version', 'usado', 'fecha_terminado', 'id_organigrama', 'nombre_organigrama', 'version_organigrama']

class SeriesDocUnidadHomologacionesSerializer(serializers.ModelSerializer):
    id_organigrama = serializers.ReadOnlyField(source='id_organigrama.id_organigrama',default=None)

    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional', 'codigo', 'nombre', 'id_organigrama']

class SeriesDocUnidadCatSerieHomologacionesSerializer(serializers.ModelSerializer):
    id_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre',default=None)

    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_unidad_organizacional', 'id_cat_serie_und', 'id_serie', 'cod_serie', 'nombre_serie', 'id_subserie', 'cod_subserie', 'nombre_subserie']

class UnidadesSeccionPersistenteTemporalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesSeccionPersistenteTemporal
        fields = '__all__'

class AgrupacionesDocumentalesPersistenteTemporalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgrupacionesDocumentalesPersistenteTemporal
        fields = '__all__'

class UnidadesSeccionResponsableTemporalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesSeccionResponsableTemporal
        fields = '__all__'

#   LLAMADO DE SERIALIZADOR DENTRO DE OTRO SERIALIZADOR CON RELACION
# class SeriesDocSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SeriesDoc
#         fields = ['id_serie_doc', 'codigo', 'nombre']

# class SubseriesDocSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SubseriesDoc
#         fields = ['id_subserie_doc', 'codigo', 'nombre']

# class CompararSeriesDocUnidadCatSerieSerializer(serializers.ModelSerializer):
#     serie = SeriesDocSerializer(source='id_catalogo_serie.id_serie_doc', read_only=True)
#     subserie = SubseriesDocSerializer(source='id_catalogo_serie.id_subserie_doc', read_only=True)


#     class Meta:
#         model = CatalogosSeriesUnidad
#         fields = ['id_unidad_organizacional', 'id_catalogo_serie', 'serie', 'subserie']

