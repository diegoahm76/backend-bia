from datetime import timedelta
from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR
from gestion_documental.serializers.pqr_serializers import AnexosPqrsdfPanelSerializer
from transversal.models.personas_models import Personas
from transversal.serializers.personas_serializers import PersonasFilterSerializer
from transversal.views.choices_views import TipoDocumentoChoices

class ComplementosSerializer(serializers.ModelSerializer):
    modo_solicitud_complemento = serializers.ReadOnlyField(source='id_medio_solicitud_comple.nombre')
    numero_radicado_complemento = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()

    def get_numero_radicado_complemento(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_id).first()
        numero_radicado_entrada = ''
        if radicado:
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_entrada = '-'.join(data_radicado)
        else:
            'SIN RADICAR'
        return numero_radicado_entrada
    
    def get_anexos(self, obj):
        anexos_complementos = []
        anexos_pqr = Anexos_PQR.objects.filter(id_complemento_usu_PQR = obj.idComplementoUsu_PQR)
        if anexos_pqr:
            ids_anexos = [anexo_pqr.id_anexo_id for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            for anexo in anexos:
                anexos_complementos.append(AnexosPqrsdfPanelSerializer(anexo).data)
        
        return anexos_complementos
    
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'

class PersonaSerializer(serializers.ModelSerializer):
    nombre_tipo_documento = serializers.ReadOnlyField(source='tipo_documento.nombre')

    
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_documento',
            'nombre_tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'razon_social',
            'nombre_comercial'
        ]
class PQRSDFSerializer(serializers.ModelSerializer):
    nombre_tipo_pqrsdf = serializers.ReadOnlyField(source='get_cod_tipo_PQRSDF_display')
    nombre_estado_pqrsdf = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre')
    nombre_relacion_titular = serializers.ReadOnlyField(source='get_cod_relacion_con_el_titular_display')
    numero_radicado_completo = serializers.SerializerMethodField()
 
    def get_numero_radicado_completo(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_id).first()
        numero_radicado_entrada = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_entrada = '-'.join(data_radicado)
        return numero_radicado_entrada

    class Meta:
        model = PQRSDF
        fields = [
            'id_PQRSDF',
            'cod_tipo_PQRSDF',
            'nombre_tipo_pqrsdf',
            'id_estado_actual_solicitud',
            'nombre_estado_pqrsdf',
            'id_radicado',
            'numero_radicado_completo',
            'fecha_radicado',
            'fecha_registro',
            'asunto',
            'descripcion',
            'cod_relacion_con_el_titular',
            'nombre_relacion_titular'
        ]

class ComplementoPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'

class ComplementoPQRSDFPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'


class SolicitudPQRSerializer(serializers.ModelSerializer):
    nombre_estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre')
    nombre_und_org_oficina_solicita = serializers.ReadOnlyField(source='id_und_org_oficina_solicita.nombre')
    numero_radicado_completo = serializers.SerializerMethodField()
    fecha_limite_respuesta = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()

    def get_numero_radicado_completo(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_salida_id).first()
        numero_radicado_salida = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_salida = '-'.join(data_radicado)
        return numero_radicado_salida
    
    def get_fecha_limite_respuesta(self, obj):
        return obj.fecha_radicado_salida + timedelta(days=obj.dias_para_respuesta)
    
    def get_anexos(self, obj):
        anexos_complementos = []
        anexos_pqr = Anexos_PQR.objects.filter(id_solicitud_usu_sobre_PQR = obj.id_solicitud_al_usuario_sobre_pqrsdf)
        if anexos_pqr:
            ids_anexos = [anexo_pqr.id_anexo_id for anexo_pqr in anexos_pqr]
            anexos = Anexos.objects.filter(id_anexo__in=ids_anexos)
            for anexo in anexos:
                anexos_complementos.append(AnexosPqrsdfPanelSerializer(anexo).data)
        
        return anexos_complementos
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = [
            'id_solicitud_al_usuario_sobre_pqrsdf',
            'id_pqrsdf',
            'fecha_solicitud',
            'id_estado_actual_solicitud',
            'nombre_estado_solicitud',
            'id_radicado_salida',
            'fecha_radicado_salida',
            'dias_para_respuesta',
            'fecha_limite_respuesta',
            'numero_radicado_completo',
            'asunto',
            'descripcion',
            'id_und_org_oficina_solicita',
            'nombre_und_org_oficina_solicita',
            'anexos'
        ]




class ComplementosUsu_PQRPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'

class Anexos_RequerimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'