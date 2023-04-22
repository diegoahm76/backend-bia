from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.trd_models import (
    TipologiasDoc,
    TablaRetencionDocumental,
    FormatosTiposMedio,
    CatSeriesUnidadOrgCCDTRD,
    SeriesSubSUnidadOrgTRDTipologias
)
from gestion_documental.choices.tipos_medios_formato_choices import tipos_medios_formato_CHOICES
from almacen.models.organigrama_models import UnidadesOrganizacionales

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
    tipo_medio_doc = serializers.SerializerMethodField()
    
    def get_tipo_medio_doc(self, obj):
        tipo_medio_doc = 'Electrónico' if obj.cod_tipo_medio_doc == 'E' else 'Físico'
        return tipo_medio_doc
    
    class Meta:
        model = FormatosTiposMedio
        fields = '__all__'

class FormatosTiposMedioPostSerializer(serializers.ModelSerializer):
    cod_tipo_medio_doc = serializers.ChoiceField(choices=tipos_medios_formato_CHOICES)
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
            'tipologias'
        )
        extra_kwargs = {
            'justificacion_cambio': {'required': True},
        }

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
        fields = ['id_catserie_unidadorg','nombre_unidad','cod_unidad_org','nombre_serie','cod_serie','nombre_subserie','cod_subserie','disposicion_final'] 


class GetSeriesSubSUnidadOrgTRDTipologiasSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SeriesSubSUnidadOrgTRDTipologias
        fields = '__all__'


class GetTipologiasDocumentalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiasDoc
        fields = '__all__'