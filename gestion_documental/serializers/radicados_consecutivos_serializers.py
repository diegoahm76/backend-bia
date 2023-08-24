from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from seguridad.models import Personas
class ConfigTiposRadicadoAgnoUpDateSerializer(serializers.ModelSerializer):
    #fecha_consecutivo_actual = serializers.ReadOnlyField()
    #id_persona_config_implementacion = serializers.PrimaryKeyRelatedField(queryset=Personas.objects.all())
    #id_persona_config_implementacion = serializers.PrimaryKeyRelatedField(queryset=Personas.objects.all())   
    #fecha_inicial_config_implementacion=serializers.ReadOnlyField()   
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