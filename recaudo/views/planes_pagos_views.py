from recaudo.models.facilidades_pagos_models import FacilidadesPago, DetallesFacilidadPago
from recaudo.serializers.planes_pagos_serializers import (
    TipoPagoSerializer, 
    PlanPagosSerializer, 
    ResolucionesPlanPagoSerializer,
    PlanPagosCuotasSerializer,
    VisualizacionCarteraSelecionadaSerializer,
    FacilidadPagoDatosPlanSerializer
    )
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.planes_pagos_models import (
    PlanPagos, 
    ResolucionesPlanPago,
    PlanPagosCuotas
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
        
        instancia_plan = PlanPagosListGetView()
        plan_pagos = instancia_plan.get_plan_pagos_cuotas(id_facilidad_pago)
        
        return plan_pagos
        
    def get(self, request, id_facilidad_pago):
        instancia_validacion = self.get_validacion(id_facilidad_pago)

        if instancia_validacion:
            return Response({'success': True, 'detail': 'Plan de plagos relacionado', 'data': instancia_validacion}, status=status.HTTP_200_OK)
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
            monto_inicial = round(float(obligacion["monto_inicial"]),2)
            dias_mora = 0
            valor_intereses = 0

            if fecha:
                fecha_final = fecha
                fecha_inicio_mora_str = obligacion["inicio"]
                fecha_inicio_mora = datetime.strptime(fecha_inicio_mora_str, '%Y-%m-%d').date()
                dias_mora = (fecha_final - fecha_inicio_mora).days
            
            if dias_mora != 0:
                valor_intereses = round(((0.12 / 360 * monto_inicial) * dias_mora),2)

            obligacion['dias_mora'] = dias_mora
            obligacion['valor_intereses'] = valor_intereses
            obligacion['valor_capital_intereses'] = round((monto_inicial + valor_intereses),2)


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
            raise NotFound("No existe facilidad de pagos relacionada con la informacion ingresada")
        
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
        

class PlanPagosAmortizacionListaViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_facilidad_pago):
        fecha_final_str = str(self.request.query_params.get('fecha_final', ''))
        cuotas = int(self.request.query_params.get('cuotas', ''))
        periodicidad = int(self.request.query_params.get('periodicidad', ''))
        fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()

        try:
            facilidad = FacilidadesPago.objects.get(id=id_facilidad_pago)
        except FacilidadesPago.DoesNotExist:
            raise NotFound("No existe facilidad de pagos relacionada con la informacion ingresada")
        
        # TABLA 1
        instancia_cartera = CarteraSeleccionadaListViews()
        data_cartera = instancia_cartera.cartera_selecionada(facilidad.id, facilidad.fecha_abono)
        # TABLA 2
        instancia_cartera_modificada = CarteraSeleccionadaListViews()
        data_cartera_modificada = instancia_cartera_modificada.cartera_selecionada(facilidad.id, fecha_final)

        # RESUMEN DE LA FACILIDAD
        resumen_inicial = {
            'capital_total': round(data_cartera['total_valor_capital_con_intereses'],2),
            'abono_facilidad': round(float(facilidad.valor_abonado),2)
        }
        # RESUMEN DE LA FACILIDAD
        resumen_facilidad = {
            'saldo_total': round(data_cartera_modificada['total_valor_capital'],2),
            'intreses_mora': round(data_cartera_modificada['total_intereses'],2),
            'deuda_total':round((data_cartera_modificada['total_valor_capital']+data_cartera_modificada['total_intereses']),2)
        }
        capital_cuotas = round((data_cartera_modificada['total_valor_capital'] / cuotas),2)
        interes_cuotas = round((data_cartera_modificada['total_intereses'] / cuotas),2)
        # DISTRIBUCION CUOTA
        distribucion_cuota= {
            'capital_cuotas': capital_cuotas,
            'interes_cuotas': interes_cuotas,
            'total_cuota': round((capital_cuotas + interes_cuotas),2)
        }

        proyeccion_plan = []
        fecha_plan = facilidad.fecha_abono

        for cuota in range(cuotas):
            fecha_plan = fecha_plan + timedelta(days=periodicidad * 30)
            proyeccion_plan.append({
                'num_cuota':cuota+1,
                'fecha_pago':fecha_plan,
                'capital':capital_cuotas,
                'interes':interes_cuotas,
                'cuota': round((capital_cuotas + interes_cuotas),2)
                })

        response_data = {
            'data_cartera':data_cartera,
            'data_cartera_modificada':data_cartera_modificada,
            'resumen_inicial':resumen_inicial,
            'resumen_facilidad':resumen_facilidad,
            'distribucion_cuota':distribucion_cuota,
            'proyeccion_plan':proyeccion_plan
        }

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')


class PlanPagosCuotasCreateView(generics.CreateAPIView):
    serializer_class = PlanPagosCuotasSerializer

    def crear_plan_pagos_cuotas(self, data):
        id_plan_pago = data['id_plan_pago']
        plan_pago = PlanPagos.objects.filter(id=id_plan_pago).first()

        if not plan_pago:
            raise NotFound("No existe plan de pagos relacionada con la informacion ingresada")
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        plan_pagos = serializer.save()

        return plan_pagos
    
    def post(self, request):
        data = request.data
        cuota_ant = None
        plan_pagos_cuotas = []

        for cuota in range(data['nro_cuotas']):
            fecha_plan = fecha_plan + timedelta(days=data['periodicidad'] * 30)
            saldo_pendiente = round(data['saldo_total'] - (data['capital'] * (cuota + 1)), 2)
            data['id_cuota_anterior'] = cuota_ant
            data['saldo_pendiente'] = saldo_pendiente
            instance_cuota = PlanPagosCuotasCreateView()
            cuota_creada = instance_cuota.crear_plan_pagos_cuotas(data)
            cuota_ant = cuota_creada.id
            plan_pagos_cuotas.append(instance_cuota.serializer_class(cuota_creada).data)
    

        if not plan_pagos_cuotas:
            raise ValidationError('No se pudo crear las cuotas del plan de pagos')

        return Response({'success':True, 'detail':'Se crea las cuotas del plan de pagos', 'data':plan_pagos_cuotas}, status=status.HTTP_201_CREATED)


class PlanPagosCreateView(generics.CreateAPIView):
    serializer_class = PlanPagosSerializer

    def crear_plan_pagos(self, data):
        id_facilidad = data['id_facilidad_pago']
        facilidad_pago = FacilidadesPago.objects.filter(id=id_facilidad).first()

        if not facilidad_pago:
            raise NotFound("No existe facilidad de pagos relacionada con la informacion ingresada")
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        plan_pagos = serializer.save()
        plan_cuotas = []
        plan_pagos_data = []

        fecha_plan = plan_pagos.fecha_pago_abono
        capital = round((data['saldo_total']/plan_pagos.nro_cuotas),2)
        intereses = round((data['intreses_mora']/plan_pagos.nro_cuotas),2)
        cuota_ant = None

        for cuota in range(plan_pagos.nro_cuotas):
            fecha_plan = fecha_plan + timedelta(days=plan_pagos.periodicidad * 30)
            saldo_pendiente = round(data['saldo_total'] - (capital * (cuota + 1)), 2)
            
            data_cuota = {
                'id_plan_pago':plan_pagos.id,
                'id_tipo_pago':1,
                'nro_cuota':cuota+1,
                'valor_capital':capital,
                'valor_interes':intereses,
                'monto_cuota': round((capital+intereses),2),
                'fecha_vencimiento':fecha_plan,
                'saldo_pendiente': round((data['saldo_total'] - (capital*(cuota))),2),
                'id_cuota_anterior': cuota_ant
                }
            
            instance_cuota = PlanPagosCuotasCreateView()
            cuota_creada = instance_cuota.crear_plan_pagos_cuotas(data_cuota)
            cuota_ant = cuota_creada.id
            plan_cuotas.append(instance_cuota.serializer_class(cuota_creada).data)

        plan_pagos_data = serializer.data
        plan_pagos_data['cuotas'] = plan_cuotas


        return plan_pagos_data
    
    def post(self, request):
        data = request.data
        user = request.user
        id_funcionario = user.persona.id_persona
        data['id_funcionario'] = id_funcionario
        plan_pagos = self.crear_plan_pagos(data)

        if not plan_pagos:
            raise ValidationError('No se pudo crear el plan de pagos')

        return Response({'success':True, 'detail':'Se crea el plan de pagos', 'data':plan_pagos}, status=status.HTTP_201_CREATED)
    

class PlanPagosCuotasListGetView(generics.ListAPIView):
    serializer_class = PlanPagosCuotasSerializer

    def get_cuotas(self, id_plan_pagos):

        plan_pago = PlanPagos.objects.filter(id=id_plan_pagos).first()

        if not plan_pago:
            raise NotFound("No existe plan de pagos relacionado con la información dada")
        
        plan_pago_cuotas = PlanPagosCuotas.objects.filter(id_plan_pago=plan_pago.id)
        serializer = self.serializer_class(plan_pago_cuotas, many=True)
        data = serializer.data
        
        return data
    
    def get(self, request, id_plan_pagos):
        plan_pago_cuotas = self.get_plan_pagos_cuotas(id_plan_pagos)
        return Response({'success': True, 'detail':'Se muestra los datos del deudor', 'data':plan_pago_cuotas}, status=status.HTTP_200_OK) 


class PlanPagosListGetView(generics.ListAPIView):
    serializer_class = PlanPagosSerializer

    def get_plan_pago(self, plan_pago):
        serializer = self.serializer_class(plan_pago, many=False)
        return serializer.data

    def get_plan_pagos_cuotas(self, id_facilidad_pago):

        facilidad_pago = FacilidadesPago.objects.filter(id=id_facilidad_pago).first()
        if not facilidad_pago:
            raise NotFound("No existe facilidad de pago relacionada con la información dada")

        plan_pago = PlanPagos.objects.filter(id_facilidad_pago=facilidad_pago.id).first()
        if not plan_pago:
            raise NotFound("No existe plan de pagos relacionado con la información dada")
        
        plan_pago_data = self.get_plan_pago(plan_pago)
        instancia_cuota = PlanPagosCuotasListGetView()
        cuotas_data = instancia_cuota.get_cuotas(plan_pago_data['id'])

        reponse_data = {
            'plan_pago':plan_pago_data,
            'cuotas':cuotas_data
        }

        return reponse_data
    
    def get(self, request, id_facilidad_pago):

        facilidad_pago = FacilidadesPago.objects.filter(id=id_facilidad_pago).first()
        if not facilidad_pago:
            raise NotFound("No existe facilidad de pago relacionada con la información dada")
        
        plan_pago_data = self.get_plan_pagos_cuotas(facilidad_pago.id)
        
        return Response({'success': True, 'detail': 'Se encontró el plan de pagos', 'data': plan_pago_data}, status=status.HTTP_200_OK)
