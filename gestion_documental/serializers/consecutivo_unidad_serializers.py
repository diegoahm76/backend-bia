from rest_framework import serializers
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad

from gestion_documental.models.consecutivo_unidad_models import ConfigTipoConsecAgno, Consecutivo
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.serializers.pqr_serializers import ArchivosSerializer
from transversal.models.organigrama_models import UnidadesOrganizacionales
from datetime import datetime, date, timedelta
class ConfigTipoConsecAgnoGetSerializer(serializers.ModelSerializer):
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad.nombre', default=None)
    persona_configura = serializers.SerializerMethodField()
    class Meta:
        model = ConfigTipoConsecAgno
        fields = '__all__'

    def get_persona_configura(self,obj):
        nombre_completo_responsable = None
        if obj.id_persona_config_implementacion:
            nombre_completo_responsable = None
            nombre_list = [obj.id_persona_config_implementacion.primer_nombre, obj.id_persona_config_implementacion.segundo_nombre,
                            obj.id_persona_config_implementacion.primer_apellido, obj.id_persona_config_implementacion.segundo_apellido]
            nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
        
class ConfigTipoConsecAgnoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTipoConsecAgno
        fields = '__all__'

class ConfigTipoConsecAgnoPutConSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTipoConsecAgno
        fields = '__all__'

class UnidadesGetSerializer(serializers.ModelSerializer):
    #nombre_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_unidad_org_actual_admin_series.nombre', default=None)
    #codigo_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_unidad_org_actual_admin_series.codigo', default=None)
    tiene_configuracion = serializers.SerializerMethodField()

    def get_tiene_configuracion(self, obj):
        id_configuracion = None
        
        hoy = date.today()
        age = hoy.year
        instance = ConfigTipoConsecAgno.objects.filter(id_unidad=obj.id_unidad_organizacional,agno_consecutivo=age).first()

    

        if not instance:
            return False
        
        return True

    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional','codigo','nombre','tiene_configuracion']

class ConsecutivoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consecutivo
        fields = '__all__'


class CatalogosSeriesUnidadGetSerializer(serializers.ModelSerializer):


    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie.id_subserie_doc.nombre',default=None)
    tiene_configuracion = serializers.SerializerMethodField()
    class Meta:
        model = CatalogosSeriesUnidad
        fields = ['id_cat_serie_und','id_serie_doc','cod_serie_doc','nombre_serie_doc','id_subserie_doc','cod_subserie_doc','nombre_subserie_doc','tiene_configuracion']
    def get_tiene_configuracion(self, obj):
        id_configuracion = None

        hoy = date.today()
        age = hoy.year
        instance = ConfigTipoConsecAgno.objects.filter(id_unidad=obj.id_unidad_organizacional, id_catalogo_serie_unidad=obj,agno_consecutivo=age).first()


        if not instance:
            return False

        return True

class ConsecutivoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consecutivo
        fields = '__all__'

class ConsecutivoGetSerializer(serializers.ModelSerializer):

    consecutivo = serializers.SerializerMethodField()
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad.nombre', default=None)
    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo.id_catalogo_serie.id_subserie_doc.nombre',default=None)
    ruta_archivo = serializers.SerializerMethodField()

    class Meta:
        model = Consecutivo
        fields = '__all__'


    def get_ruta_archivo(self, obj):
        if obj.id_archivo is None:
            return None
        id_archivo_digital = obj.id_archivo.id_archivo_digital
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital =id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data['ruta_archivo']

    def get_consecutivo(self,obj):
        conf = ConfigTipoConsecAgno.objects.filter(agno_consecutivo=obj.agno_consecutivo,id_unidad=obj.id_unidad).first()

        numero_con_ceros = str(obj.nro_consecutivo).zfill(conf.cantidad_digitos)
        cod_se_sub = ""

        if obj.id_catalogo:
            cod_serie = obj.id_catalogo.id_catalogo_serie.id_serie_doc.codigo
            cod_se_sub = cod_serie
            if obj.id_catalogo.id_catalogo_serie.id_subserie_doc:
                cod_subserie =obj.id_catalogo.id_catalogo_serie.id_subserie_doc.codigo
                cod_se_sub = cod_serie+'.'+cod_subserie
        
        if cod_se_sub != "":

            conseg_nuevo = obj.id_unidad.codigo+'.'+cod_se_sub+'.'+str(obj.agno_consecutivo)[-2:]+'.'+numero_con_ceros
        else:
            conseg_nuevo = obj.id_unidad.codigo+'.'+str(obj.agno_consecutivo)[-2:]+'.'+numero_con_ceros
        
        return conseg_nuevo

