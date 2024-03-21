from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales
from gestion_documental.choices.cod_tipo_documento_choices import cod_tipo_documento_CHOICES
from transversal.models.base_models import HistoricoCargosUndOrgPersona, ClasesTercero
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno


from gestion_documental.models.notificaciones_models import (
    NotificacionesCorrespondencia, 
    Registros_NotificacionesCorrespondecia, 
    AsignacionNotificacionCorrespondencia, 
    TiposNotificacionesCorrespondencia, 
    TiposAnexosSoporte, 
    Anexos_NotificacionesCorrespondencia, 
    EstadosNotificacionesCorrespondencia, 
    HistoricosEstados, 
    CausasOAnomalias
    )

class NotificacionesCorrespondenciaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

class NotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    cod_tipo_documento = serializers.CharField(source='get_cod_tipo_documento_display', read_only=True, default=None)
    registros_notificaciones = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    funcuinario_solicitante = serializers.SerializerMethodField()
    unidad_solicitante = serializers.CharField(source='id_und_org_oficina_solicita.nombre')

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

    def get_registros_notificaciones(self, obj):
        registros_notificaciones = Registros_NotificacionesCorrespondecia.objects.filter(id_notificacion_correspondencia=obj.id_notificacion_correspondencia)
        if registros_notificaciones:
            return Registros_NotificacionesCorrespondeciaSerializer(registros_notificaciones, many=True).data
        
    def get_expediente(self, obj):
        if obj.id_expediente_documental:
            return f"{obj.id_expediente_documental.codigo_exp_und_serie_subserie}.{obj.id_expediente_documental.codigo_exp_Agno}.{obj.id_expediente_documental.codigo_exp_consec_por_agno}"
        else:
            return None
    
    def get_funcuinario_solicitante(self, obj):
        return f"{obj.id_persona_solicita.primer_nombre} {obj.id_persona_solicita.primer_apellido}"
    

class Registros_NotificacionesCorrespondeciaSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = '__all__'

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado_salida:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado_salida.agno_radicado,cod_tipo_radicado=obj.id_radicado_salida.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado_salida.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena


class AsignacionNotificacionCorrespondenciaSerializer(serializers.ModelSerializer):
    vigencia_contrato = serializers.SerializerMethodField()
    persona_asignada = serializers.SerializerMethodField()
    # pendientes = serializers.SerializerMethodField()
    # resueltas = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionNotificacionCorrespondencia
        fields = '__all__'

    def get_vigencia_contrato(self, obj):
        vigencia_contrato = HistoricoCargosUndOrgPersona.objects.filter(id_persona=obj.id_persona_asignada)
        return HistoricoCargosUndOrgPersonaSerializer(vigencia_contrato, many=True).data
    
    def get_persona_asignada(self, obj):
        return f"{obj.id_persona_asignada.primer_nombre} {obj.id_persona_asignada.primer_apellido}"

    
class AsignacionNotiCorresCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionNotificacionCorrespondencia
        fields = '__all__'

class HistoricoCargosUndOrgPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCargosUndOrgPersona
        fields = ['fecha_final_historico']


class AnexosNotificacionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_NotificacionesCorrespondencia
        fields = '__all__'


class TiposNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposNotificacionesCorrespondencia
        fields = '__all__'

class EstadosNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosNotificacionesCorrespondencia
        fields = '__all__'

class CausasOAnomaliasNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CausasOAnomalias
        fields = '__all__'

class TiposAnexosNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposAnexosSoporte
        fields = '__all__'

