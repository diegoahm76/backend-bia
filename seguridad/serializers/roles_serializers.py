
from rest_framework import serializers
from seguridad.models import Roles,UsuariosRol





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


        
        
        
        
        
        
        
        