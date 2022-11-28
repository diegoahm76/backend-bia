from rest_framework import serializers
from seguridad.models import Auditorias
from seguridad.serializers.user_serializers import UserSerializer
from seguridad.serializers.permisos_serializers import PermisosSerializer, ModulosSerializers

class AuditoriasSerializers(serializers.ModelSerializer):
    id_modulo=ModulosSerializers(read_only=True)
    id_usuario=UserSerializer(read_only=True)
    id_cod_operacion=PermisosSerializer(read_only=True)

    class Meta:
        model=Auditorias
        fields= '__all__'
        #fields= ('id_auditoria', 'id_usuario', 'id_modulo', 'id_cod_operacion', 'fecha_accion','subsistema','dirip','descripcion','valores_actualizados')
        
class AuditoriasPostSerializers(serializers.ModelSerializer):
    class Meta:
        model=Auditorias
        fields= '__all__'
        extra_kwargs = {
                'id_auditoria': {'required': True},
                'id_usuario': {'required': True},
                'id_modulo':  {'required': True},
                'id_cod_permiso_accion': {'required': True},
                'fecha_accion': {'required': True},
                'subsistema': {'required': True},
                'dirip': {'required': True},
                'descripcion': {'required': True},
            }




        







