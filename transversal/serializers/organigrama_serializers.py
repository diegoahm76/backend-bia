from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.serializers.tca_serializers import TCASerializer
from gestion_documental.serializers.trd_serializers import TRDSerializer
from transversal.models.organigrama_models import (
    Organigramas,
    NivelesOrganigrama,
    UnidadesOrganizacionales,
    TemporalPersonasUnidad,
    CambiosUnidadMasivos
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
    tipo_documento = serializers.ReadOnlyField(source='id_persona_cargo.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona_cargo.numero_documento',default=None) 
    nombre_completo = serializers.SerializerMethodField()
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        ccd = obj.cuadrosclasificaciondocumental_set.all()
        usado = True if ccd else False
        return usado
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        if obj.id_persona_cargo:
            nombre_list = [obj.id_persona_cargo.primer_nombre, obj.id_persona_cargo.segundo_nombre, obj.id_persona_cargo.primer_apellido, obj.id_persona_cargo.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None).upper()
        return nombre_completo
    
    class Meta:
        model= Organigramas
        fields='__all__'

class OrganigramaSerializer(serializers.ModelSerializer):
    nombre=serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='El nombre del organigrama debe ser único')])
    version=serializers.CharField(max_length=10, validators=[UniqueValidator(queryset=Organigramas.objects.all(), message='La versión del organigrama debe ser único')])     
    tipo_documento = serializers.ReadOnlyField(source='id_persona_cargo.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona_cargo.numero_documento',default=None) 
    nombre_completo = serializers.SerializerMethodField()
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        ccd = obj.cuadrosclasificaciondocumental_set.all()
        usado = True if ccd else False
        return usado
    
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
                  'actual',
                  'ruta_resolucion',
                  'id_persona_cargo',
                  'tipo_documento',
                  'numero_documento',
                  'nombre_completo',
                  'usado'
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
        
class OrganigramaCambioDeOrganigramaActualSerializer(serializers.ModelSerializer):
    class Meta:
        model= Organigramas
        fields=['justificacion_nueva_version']
        
class CCDSerializer_(serializers.ModelSerializer):
    trd = serializers.SerializerMethodField()
    tca = serializers.SerializerMethodField()
    
    def get_trd(value,instance):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=instance.id_ccd).first()
        serializador = TRDSerializer(trd)
        serializador = serializador.data if serializador else None
        return serializador
    
    def get_tca(value,instance):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=instance.id_ccd).first()
        tca = TablasControlAcceso.objects.filter(id_trd=trd.id_trd).first()
        serializador = TCASerializer(tca)
        serializador = serializador.data if serializador else None
        return serializador
    
    class Meta:
        fields = ['id_ccd','id_organigrama','version','nombre','fecha_terminado','fecha_puesta_produccion','fecha_retiro_produccion','justificacion','ruta_soporte','actual','valor_aumento_serie','valor_aumento_subserie','trd','tca']
        model = CuadrosClasificacionDocumental

class ActUnidadOrgAntiguaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    cargo = serializers.ReadOnlyField(source='id_cargo.nombre', default=None)
    nombre_unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre', default=None)
    id_nueva_unidad_organizacional = serializers.ReadOnlyField(default=None)
    nombre_nueva_unidad_organizacional = serializers.ReadOnlyField(default=None)

    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre,
                        obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo

    class Meta:
        model = Personas
        fields = ['id_persona', 'nombre_completo', 'id_cargo', 'cargo', 'id_unidad_organizacional_actual', 'nombre_unidad_organizacional_actual', 'es_unidad_organizacional_actual', 'id_nueva_unidad_organizacional', 'nombre_nueva_unidad_organizacional']

class TemporalPersonasUnidadSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    id_cargo = serializers.ReadOnlyField(source='id_persona.id_cargo.id_cargo', default=None)
    cargo = serializers.ReadOnlyField(source='id_persona.id_cargo.nombre', default=None)
    id_unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_org_anterior.id_unidad_organizacional', default=None)
    nombre_unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_org_anterior.nombre', default=None)
    es_unidad_organizacional_actual = serializers.ReadOnlyField(source='id_persona.es_unidad_organizacional_actual', default=None)
    id_nueva_unidad_organizacional = serializers.ReadOnlyField(source='id_unidad_org_nueva.id_unidad_organizacional', default=None)
    nombre_nueva_unidad_organizacional = serializers.ReadOnlyField(source='id_unidad_org_nueva.nombre', default=None)

    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre,
                        obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    class Meta:
        model = TemporalPersonasUnidad
        fields = ['id_persona', 'nombre_completo', 'id_cargo', 'cargo', 'id_unidad_organizacional_actual','nombre_unidad_organizacional_actual','es_unidad_organizacional_actual', 'id_nueva_unidad_organizacional', 'nombre_nueva_unidad_organizacional']

class GetCambiosUnidadMasivosSerializer(serializers.ModelSerializer):
    persona_cambio = serializers.SerializerMethodField()
    
    def get_persona_cambio(self, obj):
        nombre_completo_solicita = None
        nombre_list = [obj.id_persona_cambio.primer_nombre, obj.id_persona_cambio.segundo_nombre,
                        obj.id_persona_cambio.primer_apellido, obj.id_persona_cambio.segundo_apellido]
        nombre_completo_solicita = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_solicita = nombre_completo_solicita if nombre_completo_solicita != "" else None
        return nombre_completo_solicita
    
    class Meta:
        model = CambiosUnidadMasivos
        fields = '__all__'