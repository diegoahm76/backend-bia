from rest_framework import serializers
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, T262Radicados, TiposPQR, MediosSolicitud
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

class PQRSDFPanelSerializer(serializers.ModelSerializer):
    denuncia = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()

    def get_denuncia(self, obj):
        denuncia = InfoDenuncias_PQRSDF.objects.filter(id_PQRSDF = obj.id_PQRSDF).first()
        if denuncia:
            return InfoDenunciasPQRSDFSerializer(denuncia).data
        return None
    
    def get_anexos(self, obj):
        anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF = obj.id_PQRSDF)
        anexos = []

        if anexos_pqr:
            for anexo_pqr in anexos_pqr:
                anexo = Anexos.objects.filter(id_anexo = anexo_pqr.id_anexo_id).first()
                anexos.append(AnexosPqrsdfPanelSerializer(anexo).data)
        return anexos
    
    def to_representation(self, instance):
        # Organiza la representación para mostrar primero la data del modelo principal y luego los datos anexos
        representation = super().to_representation(instance)
        reordered_representation = {
            'id_PQRSDF': representation['id_PQRSDF'],
            'cod_tipo_PQRSDF': representation['cod_tipo_PQRSDF'],
            'id_persona_titular': representation['id_persona_titular'],
            'id_persona_interpone': representation['id_persona_interpone'],
            'cod_relacion_con_el_titular': representation['cod_relacion_con_el_titular'],
            'es_anonima': representation['es_anonima'],
            'fecha_registro': representation['fecha_registro'],
            'id_medio_solicitud': representation['id_medio_solicitud'],
            'cod_forma_presentacion': representation['cod_forma_presentacion'],
            'asunto': representation['asunto'],
            'descripcion': representation['descripcion'],
            'cantidad_anexos': representation['cantidad_anexos'],
            'nro_folios_totales': representation['nro_folios_totales'],
            'requiere_rta': representation['requiere_rta'],
            'dias_para_respuesta': representation['dias_para_respuesta'],
            'id_sucursal_especifica_implicada': representation['id_sucursal_especifica_implicada'],
            'id_persona_recibe': representation['id_persona_recibe'],
            'id_sucursal_recepcion_fisica': representation['id_sucursal_recepcion_fisica'],
            'id_radicado': representation['id_radicado'],
            'fecha_radicado': representation['fecha_radicado'],
            'requiere_digitalizacion': representation['requiere_digitalizacion'],
            'fecha_envio_definitivo_a_digitalizacion': representation['fecha_envio_definitivo_a_digitalizacion'],
            'fecha_digitalizacion_completada': representation['fecha_digitalizacion_completada'],
            'fecha_rta_final_gestion': representation['fecha_rta_final_gestion'],
            'id_persona_rta_final_gestion': representation['id_persona_rta_final_gestion'],
            'id_estado_actual_solicitud': representation['id_estado_actual_solicitud'],
            'fecha_ini_estado_actual': representation['fecha_ini_estado_actual'],
            'id_doc_dearch_exp': representation['id_doc_dearch_exp'],
            'id_expediente_doc': representation['id_expediente_doc'],
            'denuncia': representation['denuncia'],
            'anexos': representation['anexos']
        }
        return reordered_representation
    class Meta:
        model = PQRSDF
        fields = '__all__'

class AnexosPqrsdfPanelSerializer(serializers.ModelSerializer):
    nombre_medio_almacenamiento = serializers.ReadOnlyField(source='get_cod_medio_almacenamiento_display')
    metadatos = serializers.SerializerMethodField()

    def get_metadatos(self, obj):
        metadatos = MetadatosAnexosTmp.objects.filter(id_anexo = obj.id_anexo).first()
        return MetadatoPanelSerializer(metadatos).data
    class Meta:
        model = Anexos
        fields = [
            'id_anexo',
            'nombre_anexo',
            'orden_anexo_doc',
            'cod_medio_almacenamiento',
            'nombre_medio_almacenamiento',
            'medio_almacenamiento_otros_Cual',
            'numero_folios',
            'ya_digitalizado',
            'observacion_digitalizacion',
            'metadatos'
        ]
class MetadatoPanelSerializer(serializers.ModelSerializer):
    archivo = serializers.SerializerMethodField()

    def get_archivo(self, obj):
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital = obj.id_archivo_sistema_id).first()
        return ArchivosSerializer(archivo).data
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
            'id_archivo_sistema',
            'archivo'
        ]
class PQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PQRSDF
        fields = '__all__'

class PQRSDFPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PQRSDF
        fields = '__all__'

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

class AnexosPutSerializer(serializers.ModelSerializer):
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

class MetadatosPutSerializer(serializers.ModelSerializer):
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

class InfoDenunciasPQRSDFPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoDenuncias_PQRSDF
        fields = '__all__'

class ArchivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'


#Respuesta_PQRSDF

class RespuestaPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaPQR
        fields = '__all__'       

class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'

class AnexoRespuestaPQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'





class RespuestaPQRSDFPanelSerializer(serializers.ModelSerializer):
    anexos = serializers.SerializerMethodField()
    
    def get_anexos(self, obj):
        anexos_pqr = Anexos_PQR.objects.filter(id_PQRSDF=obj.id_pqrsdf)
        anexos = []

        if anexos_pqr:
            for anexo_pqr in anexos_pqr:
                anexo = Anexos.objects.filter(id_anexo = anexo_pqr.id_anexo_id).first()
                anexos.append(AnexosPqrsdfPanelSerializer(anexo).data)
        return anexos
    
    def to_representation(self, instance):
        # Organiza la representación para mostrar primero la data del modelo principal y luego los datos anexos
        representation = super().to_representation(instance)
        reordered_representation = {
            'id_PQRSDF': representation['id_pqrsdf'],
            'id_respuesta_pqr': representation['id_respuesta_pqr'],
            'fecha_respuesta': representation['fecha_respuesta'],
            'descripcion': representation['descripcion'],
            'asunto': representation['asunto'],
            'descripcion': representation['descripcion'],
            'cantidad_anexos': representation['cantidad_anexos'],
            'nro_folios_totales': representation['nro_folios_totales'],
            'id_persona_responde': representation['id_persona_responde'],
            'id_radicado_salida': representation['id_radicado_salida'],
            'fecha_radicado_salida': representation['fecha_radicado_salida'],
            'id_doc_archivo_exp': representation['id_doc_archivo_exp'],
            'anexos': representation['anexos']
        }
        return reordered_representation
    class Meta:
        model = RespuestaPQR
        fields = '__all__'


class PersonasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = '__all__'

class PQRSDFGetSerializer(serializers.ModelSerializer):
    id_persona_recibe = PersonasSerializer(read_only=True)  # Agrega esta línea

    class Meta:
        model = PQRSDF
        fields = '__all__'

    numero_radicado = serializers.SerializerMethodField()

    def get_numero_radicado(self, pqrsdf):
        if pqrsdf.id_radicado:
            radicado = T262Radicados.objects.get(pk=pqrsdf.id_radicado.id_radicado)
            return f"{radicado.prefijo_radicado}-{radicado.agno_radicado}-{radicado.nro_radicado}"
        return None
    
class EstadosSolicitudesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadosSolicitudes
        fields = '__all__'