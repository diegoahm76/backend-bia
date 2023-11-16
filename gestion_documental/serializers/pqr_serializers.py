from rest_framework import serializers

from gestion_documental.models.radicados_models import PQRSDF, AsignacionPQR, ComplementosUsu_PQR, EstadosSolicitudes, SolicitudDeDigitalizacion, TiposPQR, MediosSolicitud

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
    



 ########################## MEDIOS DE SOLICITUD ##########################

class MediosSolicitudCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'


class MediosSolicitudSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

class MediosSolicitudUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosSolicitud
        fields = '__all__'

