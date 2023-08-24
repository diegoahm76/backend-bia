from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
class ConfigTiposRadicadoAgnoUpDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTiposRadicadoAgno
        fields = '__all__'
        validators =[
                    UniqueTogetherValidator(queryset=ConfigTiposRadicadoAgno.objects.all(),
                    fields=['agno_radicado', 'cod_tipo_radicado'],
                    message='Ya existe una configuracion para este radicado'),
                    UniqueTogetherValidator(queryset=ConfigTiposRadicadoAgno.objects.all(),
                    fields=['agno_radicado','prefijo_consecutivo'],
                    message='Ya existe una configuracion con este prefijo')
                    ]

class ConfigTiposRadicadoAgnoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigTiposRadicadoAgno
        fields = '__all__'