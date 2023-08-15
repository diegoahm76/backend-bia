from recaudo.models.facilidades_pagos_models import FacilidadesPago
from recaudo.serializers.planes_pagos_serializers import TipoPagoSerializer, PlanPagosSerializer, ResolucionesPlanPagoSerializer
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.planes_pagos_models import (
    PlanPagos, 
    ResolucionesPlanPago
)
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
 

class PlanPagosValidationView(generics.RetrieveAPIView):
    serializer_class = PlanPagosSerializer
    permission_classes = [IsAuthenticated]

    def get_validacion(self, id_facilidad_pago):
        
        if not FacilidadesPago.objects.filter(id=id_facilidad_pago).exists():
            raise NotFound("No existe facilidad de pago relacionada con la información dada")
        
        return PlanPagos.objects.filter(id_facilidad_pago=id_facilidad_pago).first()
        
    def get(self, request, id_facilidad_pago):
        instancia_validacion = self.get_validacion(id_facilidad_pago)

        if instancia_validacion:
            serializer = self.serializer_class(instancia_validacion, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No existe plan de pagos para la facilidad de pago relacionada con la información dada'})


class PlanPagosResolucionValidationView(generics.RetrieveAPIView):
    serializer_class = ResolucionesPlanPagoSerializer
    permission_classes = [IsAuthenticated]

    def get_validacion(self, id_facilidad_pago):
        
        if not FacilidadesPago.objects.filter(id=id_facilidad_pago).exists():
            raise NotFound("No existe facilidad de pago relacionada con la información ingresada")
        
        plan_pago = PlanPagos.objects.filter(id_facilidad_pago=id_facilidad_pago).first()

        if not plan_pago:
            raise NotFound("No existe plan de pagos relacionada con la facilidad de pagos ingresada")
        
        return ResolucionesPlanPago.objects.filter(id_plan_pago=plan_pago.id)
        
    def get(self, request, id_facilidad_pago):
        instancia_validacion = self.get_validacion(id_facilidad_pago)

        if instancia_validacion.exists():
            serializer = self.serializer_class(instancia_validacion, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No existe plan de pagos para la facilidad de pago relacionada con la información dada'})

