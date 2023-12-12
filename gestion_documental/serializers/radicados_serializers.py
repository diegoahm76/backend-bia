from rest_framework import serializers
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from seguridad.models import (User)
from gestion_documental.models.radicados_models import Anexos, Anexos_PQR, MetadatosAnexosTmp, T262Radicados, Otros, MediosSolicitud
from transversal.models.personas_models import Personas
from gestion_documental.models.expedientes_models import ArchivosDigitales


class RadicadosImprimirSerializer(serializers.ModelSerializer):
    nombre_tipo_radicado = serializers.SerializerMethodField()
    numero_radicado_completo = serializers.SerializerMethodField()
    asunto = serializers.SerializerMethodField()
    titular = serializers.SerializerMethodField()
    fecha_radicado = serializers.SerializerMethodField()
    agno_radicado = serializers.SerializerMethodField()
    

    def get_nombre_tipo_radicado(self, obj):
        nombre_tipo_radicado = ''
        for choice in TIPOS_RADICADO_CHOICES:
            if choice[0] == obj['cod_tipo_radicado']:
                nombre_tipo_radicado = choice[1]
                break
        
        return nombre_tipo_radicado
    
    def get_numero_radicado_completo(self, obj):
        return f"{obj['prefijo_radicado']}-{obj['agno_radicado']}-{obj['nro_radicado']}"

    def get_asunto(self, obj):
        return obj['asunto']
            
    def get_titular(self, obj):
        nombre_persona_titular = ""
        if obj['id_persona_titular']:
            persona_titular = Personas.objects.filter(id_persona = obj['id_persona_titular']).first()
            nombre_persona_titular = f"{persona_titular.primer_nombre} {persona_titular.segundo_nombre} {persona_titular.primer_apellido} {persona_titular.segundo_apellido}"
        
        return nombre_persona_titular

    def get_agno_radicado(self, obj):
        return obj['agno_radicado']
    
    def get_fecha_radicado(self, obj):
        return obj['fecha_radicado']
    
    class Meta:
        model = T262Radicados
        fields = [
            'nombre_tipo_radicado',
            'numero_radicado_completo',
            'titular',
            'asunto',
            'fecha_radicado',
            'agno_radicado'
        ]


class PersonasSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Personas
        fields = '__all__'


class OtrosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otros
        fields = '__all__'


class OTROSSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Otros
        fields = '__all__'

class MedioSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class PersonasFilterSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    tiene_usuario = serializers.SerializerMethodField()
    primer_nombre = serializers.SerializerMethodField()
    segundo_nombre = serializers.SerializerMethodField()
    primer_apellido = serializers.SerializerMethodField()
    segundo_apellido = serializers.SerializerMethodField()
    razon_social = serializers.SerializerMethodField()
    tipo_persona_desc = serializers.CharField(source='get_tipo_persona_display')
    tipo_usuario = serializers.SerializerMethodField()
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    def get_primer_nombre(self,obj):
        primer_nombre2 = obj.primer_nombre
        primer_nombre2 = primer_nombre2.upper() if primer_nombre2 else primer_nombre2
        return primer_nombre2
    
    def get_segundo_nombre(self, obj):
        segundo_nombre2 = obj.segundo_nombre
        segundo_nombre2 = segundo_nombre2.upper() if segundo_nombre2 else segundo_nombre2
        return segundo_nombre2
    
    def get_primer_apellido(self, obj):
        primer_apellido2 = obj.primer_apellido
        primer_apellido2 = primer_apellido2.upper() if primer_apellido2 else primer_apellido2
        return primer_apellido2
    
    def get_segundo_apellido(self, obj):
        segundo_apellido2 = obj.segundo_apellido
        segundo_apellido2 = segundo_apellido2.upper() if segundo_apellido2 else segundo_apellido2
        return segundo_apellido2
    
    def get_razon_social(self, obj):
        razon_social2 = obj.razon_social
        razon_social2 = razon_social2.upper() if razon_social2 else razon_social2
        return razon_social2
    def get_tipo_usuario(self, obj):
        id = obj.id_persona
        usuario = User.objects.filter(persona=id).first()
        if usuario:
            if usuario.tipo_usuario == 'I':
                return 'Interno'
            else:
                return 'Externo'
        else :
            return None
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_persona',
            'tipo_persona_desc',
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'nombre_completo',
            'razon_social',
            'nombre_comercial',
            'digito_verificacion',
            'cod_naturaleza_empresa',
            'tiene_usuario',
            'tipo_usuario'
        ]


class OtrosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otros
        fields = '__all__'


class AnexosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'



class AnexosPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'


class MetadatosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosAnexosTmp
        fields = '__all__'
 


class AnexosPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos
        fields = '__all__'

class MetadatosPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosAnexosTmp
        fields = '__all__'

class AnexosPQRSDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'

class ArchivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
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

class AnexosPQRSDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'



class RadicadoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = T262Radicados
        fields = '__all__'