from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import (
    TipologiasDoc,
    TablaRetencionDocumental,
    FormatosTiposMedio,
    CatSeriesUnidadOrgCCDTRD,
    SeriesSubSUnidadOrgTRDTipologias
)
from gestion_documental.choices.tipos_medios_formato_choices import tipos_medios_formato_CHOICES
from transversal.models.organigrama_models import UnidadesOrganizacionales

class TipologiasDocumentalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiasDoc
        fields = '__all__'
        # validators = [
        #    UniqueTogetherValidator(
        #        queryset=TipologiasDoc.objects.all(),
        #        fields = ['id_trd', 'codigo'],
        #        message='No puede registrar más de una tipología con el mismo código para esta TRD'
        #    ),
        #    UniqueTogetherValidator(
        #        queryset=TipologiasDocumentales.objects.all(),
        #        fields = ['id_trd', 'nombre'],
        #        message='No puede registrar más de una tipología con el mismo nombre para esta TRD'
        #    )
        # ]
class CrearTipologiaDocumentalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TipologiasDoc
        fields = ['nombre','cod_tipo_medio_doc']
        
class RetornarDatosTRDSerializador(serializers.ModelSerializer):
    
    nombre = serializers.ReadOnlyField(source='id_catserie_unidadorg_ccd_trd.id_trd.nombre', default=None)
    version = serializers.ReadOnlyField(source='id_catserie_unidadorg_ccd_trd.id_trd.version', default=None)
    
    class Meta:
        model = SeriesSubSUnidadOrgTRDTipologias
        fields = '__all__'

class ModificarTipologiaDocumentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiasDoc
        fields = ['nombre','activo','cod_tipo_medio_doc']
        
class BuscarTipologiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiasDoc
        fields = '__all__'

class BusquedaTRDNombreVersionSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    id_organigrama = serializers.ReadOnlyField(source='id_ccd.id_organigrama', default=None)
    
    def get_usado(self,obj):
        tca = TablasControlAcceso.objects.filter(id_trd=obj.id_trd)
        usado = True if tca else False
        
        return usado
    
    class Meta:
        model = TablaRetencionDocumental
        fields = '__all__'
        
class ModificarTRDNombreVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaRetencionDocumental
        #fields = '__all__'
        fields = ['nombre','version']
        extra_kwargs = {
            'nombre': {'allow_null':False, 'allow_blank':False},
            'version': {'allow_null':False, 'allow_blank':False},
        }
  
class TipologiasDocumentalesPutSerializer(serializers.ModelSerializer):
    # formatos = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    class Meta:
        model = TipologiasDoc
        fields = ('id_tipologia_documental', 'nombre', 'cod_tipo_medio_doc')
        # validators = [
        #    UniqueTogetherValidator(
        #        queryset=TipologiasDocumentales.objects.all(),
        #        fields = ['id_trd', 'codigo'],
        #        message='No puede registrar más de una tipología con el mismo código para esta TRD'
        #    ),
        #    UniqueTogetherValidator(
        #        queryset=TipologiasDocumentales.objects.all(),
        #        fields = ['id_trd', 'nombre'],
        #        message='No puede registrar más de una tipología con el mismo nombre para esta TRD'
        #    )
        # ]

class TRDSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        tca = TablasControlAcceso.objects.filter(id_trd=obj.id_trd)
        usado = True if tca else False
        
        return usado
    
    class Meta:
        model = TablaRetencionDocumental
        fields = '__all__'

class TRDPostSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablaRetencionDocumental.objects.all(), message='La versión de la Tabla de Retención Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablaRetencionDocumental.objects.all(), message='El nombre de la Tabla de Retención Documental debe ser único')])

    class Meta:
        model = TablaRetencionDocumental
        fields = ['id_trd', 'id_ccd', 'version', 'nombre']
        extra_kwargs = {
            'id_ccd': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }


class TRDPutSerializer(serializers.ModelSerializer):
    version = serializers.CharField(validators=[UniqueValidator(queryset=TablaRetencionDocumental.objects.all(), message='La versión de la Tabla de Retención Documental debe ser único')])
    nombre = serializers.CharField(validators=[UniqueValidator(queryset=TablaRetencionDocumental.objects.all(), message='El nombre de la Tabla de Retención Documental debe ser único')])

    class Meta:
        model = TablaRetencionDocumental
        fields = ['version', 'nombre']
        extra_kwargs = {
            'version': {'required': True},
            'nombre': {'required': True}
        }


class TRDFinalizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaRetencionDocumental
        fields = ['fecha_terminado']
        extra_kwargs = {
            'fecha_terminado': {'read_only': True}
        }

class FormatosTiposMedioSerializer(serializers.ModelSerializer):
    tipo_medio_doc = serializers.ReadOnlyField(source="cod_tipo_medio_doc.nombre")
       
    class Meta:
        model = FormatosTiposMedio
        fields = '__all__'

class FormatosTiposMedioPostSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(max_length=30)

    class Meta:
        model = FormatosTiposMedio
        fields = ['cod_tipo_medio_doc', 'nombre', 'activo']
        extra_kwargs = {
            'cod_tipo_medio_doc': {'required': True},
            'nombre': {'required': True}
        }
        validators = [
           UniqueTogetherValidator(
               queryset=FormatosTiposMedio.objects.all(),
               fields = ['cod_tipo_medio_doc', 'nombre'],
               message='No puede registrar un tipo de medio más de una vez con el mismo nombre'
           )
        ]
class ReanudarTrdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaRetencionDocumental
        fields = '__all__'

class EliminarCatSerieUndOrgCCDTRD218Serializer(serializers.ModelSerializer):
    class Meta:
        model = CatSeriesUnidadOrgCCDTRD
        fields = '__all__'
       
class SeriesSubSeriesUnidadesOrgTRDSerializer(serializers.ModelSerializer):
    tipologias = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    class Meta:
        model = CatSeriesUnidadOrgCCDTRD
        fields = (
            'id_trd',
            'id_cat_serie_und',
            'cod_disposicion_final',
            'digitalizacion_dis_final',
            'tiempo_retencion_ag',
            'tiempo_retencion_ac',
            'descripcion_procedimiento',
            'tipologias'
        )
        extra_kwargs = {
            'id_trd': {'required': True},
            'id_cat_serie_und': {'required': True},
        }
        validators = [UniqueTogetherValidator(
               queryset=CatSeriesUnidadOrgCCDTRD.objects.all(),
               fields = ['id_trd', 'id_cat_serie_und'],
               message='No puede relacionar un mismo expediente más de una vez con esta TRD'
           )]

            
class SeriesSubSeriesUnidadesOrgTRDPutSerializer(serializers.ModelSerializer):
    tipologias = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    class Meta:
        model = CatSeriesUnidadOrgCCDTRD
        fields = (
            'cod_disposicion_final',
            'digitalizacion_dis_final',
            'tiempo_retencion_ag',
            'tiempo_retencion_ac',
            'descripcion_procedimiento',
            'justificacion_cambio',
            'tipologias',
            'ruta_archivo_cambio'
        )
        

class GetSeriesSubSUnidadOrgTRDSerializer(serializers.ModelSerializer):
    nombre_unidad = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.nombre',default =None)
    cod_unidad_org = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional',default =None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre', default=None)
    cod_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    cod_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    disposicion_final = serializers.ReadOnlyField(source='cod_disposicion_final.cod_disposicion_final', default=None)
    # version = serializers.ReadOnlyField(source='id_trd.version')
    class Meta:
        model = CatSeriesUnidadOrgCCDTRD
        fields = '__all__'

class GetSeriesSubSUnidadOrgTRDTipologiasSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SeriesSubSUnidadOrgTRDTipologias
        fields = '__all__'


class GetTipologiasDocumentalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiasDoc
        fields = '__all__'