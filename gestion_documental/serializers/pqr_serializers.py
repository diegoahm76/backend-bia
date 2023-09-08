from rest_framework import serializers

from gestion_documental.models.radicados_models import TiposPQR

class TiposPQRGetSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()
    
class TiposPQRUpdateSerializer(serializers.ModelSerializer):
    cod_tipo_pqr_legible = serializers.SerializerMethodField()
    
    cod_tipo_pqr = serializers.ReadOnlyField(default=None)
    nombre = serializers.ReadOnlyField(default=None)
    class Meta:
        model = TiposPQR
        fields = '__all__'

    def get_cod_tipo_pqr_legible(self, obj):
        return obj.get_cod_tipo_pqr_display()