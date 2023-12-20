from recaudo.models.tasa_retributiva_vertimiento_models import documento_formulario_recuado
from rest_framework import serializers



class documento_formulario_recuados_serializer(serializers.ModelSerializer):
    class Meta:
        model = documento_formulario_recuado
        fields = '__all__'

