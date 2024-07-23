from django.db import connection
from django.forms import ValidationError
from recaudo.models.base_models import RangosEdad

from recaudo.models.cobros_models import (
    Cartera,
    ConceptoContable
)
from recaudo.models.extraccion_model_recaudo import Rt25Municipio, Rt954Cobro, Rt956FuenteHid, Rt970Tramite, Rt980Tua, Rt982Tuacaptacion, RtClaseUsoAgua, T920Expediente, T971TramiteTercero, T972TramiteUbicacion, T973TramiteFteHidTra, Tercero
from recaudo.models.liquidaciones_models import (
    Deudores,
    Expedientes
)
from recaudo.models.procesos_models import CategoriaAtributo, EtapasProceso, TiposAtributos
from recaudo.serializers.cobros_serializers import (
    CarteraCompararSerializer,
    CarteraGeneralSerializer,
    CarteraPostSerializer,
    ConceptoContableSerializer,
    EtapasSerializer,
    RangosSerializer,
    SubEtapasSerializer,
    TiposAtributosSerializer)
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
        queryset = self.get_queryset().order_by('-fecha_facturacion')
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
        if identificacion:
            deudores = deudores.filter(id_persona_deudor_pymisis__t03nit__icontains=identificacion) | deudores.filter(id_persona_deudor__numero_documento__icontains = identificacion)

        if nombres:
            deudores = deudores.filter(id_persona_deudor__primer_nombre__icontains=nombres) | deudores.filter(id_persona_deudor__segundo_nombre__icontains=nombres) | deudores.filter(id_persona_deudor_pymisis__t03nombre__icontains=nombres)

        if apellidos:
            deudores = deudores.filter(id_persona_deudor__primer_apellido__icontains=apellidos) | deudores.filter(id_persona_deudor__segundo_apellido__icontains=apellidos) | deudores.filter(id_persona_deudor_pymisis__t03nombre__icontains=apellidos)
        

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

        data_cartera = []

        numeros_factura_existentes = {item['numero_factura'] for item in cartera.data}
        print('numeros_factura_existentes', numeros_factura_existentes)

        data_cartera = [item_vcartera for item_vcartera in results_vcartera if item_vcartera['numfactura'] not in numeros_factura_existentes]

        return data_cartera

    def insertar_cartera(self, cartera):
        data_list = []
        for item_cartera in cartera:
            #print(item_cartera)
            data = {
                'numero_factura': item_cartera['numfactura'],
                'nombre': item_cartera['nombredeudor'],
                'dias_mora': item_cartera['diasmora'] if item_cartera['diasmora'] else 0,
                'valor_intereses': item_cartera['saldointeres'],
                'valor_sancion': 0,
                'inicio': item_cartera['cortedesde'] if item_cartera['cortedesde'] else None,
                'fin': item_cartera['cortehasta'] if item_cartera['cortehasta'] else None,
                #'codigo_contable': item_cartera['cuentacontable'],
                'fecha_facturacion': item_cartera['fechafact'],
                'fecha_notificacion': item_cartera['fechanotificacion'],
                'fecha_ejecutoriado': item_cartera['fechaenfirme'],
                'numero_factura': item_cartera['numfactura'],
                'monto_inicial': item_cartera['saldocapital'],
                'num_resolucion': item_cartera['numresolucion'],
                'tipo_cobro': item_cartera['tiporenta'],
                'caudal_concesionado': item_cartera['caudalconcesionado'] if item_cartera['caudalconcesionado'] else None,
                #'tipo_agua': item_cartera['claseusoagua'] if item_cartera['claseusoagua'] else None,
                'tipo_renta': item_cartera['tiporenta'],
            }
            deudor = Deudores.objects.filter(id_persona_deudor_pymisis__t03nit=item_cartera['nit']).first()
            if deudor:
                data['id_deudor'] = deudor.id
            else:
                tercero = Tercero.objects.filter(t03nit=item_cartera['nit']).first()
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
            elif item_cartera['cuentacontable'] == '' or item_cartera['cuentacontable'] == None:
                cuenta_contable = '0'
            else:
                cuenta_contable = '0'


            concepto = ConceptoContable.objects.filter(codigo_contable=cuenta_contable).first()
            if concepto:
                data['codigo_contable'] = concepto.id
            else:
                concepto = ConceptoContable.objects.create(
                    codigo_contable=cuenta_contable
                )
                data['codigo_contable'] = concepto.id
                

            data_list.append(data)
        cartera = self.serializer_class(data=data_list, many=True)
        if cartera.is_valid():
            cartera.save()
        else:
            print(cartera.errors)
            print('else')
            return 'Error al guardar la cartera'
        return cartera
    

class RangosGetView(generics.ListAPIView):
    queryset = RangosEdad.objects.all()
    serializer_class = RangosSerializer

    def get(self, request):
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
class ConceptoContableGetView(generics.ListAPIView):
    queryset = ConceptoContable.objects.all()
    serializer_class = ConceptoContableSerializer

    def get(self, request):
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
class EtapasGetView(generics.ListAPIView):
    queryset = EtapasProceso.objects.all()
    serializer_class = EtapasSerializer

    def get(self, request):
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
class SubEtapasGetView(generics.ListAPIView):
    queryset = CategoriaAtributo.objects.all()
    serializer_class = SubEtapasSerializer

    def get(self, request, id_etapa):
        queryset = self.get_queryset().filter(id_etapa=id_etapa)

        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
class TiposAtributosGetView(generics.ListAPIView):
    queryset = TiposAtributos.objects.all()
    serializer_class = TiposAtributosSerializer

    def get(self, request):
        queryset = self.get_queryset()

        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

class InfoTuaView(generics.ListAPIView):

    def get(self, request, id_expediente):
        expediente = Expedientes.objects.filter(id=id_expediente).first()

        data = None

        if expediente:
            if expediente.id_expediente_pimisys:
                data = self.pymisis(expediente.id_expediente_pimisys)
            else:
                data = self.bia(expediente.id_expediente_doc)
        else:
            raise ValidationError('Expediente no encontrado')

        return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)
    
    def pymisis(self, expediente):
        tramite = Rt970Tramite.objects.filter(t970codexpediente=expediente.t920codexpediente, t970codtipotramite__in = ['TUAIM', 'TRIM']).first()
        if not tramite:
            raise ValidationError('Tramite no encontrado')
        tramite_tercero = T971TramiteTercero.objects.filter(t971idtramite=tramite.t970idtramite).first()
        titular = Tercero.objects.filter(t03nit=tramite_tercero.t971nit).first()
        tramite_fuente = T973TramiteFteHidTra.objects.filter(t973idtramite=tramite.t970idtramite).first()
        fuente_hidrica = None
        municipio = None
        clase_uso_agua = None
        if tramite_fuente:
            fuente_hidrica = Rt956FuenteHid.objects.filter(t956codfuentehid=tramite_fuente.t973codfuentehid).first()
        tua = Rt980Tua.objects.filter(t980idtramite=tramite.t970idtramite).first()
        tua_captacion = Rt982Tuacaptacion.objects.filter(t982numtua=tua.t980numtua).first()
        if tua_captacion:
            clase_uso_agua = RtClaseUsoAgua.objects.filter(cod_clase_uso_agua=tua_captacion.t982codclaseusoagua).first()
        cobro = Rt954Cobro.objects.filter(t954idcobro=tua.t980idcobro).first()
        tramite_ubicacion = T972TramiteUbicacion.objects.filter(t972idtramite=tramite.t970idtramite).first()
        if tramite_ubicacion:
            municipio = Rt25Municipio.objects.filter(t25codmpio=tramite_ubicacion.t972codubicacion).first()
        data = {
            'nit_titular': titular.t03nit,
            'nombre_titular': titular.t03nombre,
            'direccion_titular': titular.t03direccion,
            'telefono_titular': titular.t03telefono,
            'representante_legal': cobro.t954replegalimportad if cobro.t954replegalimportad else None,
            'expediente': expediente.t920codexpediente,
            'num_resolucion': tramite.t970numresolperm,
            'fecha_resolucion': tramite.t970fecharesperm,
            'nombre_fuente_hidrica': fuente_hidrica.t956nombre if fuente_hidrica else None,
            'caudal_concesionado': tramite.t970tuacaudalconcesi,
            'clase_uso_agua': clase_uso_agua.nombre if clase_uso_agua else None,
            'factor_regional': cobro.t954tuafr,
            'predio': tramite.t970tuapredio,
            'municipio': municipio.t25nombre if municipio else None,

        }
        return data

    def bia(self):
        pass
        