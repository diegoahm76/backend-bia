
from rest_framework import serializers

from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.expedientes_models import ArchivosDigitales
from recaudo.models.referencia_pago_models import ConfigReferenciaPagoAgno, Referencia
from gestion_documental.serializers.pqr_serializers import ArchivosSerializer

class ConfigTipoRefgnoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigReferenciaPagoAgno
        fields = '__all__'


class ReferenciaCreateSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    tipo_documento = serializers.ReadOnlyField(source='tipo_documento.nombre')
    numero_documento = serializers.ReadOnlyField(source='id_persona_solicita.numero_documento')
    consecutivo = serializers.SerializerMethodField()
    ruta_archivo = serializers.SerializerMethodField()
    class Meta:
        model = Referencia
        fields ='__all__'

    def get_ruta_archivo(self, obj):
        if obj.id_archivo is None:
            return None
        id_archivo_digital = obj.id_archivo.id_archivo_digital
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital =id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data['ruta_archivo']
    def get_consecutivo(self,obj):
        instance = ConfigReferenciaPagoAgno.objects.filter(agno_ref=obj.agno_referencia).first()

        cod_se_sub = ""
        if instance.id_catalogo_serie_unidad:
            catalogos_unidad=CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=instance.id_catalogo_serie_unidad).first()
            cod_serie = catalogos_unidad.id_catalogo_serie.id_serie_doc.codigo
            cod_se_sub = cod_serie
            if catalogos_unidad.id_catalogo_serie.id_subserie_doc:
                cod_subserie =catalogos_unidad.id_catalogo_serie.id_subserie_doc.codigo
                cod_se_sub = cod_serie+cod_subserie
        
        numero_con_ceros = str(instance.referencia_actual+1).zfill(instance.cantidad_digitos)
        if cod_se_sub != "":

            conseg_nuevo = instance.id_unidad.codigo+cod_se_sub+str(instance.agno_ref)[-2:]+numero_con_ceros
        else:
            conseg_nuevo = instance.id_unidad.codigo+str(instance.agno_ref)[-2:]+numero_con_ceros
        
        return conseg_nuevo


    def get_nombre_completo(self, obj):
            nombre_completo_solicitante = None
            nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                            obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
            nombre_completo_solicitante = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo_solicitante = nombre_completo_solicitante if nombre_completo_solicitante != "" else None
            return nombre_completo_solicitante

class ConfigTipoRefgnoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigReferenciaPagoAgno
        fields = '__all__'


class ConfigTipoRefgnoGetSerializer(serializers.ModelSerializer):
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad.nombre', default=None)
    persona_configura = serializers.SerializerMethodField()
    id_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.id_serie_doc',default=None)
    cod_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.codigo',default=None)
    nombre_serie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_serie_doc.nombre',default=None)
    id_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.id_subserie_doc',default=None)
    cod_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.codigo',default=None)
    nombre_subserie_doc=serializers.ReadOnlyField(source='id_catalogo_serie_unidad.id_catalogo_serie.id_subserie_doc.nombre',default=None) 
    class Meta:
        model = ConfigReferenciaPagoAgno
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