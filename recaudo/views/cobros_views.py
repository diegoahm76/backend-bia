from django.db import connection
from recaudo.models.cobros_models import (
    Cartera,
    ConceptoContable,
    VistaCarteraTua
)
from recaudo.models.extraccion_model_recaudo import T920Expediente, Tercero
from recaudo.models.liquidaciones_models import (
    Deudores,
    Expedientes
)
from recaudo.serializers.cobros_serializers import (
    CarteraCompararSerializer,
    CarteraGeneralSerializer,
    CarteraPostSerializer,
    VistaCarteraTuaSerializer
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class CarteraGeneralView(generics.ListAPIView):
    queryset = Cartera.objects.all()
    serializer_class = CarteraGeneralSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10

    def get(self, request):
        self.pagination_class.default_limit = self.page_size
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({'success': True, 'data': serializer.data})
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class CarteraDeudoresView(generics.ListAPIView):
    serializer_class = CarteraGeneralSerializer

    def get(self, request):
        nombres = request.GET.get('nombres', None)
        apellidos = request.GET.get('apellidos', None)
        identificacion = request.GET.get('identificacion', None)

        deudores = Deudores.objects.all()
        if nombres is not None:
            deudores = deudores.filter(nombres__contains=nombres)

        if apellidos is not None:
            deudores = deudores.filter(apellidos__contains=apellidos)

        if identificacion is not None:
            deudores = deudores.filter(identificacion__contains=identificacion)


        queryset = Cartera.objects.filter(id_deudor__in=deudores)
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

class VistaCarteraTuaView(generics.ListAPIView):
    #queryset = VistaCarteraTua.objects.only('fecha', 'cod_cia', 'tipo_renta', 'cuenta_contable', 'nit', 'nombre_deudor', 'fecha_fac', 'fecha_notificacion', 'fecha_en_firme', 'corte_desde', 'corte_hasta', 'num_factura', 'num_liquidacion', 'periodo', 'agno', 'expediente', 'num_resolucion', 'recurso', 'doc_auto', 'saldo_capital', 'saldo_intereses', 'dias_mora')
    serializer_class = CarteraPostSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10

    def get(self, request):
        self.pagination_class.default_limit = self.page_size
        queryset = self.get_results()
        cartera = self.insertar_cartera(queryset)
        print('cartera', cartera)
        #print(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            #serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({'success': True, 'data': page})
        #serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': queryset}, status=status.HTTP_200_OK)
    
    def get_results(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM public.vcarterabiatua")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        results_vcartera = []
        for row in rows:
            results_vcartera.append(dict(zip(columns, row)))

        cartera = Cartera.objects.all()
        cartera = CarteraCompararSerializer(cartera, many=True)

        i = 0
        data_cartera = []
        for item_vcartera in results_vcartera:
            if not item_vcartera['numfactura'] in cartera.data[i]['numero_factura']:
                data_cartera.append(item_vcartera)
            i += 1
        return data_cartera

    def insertar_cartera(self, cartera):
        for item_cartera in cartera:
            print(item_cartera)
            data = {
                'numero_factura': item_cartera['numfactura'],
                'nombre': item_cartera['nombredeudor'],
                'dias_mora': item_cartera['diasmora'] if item_cartera['diasmora'] else 0,
                'valor_intereses': item_cartera['saldointeres'],
                'valor_sancion': 0,
                'inicio': item_cartera['cortedesde'],
                'fin': item_cartera['cortehasta'],
                #'codigo_contable': item_cartera['cuentacontable'],
                'fecha_facturacion': item_cartera['fechafact'],
                'fecha_notificacion': item_cartera['fechanotificacion'],
                'fecha_ejecutoriado': item_cartera['fechaenfirme'],
                'numero_factura': item_cartera['numfactura'],
                'monto_inicial': item_cartera['saldocapital'],
                'tipo_cobro': item_cartera['tiporenta'],
                'tipo_renta': item_cartera['tiporenta'],
                'id_rango': 1
            
            }
            print('holaaaa')
            deudor = Deudores.objects.filter(id_persona_deudor_pymisis__t03nit=item_cartera['nit']).first()
            print('no pase')
            if deudor:
                data['id_deudor'] = deudor.id
            else:
                tercero = Tercero.objects.filter(t03nit=item_cartera['nit']).first()
                print('tercero', tercero)
                deudor = Deudores.objects.create(
                    id_persona_deudor_pymisis=tercero
                )
                data['id_deudor'] = deudor.id

            expediente = Expedientes.objects.filter(id_expediente_pimisys__t920codexpediente=item_cartera['expediente']).first()
            if expediente:
                data['id_expediente'] = expediente.id
            else:
                expediente_pimisys = T920Expediente.objects.filter(t920codexpediente=item_cartera['expediente']).first()
                expediente = Expedientes.objects.create(
                    id_deudor=deudor,
                    id_expediente_pimisys=expediente_pimisys
                )
                data['id_expediente'] = expediente.id

        
            if item_cartera['cuentacontable']:
                cuenta_contable = item_cartera['cuentacontable']
            else:
                cuenta_contable = '0'


            concepto = ConceptoContable.objects.filter(codigo_contable=cuenta_contable).first()
            if concepto:
                data['codigo_contable'] = concepto.id
            else:
                concepto = ConceptoContable.objects.create(
                    codigo_contable=item_cartera['cuentacontable']
                )
                data['codigo_contable'] = concepto.id
                
            print('cartera: ', data)
            cartera = self.serializer_class(data=data)
            #cartera = CarteraCompararSerializer(data=item_cartera)
            if cartera.is_valid():
                cartera.save()
                print('Cartera guardada')
            else:
                print(cartera.errors)
                print('else')
                return 'Error al guardar la cartera'
        return cartera
        