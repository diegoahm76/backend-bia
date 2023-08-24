from recaudo.models.facilidades_pagos_models import FacilidadesPago, DetallesFacilidadPago
from recaudo.serializers.planes_pagos_serializers import (
    TipoPagoSerializer, 
    PlanPagosSerializer, 
    ResolucionesPlanPagoSerializer,
    VisualizacionCarteraSelecionadaSerializer,
    FacilidadPagoDatosPlanSerializer
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
            return Response({'success': True, 'detail': 'Plan de plagos relacionado', 'data': serializer.data}, status=status.HTTP_200_OK)
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
            return Response({'success': True, 'detail': 'Resoluciones', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No existe resolucion para la facilidad de pago relacionada con la información dada'})


class FacilidadPagoDatosPlanView(generics.ListAPIView):
    serializer_class = FacilidadPagoDatosPlanSerializer

    def get_datos_facilidad(self, id_facilidad_pago):

        facilidad_pago = FacilidadesPago.objects.filter(id=id_facilidad_pago).first()
        if not facilidad_pago:
            raise NotFound("No existe facilidad de pago relacionada con la información dada")
        
        serializer = self.serializer_class(facilidad_pago, many=False)
        
        return serializer.data
        
    def get(self, request, id_facilidad_pago):
        
        instancia_datos_facilidad = self.get_datos_facilidad(id_facilidad_pago)

        if instancia_datos_facilidad:
            return Response({'success': True, 'detail': 'Datos de la facilidad de pago relacionado', 'data': instancia_datos_facilidad}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No existe facilidad de pago relacionada con la información dada'})


class CarteraSeleccionadaListViews(generics.ListAPIView):
    serializer_class = VisualizacionCarteraSelecionadaSerializer

    def get_monto_total(self, carteras):
        monto_total = 0
        intereses_total = 0
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        monto_total_con_intereses = monto_total + intereses_total
        return monto_total, intereses_total, monto_total_con_intereses
    
    def cartera_selecionada(self, id_facilidad_pago):
        
        facilidad_pago = FacilidadesPago.objects.get(id=id_facilidad_pago)
        if not facilidad_pago:
            raise NotFound("No existe facilidad de pagos relacionada con la informacion ingresada")

        deudor = Deudores.objects.get(id=facilidad_pago.id_deudor.id)

        if not deudor:
            raise NotFound("No existe deudor con la informacion ingresada")
        
        cartera_ids = DetallesFacilidadPago.objects.filter(id_facilidad_pago=facilidad_pago.id)
        ids_cartera = [int(cartera_id.id_cartera.id) for cartera_id in cartera_ids if cartera_id]
        cartera_seleccion = Cartera.objects.filter(id__in=ids_cartera)
        serializer = self.serializer_class(cartera_seleccion, many=True)
        monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(cartera_seleccion)
 
        data = {
            'numero_identificacion': deudor.identificacion,
            'email': deudor.email,
            'obligaciones': serializer.data,
            'monto_total': monto_total,
            'intereses_total': intereses_total,
            'monto_total_con_intereses': monto_total_con_intereses
        }
        return data


    # def get_obligaciones(self, ids_cartera):
    #     instancia_obligaciones = CarteraDeudorListViews()
    #     carteras = Cartera.objects.filter(id__in=ids_cartera)
    #     serializer = CarteraSerializer(carteras, many=True)
    #     monto_total, intereses_total, monto_total_con_intereses = instancia_obligaciones.get_monto_total(carteras)

    #     data = {
    #         'obligaciones': serializer.data,
    #         'monto_total': monto_total,
    #         'intereses_total': intereses_total,
    #         'monto_total_con_intereses': monto_total_con_intereses
    #     }
    #     return data

    # def get(self, request):
        
    #     ids_param = self.request.query_params.get('ids')
    #     ids = [int(id_str) for id_str in ids_param.strip('[]').split(',') if id_str]
    #     cartera_data = self.get_obligaciones(ids)

    #     return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': cartera_data}, status=status.HTTP_200_OK)
    


class ConsultaCarteraDeudoresViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_facilidad_pago):

        try:
            facilidad = FacilidadesPago.objects.get(id=id_facilidad_pago)
        except FacilidadesPago.DoesNotExist:
            raise NotFound('No se encontraron resultados.')
        
        instancia_obligaciones = CarteraSeleccionadaListViews()
        response_data = instancia_obligaciones.cartera_selecionada(facilidad.id)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')
        