from rest_framework import serializers
from seguridad.serializers.personas_serializers import PersonasSerializer
from transversal.models.entidades_models import ConfiguracionEntidad, SucursalesEmpresas


class ConfiguracionEntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEntidad
        fields = '__all__'

        
class SucursalesEmpresasSerializer(serializers.ModelSerializer):    
    class Meta:
        model = SucursalesEmpresas
        fields = '__all__'
        

class SucursalesEmpresasPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SucursalesEmpresas
        fields = '__all__'
        extra_kwargs = {
                'id_persona_empresa': {'required': True},
                'descripcion_sucursal': {'required': True},
                'direccion': {'required': True},
            }
        
class SucursalesEmpresasPutSerializer(serializers.ModelSerializer):    
    class Meta:
        model = SucursalesEmpresas
        fields = ['descripcion_sucursal','direccion','direccion_sucursal_georeferenciada','municipio','pais_sucursal_exterior',
                  'direccion_notificacion','direccion_notificacion_referencia','municipio_notificacion','email_sucursal',
                  'telefono_sucursal','es_principal','activo']
        
        

