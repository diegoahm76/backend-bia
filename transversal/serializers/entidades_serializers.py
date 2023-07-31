from rest_framework import serializers
from seguridad.serializers.personas_serializers import PersonasSerializer
from transversal.models.entidades_models import ConfiguracionEntidad, HistoricoPerfilesEntidad, SucursalesEmpresas
from seguridad.models import Personas



class ConfiguracionEntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEntidad
        fields = '__all__'


class PersonaEntidadCormacarenaGetSerializer(serializers.ModelSerializer):
    nombre_tipo_documento = serializers.ReadOnlyField(source='tipo_documento.nombre', default=None)
    
    class Meta:
        model = Personas
        fields = ('id_persona', 'tipo_documento', 'numero_documento', 'nombre_tipo_documento', 'digito_verificacion', 'razon_social')
        
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
        
        

class HistoricoPerfilesEntidadGetSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = HistoricoPerfilesEntidad
        fields = '__all__'
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_perfil_histo.primer_nombre
        primer_apellido = obj.id_persona_perfil_histo.primer_apellido
        return f'{primer_nombre} {primer_apellido}'