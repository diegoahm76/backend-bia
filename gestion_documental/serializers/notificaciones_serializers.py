from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales
from gestion_documental.choices.cod_tipo_documento_choices import cod_tipo_documento_CHOICES
from transversal.models.base_models import HistoricoCargosUndOrgPersona, ClasesTercero
from transversal.models.personas_models import Personas
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno, MetadatosAnexosTmp, Anexos, ArchivosDigitales
from datetime import timedelta, datetime
from tramites.models.tramites_models import SolicitudesTramites, TiposActosAdministrativos, ActosAdministrativos


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
    nombre_tipo_documento = serializers.CharField(source='cod_tipo_documento.nombre')
    tipo_documento = serializers.SerializerMethodField()
    registros_notificaciones = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    funcuinario_solicitante = serializers.SerializerMethodField()
    unidad_solicitante = serializers.CharField(source='id_und_org_oficina_solicita.nombre')
    estado_notificacion = estado_solicitud = serializers.CharField(source='get_cod_estado_display',read_only=True,default=None)

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

    def get_tipo_documento(self, obj):
        tipo_documento = TiposDocumentos.objects.filter(id_tipo_documento = obj.cod_tipo_documento_id).first()
        return TiposDocumentosNotificacionesCorrespondenciaSerializer(tipo_documento).data

    def get_anexos(self, obj):
        anexos_notificaciones = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia = obj.id_notificacion_correspondencia)
        anexos = []

        if anexos_notificaciones:
            for anexo_notificacion in anexos_notificaciones:
                anexo = Anexos.objects.filter(id_anexo = anexo_notificacion.id_anexo_id).first()
                anexos.append(AnexosNotificacionesSerializer(anexo).data)
        return anexos

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
    
    

class NotificacionesCorrespondenciaAnexosSerializer(serializers.ModelSerializer):
    nombre_tipo_documento = serializers.CharField(source='cod_tipo_documento.nombre')
    anexos = serializers.SerializerMethodField()
    registros_notificaciones = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    funcuinario_solicitante = serializers.SerializerMethodField()
    unidad_solicitante = serializers.CharField(source='id_und_org_oficina_solicita.nombre')
    estado_notificacion = estado_solicitud = serializers.CharField(source='get_cod_estado_display',read_only=True,default=None)

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

    def get_anexos(self, obj):
        anexos_notificaciones = Anexos_NotificacionesCorrespondencia.objects.filter(id_notificacion_correspondecia = obj.id_notificacion_correspondencia)
        anexos = []

        if anexos_notificaciones:
            for anexo_notificacion in anexos_notificaciones:
                anexo = Anexos.objects.filter(id_anexo = anexo_notificacion.id_anexo_id).first()
                anexos.append(AnexosNotificacionesSerializer(anexo).data)
        return anexos

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
    
    
class AnexosNotificacionesSerializer(serializers.ModelSerializer):
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
    
class ArchivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'
    

class Registros_NotificacionesCorrespondeciaSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    funcionario_asignado = serializers.SerializerMethodField()
    estado_registro = serializers.ReadOnlyField(source='id_estado_actual_registro.nombre', default=None)
    fecha_actuacion = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()
    plazo_entrega = serializers.SerializerMethodField()
    dias_faltantes = serializers.SerializerMethodField()
    tipo_gestion = serializers.ReadOnlyField(source='id_tipo_notificacion_correspondencia.nombre', default=None)
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = '__all__'

    def get_anexos(self, obj):
        anexos_tareas = Anexos_NotificacionesCorrespondencia.objects.filter(id_registro_notificacion = obj.id_registro_notificacion_correspondencia)
        anexos = []

        if anexos_tareas:
            for anexo_tarea in anexos_tareas:
                anexo = Anexos.objects.filter(id_anexo = anexo_tarea.id_anexo_id).first()
                anexos.append(AnexosNotificacionesSerializer(anexo).data)
        return anexos

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
    
    def get_funcionario_asignado(self, obj):
        return f"{obj.id_persona_asignada.primer_nombre} {obj.id_persona_asignada.primer_apellido}"
    
    def get_fecha_actuacion(self, obj):
        if obj.id_persona_asignada and  obj.cod_estado_asignacion == 'Ac':
            return obj.fecha_eleccion_estado
        
        
class Registros_NotificacionesCorrespondeciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = '__all__'


class AsignacionNotificacionCorrespondenciaSerializer(serializers.ModelSerializer):
    vigencia_contrato = serializers.ReadOnlyField(source='id_persona_asignada.fecha_a_finalizar_cargo_actual', default=None)
    persona_asignada = serializers.SerializerMethodField()
    # pendientes = serializers.SerializerMethodField()
    # resueltas = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionNotificacionCorrespondencia
        fields = '__all__'

    # def get_vigencia_contrato(self, obj):
    #     vigencia_contrato = HistoricoCargosUndOrgPersona.objects.filter(id_persona=obj.id_persona_asignada)
    #     return HistoricoCargosUndOrgPersonaSerializer(vigencia_contrato, many=True).data
    
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


class TramitesSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    class Meta:
        model = SolicitudesTramites
        fields = '__all__'

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= obj.id_radicado.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    def get_expediente(self, obj):
        if obj.id_expediente:
            return f"{obj.id_expediente.codigo_exp_und_serie_subserie}.{obj.id_expediente.codigo_exp_Agno}.{obj.id_expediente.codigo_exp_consec_por_agno}"
        else:
            return None


class TiposActosAdministrativosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposActosAdministrativos
        fields = '__all__'

class ActosAdministrativosSerializer(serializers.ModelSerializer):
    radicado = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    class Meta:
        model = ActosAdministrativos
        fields = '__all__'

    def get_radicado(self, obj):
        cadena = ""
        if obj.id_solicitud_tramite.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=obj.id_solicitud_tramite.id_radicado.agno_radicado,cod_tipo_radicado=obj.id_solicitud_tramite.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(obj.id_solicitud_tramite.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= obj.id_solicitud_tramite.id_radicado.prefijo_radicado+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
            return cadena
    def get_expediente(self, obj):
        if obj.id_solicitud_tramite.id_expediente:
            return f"{obj.id_solicitud_tramite.id_expediente.codigo_exp_und_serie_subserie}.{obj.id_solicitud_tramite.id_expediente.codigo_exp_Agno}.{obj.id_solicitud_tramite.id_expediente.codigo_exp_consec_por_agno}"
        else:
            return None


class RegistroNotificacionesCorrespondenciaPaginasSerializer(serializers.ModelSerializer):

    tipo_documento = serializers.CharField(source='id_notificacion_correspondencia.cod_tipo_documento.nombre')
    acto_administrativo = serializers.CharField(source='id_notificacion_correspondencia.id_acto_administrativo.id_tipo_acto_administrativo.tipo_acto_administrativo', default=None)
    expediente = serializers.CharField(source='id_notificacion_correspondencia.id_expediente_documental.codigo_exp_und_serie_subserie', default=None)
    oficina_solicita = serializers.CharField(source='id_notificacion_correspondencia.id_und_org_oficina_solicita.nombre')
    fecha_solicitud = serializers.DateTimeField(source='id_notificacion_correspondencia.fecha_solicitud')
  
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = ['id_notificacion_correspondencia',
                  'id_registro_notificacion_correspondencia',
                  'tipo_documento',
                  'acto_administrativo',
                  'expediente',
                  'oficina_solicita',
                  'fecha_solicitud',
                  'fecha_asignacion',
                  'id_tipo_notificacion_correspondencia'
                  ]
        
    
        

class DatosTitularesCorreoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    representante_legal = serializers.SerializerMethodField()
    class Meta:
        model = Personas
        fields = ['id_persona',
                    'nombre_completo',
                    'tipo_documento',
                    'numero_documento',
                    'razon_social',
                    'direccion_notificaciones',
                    'email',
                    'telefono_celular',
                    'telefono_fijo_residencial',
                    'direccion_residencia',
                    'representante_legal'
                    ]
        
    def get_nombre_completo(self, obj):
        persona = Personas.objects.filter(id_persona = obj.id_persona).first()
        nombre_completo = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
        return ' '.join(filter(None, nombre_completo))
        
        
    def get_representante_legal(self, obj):
            if obj.representante_legal:
                representante = Personas.objects.filter(id_persona=obj.representante_legal.id_persona).first()
                if representante:
                    return DatosTitularesCorreoSerializer(representante).data
                else:
                    return None
        
# class DatosTitularesCorreoSerializer(serializers.ModelSerializer):
#     nombre_completo = serializers.SerializerMethodField()
#     representante_legal = serializers.SerializerMethodField()

#     class Meta:
#         model = Personas
#         fields = ['id_persona',
#                   'nombre_completo',
#                   'tipo_documento',
#                   'numero_documento',
#                   'razon_social',
#                   'direccion_notificaciones',
#                   'email',
#                   'telefono_celular',
#                   'telefono_fijo_residencial',
#                   'direccion_residencia',
#                   'representante_legal'
#                  ]

#     def get_nombre_completo(self, obj):
#         return f"{obj.primer_nombre} {obj.segundo_nombre} {obj.primer_apellido} {obj.segundo_apellido}"

#     def get_representante_legal(self, obj):
#         if obj.representante_legal:
#             representante = Personas.objects.filter(id_persona=obj.representante_legal).first()
#             if representante:
#                 return DatosTitularesCorreoSerializer(representante).data
#             else:
#                 return None
        


class AnexosNotificacionesCorrespondenciaDatosSerializer(serializers.ModelSerializer):
    id_tipo_documento = serializers.ReadOnlyField(source='cod_tipo_documento.id_tipo_anexo_soporte', default=None)
    nombre_tipo_documento = serializers.ReadOnlyField(source='cod_tipo_documento.nombre', default=None)
    id_causa_o_anomalia = serializers.ReadOnlyField(source='cod_causa_o_anomalia.id_causa_o_anomalia', default=None)
    nombre_anexo = serializers.ReadOnlyField(source='id_anexo.nombre_anexo', default=None)
    asunto = serializers.SerializerMethodField()
    funcionario = serializers.SerializerMethodField()
    archivo = serializers.SerializerMethodField()
    ruta_archivo = serializers.SerializerMethodField()

    class Meta:
        model = Anexos_NotificacionesCorrespondencia
        
        fields = [
            'id_anexo_notificacion_correspondencia',
            'id_anexo',
            'id_notificacion_correspondecia',
            'id_registro_notificacion',
            'id_tipo_documento',
            'id_causa_o_anomalia',
            'nombre_tipo_documento',
            'nombre_anexo',
            'asunto',
            'fecha_anexo',
            'funcionario',
            'doc_entrada_salida',
            'link_publicacion',
            'ruta_archivo',
            'archivo',
            'observaciones'
        ]
    
    def metadatos(self, obj):
        metadatos = MetadatosAnexosTmp.objects.filter(id_anexo=obj.id_anexo).first()
        return MetadatoPanelSerializer(metadatos).data
        
    def get_asunto(self, obj):
        asunto  = self.metadatos(obj)
        return asunto['asunto']
    
    def get_funcionario(self, obj):
        funcionario = obj.id_persona_anexa_documento
        if funcionario is not None:
            return f"{funcionario.primer_nombre} {funcionario.primer_apellido}"
        else:
            return None
        
    def get_archivo(self, obj):
        metadatos = self.metadatos(obj)
        archivo_digital = ArchivosDigitales.objects.filter(id_archivo_digital = metadatos['id_archivo_sistema']).first()

        return ArchivosSerializer(archivo_digital).data
    
    def get_ruta_archivo(self, obj):
        metadatos = self.metadatos(obj)
        archivo_digital = ArchivosDigitales.objects.filter(id_archivo_digital = metadatos['id_archivo_sistema']).first()
        archivo_digital = ArchivosSerializer(archivo_digital).data
        ruta_archivo = str(archivo_digital['ruta_archivo'])
        return ruta_archivo
        

class AnexosNotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_NotificacionesCorrespondencia
        fields = '__all__'

class TiposAnexosSoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposAnexosSoporte
        fields = ('id_tipo_anexo_soporte', 'nombre')


class CausasOAnomaliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CausasOAnomalias
        fields = ('id_causa_o_anomalia', 'nombre')


class DocumentosDeArchivoExpedienteSerializer(serializers.ModelSerializer):
    
    nombre_completo = serializers.SerializerMethodField()
    direcion = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    ciudad = serializers.SerializerMethodField()
    numero_expediente = serializers.SerializerMethodField()
    numero_acto_administrativo = serializers.SerializerMethodField()
    fecha_acto_administrativo = serializers.SerializerMethodField()

    class Meta:
        model = NotificacionesCorrespondencia
        fields = ('id_notificacion_correspondencia',
                    'nombre_completo',
                    'direcion',
                    'telefono',
                    'email',
                    'ciudad',
                    'numero_expediente',
                    'numero_acto_administrativo',
                    'fecha_acto_administrativo',
                    'id_expediente_documental',
                    'id_acto_administrativo',
                    'id_persona_titular'
                    )
        
    def get_nombre_completo(self, obj):
        if obj.id_persona_titular:
            if obj.id_persona_titular.tipo_persona == 'N':
                nombre_completo = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre, obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
                nombre_completo =  ' '.join(filter(None, nombre_completo))
                return f"{nombre_completo}"
            else:
                return obj.id_persona_titular.razon_social
        else:
            return None
    
    def get_direcion(self, obj):
        if obj.id_persona_titular:
            return obj.id_persona_titular.direccion_notificaciones
        else:
            return None
        
    def get_telefono(self, obj):
        if obj.id_persona_titular:
            if obj.id_persona_titular.telefono_celular:
                return obj.id_persona_titular.telefono_celular
            else:
                return obj.id_persona_titular.telefono_fijo_residencial
        else:
            return None
        
    def get_email(self, obj):
        if obj.id_persona_titular:
            if obj.id_persona_titular.email:
                return obj.id_persona_titular.email
            else:
                return 'no registra'
        else:
            return None
        
    def get_ciudad(self, obj):
        if obj.id_persona_titular:
            if obj.id_persona_titular.pais_residencia:
                if obj.id_persona_titular.pais_residencia.cod_pais == 'CO':
                    return f"{obj.id_persona_titular.cod_municipio_residencia.nombre}, {obj.id_persona_titular.cod_municipio_residencia.cod_departamento.nombre}"
                else:
                    return f"{obj.id_persona_titular.pais_residencia.nombre}"
        else:
            return None

    def get_numero_expediente(self, obj):
        if obj.id_expediente_documental:
            numero_expediente = f"{obj.id_expediente_documental.codigo_exp_und_serie_subserie}-{obj.id_expediente_documental.codigo_exp_Agno}-{obj.id_expediente_documental.codigo_exp_consec_por_agno}"
            return numero_expediente
        else:
            return None
        
    def get_numero_acto_administrativo(self, obj):
        if obj.id_acto_administrativo:
            return obj.id_acto_administrativo.numero_acto_administrativo
        else:
            return None
        
    def get_fecha_acto_administrativo(self, obj):
        if obj.id_acto_administrativo:
            return obj.id_acto_administrativo.fecha_acto_administrativo
        else:
            return None
    

class ConstanciaNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionesCorrespondencia
        fields = ('id_notificacion_correspondencia', 
                  'fecha_notificacion',
                  'hora_notificacion',
                  'id_persona_notificada',
                  'id_persona_notifica',
                  'id_registro_notificacion_correspondencia',
                  'id_tipo_notificacion_correspondencia',
                  'nombre_tipo_notificacion',
                  'id_causa_o_anomalia',
                  'observaciones',
                  'id_estado_actual_notificacion_correspondencia')
        

class GeneradorDocumentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionesCorrespondencia
        fields = ('id_notificacion_correspondencia', 
                  'fecha_notificacion',
                  'hora_notificacion',
                  'id_persona_notificada',
                  'id_persona_notifica',
                  'id_registro_notificacion_correspondencia',
                  'id_tipo_notificacion_correspondencia',
                  'id_causa_o_anomalia',
                  'observaciones',
                  'id_estado_actual_notificacion_correspondencia')

# class Algo(serializers.ModelSerializer):
#     class Meta:
#         model = TiposDocumentos
#         fields = ('id_tipo_documento', 'nombre')
        
#     def algo(self, obj):
#         print(obj)
#         data = {
#             "tipo_documento": 1,
#             "id_expediente_documental": None,
#             "id_solicitud_tramite": 1,
#             "id_acto_administrativo": None,
#             "procede_recurso_reposicion": True,
#             "es_anonima": False,
#             "asunto": "sadasdasdasdas",
#             "descripcion": "sadasdasdsa",
#             "id_persona_solicita": 1,
#             "id_und_org_oficina_solicita": 815,
#             "allega_copia_fisica": True,
#             "cantidad_anexos": 4,
#             "nro_folios_totales": 20,
#             "requiere_digitalizacion": True,
#             "datos_manual": True,
#             "permite_notificacion_email": True,
#             "cod_tipo_documentoID": "CC",
#             "persona_a_quien_se_dirige": "brayan barragan",
#             "nro_documentoID": 12345,
#             "dir_notificacion_nal": "asdasdasdasdasda",
#             "cod_municipio_notificacion_nal": "05001",
#             "tel_fijo": 231333,
#             "tel_celular": 4324324,
#             "email_notificacion": "sdasdasdsadasd",
#             "id_persona_notificada": 1,
#             "anexos":[
#                 {"nombre_anexo": "Nombre anexo",
#                  "orden_anexo_doc": 0,
#                  "cod_medio_almacenamiento": "Pa",
#                  "medio_almacenamiento_otros_Cual": None,
#                  "numero_folios": 0,
#                  "ya_digitalizado": True,
#                  "uso_del_documento": True,
#                  "cod_tipo_documento": 1
#                  },
#                 {"nombre_anexo": "Nombre anexo 1",
#                  "orden_anexo_doc": 0,
#                  "cod_medio_almacenamiento": "Pa",
#                  "medio_almacenamiento_otros_Cual": None,
#                  "numero_folios": 0,
#                  "ya_digitalizado": True,
#                  "uso_del_documento": True,
#                  "cod_tipo_documento": 1
#                   }
#             ]
#         }



