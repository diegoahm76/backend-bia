
from rest_framework import serializers
from seguridad.models import Roles,UsuariosRol


class RolesByIdUsuarioSerializer(serializers.ModelSerializer):
    representante_legal = serializers.BooleanField(default=False) 
    nombre_empresa = serializers.CharField(default=None)                             
    class Meta:
        model = Roles
        fields = ['id_rol','nombre_rol','descripcion_rol','Rol_sistema','representante_legal','nombre_empresa']
        extra_kwargs = {
        "Rol_sistema": {"read_only": True}
         }


class RolesSerializer(serializers.ModelSerializer):
     class Meta:
         model = Roles
         fields = '__all__'
         extra_kwargs = {
            "Rol_sistema": {"read_only": True}
         }
         
class UsuarioRolesSerializers(serializers.ModelSerializer):
    
    class Meta:
        model=UsuariosRol
        fields='__all__'


        
        
        
        
        
        
        
        