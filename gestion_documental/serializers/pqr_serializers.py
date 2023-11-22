from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR, MediosSolicitud
from transversal.models.personas_models import Personas

class TiposPQRGetSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()
    
class TiposPQRUpdateSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    
    cod_tipo_pqr = serializers.ReadOnlyField(default=None)
    nombre = serializers.ReadOnlyField(default=None)
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()
    



 ########################## MEDIOS DE SOLICITUD ##########################

class MediosSolicitudCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'


class MediosSolicitudSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class SolicitudesSerializer(serializers.ModelSerializer):
    nombre_und_org_oficina_solicita = serializers.ReadOnlyField(source='id_und_org_oficina_solicita.nombre')
    nombre_tipo_oficio = serializers.ReadOnlyField(source='get_cod_tipo_oficio_display')
    numero_radicado_salida = serializers.SerializerMethodField()

    def get_numero_radicado_salida(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_salida_id).first()
        numero_radicado_salida = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_salida = '-'.join(data_radicado)
        return numero_radicado_salida
    class Meta:
        model = SolicitudAlUsuarioSobrePQRSDF
        fields = [
            'id_solicitud_al_usuario_sobre_pqrsdf',
            'id_pqrsdf',
            'id_und_org_oficina_solicita',
            'nombre_und_org_oficina_solicita',
            'fecha_solicitud',
            'asunto',
            'descripcion',
            'fecha_radicado_salida',
            'numero_radicado_salida',
            'cod_tipo_oficio',
            'nombre_tipo_oficio'
        ]

class PQRSDFSerializer(serializers.ModelSerializer):
    nombre_estado_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre')
    numero_radicado = serializers.ReadOnlyField(source='id_radicado.nro_radicado')
    numero_radicado_entrada = serializers.SerializerMethodField()
    nombre_completo_titular = serializers.SerializerMethodField()
    solicitudes_pqr = serializers.SerializerMethodField()

    def get_numero_radicado_entrada(self, obj):
        radicado = T262Radicados.objects.filter(id_radicado=obj.id_radicado_id).first()
        numero_radicado_entrada = ''
        if radicado:  
            data_radicado = [radicado.prefijo_radicado, str(radicado.fecha_radicado.year), str(radicado.nro_radicado)]
            numero_radicado_entrada = '-'.join(data_radicado)
        return numero_radicado_entrada

    def get_nombre_completo_titular(self, obj):
        persona = Personas.objects.filter(id_persona=obj.id_persona_titular_id).first()
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo
    
    def get_solicitudes_pqr(self, obj):
        solicitudes = SolicitudAlUsuarioSobrePQRSDF.objects.filter(id_pqrsdf=obj.id_PQRSDF)
        solicitudes_titular = []
        if solicitudes:
            for solicitud in solicitudes:
                estado_solicitud = EstadosSolicitudes.objects.filter(id_estado_solicitud=solicitud.id_estado_actual_solicitud_id).first()
                if(estado_solicitud.nombre != "GUARDADA" and estado_solicitud.nombre != "RESPONDIDA"):
                    solicitudes_serializer = SolicitudesSerializer(solicitud)
                    solicitudes_titular.append(solicitudes_serializer.data)
        return solicitudes_titular

    class Meta:
        model = PQRSDF
        fields = '__all__'

class PQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PQRSDF
        fields = '__all__'

class PQRSDFPutSerializer(serializers.ModelSerializer):
    class Meta:
        model: PQRSDF
        fields = [
            'cod_tipo_PQRSDF',
            'id_persona_titular',
            'id_persona_interpone',
            'cod_relacion_con_el_titular',
            'es_anonima',
            'id_medio_solicitud',
            'cod_forma_presentacion',
            'asunto',
            'descripcion',
            'cantidad_anexos',
            'nro_folios_totales',
            'requiere_rta',
            'dias_para_respuesta',
            'id_sucursal_especifica_implicada',
            'id_persona_recibe',
            'id_sucursal_recepcion_fisica',
            'id_radicado',
            'fecha_radicado',
            'requiere_digitalizacion',
            'id_estado_actual_solicitud',
            'fecha_ini_estado_actual'
        ]

class RadicadoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = T262Radicados
        fields = '__all__'

class AnexosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = [
            'id_anexo',
            'nombre_anexo',
            'orden_anexo_doc',
            'cod_medio_almacenamiento',
            'medio_almacenamiento_otros_Cual',
            'numero_folios',
            'ya_digitalizado'
        ]

class AnexosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'

class AnexosPQRSDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'

class AnexosPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'

class MetadatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosAnexosTmp
        fields = [
            'id_metadatos_anexo_tmp',
            'id_anexo',
            'fecha_creacion_doc',
            'asunto',
            'descripcion',
            'cod_categoria_archivo',
            'es_version_original',
            'tiene_replica_fisica',
            'nro_folios_documento',
            'cod_origen_archivo',
            'id_tipologia_doc',
            'tipologia_no_creada_TRD',
            'palabras_clave_doc',
            'id_archivo_sistema'
        ]
class MetadatosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosAnexosTmp
        fields = '__all__'

class InfoDenunciasPQRSDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoDenuncias_PQRSDF
        fields = '__all__'

class InfoDenunciasPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoDenuncias_PQRSDF
        fields = '__all__'
