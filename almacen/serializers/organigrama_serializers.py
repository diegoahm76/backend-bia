from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.organigrama_models import (
    Organigramas,
    NivelesOrganigrama,
    UnidadesOrganizacionales
)
from seguridad.models import User, Personas

class NivelesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelesOrganigrama
        fields = '__all__'


class NivelesUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = NivelesOrganigrama
        fields = '__all__'
        extra_kwargs = {
            'id_organigrama': {'required': True},
            'nombre': {'required': True},
            'orden_nivel': {'required': True}
        }
        validators = [
           UniqueTogetherValidator(
               queryset=NivelesOrganigrama.objects.all(),
               fields = ['id_organigrama', 'orden_nivel'],
               message='No puede existir más de un nivel con el mismo orden en el organigrama ingresado'
           ),
           UniqueTogetherValidator(
               queryset=NivelesOrganigrama.objects.all(),
               fields = ['id_organigrama', 'nombre'],
               message='Ya existe un nivel con el mismo nombre en el organigrama elegido'
           )
        ]
        
class UnidadesPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesOrganizacionales
        exclude = ['id_unidad_org_padre']
        validators = [
            UniqueTogetherValidator(
                queryset=UnidadesOrganizacionales.objects.all(),
                fields=['id_organigrama', 'codigo'],
                message='Ya existe una unidad con el mismo código en el organigrama elegido'
            ),
            UniqueTogetherValidator(
                queryset=UnidadesOrganizacionales.objects.all(),
                fields=['id_organigrama', 'nombre'],
                message='Ya existe una unidad con el mismo nombre en el organigrama elegido'
            )
        ]
        extra_kwargs = {"cod_tipo_unidad": {"error_messages": {"required": "El campo de cod_tipo_unidad es requerido"}}}

class UnidadesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadesOrganizacionales
        fields = '__all__'

class PersonaOrgSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    tiene_usuario = serializers.SerializerMethodField()
    
    def get_tiene_usuario(self, obj):
        usuario = User.objects.filter(persona=obj.id_persona).exists()
        return usuario

    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    class Meta:
        model = Personas
        fields = ['id_persona',
                  'tipo_documento',
                  'numero_documento',
                  'nombre_completo',
                  'tiene_usuario']
        
class NewUserOrganigramaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Organigramas
        fields='__all__'

class OrganigramaSerializer(serializers.ModelSerializer):
    nombre=serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='El nombre del organigrama debe ser único')])
    version=serializers.CharField(max_length=10, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='La versión del organigrama debe ser único')])     
    tipo_documento = serializers.ReadOnlyField(source='id_persona_cargo.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona_cargo.numero_documento',default=None) 
    nombre_completo = serializers.SerializerMethodField()
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        if obj.id_persona_cargo:
            nombre_list = [obj.id_persona_cargo.primer_nombre, obj.id_persona_cargo.segundo_nombre, obj.id_persona_cargo.primer_apellido, obj.id_persona_cargo.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None).upper()
        return nombre_completo
    
    class Meta:
        model = Organigramas
        fields = ['id_organigrama',
                  'nombre',
                  'fecha_terminado',
                  'descripcion',
                  'fecha_puesta_produccion',
                  'fecha_retiro_produccion',
                  'justificacion_nueva_version',
                  'version',
                  'ruta_resolucion',
                  'id_persona_cargo',
                  'tipo_documento',
                  'numero_documento',
                  'nombre_completo'
                ]
        read_only_fields = ['actual']


class OrganigramaPostSerializer(serializers.ModelSerializer):
    nombre=serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='El nombre de organigrama debe ser único')])     
    version=serializers.CharField(max_length=10, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='La versión del organigrama debe ser único')])     

    class Meta:
        model = Organigramas
        fields = ['id_organigrama',
                  'nombre',
                  'descripcion',
                  'version',
                  'ruta_resolucion',
                  'id_persona_cargo'
                  ]
        extra_kwargs = {
            'nombre': {'required': True},
            'descripcion': {'required': True},
            'version': {'required': True}
        }

class OrganigramaPutSerializer(serializers.ModelSerializer):
    nombre=serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='El nombre de organigrama debe ser único')])     
    version=serializers.CharField(max_length=10, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='La versión del organigrama debe ser única')])     
    
    class Meta:
        model = Organigramas
        fields = ['nombre', 'descripcion', 'version', 'ruta_resolucion']
        extra_kwargs = {
            'nombre': {'required': True},
            'descripcion': {'required': True},
            'version': {'required': True}
        }

class OrganigramaActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organigramas
        fields = ['actual']