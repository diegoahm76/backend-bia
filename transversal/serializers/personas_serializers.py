from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from transversal.models.personas_models import Personas
from seguridad.models import (
    User
)
from transversal.models.base_models import (
    Departamento,
    EstadoCivil,
    TipoDocumento,
    ApoderadoPersona,
    HistoricoCambiosIDPersonas,
    Cargos,
    ClasesTercero,
    ClasesTerceroPersona,
    HistoricoEmails,
    HistoricoDireccion,
    HistoricoAutirzacionesNotis,
    HistoricoRepresentLegales,
    HistoricoCargosUndOrgPersona,
)


class EstadoCivilSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCivil
        fields = '__all__'
        extra_kwargs = {
            'cod_estado_civil': {'required': True},  
            'nombre': {'required': True}, 
            'precargado': {'read_only': True},
            'activo': {'read_only': True},
            'item_ya_usado': {'read_only': True}
        }

class EstadoCivilPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCivil
        fields = ['cod_estado_civil', 'nombre']
        extra_kwargs = {
            'cod_estado_civil': {'required': True},  
            'nombre': {'required': True}
        }

class EstadoCivilPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCivil
        fields = ['nombre', 'activo']
        extra_kwargs = {
            'nombre': {'required': True}, 
        }
        
class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = '__all__'
        extra_kwargs = {
            'cod_tipo_documento': {'required': True},
            'nombre': {'required': True},
            'precargado': {'read_only': True},
            'activo': {'read_only': True},
            'item_ya_usado': {'read_only': True}
        }

class TipoDocumentoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['cod_tipo_documento', 'nombre']
        extra_kwargs = {
            'cod_tipo_documento': {'required': True},
            'nombre': {'required': True}
        }

class TipoDocumentoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['nombre', 'activo']
        extra_kwargs = {
            'nombre': {'required': True}
        }

class RepresentanteLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = '__all__'

class PersonasSerializer(serializers.ModelSerializer):
    nombre_unidad_organizacional_actual=serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre',default=None)
    tiene_usuario = serializers.SerializerMethodField()
    primer_nombre = serializers.SerializerMethodField()
    segundo_nombre = serializers.SerializerMethodField()
    primer_apellido = serializers.SerializerMethodField()
    segundo_apellido = serializers.SerializerMethodField()
    cod_departamento_expedicion = serializers.ReadOnlyField(source='cod_municipio_expedicion_id.cod_departamento.cod_departamento',default=None)
    cod_departamento_residencia = serializers.SerializerMethodField()
    cod_departamento_notificacion = serializers.SerializerMethodField()
    cod_departamento_laboral = serializers.SerializerMethodField()
    
    def get_cod_departamento_residencia(self, obj):
        cod_departamento_residencia = None
        departamento = Departamento.objects.filter(cod_departamento=obj.municipio_residencia.cod_municipio[:2]).first() if obj.municipio_residencia else None
        if departamento:
            cod_departamento_residencia = departamento.cod_departamento
        return cod_departamento_residencia
    
    def get_cod_departamento_notificacion(self, obj):
        cod_departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            cod_departamento_notificacion = departamento.cod_departamento
        return cod_departamento_notificacion
    
    def get_cod_departamento_laboral(self, obj):
        cod_departamento_laboral = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_laboral_nal.cod_municipio[:2]).first() if obj.cod_municipio_laboral_nal else None
        if departamento:
            cod_departamento_laboral = departamento.cod_departamento
        return cod_departamento_laboral
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    
    def get_primer_nombre(self, obj):
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
    
    #MOSTRAR EL NOMBRE EN MAYUSCULA
        
    class Meta:
        model = Personas
        fields = '__all__'

class PersonaNaturalSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    estado_civil = EstadoCivilSerializer(read_only=True)
    tiene_usuario = serializers.SerializerMethodField()
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_documento',
            'numero_documento',
            'digito_verificacion',
            'tipo_persona',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'nombre_comercial',
            'direccion_residencia',
            'direccion_residencia_ref',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'municipio_residencia',
            'pais_residencia',
            'direccion_laboral',
            'cod_municipio_laboral_nal',
            'direccion_notificaciones',
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_fijo_residencial',
            'telefono_celular',
            'telefono_empresa_2',
            'fecha_nacimiento',
            'pais_nacimiento',
            'sexo',
            'estado_civil',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
            'tiene_usuario'
        ]     
    
class PersonaJuridicaSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    tiene_usuario = serializers.SerializerMethodField()
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    class Meta:
        model = Personas
        fields = [
            'id_persona', 
            'tipo_persona', 
            'tipo_documento', 
            'numero_documento', 
            'digito_verificacion', 
            'nombre_comercial',
            'razon_social', 
            'email', 
            'email_empresarial',
            'telefono_celular', 
            'direccion_notificaciones', 
            'direccion_residencia',
            'pais_residencia',
            'municipio_residencia',
            'cod_municipio_notificacion_nal',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'telefono_empresa',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
            'tiene_usuario'
        ]          
        
#CREACION DE PERSONA NATURAL
class PersonaNaturalPostSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Personas
        fields = [
            'tipo_persona', 
            'tipo_documento', 
            'numero_documento', 
            'nombre_comercial', 
            'primer_nombre', 
            'segundo_nombre', 
            'primer_apellido', 
            'segundo_apellido', 
            'fecha_nacimiento', 
            'email', 
            'telefono_celular',
            'telefono_empresa_2',
            'sexo',
            'estado_civil',
            'pais_nacimiento',
            'email_empresarial',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'telefono_fijo_residencial',
            'pais_residencia',
            'municipio_residencia',
            'direccion_residencia',
            'direccion_laboral',
            'direccion_residencia_ref',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_laboral_nal',
            'cod_municipio_notificacion_nal',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
            "cod_municipio_expedicion_id",
            "id_persona_crea",
        
        ]
        
        validators = [
            UniqueTogetherValidator(
                queryset = Personas.objects.all(),
                fields = ['tipo_documento', 'numero_documento'],
                message = 'Ya existe un registro con el tipo de documento y el número de documento ingresado'
            )
        ]
        extra_kwargs = {
            'tipo_persona': {'required': True,'allow_null':False, 'allow_blank':False},
            'tipo_documento': {'required': True,'allow_null':False},
            'numero_documento': {'required': True,'allow_null':False, 'allow_blank':False},
            'primer_nombre': {'required': True,'allow_null':False, 'allow_blank':False},
            'primer_apellido': {'required': True,'allow_null':False, 'allow_blank':False},
            'fecha_nacimiento': {'required': True,'allow_null':False},
            'email': {'required': True,'allow_null':False, 'allow_blank':False},
            'sexo': {'required': True,'allow_null':False},
            'estado_civil': {'required': True,'allow_null':False},
            'cod_municipio_expedicion_id': {'required': True,'allow_null':False},
            'pais_residencia': {'required': True,'allow_null':False},
            'direccion_residencia': {'required': False,'allow_null':True, 'allow_blank':False},
            'direccion_notificaciones': {'required': True,'allow_null':False, 'allow_blank':False},
            'cod_municipio_notificacion_nal': {'required': True,'allow_null':False},
            'acepta_notificacion_sms': {'required': True,'allow_null':False},
            'acepta_notificacion_email': {'required': True,'allow_null':False},
            'acepta_tratamiento_datos': {'required': True,'allow_null':False},
        }
        
#ACTUALIZACION PERSONA NATURAL
class PersonaNaturalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'nombre_comercial',
            'direccion_residencia',
            'direccion_residencia_ref',
            'direccion_notificacion_referencia',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'municipio_residencia',
            'pais_residencia',
            'direccion_laboral',
            'cod_municipio_laboral_nal',
            'direccion_notificaciones',
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_fijo_residencial',
            'telefono_celular',
            'telefono_empresa_2',
            'fecha_nacimiento',
            'pais_nacimiento',
            'sexo',
            'estado_civil',
            "cod_municipio_expedicion_id",
            "fecha_ultim_actualiz_diferente_crea",
            "id_persona_ultim_actualiz_diferente_crea"
        ]
            
        extra_kwargs = {
                'fecha_nacimiento': {'required': True,'allow_null':False},
                'email': {'required': True,'allow_null':False, 'allow_blank':False},
                'sexo': {'required': True,'allow_null':False},
                'estado_civil': {'required': True,'allow_null':False},
                'cod_municipio_expedicion_id': {'required': True,'allow_null':False},
                'pais_residencia': {'required': True,'allow_null':False},
                'direccion_notificaciones': {'required': True,'allow_null':False, 'allow_blank':False},
                'cod_municipio_notificacion_nal': {'required': True,'allow_null':False},
                'direccion_residencia': {'required': True,'allow_null':False, 'allow_blank':False},
            }
        
class PersonaNaturalUpdateAdminSerializer(PersonaNaturalUpdateSerializer):
    
    class Meta:
        model =  Personas
        fields = PersonaNaturalUpdateSerializer.Meta.fields
        extra_kwargs = PersonaNaturalUpdateSerializer.Meta.extra_kwargs | {'direccion_notificaciones': {'required': False,'allow_null':True, 'allow_blank':True}}


class PersonaNaturalPostAdminSerializer(PersonaNaturalPostSerializer):
    
    class Meta:
        model =  Personas
        fields = PersonaNaturalPostSerializer.Meta.fields
        validators = PersonaNaturalPostSerializer.Meta.validators
        extra_kwargs = PersonaNaturalPostSerializer.Meta.extra_kwargs | {'direccion_notificaciones': {'required': False,'allow_null':True, 'allow_blank':True}}


#CREACION DE PERSONA JURIDICA
class PersonaJuridicaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'tipo_persona', 
            'tipo_documento', 
            'numero_documento', 
            'digito_verificacion', 
            'nombre_comercial',
            'razon_social', 
            'email', 
            'email_empresarial',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_notificacion_nal',
            'cod_pais_nacionalidad_empresa',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'telefono_empresa',
            'representante_legal',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'representante_legal',
            'fecha_inicio_cargo_rep_legal',
            "id_persona_crea",
            "cod_naturaleza_empresa"
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Personas.objects.all(),
                fields = ['tipo_documento', 'numero_documento'],
                message = 'Ya existe un registro con el tipo de documento y el número de documento ingresado'
            )
        ]
        
        extra_kwargs = {
            'tipo_persona': {'required': True,'allow_null':False},
            'tipo_documento': {'required': True,'allow_null':False},
            'numero_documento': {'required': True,'allow_null':False, 'allow_blank':False},
            'digito_verificacion': {'required': True,'allow_null':False, 'allow_blank':False},
            'razon_social': {'required': True,'allow_null':False, 'allow_blank':False},
            'nombre_comercial': {'required': True,'allow_null':False, 'allow_blank':False},
            'representante_legal': {'required': True,'allow_null':False},
            'cod_naturaleza_empresa': {'required': True,'allow_null':False},
            'email': {'required': True,'allow_null':False, 'allow_blank':False},
            'direccion_notificaciones': {'required': True,'allow_null':False, 'allow_blank':False},
            'cod_municipio_notificacion_nal': {'required': True,'allow_null':False},
            'fecha_inicio_cargo_rep_legal': {'required':True,'allow_null':False},
            'acepta_notificacion_sms': {'required':True,'allow_null':False},
            'acepta_notificacion_email': {'required':True,'allow_null':False}
        }

#ACTUALIZACION DE PERSONA JURIDICA
class PersonaJuridicaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_empresa',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'cod_pais_nacionalidad_empresa',
            "representante_legal",
            "fecha_inicio_cargo_rep_legal",
            "fecha_ultim_actualiz_diferente_crea",
            "id_persona_ultim_actualiz_diferente_crea",
            "fecha_cambio_representante_legal"
        ]
        
        extra_kwargs = {
            'representante_legal': {'required': True,'allow_null':False},
            'email': {'required': True},'allow_null':False, 'allow_blank':False,
            'direccion_notificaciones': {'required': True,'allow_null':False, 'allow_blank':False},
            'fecha_inicio_cargo_rep_legal': {'required':True,'allow_null':False},
            'cod_municipio_notificacion_nal': {'required':True,'allow_null':False},
            'cod_pais_nacionalidad_empresa': {'required':True,'allow_null':False}
        }
        
class GetClaseTerceroSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = ClasesTercero
        fields = '__all__'


class GetPersonaJuridicaByRepresentanteLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'representante_legal',
            'id_persona', 
            'tipo_persona', 
            'tipo_documento', 
            'numero_documento', 
            'digito_verificacion', 
            'nombre_comercial',
            'razon_social', 
            'email', 
            'email_empresarial',
            'telefono_celular', 
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'direccion_residencia',
            'pais_residencia',
            'municipio_residencia',
            'cod_municipio_notificacion_nal',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'telefono_empresa',
        ]

class PersonaNaturalPostByUserSerializer(serializers.ModelSerializer):
    numero_documento = serializers.CharField(max_length=20, min_length=5)
    primer_nombre = serializers.CharField(max_length=30)
    primer_apellido = serializers.CharField(max_length=30)
    telefono_celular = serializers.CharField(max_length=15, min_length=10)
    
    class Meta:
        model = Personas
        fields = [ 
            'tipo_persona', 
            'tipo_documento', 
            'numero_documento', 
            'digito_verificacion', 
            'nombre_comercial', 
            'primer_nombre', 
            'segundo_nombre', 
            'primer_apellido', 
            'segundo_apellido', 
            'fecha_nacimiento', 
            'email', 
            'telefono_celular',
            'telefono_empresa_2',
            'sexo',
            'estado_civil',
            'pais_nacimiento',
            'email_empresarial',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'telefono_fijo_residencial',
            'pais_residencia',
            'municipio_residencia',
            'direccion_residencia',
            'direccion_laboral',
            'direccion_residencia_ref',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_laboral_nal',
            'cod_municipio_notificacion_nal',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
        ]
        
        validators = [
            UniqueTogetherValidator(
                queryset = Personas.objects.all(),
                fields = ['tipo_documento', 'numero_documento'],
                message = 'Ya existe un registro con el tipo de documento y el número de documento ingresado'
                
            )
        ]
        extra_kwargs = {
                'tipo_persona': {'required': True},
                'tipo_documento': {'required': True},
                'numero_documento': {'required': True},
                'primer_nombre': {'required': True},
                'primer_apellido': {'required': True},
                'fecha_nacimiento': {'required': True},
                'email': {'required': True}
            }

# class PersonaNaturalExternoUpdateSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(validators=[UniqueValidator(queryset=Personas.objects.all())])
#     telefono_celular = serializers.CharField(max_length=15, min_length=10)
#     ubicacion_georeferenciada = serializers.CharField(max_length=50, min_length=5)

#     class Meta:
#         model = Personas
#         fields = [
#             'digito_verificacion',
#             'nombre_comercial',
#             'direccion_residencia',
#             'direccion_residencia_ref',
#             'ubicacion_georeferenciada',
#             'municipio_residencia',
#             'pais_residencia',
#             'direccion_laboral',
#             'cod_municipio_laboral_nal',
#             'direccion_notificaciones',
#             'cod_municipio_notificacion_nal',
#             'email',
#             'email_empresarial',
#             'telefono_fijo_residencial',
#             'telefono_celular',
#             'telefono_empresa_2',
#             'fecha_nacimiento',
#             'pais_nacimiento',
#             'sexo',
#             'estado_civil',
#             'acepta_notificacion_sms',
#             'acepta_notificacion_email',
#             'acepta_tratamiento_datos'
#         ]


class PersonaNaturalUpdateUserPermissionsSerializer(serializers.ModelSerializer):
    telefono_celular = serializers.CharField(max_length=15, min_length=10)
    ubicacion_georeferenciada = serializers.CharField(max_length=50, min_length=5)

    class Meta:
        model = Personas
        fields = [
            'digito_verificacion',
            'nombre_comercial',
            'direccion_residencia',
            'direccion_residencia_ref',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon',
            'municipio_residencia',
            'pais_residencia',
            'direccion_laboral',
            'cod_municipio_laboral_nal',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_fijo_residencial',
            'telefono_celular',
            'telefono_empresa_2',
            'fecha_nacimiento',
            'pais_nacimiento',
            'sexo',
            'estado_civil',
            'id_cargo',
            'id_unidad_organizacional_actual',
            'fecha_asignacion_unidad',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
            'es_unidad_organizacional_actual'
        ]

# class PersonaJuridicaInternaUpdateSerializer(serializers.ModelSerializer):
#     telefono_celular_empresa = serializers.CharField(max_length=15, min_length=10)


#     class Meta:
#         model = Personas
#         fields = [
#             'direccion_notificaciones', 
#             'cod_municipio_notificacion_nal',
#             'email',
#             'email_empresarial',
#             'telefono_empresa',
#             'telefono_celular_empresa',
#             'telefono_empresa_2',
#             'cod_pais_nacionalidad_empresa',
#             'acepta_notificacion_sms',
#             'acepta_notificacion_email',
#             'acepta_tratamiento_datos',
#             'representante_legal'
#         ]


        
class PersonaJuridicaUpdateUserPermissionsSerializer(serializers.ModelSerializer):
    telefono_celular_empresa = serializers.CharField(max_length=15, min_length=10)

    class Meta:
        model = Personas
        fields = [
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_empresa',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'cod_pais_nacionalidad_empresa',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos'
        ]

class ApoderadoPersonaSerializer(serializers.ModelSerializer):
    persona_poderdante = PersonasSerializer(read_only=True)
    persona_apoderada = PersonasSerializer(read_only=True)
    
    class Meta:
        model = ApoderadoPersona
        fields = '__all__'
        
class ApoderadoPersonaGetSerializer(serializers.ModelSerializer):
    id_persona = serializers.ReadOnlyField(source='persona_poderdante.id_persona', default=None)
    tipo_documento = serializers.ReadOnlyField(source='persona_poderdante.tipo_documento.cod_tipo_documento', default=None)
    numero_documento = serializers.ReadOnlyField(source='persona_poderdante.numero_documento', default=None)
    nombre_persona_poderdante = serializers.SerializerMethodField()
    cod_relacion_con_el_titular = serializers.SerializerMethodField()
    id_usuario = serializers.SerializerMethodField()
    
    def get_cod_relacion_con_el_titular(self, obj):
        return 'AP'
    
    def get_id_usuario(self, obj):
        id_usuario = None
        usuario = obj.persona_poderdante.user_set.all()
        if usuario:
            usuario = usuario.exclude(id_usuario=1).first()
            id_usuario = usuario.id_usuario
            
        return id_usuario
    
    def get_nombre_persona_poderdante(self, obj):
        nombre_persona_poderdante = None
        if obj.persona_poderdante.tipo_persona == 'N':
            nombre_list = [obj.persona_poderdante.primer_nombre, obj.persona_poderdante.segundo_nombre, obj.persona_poderdante.primer_apellido, obj.persona_poderdante.segundo_apellido]
            nombre_persona_poderdante = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_poderdante = nombre_persona_poderdante.upper()
        if obj.persona_poderdante.tipo_persona == 'J':
            nombre_persona_poderdante = obj.persona_poderdante.razon_social
        return nombre_persona_poderdante
    
    class Meta:
        model = ApoderadoPersona
        fields = [
            'id_apoderados_persona',
            'id_persona',
            'tipo_documento',
            'numero_documento',
            'nombre_persona_poderdante',
            'cod_relacion_con_el_titular',
            'id_usuario'
        ]
        
class RepresentanteLegalGetSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.ReadOnlyField(source='tipo_documento.cod_tipo_documento', default=None)
    cod_relacion_con_el_titular = serializers.SerializerMethodField()
    id_usuario = serializers.SerializerMethodField()
    
    def get_cod_relacion_con_el_titular(self, obj):
        return 'RL'
    
    def get_id_usuario(self, obj):
        id_usuario = None
        usuario = obj.user_set.all()
        if usuario:
            usuario = usuario.exclude(id_usuario=1).first()
            id_usuario = usuario.id_usuario
            
        return id_usuario
    
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'razon_social',
            'tipo_documento',
            'numero_documento',
            'cod_relacion_con_el_titular',
            'id_usuario'
        ]
        
class ApoderadoPersonaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApoderadoPersona
        fields = '__all__'
        extra_kwargs = {
                'persona_poderdante': {'required': True},
                'id_proceso': {'required': True},
                'persona_apoderada': {'required': True},
                'fecha_inicio': {'required': True},
            }
        

class HistoricoEmailsSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    def get_nombre_completo(self, obj):
        return f"{obj.id_persona.primer_nombre} {obj.id_persona.segundo_nombre} {obj.id_persona.primer_apellido} {obj.id_persona.segundo_apellido}"

        
    class Meta:
        model = HistoricoEmails
        fields = '__all__'

class HistoricoDireccionSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    def get_nombre_completo(self, obj):
        return f"{obj.id_persona.primer_nombre} {obj.id_persona.segundo_nombre} {obj.id_persona.primer_apellido} {obj.id_persona.segundo_apellido}"
        
    class Meta:
        model = HistoricoDireccion
        fields = '__all__'
    
class ClasesTerceroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasesTercero
        fields = '__all__'
        
        
class ClasesTerceroPersonaSerializer(serializers.ModelSerializer):
    id_clase_tercero = ClasesTerceroSerializer(read_only=True)
    id_persona = PersonasSerializer(read_only=True)
    class Meta:
        model = ClasesTerceroPersona
        fields = '__all__'
        

class ClasesTerceroPersonapostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasesTerceroPersona
        fields = '__all__'
        extra_kwargs = {
                'id_persona': {'required': True},
                'id_clase_tercero': {'required': True},
            }
        
class CargosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cargos
        fields = ['id_cargo', 'nombre', 'activo']
        extra_kwargs = {
            'nombre': {'required': True},
            'id_cargo': {'read_only': True}
        }
    
class HistoricoCargosUndOrgPersonapostSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCargosUndOrgPersona
        fields = '__all__'
        # extra_kwargs = {
            # 'id_cargo': {'read_only': True}
        # }
    

# class BusquedaPersonaNaturalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Personas
#         fields = ['tipo_documento','numero_documento','primer_nombre','primer_apellido']

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
        if obj.tipo_persona == 'J':
            nombre_completo = obj.razon_social
        else:
            nombre_list = [obj.primer_nombre, obj.segundo_nombre,
                            obj.primer_apellido, obj.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            nombre_completo = nombre_completo if nombre_completo != "" else None
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
            'tipo_usuario',
            'id_unidad_organizacional_actual'
        ]

class UsuarioAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id_usuario', 'nombre_de_usuario']

class PersonasFilterAdminUserSerializer(PersonasFilterSerializer):
    usuarios = serializers.SerializerMethodField()
    
    def get_usuarios(self, obj):
        usuarios = User.objects.filter(persona=obj.id_persona)
        usuarios_serializer = UsuarioAdminSerializer(usuarios, many=True)
        usuarios_data = usuarios_serializer.data if usuarios_serializer else []
        return usuarios_data
        
    class Meta:
        model = Personas
        fields = PersonasFilterSerializer.Meta.fields + ['usuarios']

class BusquedaHistoricoCambiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCambiosIDPersonas
        fields = '__all__'

class UpdatePersonasNaturalesSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    def get_nombre_completo(self, obj):
        return f"{obj.primer_nombre} {obj.segundo_nombre} {obj.primer_apellido} {obj.segundo_apellido}"

    class Meta:
        model = Personas
        fields = ('id_persona', 'tipo_documento', 'numero_documento', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido','nombre_completo')

        validators = [
                UniqueTogetherValidator(
                    queryset = Personas.objects.all(),
                    fields = ['tipo_documento', 'numero_documento'],
                    message = 'Ya existe un registro con el tipo de documento y el número de documento ingresado'
                    
                )
            ]
    
class UpdatePersonasJuridicasSerializer(serializers.ModelSerializer):

    class Meta:
        model = Personas
        fields = ('id_persona', 'numero_documento', 'razon_social', 'nombre_comercial', 'cod_naturaleza_empresa')


        validators = [
                UniqueTogetherValidator(
                    queryset = Personas.objects.all(),
                    fields = ['numero_documento'],
                    message = 'Ya existe un registro con ese número de documento ingresado'    
                )
            ]

class HistoricoNotificacionesSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    def get_nombre_completo(self, obj):
        return f"{obj.id_persona.primer_nombre} {obj.id_persona.segundo_nombre} {obj.id_persona.primer_apellido} {obj.id_persona.segundo_apellido}"
        
    class Meta:
        model = HistoricoAutirzacionesNotis
        fields = '__all__'

class HistoricoRepresentLegalSerializer(serializers.ModelSerializer):
    nombre_comercial = serializers.CharField(source='id_persona_empresa.nombre_comercial', read_only=True)
    razon_social = serializers.CharField(source='id_persona_empresa.razon_social', read_only=True)
    nombre_completo_replegal = serializers.SerializerMethodField()

    def get_nombre_completo_replegal(self, obj):
        return f"{obj.id_persona_represent_legal.primer_nombre} {obj.id_persona_represent_legal.segundo_nombre} {obj.id_persona_represent_legal.primer_apellido} {obj.id_persona_represent_legal.segundo_apellido}"
        
    class Meta:
        model = HistoricoRepresentLegales
        fields = ['id_historico_represent_legal', 'consec_representacion', 'fecha_cambio_sistema', 'fecha_inicio_cargo', 'id_persona_empresa', 'nombre_comercial', 'razon_social','id_persona_represent_legal','nombre_completo_replegal']

class EmpresaSerializer(serializers.ModelSerializer):
    id_persona = serializers.SerializerMethodField()
    tipo_documento_id = serializers.SerializerMethodField()
    tipo_documento = serializers.SerializerMethodField()
    numero_documento = serializers.SerializerMethodField()
    nombre_comercial = serializers.SerializerMethodField()
    razon_social = serializers.SerializerMethodField()
    tipo_persona = serializers.SerializerMethodField()
    tipo_persona_desc = serializers.CharField(source='get_tipo_persona_display')
    persona_representante = serializers.SerializerMethodField()

    def get_id_persona(sefl, obj):
        return obj.id_persona
    
    def get_tipo_documento_id(self, obj):
        return obj.tipo_documento_id
    
    def get_tipo_documento(self, obj):
        return obj.tipo_documento.nombre
    
    def get_numero_documento(self, obj):
        return obj.numero_documento
    
    def get_nombre_comercial(self, obj):
        nombre_comercial1 = obj.nombre_comercial
        nombre_comercial1 = nombre_comercial1.upper() if nombre_comercial1 else nombre_comercial1
        return nombre_comercial1
    
    def get_razon_social(self, obj):
        razon_social2 = obj.razon_social
        razon_social2 = razon_social2.upper() if razon_social2 else razon_social2
        return razon_social2
    
    def get_tipo_persona(self, obj):
        return obj.tipo_persona
    
    def get_persona_representante(self, obj):
        persona = Personas.objects.filter(id_persona=obj.representante_legal.id_persona).first()
        representante_serializer = RepresentanteLegalSerializer(persona, read_only=True)
        representante = representante_serializer.data if representante_serializer else None
        return representante
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_documento_id',
            'tipo_documento',
            'numero_documento',
            'nombre_comercial',
            'razon_social',
            'tipo_persona',
            'tipo_persona_desc',
            'persona_representante'
        ]

class RepresentanteLegalSerializer(serializers.ModelSerializer):
    tipo_persona = serializers.SerializerMethodField()
    tipo_persona_desc = serializers.CharField(source='get_tipo_persona_display')
    tipo_documento_id = serializers.SerializerMethodField()
    tipo_documento = serializers.SerializerMethodField()
    numero_documento = serializers.SerializerMethodField()
    primer_nombre = serializers.SerializerMethodField()
    segundo_nombre = serializers.SerializerMethodField()
    primer_apellido = serializers.SerializerMethodField()
    segundo_apellido = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()

    def get_tipo_persona(self, obj):
        return obj.tipo_persona
    
    def get_tipo_documento_id(self, obj):
        return obj.tipo_documento_id
    
    def get_tipo_documento(self, obj):
        return obj.tipo_documento.nombre
    
    
    def get_numero_documento(self, obj):
        return obj.numero_documento

    def get_primer_nombre(self,obj):
        return obj.primer_nombre
    
    def get_segundo_nombre(self, obj):
         return obj.segundo_nombre
    
    def get_primer_apellido(self, obj):
         return obj.primer_apellido
    
    def get_segundo_apellido(self, obj):
         return obj.segundo_apellido
    
    def get_nombre_completo(self, obj):
        return f"{obj.primer_nombre} {obj.segundo_nombre} {obj.primer_apellido} {obj.segundo_apellido}"
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_persona',
            'tipo_persona_desc',
            'tipo_documento_id',
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'nombre_completo'
        ]
