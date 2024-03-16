from rest_framework import serializers
from django.contrib import auth
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno

from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, PermisosAmbientales, SolicitudesTramites
from transversal.models.base_models import Departamento
from transversal.models.personas_models import Personas

class ListTramitesGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PermisosAmbientales
        fields = '__all__'
        
class PersonaTitularInfoGetSerializer(serializers.ModelSerializer):
    cod_departamento_notificacion = serializers.SerializerMethodField()
    departamento_notificacion = serializers.SerializerMethodField()
    municipio_notificacion_nal = serializers.ReadOnlyField(source='cod_municipio_notificacion_nal.nombre', default=None)
    
    def get_cod_departamento_notificacion(self, obj):
        cod_departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            cod_departamento_notificacion = departamento.cod_departamento
        return cod_departamento_notificacion
    
    def get_departamento_notificacion(self, obj):
        departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            departamento_notificacion = departamento.nombre
        return departamento_notificacion

    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'cod_departamento_notificacion',
            'departamento_notificacion',
            'cod_municipio_notificacion_nal',
            'municipio_notificacion_nal',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon'
        ]

class GeneralTramitesGetSerializer(serializers.ModelSerializer):
    nombre_persona_interpone = serializers.SerializerMethodField()
    nombre_persona_titular = serializers.SerializerMethodField()
    nombre_persona_registra = serializers.SerializerMethodField()
    relacion_con_el_titular = serializers.CharField(source='get_cod_relacion_con_el_titular_display')
    tipo_operacion_tramite = serializers.CharField(source='get_cod_tipo_operacion_tramite_display')
    medio_solicitud = serializers.ReadOnlyField(source='id_medio_solicitud.nombre', default=None)
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_estado_actual_solicitud.nombre', default=None)
    cod_tipo_radicado = serializers.ReadOnlyField(source='id_radicado.cod_tipo_radicado', default=None)
    tipo_radicado = serializers.ReadOnlyField(source='id_radicado.get_cod_tipo_radicado_display', default=None)
    id_modulo_radica = serializers.ReadOnlyField(source='id_radicado.id_modulo_que_radica.id_ModuloQueRadica', default=None)
    modulo_radica = serializers.ReadOnlyField(source='id_radicado.id_modulo_que_radica.nombre', default=None)
    numero_radicado = serializers.ReadOnlyField(source='id_radicado.nro_radicado', default=None)
    agno_radicado = serializers.ReadOnlyField(source='id_radicado.agno_radicado', default=None)
    anexos = serializers.SerializerMethodField()
    
    def get_nombre_persona_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_titular:
            if obj.id_persona_titular.tipo_persona == 'J':
                nombre_persona_titular = obj.id_persona_titular.razon_social
            else:
                nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                                obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    def get_nombre_persona_interpone(self, obj):
        nombre_persona_interpone = None
        if obj.id_persona_interpone:
            if obj.id_persona_interpone.tipo_persona == 'J':
                nombre_persona_interpone = obj.id_persona_interpone.razon_social
            else:
                nombre_list = [obj.id_persona_interpone.primer_nombre, obj.id_persona_interpone.segundo_nombre,
                                obj.id_persona_interpone.primer_apellido, obj.id_persona_interpone.segundo_apellido]
                nombre_persona_interpone = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_interpone = nombre_persona_interpone if nombre_persona_interpone != "" else None
        return nombre_persona_interpone
    
    def get_nombre_persona_registra(self, obj):
        nombre_persona_registra = None
        if obj.id_persona_registra:
            if obj.id_persona_registra.tipo_persona == 'J':
                nombre_persona_registra = obj.id_persona_registra.razon_social
            else:
                nombre_list = [obj.id_persona_registra.primer_nombre, obj.id_persona_registra.segundo_nombre,
                                obj.id_persona_registra.primer_apellido, obj.id_persona_registra.segundo_apellido]
                nombre_persona_registra = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_registra = nombre_persona_registra if nombre_persona_registra != "" else None
        return nombre_persona_registra
    
    def get_anexos(self, obj):
        anexos_instances = AnexosTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite)
        serializer_get = AnexosGetSerializer(anexos_instances, many=True)
        return serializer_get.data
    
    class Meta:
        model = SolicitudesTramites
        fields = [
            'id_solicitud_tramite',
            'id_persona_titular',
            'nombre_persona_titular',
            'id_persona_interpone',
            'nombre_persona_interpone',
            'cod_relacion_con_el_titular',
            'relacion_con_el_titular',
            'cod_tipo_operacion_tramite',
            'tipo_operacion_tramite',
            'nombre_proyecto',
            'costo_proyecto',
            'id_medio_solicitud',
            'medio_solicitud',
            'id_persona_registra',
            'nombre_persona_registra',
            'id_estado_actual_solicitud',
            'estado_actual_solicitud',
            'fecha_ini_estado_actual',
            'id_radicado',
            'numero_radicado',
            'agno_radicado',
            'fecha_radicado',
            'cod_tipo_radicado',
            'tipo_radicado',
            'id_modulo_radica',
            'modulo_radica',
            'anexos'
        ]

class InicioTramiteCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SolicitudesTramites
        fields = [
            'id_solicitud_tramite',
            'id_persona_titular',
            'id_persona_interpone',
            'cod_relacion_con_el_titular',
            'cod_tipo_operacion_tramite',
            'nombre_proyecto',
            'costo_proyecto',
            'id_medio_solicitud',
            'id_persona_registra',
            'id_estado_actual_solicitud',
            'fecha_ini_estado_actual',
            'requiere_digitalizacion'
        ]
        extra_kwargs = {
            'id_solicitud_tramite': {'read_only': True},
            'id_persona_titular': {'required': True, 'allow_null': False},
            'id_persona_interpone': {'required': True, 'allow_null': False},
            'cod_relacion_con_el_titular': {'required': True, 'allow_null': False, 'allow_blank': False},
            'cod_tipo_operacion_tramite': {'required': True, 'allow_null': False, 'allow_blank': False},
            'nombre_proyecto': {'required': True, 'allow_null': False, 'allow_blank': False},
            'costo_proyecto': {'required': True, 'allow_null': False},
            'id_medio_solicitud': {'required': True, 'allow_null': False},
            'id_persona_registra': {'required': True, 'allow_null': False},
            'id_estado_actual_solicitud': {'required': True, 'allow_null': False},
            'fecha_ini_estado_actual': {'required': True, 'allow_null': False},

        }

class TramiteListGetSerializer(serializers.ModelSerializer):
    id_persona_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_titular.id_persona', default=None)
    cod_tipo_documento_persona_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_titular.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_titular.numero_documento', default=None)
    nombre_persona_titular = serializers.SerializerMethodField()
    id_persona_interpone = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_interpone.id_persona', default=None)
    cod_tipo_documento_persona_interpone = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_interpone.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_interpone = serializers.ReadOnlyField(source='id_solicitud_tramite.id_persona_interpone.numero_documento', default=None)
    nombre_persona_interpone = serializers.SerializerMethodField()
    cod_relacion_con_el_titular = serializers.ReadOnlyField(source='id_solicitud_tramite.cod_relacion_con_el_titular', default=None)
    relacion_con_el_titular = serializers.CharField(source='id_solicitud_tramite.get_cod_relacion_con_el_titular_display')
    cod_tipo_operacion_tramite = serializers.ReadOnlyField(source='id_solicitud_tramite.cod_tipo_operacion_tramite', default=None)
    tipo_operacion_tramite = serializers.CharField(source='id_solicitud_tramite.get_cod_tipo_operacion_tramite_display')
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    costo_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.costo_proyecto', default=None)
    id_estado_actual_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud', default=None)
    estado_actual_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.nombre', default=None)
    fecha_ini_estado_actual = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_ini_estado_actual', default=None)
    cod_tipo_permiso_ambiental = serializers.ReadOnlyField(source='id_permiso_ambiental.cod_tipo_permiso_ambiental', default=None)
    tipo_permiso_ambiental = serializers.CharField(source='id_permiso_ambiental.get_cod_tipo_permiso_ambiental_display')
    permiso_ambiental = serializers.ReadOnlyField(source='id_permiso_ambiental.nombre', default=None)
    municipio = serializers.ReadOnlyField(source='cod_municipio.nombre', default=None)
    id_expediente = serializers.ReadOnlyField(source='id_solicitud_tramite.id_expediente.id_expediente_documental', default=None)
    expediente = serializers.ReadOnlyField(source='id_solicitud_tramite.id_expediente.titulo_expediente', default=None)
    cod_departamento = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField()
    
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_solicitud_tramite.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_solicitud_tramite.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_solicitud_tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_solicitud_tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= obj.id_solicitud_tramite.id_radicado.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    
    def get_nombre_persona_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_solicitud_tramite.id_persona_titular:
            if obj.id_solicitud_tramite.id_persona_titular.tipo_persona == 'J':
                nombre_persona_titular = obj.id_solicitud_tramite.id_persona_titular.razon_social
            else:
                nombre_list = [obj.id_solicitud_tramite.id_persona_titular.primer_nombre, obj.id_solicitud_tramite.id_persona_titular.segundo_nombre,
                                obj.id_solicitud_tramite.id_persona_titular.primer_apellido, obj.id_solicitud_tramite.id_persona_titular.segundo_apellido]
                nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    def get_nombre_persona_interpone(self, obj):
        nombre_persona_interpone = None
        if obj.id_solicitud_tramite.id_persona_interpone:
            if obj.id_solicitud_tramite.id_persona_interpone.tipo_persona == 'J':
                nombre_persona_interpone = obj.id_solicitud_tramite.id_persona_interpone.razon_social
            else:
                nombre_list = [obj.id_solicitud_tramite.id_persona_interpone.primer_nombre, obj.id_solicitud_tramite.id_persona_interpone.segundo_nombre,
                                obj.id_solicitud_tramite.id_persona_interpone.primer_apellido, obj.id_solicitud_tramite.id_persona_interpone.segundo_apellido]
                nombre_persona_interpone = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_interpone = nombre_persona_interpone if nombre_persona_interpone != "" else None
        return nombre_persona_interpone
    
    def get_cod_departamento(self, obj):
        cod_departamento = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio.cod_municipio[:2]).first() if obj.cod_municipio else None
        if departamento:
            cod_departamento = departamento.cod_departamento
        return cod_departamento
    
    def get_departamento(self, obj):
        departamento_nombre = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio.cod_municipio[:2]).first() if obj.cod_municipio else None
        if departamento:
            departamento_nombre = departamento.nombre
        return departamento_nombre
    
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = [
            'id_solicitud_tramite',
            'id_persona_titular',
            'cod_tipo_documento_persona_titular',
            'numero_documento_persona_titular',
            'nombre_persona_titular',
            'id_persona_interpone',
            'cod_tipo_documento_persona_interpone',
            'numero_documento_persona_interpone',
            'nombre_persona_interpone',
            'cod_relacion_con_el_titular',
            'relacion_con_el_titular',
            'cod_tipo_operacion_tramite',
            'tipo_operacion_tramite',
            'nombre_proyecto',
            'costo_proyecto',
            'id_estado_actual_solicitud',
            'estado_actual_solicitud',
            'fecha_ini_estado_actual',
            'id_permiso_ambiental',
            'cod_tipo_permiso_ambiental',
            'tipo_permiso_ambiental',
            'permiso_ambiental',
            'cod_departamento',
            'departamento',
            'cod_municipio',
            'municipio',
            'direccion',
            'descripcion_direccion',
            'coordenada_x',
            'coordenada_y',
            'id_expediente',
            'expediente',
            'radicado'
        ]
        
class AnexosUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AnexosTramite
        fields = '__all__'
        
class AnexosGetSerializer(serializers.ModelSerializer):
    numero_folios = serializers.ReadOnlyField(source='id_anexo.numero_folios', default=None)
    cod_medio_almacenamiento = serializers.ReadOnlyField(source='id_anexo.cod_medio_almacenamiento', default=None)
    medio_almacenamiento = serializers.ReadOnlyField(source='id_anexo.get_cod_medio_almacenamiento_display', default=None)
    nombre = serializers.SerializerMethodField()
    descripcion = serializers.SerializerMethodField()
    id_archivo_digital = serializers.SerializerMethodField()
    formato = serializers.SerializerMethodField()
    tamagno_kb = serializers.SerializerMethodField()
    nro_folios_documento = serializers.SerializerMethodField()
    cod_categoria_archivo = serializers.SerializerMethodField()
    categoria_archivo = serializers.SerializerMethodField()
    cod_origen_archivo = serializers.SerializerMethodField()
    origen_archivo = serializers.SerializerMethodField()
    es_version_original = serializers.SerializerMethodField()
    tiene_replica_fisica = serializers.SerializerMethodField()
    id_tipologia_doc = serializers.SerializerMethodField()
    tipologia_doc = serializers.SerializerMethodField()
    tipologia_no_creada_TRD = serializers.SerializerMethodField()
    asunto = serializers.SerializerMethodField()
    palabras_clave_doc = serializers.SerializerMethodField()
    ruta_archivo = serializers.SerializerMethodField()
    
    def get_nombre(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().nombre_original_archivo
    
    def get_descripcion(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().descripcion
    
    def get_id_archivo_digital(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().id_archivo_sistema.id_archivo_digital
    
    def get_formato(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().id_archivo_sistema.formato
    
    def get_tamagno_kb(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().id_archivo_sistema.tamagno_kb
    
    def get_nro_folios_documento(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().nro_folios_documento
    
    def get_cod_categoria_archivo(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().cod_categoria_archivo
    
    def get_categoria_archivo(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().get_cod_categoria_archivo_display()
    
    def get_cod_origen_archivo(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().cod_origen_archivo
    
    def get_origen_archivo(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().get_cod_origen_archivo_display()
    
    def get_es_version_original(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().es_version_original
    
    def get_tiene_replica_fisica(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().tiene_replica_fisica
    
    def get_id_tipologia_doc(self, obj):
        id_tipologia_doc = obj.id_anexo.metadatosanexostmp_set.first().id_tipologia_doc
        if id_tipologia_doc:
            return id_tipologia_doc.id_tipologia_documental
        return id_tipologia_doc
    
    def get_tipologia_doc(self, obj):
        tipologia_doc = obj.id_anexo.metadatosanexostmp_set.first().id_tipologia_doc
        if tipologia_doc:
            return tipologia_doc.nombre
        return tipologia_doc
    
    def get_tipologia_no_creada_TRD(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().tipologia_no_creada_TRD
    
    def get_asunto(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().asunto
    
    def get_palabras_clave_doc(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().palabras_clave_doc
    
    def get_ruta_archivo(self, obj):
        return obj.id_anexo.metadatosanexostmp_set.first().id_archivo_sistema.ruta_archivo.url
    
    class Meta:
        model = AnexosTramite
        fields = [
            'id_anexo_tramite',
            'id_solicitud_tramite',
            'id_permiso_amb_solicitud_tramite',
            'id_anexo',
            'nombre',
            'descripcion',
            'numero_folios',
            'cod_medio_almacenamiento',
            'medio_almacenamiento',
            'id_archivo_digital',
            'formato',
            'tamagno_kb',
            'nro_folios_documento',
            'cod_categoria_archivo',
            'categoria_archivo',
            'cod_origen_archivo',
            'origen_archivo',
            'es_version_original',
            'tiene_replica_fisica',
            'id_tipologia_doc',
            'tipologia_doc',
            'tipologia_no_creada_TRD',
            'asunto',
            'palabras_clave_doc',
            'ruta_archivo'
        ]

class OPASSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisosAmbSolicitudesTramite
        fields = '__all__'