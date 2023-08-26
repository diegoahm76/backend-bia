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
from datetime import datetime, date, timedelta
 

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
        monto_total = sum(float(cartera["monto_inicial"]) for cartera in carteras)
        intereses_total = sum(cartera["valor_intereses"] for cartera in carteras)
        monto_total_con_intereses = monto_total + intereses_total
        return monto_total, intereses_total, monto_total_con_intereses
        
    
    def cartera_selecionada(self, id_facilidad_pago, fecha):
        
        facilidad_pago = FacilidadesPago.objects.get(id=id_facilidad_pago)
        if not facilidad_pago:
            raise NotFound("No existe facilidad de pagos relacionada con la informacion ingresada")

        deudor = Deudores.objects.get(id=facilidad_pago.id_deudor.id)

        if not deudor:
            raise NotFound("No existe deudor con la informacion ingresada")
        
        cartera_ids = DetallesFacilidadPago.objects.filter(id_facilidad_pago=facilidad_pago.id)
        ids_cartera = [int(cartera_id.id_cartera.id) for cartera_id in cartera_ids if cartera_id]
        cartera_seleccion = Cartera.objects.filter(id__in=ids_cartera)

        obligaciones = self.serializer_class(cartera_seleccion, many=True).data


        for obligacion in obligaciones:
            monto_inicial = float(obligacion["monto_inicial"]) 
            dias_mora = 0
            valor_intereses = 0

            if fecha:
                fecha_final = fecha
                fecha_inicio_mora_str = obligacion["inicio"]
                fecha_inicio_mora = datetime.strptime(fecha_inicio_mora_str, '%Y-%m-%d').date()
                dias_mora = (fecha_final - fecha_inicio_mora).days
            
            if dias_mora != 0:
                valor_intereses = (0.12 / 360 * monto_inicial) * dias_mora

            obligacion['dias_mora'] = dias_mora
            obligacion['valor_intereses'] = valor_intereses
            obligacion['valor_capital_intereses'] = monto_inicial + valor_intereses


        monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(obligaciones)
 
        data = {
            'obligaciones': obligaciones,
            'total_valor_capital': monto_total,
            'total_intereses': intereses_total,
            'total_valor_capital_con_intereses': monto_total_con_intereses
        }
        return data


class CarteraSeleccionadaDeudorListaViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_facilidad_pago):

        try:
            facilidad = FacilidadesPago.objects.get(id=id_facilidad_pago)
        except FacilidadesPago.DoesNotExist:
            raise NotFound('No se encontraron resultados.')
        
        instancia_obligaciones = CarteraSeleccionadaListViews()
        response_data = instancia_obligaciones.cartera_selecionada(facilidad.id, facilidad.fecha_abono)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')
        

class CarteraSeleccionadaModificadaDeudorListaViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_facilidad_pago):
        fecha_final_str = str(self.request.query_params.get('fecha_final', ''))
        fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()

        try:
            facilidad = FacilidadesPago.objects.get(id=id_facilidad_pago)
        except FacilidadesPago.DoesNotExist:
            raise NotFound('No se encontraron resultados.')
        
        instancia_obligaciones = CarteraSeleccionadaListViews()
        response_data = instancia_obligaciones.cartera_selecionada(facilidad.id, fecha_final)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')
        

class PlanPagosCarteraListaViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_facilidad_pago):
        fecha_final_str = str(self.request.query_params.get('fecha_final', ''))
        fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()

        try:
            facilidad = FacilidadesPago.objects.get(id=id_facilidad_pago)
        except FacilidadesPago.DoesNotExist:
            raise NotFound('No se encontraron resultados.')
        
        instancia_cartera = CarteraSeleccionadaListViews()
        data_cartera = instancia_cartera.cartera_selecionada(facilidad.id, fecha_final)

        instancia_cartera_modificada = CarteraSeleccionadaListViews()
        data_cartera_modificada = instancia_cartera_modificada.cartera_selecionada(facilidad.id, fecha_final)

        response_data = {
            'data_cartera':data_cartera,
            'data_cartera_modificada':data_cartera_modificada
        }

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')



class ProyeccionPlanPagosView(generics.ListAPIView):
    serializer_class = "ddsd"