from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import CatalogosSeries, CatalogosSeriesUnidad
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import (
    HistoricosCatSeriesUnidadOrgCCDTRD,
    TipologiasDoc,
    TablaRetencionDocumental,
    FormatosTiposMedio,
    CatSeriesUnidadOrgCCDTRD,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedioTipoDoc
)
from gestion_documental.choices.tipos_medios_formato_choices import tipos_medios_formato_CHOICES
from transversal.models.organigrama_models import UnidadesOrganizacionales

class TipologiasDocumentalesSerializer(serializers.ModelSerializer):
    tipo_medio_doc = serializers.ReadOnlyField(source='cod_tipo_medio_doc.nombre', default=None)
    
    class Meta:
        model = TipologiasDoc
        fields = '__all__'
        
class TipologiasSeriesSubSUnidadOrgTRDSerializer(serializers.ModelSerializer):
    id_tipologia_documental = serializers.ReadOnlyField(source='id_tipologia_doc.id_tipologia_documental', default=None)
    nombre = serializers.ReadOnlyField(source='id_tipologia_doc.nombre', default=None)
    cod_tipo_medio_doc = serializers.ReadOnlyField(source='id_tipologia_doc.cod_tipo_medio_doc.cod_tipo_medio_doc', default=None)
    item_ya_usado = serializers.ReadOnlyField(source='id_tipologia_doc.item_ya_usado', default=None)
    
    class Meta:
        model = SeriesSubSUnidadOrgTRDTipologias
        fields = [
            'id_tipologia_documental',
            'nombre',
            'cod_tipo_medio_doc',
            'activo',
            'item_ya_usado',
            'reservada'
        ]

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
    formatos = serializers.SerializerMethodField()
    tipo_medio_doc = serializers.ReadOnlyField(source='cod_tipo_medio_doc.nombre', default=None)

    def get_formatos(self, obj):
        formatos = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=obj.id_tipologia_documental)
        list_id_formatos = formatos.values_list('id_formato_tipo_medio__id_formato_tipo_medio', flat=True)
        return list_id_formatos

    class Meta:
        model = TipologiasDoc
        fields = ['id_tipologia_documental', 'nombre', 'cod_tipo_medio_doc', 'tipo_medio_doc', 'activo', 'item_ya_usado', 'formatos']


class BusquedaTRDNombreVersionSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    id_organigrama = serializers.ReadOnlyField(source='id_ccd.id_organigrama.id_organigrama', default=None)
    
    def get_usado(self,obj):
        tca = TablasControlAcceso.objects.filter(id_trd=obj.id_trd)
        usado = True if tca else False
        
        return usado
    
    class Meta:
        model = TablaRetencionDocumental
        fields = ['id_trd','id_ccd','id_organigrama','version','nombre','fecha_terminado','fecha_puesta_produccion','fecha_retiro_produccion','actual','usado']

class GetHistoricoTRDSerializer(serializers.ModelSerializer):
    persona_cambia = serializers.SerializerMethodField()
    
    def get_persona_cambia(self, obj):
        persona_cambia = None
        if obj.id_persona_cambia:
            nombre_list = [obj.id_persona_cambia.primer_nombre, obj.id_persona_cambia.segundo_nombre,
                            obj.id_persona_cambia.primer_apellido, obj.id_persona_cambia.segundo_apellido]
            persona_cambia = ' '.join(item for item in nombre_list if item is not None)
            persona_cambia = persona_cambia if persona_cambia != "" else None
        return persona_cambia
    
    class Meta:
        model = HistoricosCatSeriesUnidadOrgCCDTRD
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

    class Meta:
        model = TablaRetencionDocumental
        fields = ['id_trd', 'id_ccd', 'version', 'nombre']
        extra_kwargs = {
            'id_ccd': {'required': True},
            'version': {'required': True},
            'nombre': {'required': True}
        }


class TRDPutSerializer(serializers.ModelSerializer):

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
        #fields = ['cod_tipo_medio_doc', 'nombre', 'activo']
        fields = '__all__'
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


class FormatosTiposMedioPutSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(max_length=30)
    id_formato_tipo_medio = serializers.ReadOnlyField()
    cod_tipo_medio_doc = serializers.ReadOnlyField()
    nombre = serializers.ReadOnlyField()
    class Meta:
        model = FormatosTiposMedio
        #fields = ['cod_tipo_medio_doc', 'nombre', 'activo']
        fields = '__all__'
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
    cod_unidad_org = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.codigo',default =None)
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

#Enetrega 61 reportes de permisos de documentos

class TablasControlAccesoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = ['id_tca','nombre','nombre','version']

class TablaRetencionDocumentalPermisosGetsSerializer(serializers.ModelSerializer):
    #id_ccd
    id_ccd = serializers.ReadOnlyField(source='id_ccd.id_ccd',default=None)
    nombre_ccd = serializers.ReadOnlyField(source='id_ccd.nombre',default=None)
    version_ccd = serializers.ReadOnlyField(source='id_ccd.version',default=None)
    id_organigrama = serializers.ReadOnlyField(source='id_ccd.id_organigrama.id_organigrama',default=None)
    nombre_organigrama = serializers.ReadOnlyField(source='id_ccd.id_organigrama.nombre',default=None)
    version_organigrama = serializers.ReadOnlyField(source='id_ccd.id_organigrama.version',default=None)
    tablas_control_acceso = TablasControlAccesoGetSerializer(source='tablascontrolacceso', many=False, read_only=True,default=None)
    class Meta:
        model = TablaRetencionDocumental
        fields = '__all__'
        #fields = ['id_trd','nombre_ccd','version_ccd','tablas_control_acceso']
        # extra_kwargs = {
        #     'id_trd': {'required': True},
        #     'id_ccd': {'required': True}}
class UnidadSeccionSubseccionGetSerializer(serializers.ModelSerializer):
    #nombre_unidad = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre',default=None)
    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional','nombre']

class PermisosUndsOrgActualesSerieExpCCDSerializer(serializers.ModelSerializer):
    nombre_unidad_ornaginazional_actual = serializers.ReadOnlyField(source='id_und_organizacional_actual.nombre',default=None)

    class Meta:
        model = PermisosUndsOrgActualesSerieExpCCD
        fields = '__all__'

class SerieSubserieReporteSerializer(serializers.ModelSerializer):
    nombre_serie = serializers.ReadOnlyField(source='id_serie_doc.nombre',default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_subserie_doc.nombre',default=None)
    class Meta:
        model = CatalogosSeries
        fields = ['id_catalogo_serie' ,'id_serie_doc','nombre_serie','id_subserie_doc','nombre_subserie']

class DenegacionPermisosGetUnidadSerializer(serializers.ModelSerializer):
    
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