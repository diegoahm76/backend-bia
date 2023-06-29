from rest_framework import serializers
from transversal.models.organigrama_models import Organigramas
from transversal.models.lideres_models import LideresUnidadesOrg

class BusquedaAvanzadaOrganigramasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organigramas
        fields = '__all__'
        
class GetListLideresAsignadosSerializer(serializers.ModelSerializer):
    nombre_organigrama = serializers.ReadOnlyField(source='id_unidad_organizacional.id_organigrama.nombre', default=None)
    version_organigra = serializers.ReadOnlyField(source='id_unidad_organizacional.id_organigrama.version', default=None)
    codigo_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.codigo', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    tipo_documento = serializers.ReadOnlyField(source='id_persona.tipo_documento', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona.numero_documento', default=None)
    nombre_completo = serializers.SerializerMethodField()
    
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.primer_nombre, obj.segundo_nombre, obj.primer_apellido, obj.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo.upper()
    
    class Meta:
        model = LideresUnidadesOrg
        fields = '__all__'