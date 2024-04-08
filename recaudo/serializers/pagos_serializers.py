from rest_framework import serializers
from recaudo.models.pagos_models import (
    Pagos
)

class InicioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'