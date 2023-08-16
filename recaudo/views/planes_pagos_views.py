from recaudo.models.facilidades_pagos_models import FacilidadesPago
from recaudo.serializers.planes_pagos_serializers import (
    TipoPagoSerializer, 
    PlanPagosSerializer, 
    ResolucionesPlanPagoSerializer,
    VisualizacionCarteraSelecionadaSerializer
    )
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.planes_pagos_models import (
    PlanPagos, 
    ResolucionesPlanPago
)
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.cobros_models import Cartera
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
            return Response({'success': False, 'detail': 'No existe resolucion para la facilidad de pago relacionada con la información dada'})


class ObligacionesDeudorListViews(generics.ListAPIView):
    serializer_class = VisualizacionCarteraSelecionadaSerializer

    def get_monto_total(self, carteras):
        monto_total = 0
        intereses_total = 0
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        monto_total_con_intereses = monto_total + intereses_total
        return monto_total, intereses_total, monto_total_con_intereses
    
    def cartera_selecionada(self, id):

        deudor = Deudores.objects.get(id=id)
        if not deudor:
            raise NotFound("No existe deudor con la informacion ingresada")
        
        facilidad = FacilidadesPago.objects.filter(id_deudor=deudor.id).exists()
        cartera = Cartera.objects.filter(id_deudor=deudor)
        serializer = self.serializer_class(cartera, many=True)
        monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(cartera)
        data = {
            'numero_identificacion': deudor.identificacion,
            'email': deudor.email,
            'obligaciones': serializer.data,
            'monto_total': monto_total,
            'intereses_total': intereses_total,
            'monto_total_con_intereses': monto_total_con_intereses,
            'tiene_facilidad' : facilidad
        }
        return data


class ListadoObligacionesViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        numero_identificacion = user.persona.numero_documento
        try:
            deudor = Deudores.objects.get(identificacion=numero_identificacion)
        except Deudores.DoesNotExist:
            raise NotFound('No se encontró un objeto deudor para este usuario.')
        
        instancia_obligaciones = ObligacionesDeudorListViews()
        response_data = instancia_obligaciones.cartera_selecionada(deudor.id)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')  