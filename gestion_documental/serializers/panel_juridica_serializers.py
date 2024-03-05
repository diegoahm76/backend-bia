from rest_framework import serializers
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas
from gestion_documental.models.expedientes_models import ArchivosDigitales

from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, ComplementosUsu_PQR, ConfigTiposRadicadoAgno, Estados_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MetadatosAnexosTmp, Otros, SolicitudAlUsuarioSobrePQRSDF, SolicitudDeDigitalizacion, TiposPQR, MediosSolicitud
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, SolicitudesDeJuridica, SolicitudesTramites
from transversal.models.base_models import Departamento
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.models.personas_models import Personas
from datetime import datetime, timedelta

from django.db.models import Q


class SolicitudesJuridicaGetSerializer(serializers.ModelSerializer):
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    fecha_radicado = serializers.ReadOnlyField(source='id_solicitud_tramite.fecha_radicado', default=None)
    cod_tipo_operacion_tramite = serializers.ReadOnlyField(source='id_solicitud_tramite.cod_tipo_operacion_tramite', default=None)
    tipo_operacion_tramite = serializers.CharField(source='id_solicitud_tramite.get_cod_tipo_operacion_tramite_display')
    pago = serializers.ReadOnlyField(source='id_solicitud_tramite.pago', default=None)
    id_sucursal_recepcion_fisica = serializers.ReadOnlyField(source='id_solicitud_tramite.id_sucursal_recepcion_fisica.id_sucursal_empresa', default=None)
    sucursal_recepcion_fisica = serializers.ReadOnlyField(source='id_solicitud_tramite.id_sucursal_recepcion_fisica.descripcion_sucursal', default=None)
    id_estado_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.id_estado_solicitud', default=None)
    estado_solicitud = serializers.ReadOnlyField(source='id_solicitud_tramite.id_estado_actual_solicitud.nombre', default=None)
    id_expediente = serializers.ReadOnlyField(source='id_solicitud_tramite.id_expediente.id_expediente_documental', default=None)
    expediente = serializers.ReadOnlyField(source='id_solicitud_tramite.id_expediente.titulo_expediente', default=None)
    estado_tipo_solicitud_juridica = serializers.CharField(source='get_cod_estado_tipo_solicitud_juridica_display')
    radicado = serializers.SerializerMethodField()
    persona_solicita_revision = serializers.SerializerMethodField()
    
    def get_radicado(self, obj):
        cadena = ""
        if obj.id_solicitud_tramite.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_solicitud_tramite.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_solicitud_tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_solicitud_tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= obj.id_solicitud_tramite.id_radicado.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    
    def get_persona_solicita_revision(self, obj):
        nombre_persona_solicita_revision = None
        if obj.id_persona_solicita_revision:
            if obj.id_persona_solicita_revision.tipo_persona == 'N':
                nombre_list = [obj.id_persona_solicita_revision.primer_nombre, obj.id_persona_solicita_revision.segundo_nombre,
                                obj.id_persona_solicita_revision.primer_apellido, obj.id_persona_solicita_revision.segundo_apellido]
                nombre_persona_solicita_revision = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_solicita_revision = nombre_persona_solicita_revision if nombre_persona_solicita_revision != "" else None
            else:
                nombre_persona_solicita_revision = obj.id_persona_solicita_revision.razon_social
                
        return nombre_persona_solicita_revision
    
    class Meta:
        model = SolicitudesDeJuridica
        fields = [
            'id_solicitud_de_juridica',
            'id_solicitud_tramite',
            'nombre_proyecto',
            'radicado',
            'fecha_radicado',
            'cod_tipo_operacion_tramite',
            'tipo_operacion_tramite',
            'id_expediente',
            'expediente',
            'pago',
            'id_sucursal_recepcion_fisica',
            'sucursal_recepcion_fisica',
            'id_persona_solicita_revision',
            'persona_solicita_revision',
            'id_estado_solicitud',
            'estado_solicitud',
            'cod_estado_tipo_solicitud_juridica',
            'estado_tipo_solicitud_juridica'
        ]
        
class SolicitudesJuridicaInformacionOPAGetSerializer(serializers.ModelSerializer):
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
    fecha_rta_solicitud = serializers.SerializerMethodField()
    aprueba_solicitud_tramite = serializers.SerializerMethodField()
    solicitud_completada = serializers.SerializerMethodField()
    solicitud_sin_completar = serializers.SerializerMethodField()
    
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
    
    def get_fecha_rta_solicitud(self, obj):
        fecha_rta_solicitud = None
        solicitud_juridica = obj.id_solicitud_tramite.solicitudesdejuridica_set.first()
        if solicitud_juridica:
            fecha_rta_solicitud = solicitud_juridica.fecha_rta_solicitud
        return fecha_rta_solicitud
    
    def get_aprueba_solicitud_tramite(self, obj):
        aprueba_solicitud_tramite = None
        solicitud_juridica = obj.id_solicitud_tramite.solicitudesdejuridica_set.first()
        if solicitud_juridica:
            aprueba_solicitud_tramite = solicitud_juridica.aprueba_solicitud_tramite
        return aprueba_solicitud_tramite
    
    def get_solicitud_completada(self, obj):
        solicitud_completada = None
        solicitud_juridica = obj.id_solicitud_tramite.solicitudesdejuridica_set.first()
        if solicitud_juridica:
            solicitud_completada = solicitud_juridica.solicitud_completada
        return solicitud_completada
    
    def get_solicitud_sin_completar(self, obj):
        solicitud_sin_completar = None
        solicitud_juridica = obj.id_solicitud_tramite.solicitudesdejuridica_set.first()
        if solicitud_juridica:
            solicitud_sin_completar = solicitud_juridica.solicitud_sin_completar
        return solicitud_sin_completar
    
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
            'radicado',
            'fecha_rta_solicitud',
            'aprueba_solicitud_tramite',
            'solicitud_completada',
            'solicitud_sin_completar',
        ]