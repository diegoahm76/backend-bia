from datetime import datetime
from django.core import signing
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from seguridad.models import OperacionesSobreUsuario, User, UsuariosRol, HistoricoActivacion,Login,LoginErroneo,PermisosModuloRol
from transversal.models.personas_models import Personas
from transversal.serializers.personas_serializers import PersonasSerializer
from seguridad.serializers.permisos_serializers import PermisosModuloRolSerializer
import re
from seguridad.utils import Util

class HistoricoActivacionSerializers(serializers.ModelSerializer):
    nombre_operador = serializers.SerializerMethodField()
    
    def get_nombre_operador(self, obj):
        nombre_operador = None
        nombre_list = [obj.usuario_operador.persona.primer_nombre, obj.usuario_operador.persona.primer_apellido]
        nombre_operador = ' '.join(item for item in nombre_list if item is not None)
        return nombre_operador.upper()
    
    class Meta:
        model= HistoricoActivacion
        fields = '__all__'

class UserRolesSerializer(serializers.ModelSerializer):
    permisos_rol = serializers.SerializerMethodField()
    
    class Meta:
        model = UsuariosRol
        fields = '__all__'

    def get_permisos_rol(self, obj):
        permisos_rol = PermisosModuloRol.objects.filter(id_rol=obj.id_rol)
        return PermisosModuloRolSerializer(permisos_rol, many=True).data
        
class UsuarioCreadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    id_usuario_creador = UsuarioCreadorSerializer(read_only=True)
    persona = PersonasSerializer(read_only=True)
    usuario_rol = UserRolesSerializer(read_only=True)
    

    class Meta:
        model = User
        fields = '__all__'

    def get_usuario_rol(self, obj):
        rol = obj.usuariosrol_set.all()
        serializer = UserRolesSerializer(rol, many=True)
        return serializer.data

    def get__id(self, obj):
        return obj.id_usuario

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_usuario_creador(self,obj):
        usuario_creador= obj.id_usuario_creador
        serializer = UsuarioCreadorSerializer(usuario_creador,many=True)
        return serializer.data
    
    def create(self, validated_data):
        usuario_creador = validated_data.pop('usuario_creador')
        user_instance = User.objects.create(**validated_data)
        for user in usuario_creador:
            User.objects.create(user=user_instance,**user)
        return user_instance

class UserPutSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    profile_img = serializers.ReadOnlyField(source='id_archivo_foto.ruta_archivo.url', default=None)

    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un .')
        return value
    
    def validate(self, data):
        password = data.get('password')
        data['password'] = make_password(password)
        return data
    
    class Meta:
        model = User
        fields =['password', 'id_archivo_foto', 'profile_img']

class UserPutAdminSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField(max_length=1, write_only=True)
    profile_img = serializers.ReadOnlyField(source='id_archivo_foto.ruta_archivo.url', default=None)
    is_active = serializers.BooleanField(required=False)
    is_blocked = serializers.BooleanField(write_only=True)
    justificacion = serializers.CharField(max_length=255, write_only=True, required=False)
    #sucursal_defecto = serializers.ReadOnlyField(source='sucursal_defecto.id_sucursal_empresa', default=None)

    class Meta:
        model = User
        fields = ['is_active', 'is_blocked', 'tipo_usuario', 'id_archivo_foto', 'profile_img', 'justificacion', 'sucursal_defecto']

class UsuarioRolesLookSerializers(serializers.ModelSerializer):
    nombre_usuario = serializers.ReadOnlyField(source='id_usuario.nombre_de_usuario', default=None)
    id_persona = serializers.ReadOnlyField(source='id_usuario.persona.id_persona', default=None)
    email = serializers.ReadOnlyField(source='id_usuario.persona.email', default=None)
    nombre_persona = serializers.SerializerMethodField()
    
    def get_nombre_persona(self, obj):
        nombre_persona = None
        if obj.id_usuario:
            if obj.id_usuario.persona:
                if obj.id_usuario.persona.tipo_persona == 'N':
                    nombre_list = [obj.id_usuario.persona.primer_nombre, obj.id_usuario.persona.segundo_nombre,
                                   obj.id_usuario.persona.primer_apellido, obj.id_usuario.persona.segundo_apellido]
                    nombre_persona = ' '.join(item for item in nombre_list if item is not None)
                    nombre_persona = nombre_persona if nombre_persona != "" else None
                else:
                    nombre_persona = obj.id_usuario.persona.razon_social
        return nombre_persona
    
    class Meta:
        model=UsuariosRol
        fields=['id_rol', 'id_usuario', 'nombre_usuario', 'id_persona', 'nombre_persona', 'email']
        
class RolesSerializers(serializers.ModelSerializer):
    nombre_rol = serializers.ReadOnlyField(source='id_rol.nombre_rol', default=None)
    class Meta:
        model=UsuariosRol
        fields=['id_rol', 'nombre_rol']

class RegisterSerializer(serializers.ModelSerializer):
    profile_img = serializers.ReadOnlyField(source='id_archivo_foto.ruta_archivo.url', default=None)
    
    def validate_nombre_de_usuario(self, value):
        # if not value.isalnum():
        #     raise serializers.ValidationError("El nombre de usuario solo debe tener caracteres alfanumericos")
        if " " in value:
            raise serializers.ValidationError("No puede contener espacios en el nombre de usuario")
        
        value = str(value).lower()
        
        return value
    
    def validate_persona(self, value):
        if not value.email:
            raise serializers.ValidationError("La persona no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion de datos para proceder con la creación del usuario en el sistema")
        return value
    
    class Meta:
        model = User
        fields = ['persona', 'nombre_de_usuario', 'id_archivo_foto', 'profile_img', 'tipo_usuario', 'id_usuario_creador']

class RegisterExternoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length= 68, min_length = 8, write_only=True)
    redirect_url=serializers.CharField(max_length=500, read_only=True)
    
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un caracter especial.')
        return value

    def validate(self, attrs):
        nombre_de_usuario=attrs.get('nombre_de_usuario', '')
        # redirect_url=attrs.get('redirect_url','')
        # if not nombre_de_usuario.isalnum():
        #     raise serializers.ValidationError("El Nombre de usuario solo debe tener caracteres alfanumericos")
        
        attrs['nombre_de_usuario'] = str(attrs['nombre_de_usuario']).lower()
        
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    class Meta:
        model = User
        fields = ['nombre_de_usuario', 'persona', 'password','redirect_url','creado_por_portal','is_active']

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

from seguridad.models import Login,LoginErroneo

class LoginSerializers(serializers.ModelSerializer):
    id_usuario=UserSerializer(read_only=True)
    class Meta:
        model=Login
        fields= '__all__'

class LoginSerializer(serializers.ModelSerializer):

    email = serializers.CharField(max_length=255, min_length=3,read_only=True)
    telefono_celular = serializers.CharField(max_length=15, read_only=True)
    tipo_documento = serializers.CharField(max_length=2, read_only=True)
    numero_documento = serializers.CharField(max_length=20, read_only=True)
    password= serializers.CharField(max_length=68, min_length=6, write_only=True)
    nombre_de_usuario = serializers.CharField(max_length=68, min_length=6)
    nombre = serializers.CharField(read_only=True)
    tokens = serializers.DictField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True, default=False)
    id_usuario = serializers.IntegerField(read_only=True)
    tipo_usuario = serializers.CharField(read_only=True)
    id_persona = serializers.IntegerField(read_only=True)
    tipo_persona = serializers.CharField(read_only=True)
    id_unidad_organizacional_actual = serializers.IntegerField(read_only=True)
    nombre_unidad_organizacional = serializers.CharField(read_only=True)
    activated_at = serializers.DateTimeField(read_only=True)
    id_archivo_foto = serializers.IntegerField(read_only=True)
    profile_img = serializers.CharField(read_only=True)
    permisos = serializers.DictField(read_only=True)
    representante_legal =serializers.DictField(read_only=True)
    
    class Meta:
        model=Login
        fields= ['email', 'telefono_celular', 'tipo_documento', 'numero_documento', 'password', 'nombre_de_usuario', 'nombre', 'tokens', 'is_superuser', 'id_usuario', 'tipo_usuario', 'id_persona', 'tipo_persona', 'id_unidad_organizacional_actual', 'nombre_unidad_organizacional', 'activated_at', 'id_archivo_foto', 'profile_img', 'permisos', 'representante_legal']
    
    def validate(self, attrs):
        nombre_de_usuario = attrs.get('nombre_de_usuario', '').lower()
        password = attrs.get('password', '')
        user= auth.authenticate(nombre_de_usuario=nombre_de_usuario, password=password)
        tokens = None

        if not user:
            raise AuthenticationFailed('Credenciales invalidas intenta de nuevo')
        
        if not user.is_active:
            raise AuthenticationFailed('Cuenta no verificada')
        
        if user.is_blocked:
            raise AuthenticationFailed('Tu cuenta ha sido bloqueada, contacta un Admin')
        
        if user.tipo_usuario == 'E':
            tokens = Util.change_token_expire_externo(user)
        else:
            tokens = user.tokens()
            
        if user.persona.tipo_persona == 'N':
            nombre_list = [user.persona.primer_nombre, user.persona.segundo_nombre,
                            user.persona.primer_apellido, user.persona.segundo_apellido]
            nombre = ' '.join(item for item in nombre_list if item is not None)
            nombre = nombre if nombre != "" else None
        else:
            nombre = user.persona.razon_social

        return {
            'email': user.persona.email,
            'telefono_celular': user.persona.telefono_celular,
            'tipo_documento': user.persona.tipo_documento.cod_tipo_documento,
            'numero_documento': user.persona.numero_documento,
            'nombre_de_usuario': user.nombre_de_usuario,
            'nombre':nombre,
            'tokens': tokens,
            'is_superuser': user.is_superuser,
            'id_usuario': user.id_usuario,
            'tipo_usuario': user.tipo_usuario,
            'id_persona': user.persona.id_persona,
            'tipo_persona': user.persona.tipo_persona,
            'id_unidad_organizacional_actual': user.persona.id_unidad_organizacional_actual.id_unidad_organizacional if user.persona.id_unidad_organizacional_actual else None,
            'nombre_unidad_organizacional': user.persona.id_unidad_organizacional_actual.nombre if user.persona.id_unidad_organizacional_actual else None,
            'activated_at': user.activated_at,
            'id_archivo_foto': user.id_archivo_foto.id_archivo_digital if user.id_archivo_foto else None,
            'profile_img': user.id_archivo_foto.ruta_archivo.url if user.id_archivo_foto else None
        }
 
class LoginPostSerializers(serializers.ModelSerializer):
    class Meta:
        model=Login
        fields= '__all__'
        extra_kwargs = {
                'id_login': {'required': True},
                'id_usuario': {'required': True},
                'dirip':  {'required': True},
                'dispositivo_conexion': {'required': True},
                'fecha_login': {'required': True},
            }
        
class LoginErroneoSerializers(serializers.ModelSerializer):
    id_usuario=UserSerializer(read_only=True)
    class Meta:
        model=LoginErroneo
        fields= '__all__'

class LoginErroneoPostSerializers(serializers.ModelSerializer):
    restantes = serializers.IntegerField(read_only=True)
    class Meta:
     model=LoginErroneo
     fields= '__all__'
     extra_kwargs = {
                'id_login_error': {'required': True},
                'id_usuario': {'required': True},
                'dirip':  {'required': True},
                'dispositivo_conexion': {'required': True},
                'fecha_login_error': {'required': True},
                'contador': {'required': True},
            }
    
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        models = User
        fields = ['token']

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    redirect_url=serializers.CharField(max_length=1000, required=False)

    class Meta:
        fields=['email','redirect_url']
    
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8,max_length=68,write_only=True)
    token = serializers.CharField(min_length=1,write_only=True)   
    uidb64 = serializers.CharField(min_length=1,write_only=True)
    
    def validate(self, attrs):
        password = attrs.get('password')
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')

        id = int(signing.loads(uidb64)['user'])
        user = User.objects.get(id_usuario=id)
        
        # VALIDACIONES PASSWORD
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'\d', password):
            raise serializers.ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[^A-Za-z0-9]', password):
            raise serializers.ValidationError('La contraseña debe contener al menos un caracter especial.')
        
        # VALIDACIONES LINK
        if not PasswordResetTokenGenerator().check_token(user,token):
            if user.password:
                raise AuthenticationFailed('Link de actualización de contraseña invalido')
            else:
                raise AuthenticationFailed('Link de activación de usuario invalido')

        return attrs
    
    class Meta:
        fields = ['password','token','uidb64']
       


class DesbloquearUserSerializer(serializers.Serializer):
    nombre_de_usuario = serializers.CharField(max_length=30, min_length=1)
    tipo_documento = serializers.CharField(read_only=True)
    numero_documento = serializers.CharField(read_only=True)
    telefono_celular = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    fecha_nacimiento = serializers.CharField(read_only=True)
    redirect_url = serializers.CharField(max_length=1000, required=False)

    class Meta:
        fields = ['nombre_de_usuario', 'tipo_documento', 'numero_documento', 'telefono_celular', 'email', 'fecha_nacimiento', 'redirect_url']

class SetNewPasswordUnblockUserSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']
        
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un número.')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError('La contraseña debe contener al menos un caracter especial.')
        return value
    
    def validate(self, attrs):
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = int(signing.loads(uidb64)['user'])
            user = User.objects.get(id_usuario=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Link de desbloqueo de usuario invalido', 401)
            
            user.set_password(password)
            user.is_blocked = False
            user.save()
            
            cod_operacion_instance = OperacionesSobreUsuario.objects.filter(cod_operacion='D').first()
            
            # HISTORICO DESBLOQUEO
            HistoricoActivacion.objects.create(
                id_usuario_afectado=user,
                cod_operacion=cod_operacion_instance,
                fecha_operacion=datetime.now(),
                justificacion='Usuario desbloqueado por validación de datos',
                usuario_operador=user
            )

            return user

class UsuarioInternoAExternoSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active','tipo_usuario']
        

#BUSQUEDA USUARIO
class UsuarioBasicoSerializer(serializers.ModelSerializer):
    numero_documento = serializers.ReadOnlyField(source='persona.numero_documento',default=None)
    tipo_persona = serializers.ReadOnlyField(source='persona.tipo_persona', default=None)
    primer_nombre = serializers.SerializerMethodField(default=None)
    primer_apellido = serializers.SerializerMethodField(default=None)
    razon_social = serializers.ReadOnlyField(source='persona.razon_social',default=None)
    nombre_comercial = serializers.ReadOnlyField(source='persona.nombre_comercial',default=None)
    nombre_completo = serializers.SerializerMethodField()
    
    #RETORNAR NOMBRE COMPLETO
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.persona.primer_nombre, obj.persona.segundo_nombre, obj.persona.primer_apellido, obj.persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    #RETORNE LOS DATOS EN MAYUSCULAS
    def get_primer_nombre(self, obj):
        primer_nombre2 = obj.persona.primer_nombre
        primer_nombre2 = primer_nombre2.upper() if primer_nombre2 else primer_nombre2
        return primer_nombre2
    
    def get_primer_apellido(self, obj):
        primer_apellido2 = obj.persona.primer_apellido
        primer_apellido2 = primer_apellido2.upper() if primer_apellido2 else primer_apellido2
        return primer_apellido2
    class Meta:
        fields = [
            'id_usuario',
            'nombre_de_usuario',
            'persona',
            'tipo_persona',
            'numero_documento',
            'primer_nombre',
            'primer_apellido',
            'nombre_completo',
            'razon_social',
            'nombre_comercial',
            'is_superuser'
        ]
        model = User

class UsuarioFullSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.ReadOnlyField(source='persona.tipo_documento.cod_tipo_documento',default=None)
    numero_documento = serializers.ReadOnlyField(source='persona.numero_documento',default=None)
    primer_nombre = serializers.SerializerMethodField(default=None)
    segundo_nombre = serializers.SerializerMethodField(default=None)
    primer_apellido = serializers.SerializerMethodField(default=None)
    segundo_apellido = serializers.SerializerMethodField(default=None)
    razon_social = serializers.ReadOnlyField(source='persona.razon_social',default=None)
    nombre_comercial = serializers.ReadOnlyField(source='persona.nombre_comercial',default=None)
    tipo_persona = serializers.ReadOnlyField(source='persona.tipo_persona', default=None)
    nombre_completo = serializers.SerializerMethodField()
    primer_nombre_usuario_creador = serializers.SerializerMethodField(source='id_usuario_creador.persona.primer_nombre',default=None)
    primer_apellido_usuario_creador = serializers.SerializerMethodField(source='id_usuario_creador.persona.primer_apellido',default=None)
    roles = serializers.SerializerMethodField()
    fecha_ultimo_cambio_activacion = serializers.SerializerMethodField()
    justificacion_ultimo_cambio_activacion = serializers.SerializerMethodField()
    fecha_ultimo_cambio_bloqueo = serializers.SerializerMethodField()
    justificacion_ultimo_cambio_bloqueo = serializers.SerializerMethodField()
    id_sucursal_empresa = serializers.ReadOnlyField(source='sucursal_defecto.id_sucursal_empresa',default=None)
    descripcion_sucursal_empresa = serializers.ReadOnlyField(source='sucursal_defecto.descripcion_sucursal',default=None)
    profile_img = serializers.ReadOnlyField(source='id_archivo_foto.ruta_archivo.url', default=None)
    
    #RETORNAR NOMBRE COMPLETO
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.persona.primer_nombre, obj.persona.segundo_nombre, obj.persona.primer_apellido, obj.persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    #RETORNE LOS DATOS EN MAYUSCULAS
    def get_primer_nombre(self, obj):
        primer_nombre2 = obj.persona.primer_nombre
        primer_nombre2 = primer_nombre2.upper() if primer_nombre2 else primer_nombre2
        return primer_nombre2
    
    def get_segundo_nombre(self, obj):
        segundo_nombre2 = obj.persona.segundo_nombre
        segundo_nombre2 = segundo_nombre2.upper() if segundo_nombre2 else segundo_nombre2
        return segundo_nombre2
    
    def get_primer_apellido(self, obj):
        primer_apellido2 = obj.persona.primer_apellido
        primer_apellido2 = primer_apellido2.upper() if primer_apellido2 else primer_apellido2
        return primer_apellido2
    
    def get_segundo_apellido(self, obj):
        segundo_apellido2 = obj.persona.segundo_apellido
        segundo_apellido2 = segundo_apellido2.upper() if segundo_apellido2 else segundo_apellido2
        return segundo_apellido2
    
    def get_primer_nombre_usuario_creador(self, obj):
        primer_nombre2 = None
        if obj.id_usuario_creador:
            primer_nombre2 = obj.id_usuario_creador.persona.primer_nombre
            primer_nombre2 = primer_nombre2.upper() if primer_nombre2 else primer_nombre2
        return primer_nombre2
    
    def get_primer_apellido_usuario_creador(self, obj):
        primer_apellido2 = None
        if obj.id_usuario_creador:
            primer_apellido2 = obj.id_usuario_creador.persona.primer_apellido
            primer_apellido2 = primer_apellido2.upper() if primer_apellido2 else primer_apellido2
        return primer_apellido2
    
    def get_roles(self, obj):
        roles = obj.usuariosrol_set.all()
        serializer_roles = RolesSerializers(roles, many=True)
        return serializer_roles.data
    
    def get_fecha_ultimo_cambio_activacion(self, obj):
        estado_activo = 'A' if obj.is_active else 'I'
        hist_activacion = HistoricoActivacion.objects.filter(id_usuario_afectado=obj.id_usuario, cod_operacion=estado_activo).last()
        fecha_ultimo_cambio_activacion = hist_activacion.fecha_operacion if hist_activacion else None
        return fecha_ultimo_cambio_activacion
    
    def get_justificacion_ultimo_cambio_activacion(self, obj):
        estado_activo = 'A' if obj.is_active else 'I'
        hist_activacion = HistoricoActivacion.objects.filter(id_usuario_afectado=obj.id_usuario, cod_operacion=estado_activo).last()
        justificacion_ultimo_cambio_activacion = hist_activacion.justificacion if hist_activacion else None
        return justificacion_ultimo_cambio_activacion
    
    def get_fecha_ultimo_cambio_bloqueo(self, obj):
        estado_bloqueo = 'B' if obj.is_blocked else 'D'
        hist_activacion = HistoricoActivacion.objects.filter(id_usuario_afectado=obj.id_usuario, cod_operacion=estado_bloqueo).last()
        fecha_ultimo_cambio_bloqueo = hist_activacion.fecha_operacion if hist_activacion else None
        return fecha_ultimo_cambio_bloqueo
    
    def get_justificacion_ultimo_cambio_bloqueo(self, obj):
        estado_bloqueo = 'B' if obj.is_blocked else 'D'
        hist_activacion = HistoricoActivacion.objects.filter(id_usuario_afectado=obj.id_usuario, cod_operacion=estado_bloqueo).last()
        justificacion_ultimo_cambio_bloqueo = hist_activacion.justificacion if hist_activacion else None
        return justificacion_ultimo_cambio_bloqueo
    
    class Meta:
        fields = [
            'id_usuario',
            'nombre_de_usuario',
            'persona',
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
            'is_active',
            'fecha_ultimo_cambio_activacion',
            'justificacion_ultimo_cambio_activacion',
            'is_blocked',
            'fecha_ultimo_cambio_bloqueo',
            'justificacion_ultimo_cambio_bloqueo',
            'tipo_usuario',
            'id_archivo_foto',
            'profile_img',
            'creado_por_portal',
            'created_at',
            'activated_at',
            'id_usuario_creador',
            'primer_nombre_usuario_creador',
            'primer_apellido_usuario_creador',
            'roles',
            'id_sucursal_empresa',
            'descripcion_sucursal_empresa'
        ]
        model = User

#BUQUEDA DE PERSONA POR ID Y TRAIGA LA LISTA DE LOS DATOS DE LA TABLA USUARIOS
class GetBuscarIdPersona(serializers.ModelSerializer): #modelserializer para identificadores

    class Meta:
        fields = '__all__' #['nombre_de_usuario','profile_img','tipo_usuario','is_active','created_at','creado_por_portal','id_usuario_creador']
        model = User
        

class RecuperarUsuarioSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ['tipo_documento','numero_documento','email']
        model = Personas
        
        extra_kwargs= {
            'tipo_documento': {'required': True, 'allow_null':False},
            'numero_documento': {'required': True, 'allow_null':False, 'allow_blank':False},
            'email': {'required': True, 'allow_null':False, 'allow_blank':False},
        }