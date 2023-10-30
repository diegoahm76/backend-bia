
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.choices.rango_edad_choices import RANGO_EDAD_CHOICES
from gestion_documental.models.encuencas_models import AsignarEncuesta, DatosEncuestasResueltas, EncabezadoEncuesta, OpcionesRta, PreguntasEncuesta, RespuestaEncuesta
from seguridad.models import User
from transversal.models.alertas_models import AlertasGeneradas
from transversal.models.personas_models import Personas 
import datetime
#from dateutil.relativedelta import relativedelta


class  EncabezadoEncuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'

class  EncabezadoEncuestaUpdateSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.ReadOnlyField()
   
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'
class  EncabezadoEncuestaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = ['id_encabezado_encuesta','nombre_encuesta','fecha_creacion']

class  EncuestaActivaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = ['id_encabezado_encuesta','nombre_encuesta','item_ya_usado']

class  EncabezadoEncuestaGetDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'
class  EncabezadoEncuestaDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EncabezadoEncuesta
        fields = '__all__'
            

class  PreguntasEncuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PreguntasEncuesta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=PreguntasEncuesta.objects.all(),
                fields=['id_encabezado_encuesta', 'redaccion_pregunta'],
                message='Esta pregunta ya existe en esta encuesta.'
            )
        ]
class  PreguntasEncuestaDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PreguntasEncuesta
        fields = '__all__'

class  PreguntasEncuestaUpdateSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.ReadOnlyField()
   
    class Meta:
        model =  PreguntasEncuesta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=PreguntasEncuesta.objects.all(),
                fields=['id_encabezado_encuesta', 'redaccion_pregunta'],
                message='Esta pregunta ya existe en esta encuesta.'
            )
        ]

class  PreguntasEncuestaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PreguntasEncuesta
        fields = ['id_pregunta_encuesta','id_encabezado_encuesta','redaccion_pregunta',]


class  OpcionesRtaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  OpcionesRta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=OpcionesRta.objects.all(),
                fields=['id_pregunta', 'opcion_rta'],
                message='Esta opcion ya existe en esta pregunta.'
            )
        ]
class  OpcionesRtaGetSerializer(serializers.ModelSerializer):

    class Meta:
        model =  OpcionesRta
        fields = ['id_opcion_rta','opcion_rta','id_pregunta']


class  OpcionesRtaUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model =  OpcionesRta
        fields = '__all__'



class  OpcionesRtaDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model =  OpcionesRta
        fields = '__all__'

class DatosEncuestasResueltasCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatosEncuestasResueltas
        fields = '__all__'

class PersonaRegistradaEncuentaGet(serializers.ModelSerializer):
    id_tipo_documento_usuario=serializers.ReadOnlyField(source='tipo_documento.cod_tipo_documento',default=None)
    nombre_completo = serializers.SerializerMethodField()
    cod_sexo = serializers.ReadOnlyField(source='sexo.cod_sexo',default=None)
    rango_edad = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    id_municipio_para_nacional = serializers.SerializerMethodField()
    id_pais_para_extranjero = serializers.SerializerMethodField()
    nro_documento_id=serializers.ReadOnlyField(source='numero_documento',default=None)
    class Meta:
        model = Personas
        fields = ['id_persona','id_tipo_documento_usuario','nro_documento_id','nombre_completo','cod_sexo','rango_edad','tipo_persona','email','telefono','id_pais_para_extranjero','id_municipio_para_nacional']

       
    
    #RETORNAR NOMBRE COMPLETO
    def get_nombre_completo(self, obj):
        if obj.tipo_persona == 'N':
            nombre_completo = None
            nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
            return nombre_completo.upper()
        if obj.tipo_persona == 'J':
            return obj.razon_social
        return None
    def get_rango_edad(self,obj):
        if obj.tipo_persona == 'N':
            rango = RANGO_EDAD_CHOICES
            rangos = [('A',18,25),('B',26,36),('C',37,46),('D',47,56),('E',56,None)]
            fecha_nacimiento = obj.fecha_nacimiento
            if fecha_nacimiento:
                fecha_actual = datetime.date.today()
                edad = fecha_actual.year - fecha_nacimiento.year
                if (fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                    edad -= 1

                años = edad

                for categoria, limite_inferior, limite_superior in rangos:
                    if limite_superior is None:
                        if años >= limite_inferior:
                            return categoria
                    elif limite_inferior <= años <= limite_superior:
                        return categoria
                return None

        else:
            return None
    def get_telefono(self, obj):
            if obj.tipo_persona == 'N':

                if not obj.telefono_celular:

                    return obj.telefono_fijo_residencial
                
                return obj.telefono_celular
            if obj.tipo_persona == 'J':

                if not obj.telefono_empresa:
                    return obj.telefono_celular_empresa
                
                if not obj.telefono_celular_empresa:
                    return obj.telefono_empresa_2
             
                return obj.telefono_empresa
            return None
    def get_id_municipio_para_nacional(self,obj):


        if obj.tipo_persona == 'N':
            if  not obj.municipio_residencia:

                return None
            
            return obj.municipio_residencia.cod_municipio
        if obj.tipo_persona == 'J':
            if not obj.cod_municipio_notificacion_nal:
                return None

            return obj.cod_municipio_notificacion_nal.cod_municipio
        
        return None
    def get_id_pais_para_extranjero(self,obj):

        if obj.tipo_persona == 'N':
            if not obj.pais_residencia:
                return None
            
            return obj.pais_residencia.cod_pais
        
        if obj.tipo_persona == 'J':
            if not  obj.cod_pais_nacionalidad_empresa:
                return None

            return obj.cod_pais_nacionalidad_empresa.cod_pais
        
        return None
    
class RespuestaEncuestaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RespuestaEncuesta
        fields = '__all__'

class DatosEncuestasResueltasConteoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosEncuestasResueltas
        fields = '__all__'

class AlertasGeneradasEncuestaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertasGeneradas
        fields = '__all__'

class AsignarEncuestaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignarEncuesta
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=AsignarEncuesta.objects.all(),
                fields = ['id_encuesta', 'id_persona'],
                message='La encuesta ya se encuentra asignada a esta persona'
            )
        ]  

class AsignarEncuestaGetSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    nombre_encuesta=serializers.ReadOnlyField(source='id_encuesta.nombre_encuesta',default=None)
    class Meta:
        model = AsignarEncuesta
        fields = '__all__'
    def get_nombre_completo(self, obj):
        nombre_completo_responsable = None
        nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre,
                        obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    

class PersonasFilterEncuestaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    tiene_usuario = serializers.SerializerMethodField()
    primer_nombre = serializers.SerializerMethodField()
    segundo_nombre = serializers.SerializerMethodField()
    primer_apellido = serializers.SerializerMethodField()
    segundo_apellido = serializers.SerializerMethodField()
    razon_social = serializers.SerializerMethodField()
    tipo_persona_desc = serializers.CharField(source='get_tipo_persona_display')
    usuario =  serializers.SerializerMethodField()
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
    
    def get_usuario(self, obj):
        id = obj.id_persona
        usuario = User.objects.filter(persona=id).first()
        if usuario:
            return usuario.tipo_usuario
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
            'usuario'
        ]
