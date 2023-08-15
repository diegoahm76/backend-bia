from recaudo.models.facilidades_pagos_models import FacilidadesPago
from recaudo.serializers.planes_pagos_serializers import TipoPagoSerializer, PlanPagosSerializer
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.planes_pagos_models import PlanPagos

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PlanPagosValidationView(generics.RetrieveAPIView):
    serializer_class = PlanPagosSerializer

    def get_validacion(self, id_facilidad_pago):

        if not FacilidadesPago.objects.filter(id=id_facilidad_pago).exists():
            raise NotFound("No existe facilidad de pago relacionada con la informacion dada")
        
        validado = PlanPagos.objects.filter(id_facilidad_pago=id_facilidad_pago).exists()
        return validado
        
    def get(self, request, id_facilidad_pago):
        instancia_validation = self.get_validacion(id_facilidad_pago)

        if instancia_validation:
            serializer = self.serializer_class(instancia_validation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotFound("No existe plan de pagos para la facilidad de pago relacionada con la informacion dada")
