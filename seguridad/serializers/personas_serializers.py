from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from seguridad.models import (
    Personas, 
    User,
    TipoDocumento, 
    EstadoCivil,
    ApoderadoPersona,
    SucursalesEmpresas,
    HistoricoEmails,
    HistoricoDireccion,
    ClasesTercero,
    ClasesTerceroPersona,
    Cargos,
    HistoricoCargosUndOrgPersona,
    HistoricoCambiosIDPersonas
)


class EstadoCivilSerializer(serializers.ModelSerializer):
    cod_estado_civil = serializers.CharField(max_length=1, validators=[UniqueValidator(queryset=EstadoCivil.objects.all(), message='El cod_estado_civil debe ser único')])

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
    cod_estado_civil = serializers.CharField(max_length=1, validators=[UniqueValidator(queryset=EstadoCivil.objects.all(), message='El cod_estado_civil debe ser único')])
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
    cod_tipo_documento = serializers.CharField(max_length=2, validators=[UniqueValidator(queryset=TipoDocumento.objects.all(), message='El cod_tipo_documento debe ser único')])
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
    cod_tipo_documento = serializers.CharField(max_length=2, validators=[UniqueValidator(queryset=TipoDocumento.objects.all(), message='El cod_tipo_documento debe ser único')])
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
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    
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
            'telefono_fijo_residencial',
            'pais_residencia',
            'municipio_residencia',
            'direccion_residencia',
            'direccion_laboral',
            'direccion_residencia_ref',
            'direccion_notificaciones',
            'cod_municipio_laboral_nal',
            'cod_municipio_notificacion_nal',
            'acepta_notificacion_sms',
            'acepta_notificacion_email',
            'acepta_tratamiento_datos',
            "cod_municipio_expedicion_id"
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
            'email': {'required': True},
            'sexo': {'required': True},
            'estado_civil': {'required': True},
            'cod_municipio_expedicion_id': {'required': True},
            'pais_residencia': {'required': True},
            'direccion_residencia': {'required': True},
            'direccion_notificaciones': {'required': True},
            'cod_municipio_notificacion_nal': {'required': True},
            'acepta_notificacion_sms': {'required': True},
            'acepta_notificacion_email': {'required': True},
            'acepta_tratamiento_datos': {'required': True},
        }
        

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
            'tipo_persona': {'required': True},
            'tipo_documento': {'required': True},
            'numero_documento': {'required': True},
            'digito_verificacion': {'required': True},
            'razon_social': {'required': True},
            'nombre_comercial': {'required': True},
            'representante_legal': {'required': True},
            'cod_naturaleza_empresa': {'required': True},
            'email': {'required': True},
            'direccion_notificaciones': {'required': True},
            'cod_municipio_notificacion_nal': {'required': True},
            'fecha_inicio_cargo_rep_legal': {'required':True},
            'acepta_notificacion_sms': {'required':True},
            'acepta_notificacion_email': {'required':True}
        }
        
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
            'direccion_residencia',
            'pais_residencia',
            'municipio_residencia',
            'cod_municipio_notificacion_nal',
            'ubicacion_georeferenciada',
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
            'telefono_fijo_residencial',
            'pais_residencia',
            'municipio_residencia',
            'direccion_residencia',
            'direccion_laboral',
            'direccion_residencia_ref',
            'direccion_notificaciones',
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


#ACTUALIZACION PERSONA NATURAL
class PersonaNaturalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'digito_verificacion',
            'nombre_comercial',
            'direccion_residencia',
            'direccion_residencia_ref',
            'ubicacion_georeferenciada',
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
            "cod_municipio_expedicion_id"
        ]
        
        extra_kwargs = {
                'fecha_nacimiento': {'required': True},
                'email': {'required': True},
                'sexo': {'required': True},
                'estado_civil': {'required': True},
                'cod_municipio_expedicion_id': {'required': True},
                'pais_residencia': {'required': True},
                'direccion_notificaciones': {'required': True},
                'cod_municipio_notificacion_nal': {'required': True},
                'direccion_residencia': {'required': True},
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
    email = serializers.EmailField(validators=[UniqueValidator(queryset=Personas.objects.all())])
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


#ACTUALIZACION DE PERSONA JURIDICA
class PersonaJuridicaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = [
            'direccion_notificaciones', 
            'cod_municipio_notificacion_nal',
            'email',
            'email_empresarial',
            'telefono_empresa',
            'telefono_celular_empresa',
            'telefono_empresa_2',
            'cod_pais_nacionalidad_empresa',
            "representante_legal",
            "fecha_inicio_cargo_rep_legal"
        ]
        
        extra_kwargs = {
            'representante_legal': {'required': True},
            'email': {'required': True},
            'direccion_notificaciones': {'required': True},
            'fecha_inicio_cargo_rep_legal': {'required':True},
            'cod_municipio_notificacion_nal': {'required':True},
            'cod_pais_nacionalidad_empresa': {'required':True}
        }
        
class PersonaJuridicaUpdateUserPermissionsSerializer(serializers.ModelSerializer):
    telefono_celular_empresa = serializers.CharField(max_length=15, min_length=10)

    class Meta:
        model = Personas
        fields = [
            'direccion_notificaciones', 
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
        
        
class SucursalesEmpresasSerializer(serializers.ModelSerializer):
    id_empresa = PersonasSerializer(read_only=True)
    
    class Meta:
        model = SucursalesEmpresas
        fields = '__all__'
        

class SucursalesEmpresasPostSerializer(serializers.ModelSerializer):
    sucursal = serializers.CharField(validators=[UniqueValidator(queryset=SucursalesEmpresas.objects.all())])
    class Meta:
        model = SucursalesEmpresas
        fields = '__all__'
        extra_kwargs = {
                'id_empresa': {'required': True},
                'sucursal': {'required': True},
                'direccion': {'required': True},
                'direccion_sucursal_georeferenciada': {'required': True},
                'pais_sucursal_exterior': {'required': True},
                'direccion_correspondencias': {'required': True},
                'email_sucursal': {'required': True},
                'telefono_sucursal': {'required': True},
            }
        

class HistoricoEmailsSerializer(serializers.ModelSerializer):
    id_persona = PersonasSerializer(read_only=True)
    class Meta:
        model = HistoricoEmails
        fields = '__all__'
        
        
class HistoricoDireccionSerializer(serializers.ModelSerializer):
    id_persona = PersonasSerializer(read_only=True)
    
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
    nombre = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=Cargos.objects.all(), message='El nombre del cargo debe ser único')])

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
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()   
        return usuario
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo
        
    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'tipo_persona',
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'nombre_completo',
            'razon_social',
            'nombre_comercial',
            'tiene_usuario'
        ]

class BusquedaHistoricoCambiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCambiosIDPersonas
        fields = '__all__'

class UpdatePersonasNaturalesSerializer(serializers.ModelSerializer):
    justificacion = serializers.CharField(required=True)

    class Meta:
        model = Personas
        fields = ('id_persona', 'tipo_documento', 'numero_documento', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'justificacion')


        validators = [
                UniqueTogetherValidator(
                    queryset = Personas.objects.all(),
                    fields = ['tipo_documento', 'numero_documento'],
                    message = 'Ya existe un registro con el tipo de documento y el número de documento ingresado'
                    
                )
            ]
    
class UpdatePersonasJuridicasSerializer(serializers.ModelSerializer):
    justificacion = serializers.CharField(required=True)

    class Meta:
        model = Personas
        fields = ('id_persona', 'numero_documento', 'razon_social', 'nombre_comercial', 'cod_naturaleza_empresa','justificacion')


        validators = [
                UniqueTogetherValidator(
                    queryset = Personas.objects.all(),
                    fields = ['numero_documento'],
                    message = 'Ya existe un registro con ese número de documento ingresado'    
                )
            ]

class ConsultaVinculacionColaboradorSerializer(serializers.ModelSerializer):
    cargo_actual = serializers.CharField(source='id_cargo.nombre', read_only=True)
    unidad_organizacional_actual = serializers.CharField(source='id_unidad_organizacional_actual.nombre', read_only=True)
    fecha_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Personas
        fields = ('cargo_actual','unidad_organizacional_actual','fecha_inicio_cargo_actual', 'fecha_asignacion_unidad', 'fecha_a_finalizar_cargo_actual', 'observaciones_vinculacion_cargo_actual','fecha_vencida')