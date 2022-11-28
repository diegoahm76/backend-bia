from seguridad.serializers.roles_serializers import RolesSerializer
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from seguridad.models import (
    Permisos, 
    PermisosModulo, 
    PermisosModuloRol,
    Modulos
)

class ModulosSerializers(serializers.ModelSerializer):
    class Meta:
        model=Modulos
        fields='__all__'

class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permisos
        fields = '__all__'
        
class PermisosModuloSerializer(serializers.ModelSerializer):
    id_modulo = ModulosSerializers(read_only=True)
    cod_permiso = PermisosSerializer(read_only=True)    
    class Meta:
        model = PermisosModulo
        fields = '__all__'

class PermisosModuloPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisosModulo
        fields = '__all__'

class PermisosModuloRolSerializer(serializers.ModelSerializer):
    cod_permiso = PermisosSerializer(read_only=True)
    id_rol = RolesSerializer(read_only=True)
    id_permiso_modulo = PermisosModuloSerializer(read_only=True)
    class Meta:
        model = PermisosModuloRol
        fields = '__all__'

class PermisosModuloRolSerializerHyper(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PermisosModuloRol
        fields = '__all__'
        extra_kwargs = {
            'id_rol' : {'view_name': 'roles_app:rol-id', 'lookup_field':'pk'},
            'id_modulo' : {'view_name': 'auditorias:consultar-módulo', 'lookup_field':'pk'},
            'cod_permiso' : {'view_name': 'permisos_app:permiso-ver', 'lookup_field':'pk'}
        }
        
class PermisosModuloRolPostSerializer(serializers.ModelSerializer):
     class Meta:
        model = PermisosModuloRol
        fields = '__all__'
        validators = [
           UniqueTogetherValidator(
               queryset=PermisosModuloRol.objects.all(),
               fields = ['id_rol', 'id_permiso_modulo']
           )
        ]