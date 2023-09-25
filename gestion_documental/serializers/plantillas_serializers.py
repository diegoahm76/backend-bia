from rest_framework import serializers
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc


class ArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'


class  PlantillasDocCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PlantillasDoc
        fields = '__all__'

class PlantillasDocBusquedaAvanzadaSerializer(serializers.ModelSerializer):
    nombre_tipologia=serializers.ReadOnlyField(source='id_tipologia_doc_trd.nombre',default=None)
    archivos_digitales = ArchivosDigitalesSerializer(source='id_archivo_digital', read_only=True)
    class Meta:
        model = PlantillasDoc
        
        fields = ['id_plantilla_doc',
    'nombre',
    'descripcion',
    'id_archivo_digital',
    'id_formato_tipo_medio',
    'asociada_a_tipologia_doc_trd',
    'id_tipologia_doc_trd',
    'nombre_tipologia',
    'otras_tipologias',
    'codigo_formato_calidad_asociado',
    'version_formato_calidad_asociado',
    'cod_tipo_acceso',
    'observacion',
    'activa',
    'fecha_creacion',
    'id_persona_crea_plantilla','archivos_digitales']
        
class  PlantillasDocBusquedaAvanzadaDetalleSerializer(serializers.ModelSerializer):
    nombre_tipologia=serializers.ReadOnlyField(source='id_tipologia_doc_trd.nombre',default=None)
    ruta=serializers.ReadOnlyField(source='id_archivo_digital.ruta_archivo',default=None)
    extension=serializers.ReadOnlyField(source='id_archivo_digital.formato',default=None)
    cod_tipo_acceso_display = serializers.CharField(source='get_cod_tipo_acceso_display', default=None)
    class Meta:
        model =  PlantillasDoc
        fields = ['id_plantilla_doc','nombre','fecha_creacion','nombre_tipologia','ruta','extension','activa','cod_tipo_acceso_display']


class  PlantillasDocGetSeriallizer(serializers.ModelSerializer):
    nombre_creador=serializers.ReadOnlyField(source='id_persona_crea_plantilla.nombre',default=None)
    nombre_completo = serializers.SerializerMethodField()
    cod_tipo_acceso_display = serializers.CharField(source='get_cod_tipo_acceso_display', default=None)
    class Meta:
        model =  PlantillasDoc
        fields = '__all__'

    def get_nombre_completo(self, obj):
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_crea_plantilla.primer_nombre, obj.id_persona_crea_plantilla.segundo_nombre,
                            obj.id_persona_crea_plantilla.primer_apellido, obj.id_persona_crea_plantilla.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
            return nombre_completo_responsable





class  PlantillasDocUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PlantillasDoc
        fields = '__all__'
class  TipologiasDocSerializerGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TipologiasDoc
        fields = '__all__'

class AccesoUndsOrg_PlantillaDocCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  AccesoUndsOrg_PlantillaDoc
        fields = '__all__'

class AccesoUndsOrg_PlantillaDocGetSerializer(serializers.ModelSerializer):
    nombre_unidad=serializers.ReadOnlyField(source='id_und_organizacional.nombre',default=None)
    class Meta:
        model =  AccesoUndsOrg_PlantillaDoc
        fields = '__all__'





class PlantillasDocSerializer(serializers.ModelSerializer):
    accesos_unidades_organizacionales = AccesoUndsOrg_PlantillaDocGetSerializer(many=True, read_only=True)
    class Meta:
        model = PlantillasDoc
        fields = '__all__'



