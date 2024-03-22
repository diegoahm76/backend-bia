from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales
from gestion_documental.choices.cod_tipo_documento_choices import cod_tipo_documento_CHOICES
from transversal.models.base_models import HistoricoCargosUndOrgPersona, ClasesTercero
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno
from datetime import timedelta, datetime


from gestion_documental.models.notificaciones_models import (
    NotificacionesCorrespondencia, 
    Registros_NotificacionesCorrespondecia, 
    AsignacionNotificacionCorrespondencia, 
    TiposNotificacionesCorrespondencia, 
    TiposAnexosSoporte, 
    Anexos_NotificacionesCorrespondencia, 
    EstadosNotificacionesCorrespondencia, 
    HistoricosEstados, 
    CausasOAnomalias,
    TiposDocumentos
    )

class NotificacionesCorrespondenciaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

class NotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    nommbre_tipo_documento = serializers.CharField(source='cod_tipo_documento.nombre')
    registros_notificaciones = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    funcuinario_solicitante = serializers.SerializerMethodField()
    unidad_solicitante = serializers.CharField(source='id_und_org_oficina_solicita.nombre')
    estado_notificacion = estado_solicitud = serializers.CharField(source='get_cod_estado_display',read_only=True,default=None)

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
    #estado = serializers.CharField(source='id_estado_actual_registro.nombre')
    plazo_entrega = serializers.SerializerMethodField()
    dias_faltantes = serializers.SerializerMethodField()
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
    
    def get_plazo_entrega(self, obj):
        return obj.fecha_registro + timedelta(days=obj.id_tipo_notificacion_correspondencia.tiempo_en_dias)
    
    def get_dias_faltantes(self, obj):
        fecha_actual = datetime.now()
        dias = fecha_actual - obj.fecha_registro
        return obj.id_tipo_notificacion_correspondencia.tiempo_en_dias - dias.days
        
class Registros_NotificacionesCorrespondeciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = '__all__'


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

class AsignacionNotiCorresGetSerializer(serializers.ModelSerializer):
    id_orden_notificacion = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionNotificacionCorrespondencia
        fields = '__all__'

    def get_id_orden_notificacion(self, obj):
        print(obj.id_persona_asignada.primer_apellido)
        orden_notificacion = Registros_NotificacionesCorrespondecia.objects.filter(id_registro_notificacion_correspondencia=obj.id_orden_notificacion).first()
        return Registros_NotificacionesCorrespondeciaCreateSerializer(orden_notificacion).data
    


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


class TiposDocumentosNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposDocumentos
        fields = '__all__'

