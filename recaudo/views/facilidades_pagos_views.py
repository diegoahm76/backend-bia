from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.pqr_views import RadicadoCreate
from recaudo.serializers.facilidades_pagos_serializers import (
    AvaluosSerializer,
    CarteraSerializer,
    ConsultaCarteraSerializer,
    CumplimientoRequisitosGetSerializer,
    GarantiasFacilidadGetSerializer,
    ListadoDeudoresUltSerializer,
    DeudorDatosSerializer,
    FacilidadesPagoSerializer,
    GarantiasFacilidadSerializer,
    RequisitosActuacionSerializer,
    DetallesBienFacilidadPagoSerializer,
    CumplimientoRequisitosSerializer,
    BienesDeudorSerializer,
    RespuestaSolicitudGetSerializer,
    TipoBienSerializer,
    TipoActuacionSerializer,
    ListadoFacilidadesPagoSerializer,
    FacilidadesPagoFuncionarioPutSerializer,
    FuncionariosSerializer,
    FacilidadPagoGetByIdSerializer,
    BienSerializer,
    RespuestaSolicitudSerializer,
    DetallesFacilidadPagoSerializer,
    ListadoFacilidadesSeguimientoSerializer
)
from recaudo.models.facilidades_pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    GarantiasFacilidad,
    DetallesFacilidadPago,
    RespuestaSolicitud,
    DetallesBienFacilidadPago
)
from recaudo.models.procesos_models import Bienes
from recaudo.models.base_models import TiposBien, TipoActuacion
from recaudo.models.garantias_models import RolesGarantias
from recaudo.models.liquidaciones_models import Deudores, Expedientes
from seguridad.permissions.permissions_recaudo import PermisoActualizarSolicitudFacilidadPago, PermisoCrearSolicitudFacilidadPago
from transversal.models.personas_models import Personas
from transversal.models.base_models import ClasesTerceroPersona
from recaudo.models.cobros_models import Cartera
from datetime import timedelta, date
from django.db.models.functions import Concat
from django.db.models import Q, Value as V
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, date, timedelta
import random
import string

@staticmethod
def get_data_deudor(id_deudor):
    try:
        deudor = Deudores.objects.get(id=id_deudor)
    except Deudores.DoesNotExist:
        raise NotFound('No se encontró ningun registro con el parámetro ingresado')
    
    id_deudor = deudor.id
    id_persona_deudor = deudor.id_persona_deudor if deudor.id_persona_deudor else None
    id_persona_deudor_pymisis = deudor.id_persona_deudor_pymisis if deudor.id_persona_deudor_pymisis else None
    numero_identificacion = deudor.id_persona_deudor.numero_documento if id_persona_deudor else deudor.id_persona_deudor_pymisis.t03nit

    if id_persona_deudor:
        if id_persona_deudor.razon_social:
            nombre_completo = id_persona_deudor.razon_social
            email = id_persona_deudor.email
        else:
            nombre_completo = ' '.join(filter(None, [id_persona_deudor.primer_nombre, id_persona_deudor.segundo_nombre, id_persona_deudor.primer_apellido, id_persona_deudor.segundo_apellido]))
            email = id_persona_deudor.email
    elif id_persona_deudor_pymisis:
        nombre_completo = deudor.id_persona_deudor_pymisis.t03nombre
        email = deudor.id_persona_deudor_pymisis.t03email

    data = {
        'id_deudor': id_deudor,
        'numero_identificacion': numero_identificacion,
        'nombre_completo': nombre_completo,
        'email': email
    }

    return data
    

@staticmethod
def get_info_deudor(id_deudor_in, numero_identificacion_in, nombre_completo_in):
    
    if id_deudor_in:
        return get_data_deudor(id_deudor_in)
        
    elif numero_identificacion_in or nombre_completo_in:
        data = []
        deudor = Deudores.objects.all()

        if numero_identificacion_in:
            deudor = deudor.filter(Q(id_persona_deudor_pymisis__t03nit=numero_identificacion_in) | Q(id_persona_deudor__numero_documento = numero_identificacion_in))

        if nombre_completo_in:
            nombre_completo_split = str(nombre_completo_in).split()
            for nombre in nombre_completo_split:
                deudor = deudor.filter(Q(id_persona_deudor_pymisis__t03nombre__icontains=nombre) |
                                       Q(id_persona_deudor__primer_nombre__icontains=nombre) | 
                                       Q(id_persona_deudor__segundo_nombre__icontains=nombre) | 
                                       Q(id_persona_deudor__primer_apellido__icontains=nombre) | 
                                       Q(id_persona_deudor__segundo_apellido__icontains=nombre) |
                                       Q(id_persona_deudor__razon_social__icontains=nombre))
                
        for deud in deudor:
            data.append(get_data_deudor(deud.id))
        
        return data


### VISTAS QUE MUESTRAN LAS OBLIGACIONES

class CarteraDeudorListViews(generics.ListAPIView):
    serializer_class = CarteraSerializer

    def get_monto_total(self, carteras):
        monto_total = 0
        intereses_total = 0
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        monto_total_con_intereses = monto_total + intereses_total
        return monto_total, intereses_total, monto_total_con_intereses
    
    def obligaciones_deudor(self, numero_identificacion):

        deudor = None
        deudor = get_info_deudor(None, numero_identificacion, None)

        if deudor and len(deudor) == 1: 
            deudor = deudor[0]
            cartera = Cartera.objects.filter(id_deudor=Deudores.objects.get(id=deudor['id_deudor']))
            serializer = self.serializer_class(cartera, many=True)
            monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(cartera)
            
            data = {
                'id_deudor': deudor['id_deudor'],
                'nombre_completo': deudor['nombre_completo'],
                'numero_identificacion': deudor['numero_identificacion'],
                'email': deudor['email'],
                'obligaciones': serializer.data,
                'monto_total': monto_total,
                'intereses_total': intereses_total,
                'monto_total_con_intereses': monto_total_con_intereses,
            }
            return data
        else:
            persona = Personas.objects.filter(numero_documento=numero_identificacion).first()
            data = {
                'id_deudor': persona.id_persona,
                'nombre_completo': persona.primer_nombre + " " + persona.primer_apellido,
                'numero_identificacion': persona.numero_documento,
                'email': persona.email,
                'obligaciones': None,
                'monto_total': None,
                'intereses_total': None,
                'monto_total_con_intereses': None,
                'tiene_facilidad' : None
            }
            return data


class ListadoCarteraViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        numero_identificacion = user.persona.numero_documento
        instancia_obligaciones = CarteraDeudorListViews()
        response_data = instancia_obligaciones.obligaciones_deudor(numero_identificacion)
        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No se encontraron deudas asociadas para este usuario.')  


class ConsultaCarteraDeudoresViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, identificacion):
        numero_identificacion = identificacion
        instancia_obligaciones = CarteraDeudorListViews()
        response_data = instancia_obligaciones.obligaciones_deudor(numero_identificacion)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')
        

class ConsultaCarteraViews(generics.ListAPIView):
    serializer_class = ConsultaCarteraSerializer
    
    def get_queryset(self):
        id_obligaciones = self.kwargs['id_obligaciones']
        queryset = Cartera.objects.filter(id=id_obligaciones)
        
        if not queryset.exists():
            raise NotFound("La obligación consultada no existe")
        return queryset


# class ListadoDeudoresViews(generics.ListAPIView):
#     serializer_class = ListadoDeudoresUltSerializer
#     permission_classes = [IsAuthenticated]

#     def get_lista_deudores(self):

#         identificacion = self.request.query_params.get('identificacion', '')
#         nombre_contribuyente = self.request.query_params.get('nombre_contribuyente', '')
#         nombres_apellidos = nombre_contribuyente.split()

#         deudores = Deudores.objects.annotate(nombre_contribuyente=Concat('nombres', V(' '), 'apellidos')).filter(identificacion__icontains=identificacion)

#         for nombre_apellido in nombres_apellidos:
#             deudores = deudores.filter(nombre_contribuyente__icontains=nombre_apellido)

#         serializer = self.serializer_class(deudores, many=True)

#         data_deudores = serializer.data
#         instancia_obligaciones = CarteraDeudorListViews()
        

#         for data in data_deudores:
#             response_data = instancia_obligaciones.obligaciones_deudor(data['identificacion'])
#             if response_data['obligaciones']:
#                 data['obligaciones'] = True
#                 data['monto_total'] = response_data.get('monto_total')
#                 data['monto_total_con_intereses'] = response_data.get('monto_total_con_intereses')
#             else:
#                 data['obligaciones'] = False
#                 data['monto_total'] = None
#                 data['monto_total_con_intereses'] = None

#         return data_deudores
  

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_lista_deudores()

#         if not queryset:
#             raise NotFound('No se encontraron resultados.')
    
#         return Response({'success': True, 'detail': 'Se muestra los deudores', 'data': queryset}, status=status.HTTP_200_OK)


class ListadoDeudoresViews(generics.ListAPIView):
    serializer_class = ListadoDeudoresUltSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        identificacion = self.request.query_params.get('identificacion', '')
        nombre_contribuyente = self.request.query_params.get('nombre_contribuyente', '')
        deudores = Deudores.objects.all()

        deudores_data = get_info_deudor(None, identificacion, nombre_contribuyente)
        if deudores_data:
            deudores = deudores.filter(id__in=[deudor['id_deudor'] for deudor in deudores_data])
            
        serializer = self.serializer_class(deudores, many=True)
        data_deudores = serializer.data
   
        return Response({'success': True, 'detail': 'Se muestra los deudores', 'data': data_deudores}, status=status.HTTP_200_OK)


### VISTAS QUE SE MUESTRAN AL MOMENTO DE CREAR UNA FACILIDAD

class DatosDeudorView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudorDatosSerializer

    def get_datos_deudor(self, id):
        try:
            deudor = Deudores.objects.get(id=id)
        except Deudores.DoesNotExist:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')

        serializer = self.serializer_class(deudor)
        return serializer.data

    def get(self, request, id):
        deudor = self.get_datos_deudor(id)
        return Response({'success': True, 'detail':'Se muestra los datos del deudor', 'data': deudor}, status=status.HTTP_200_OK) 


class ListaCarteraDeudorSeleccionadasIds(generics.ListAPIView):
    serializer_class = CarteraSerializer

    def get_obligaciones(self, ids_cartera):
        instancia_obligaciones = CarteraDeudorListViews()
        carteras = Cartera.objects.filter(id__in=ids_cartera)
        serializer = CarteraSerializer(carteras, many=True)
        monto_total, intereses_total, monto_total_con_intereses = instancia_obligaciones.get_monto_total(carteras)

        data = {
            'obligaciones': serializer.data,
            'monto_total': monto_total,
            'intereses_total': intereses_total,
            'monto_total_con_intereses': monto_total_con_intereses
        }
        return data

    def get(self, request):
        
        ids_param = self.request.query_params.get('ids')
        ids = [int(id_str) for id_str in ids_param.strip('[]').split(',') if id_str]
        cartera_data = self.get_obligaciones(ids)
        return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': cartera_data}, status=status.HTTP_200_OK) 


class TipoActuacionView(generics.ListAPIView):
    queryset = TipoActuacion.objects.all()
    serializer_class = TipoActuacionSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'success': True, 
            'detail':'Se muestran los tipos de actuacion de deudor', 
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

class DatosContactoDeudorView(generics.ListAPIView):
    serializer_class = DeudorDatosSerializer

    def get_datos_deudor(self, id_deudor):
        try:
            deudor = Deudores.objects.get(id=id_deudor)
        except Deudores.DoesNotExist:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
    
        serializer = self.serializer_class(deudor)
        return serializer.data
    
    def get(self, request, id):
        deudor = self.get_datos_deudor(id)
        return Response({'success': True, 'detail':'Se muestra los datos de contacto del deudor', 'data': deudor}, status=status.HTTP_200_OK)   


class RequisitosActuacionView(generics.ListAPIView):
    serializer_class = RequisitosActuacionSerializer
    queryset = RequisitosActuacion
    
    def get(self, request, id):
        queryset = RequisitosActuacion.objects.filter(id_tipo_actuacion=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los requisitos deltipo de actuacion del deudor',  'data': serializer.data}, status=status.HTTP_200_OK)


class TiposBienesView(generics.ListAPIView):
    serializer_class = TipoBienSerializer
    queryset = TiposBien.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Se muestra los tipos de bienes', 'data': serializer.data}, status=status.HTTP_200_OK)


### SERVICION QUE CREAN AL MOMENTO DE HACER UNA FACILIDAD DE PAGO

class AvaluoCreateView(generics.CreateAPIView):
    serializer_class = AvaluosSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_avaluo(self, data_in):
        bien = Bienes.objects.filter(id=data_in['id_bien']).first()
        
        if not bien:
            raise NotFound('No existe bien relacionado con la informacion ingresada')
        
        fecha_avaluo = date.today()
        fecha_fin_vigencia = fecha_avaluo + timedelta(days=bien.id_tipo_bien.vigencia_avaluo)
        data = {
            'id_bien' : bien.id,
            'fecha_avaluo': fecha_avaluo,
            'fecha_fin_vigencia': fecha_fin_vigencia,
            'id_funcionario_perito': data_in['id_funcionario_perito'],
            'valor': data_in['valor']
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        avaluo_creado = serializer.save()
        return avaluo_creado

    def post(self, request):
        data_in = request.data

        # CREAR AVALUO
        avaluo = self.crear_avaluo(data_in)

        if not avaluo:
            raise ValidationError('No se pudo crear el avaluo')
        
        return Response({'success': True, 'detail': 'Se crea el avalauo', 'data': self.serializer_class(avaluo).data}, status=status.HTTP_201_CREATED)


class BienCreateView(generics.CreateAPIView):
    serializer_class = BienSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_bien(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bien_creado = serializer.save()
        return bien_creado

    def post(self, request):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('documento_soporte')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "BienesRecaudo")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['documento_soporte'] = archivo_creado_instance.id_archivo_digital

        # CREAR BIEN
        bien = self.crear_bien(data)

        if not bien:
            raise ValidationError('No se pudo crear el bien')

        return Response({'success': True, 'detail': 'Se crea el bien que coloca el deudor', 'data': self.serializer_class(bien).data}, status=status.HTTP_201_CREATED)


class DetallesBienFacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = DetallesBienFacilidadPagoSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_bienes_facilidad(self, data):
        bien = Bienes.objects.filter(id=data['id_bien']).first()
        facilidad_pago = FacilidadesPago.objects.filter(id=data['id_facilidad_pago']).first()
        
        if not bien:
            raise NotFound('No existe bien relacionado con la informacion ingresada')
        
        if not facilidad_pago:
            raise NotFound('No existe facilidad de pago relacionada con la informacion ingresada')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bienes_facilidad = serializer.save()
        return bienes_facilidad

    def post(self, request):
        data = request.data

        # Crear relación de facilidades de pago y bienes
        bienes_facilidad = self.crear_bienes_facilidad(data)

        if not bienes_facilidad:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes', 'data':self.serializer_class(bienes_facilidad).data}, status=status.HTTP_201_CREATED)


class GarantiasFacilidadCreateView(generics.CreateAPIView):
    serializer_class = GarantiasFacilidadSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_garantias_facilidad(self, data):
        rol = RolesGarantias.objects.filter(id=data['id_rol']).first()
        facilidad_pago = FacilidadesPago.objects.filter(id=data['id_facilidad_pago']).first()
        
        if not rol:
            raise NotFound('No existe rol de garantia relacionado con la informacion ingresada')
        
        if not facilidad_pago:
            raise NotFound('No existe facilidad de pago relacionada con la informacion ingresada')

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        garantias_facilidad = serializer.save()
        return garantias_facilidad

    def post(self, request):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('documento_garantia')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "GarantiasFacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['documento_garantia'] = archivo_creado_instance.id_archivo_digital

        # Crear relación de facilidades de pago y bienes mediante garantías
        garantias_facilidad = self.crear_garantias_facilidad(data)

        if not garantias_facilidad:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y garantías', 'data':self.serializer_class(garantias_facilidad).data}, status=status.HTTP_201_CREATED)


class CumplimientoRequisitosCreateView(generics.CreateAPIView):
    serializer_class = CumplimientoRequisitosSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_cumplimiento_requisitos(self, data):
        requisito_actuacion = RequisitosActuacion.objects.filter(id=data['id_requisito_actuacion']).first()
        facilidad_pago = FacilidadesPago.objects.filter(id=data['id_facilidad_pago']).first()
        
        if not requisito_actuacion:
            raise NotFound('No existe requisito relacionado con la informacion ingresada')
        
        if not facilidad_pago:
            raise NotFound('No existe facilidad de pago relacionada con la informacion ingresada')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        cumplimiento_requisitos = serializer.save()
        return cumplimiento_requisitos

    def post(self, request):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('documento')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "CumplimientoRequisitosFacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['documento'] = archivo_creado_instance.id_archivo_digital

        # Crear relación de facilidades de pago y bienes mediante garantías
        cumplimiento_requisitos = self.crear_cumplimiento_requisitos(data)

        if not cumplimiento_requisitos:
            raise ValidationError('No se pudo crear los cumplimientos')

        return Response({'success':True, 'detail':'Se crea los cumplimientos', 'data':self.serializer_class(cumplimiento_requisitos).data}, status=status.HTTP_201_CREATED)
   

class DetallesFacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = DetallesFacilidadPagoSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_cartera_facilidad(self, data):
        try:
            cartera = Cartera.objects.get(id=data['id_cartera'])
        except Cartera.DoesNotExist:
            raise NotFound('No existe cartera relacionado con la informacion ingresada')
        
        try:
            facilidad_pago = FacilidadesPago.objects.get(id=data['id_facilidad_pago'])
        except FacilidadesPago.DoesNotExist:
            raise NotFound('No existe facilidad de pago relacionada con la informacion ingresada')
        
        if cartera.id_deudor != facilidad_pago.id_deudor:
            raise ValidationError('El deudor no coinciden con los dados ingresados')
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bienes_facilidad = serializer.save()
        return bienes_facilidad

    def post(self, request):
        data = request.data

        # Crear relación de facilidades de pago y cartera
        cartera_facilidad = self.crear_cartera_facilidad(data)

        if not cartera_facilidad:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y cartera', 'data':self.serializer_class(cartera_facilidad).data}, status=status.HTTP_201_CREATED)


class FacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = FacilidadesPagoSerializer
    permission_classes = [IsAuthenticated, PermisoCrearSolicitudFacilidadPago]

    def crear_facilidad_pago(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        periodicidad = serializer.validated_data.get('periodicidad')
        cuotas = serializer.validated_data.get('cuotas')
        total_plazos = periodicidad * cuotas

        if total_plazos > 61:
            raise PermissionDenied('Las cuotas deben ser menores a 60 meses')

        facilidad_pago = serializer.save()
        return facilidad_pago, total_plazos
    
    def post(self, request):
        data_in = request.data
        data_in._mutable=True
        print(data_in)
        fecha_actual =datetime.now()
        instancia_bien = BienCreateView()
        instancia_avaluo = AvaluoCreateView()
        instancia_det_bien_facilidad = DetallesBienFacilidadPagoCreateView()
        documento_soporte = request.FILES.get('documento_soporte')
        consignacion_soporte = request.FILES.get('consignacion_soporte')
        documento_no_enajenacion = request.FILES.get('documento_no_enajenacion')

        data_radicado = {}
        data_radicado['fecha_actual'] = fecha_actual
        data_radicado['id_persona'] = request.user.persona.id_persona
        data_radicado['tipo_radicado'] = "E" #validar cual tipo de radicado
        data_radicado['modulo_radica'] = 'Solicitudes para realizar facilidades de pago'

        radicadoCreate = RadicadoCreate()
                
        respuesta_radicado = radicadoCreate.post(data_radicado)
        print(respuesta_radicado)

        data_in['id_radicado'] = respuesta_radicado['id_radicado']
        data_in['fecha_radicado'] = respuesta_radicado['fecha_radicado']

        #CREAR FACILIDAD DE PAGO
        facilidad_pago = None

        fecha_abono_a = data_in['fecha_abono']

        try:
            fecha_abono = datetime.strptime(fecha_abono_a, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError('Formato de fecha de abono inválido')
        
        if fecha_abono > datetime.now().date():
            raise ValidationError('La fecha de abono es incorrecta')
        
        # CREAR ARCHIVO EN T238
        if documento_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(documento_soporte, "FacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data_in['documento_soporte'] = archivo_creado_instance.id_archivo_digital
        
        if consignacion_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(consignacion_soporte, "FacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data_in['consignacion_soporte'] = archivo_creado_instance.id_archivo_digital
        
        if documento_no_enajenacion:
            archivo_creado = UtilsGestor.create_archivo_digital(documento_no_enajenacion, "FacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data_in['documento_no_enajenacion'] = archivo_creado_instance.id_archivo_digital
        
        facilidad_data = {
            'id_deudor': data_in['id_deudor'],
            'id_tipo_actuacion':data_in['id_tipo_actuacion'],
            'observaciones':data_in['observaciones'],
            'periodicidad':data_in['periodicidad'],
            'cuotas':data_in['cuotas'],
            'documento_soporte':data_in['documento_soporte'],
            'consignacion_soporte':data_in['consignacion_soporte'],
            'valor_abonado':data_in['valor_abonado'],
            'fecha_abono':data_in['fecha_abono'],
            'documento_no_enajenacion':data_in['documento_no_enajenacion'],
            'id_funcionario':data_in['id_funcionario'],
            'notificaciones':data_in['notificaciones'],
            'id_radicado': respuesta_radicado['id_radicado']
        }

        descripciones_bien = data_in.getlist('descripcion')
        direcciones_bien = data_in.getlist('direccion')
        id_tipos_bien = data_in.getlist('id_tipo_bien')
        documentos_soporte_bien = request.FILES.getlist('documento_soporte_bien')
        id_ubicaciones = data_in.getlist('id_ubicacion')
        avaluos_bien = data_in.getlist('valor')

        if len(descripciones_bien) != len(avaluos_bien):
            raise ValidationError("Todos los bienes deben tener un valor avaluado.")
        
        tamaños_campos = [len(descripciones_bien), len(direcciones_bien), len(id_tipos_bien), len(documentos_soporte_bien), len(id_ubicaciones)]

        for tamaño in tamaños_campos:
            if tamaños_campos[0] != tamaño:
                raise ValidationError("Faltan datos por ingresar en los bienes.")
            
        list_id_bienes = []

        for descripcion, direccion, id_tipo_bien, documento_soporte, id_ubicacion, valor in zip(
                descripciones_bien, direcciones_bien, id_tipos_bien, documentos_soporte_bien, id_ubicaciones,
                avaluos_bien):
            
            # CREAR ARCHIVO EN T238
            if documento_soporte:
                archivo_creado = UtilsGestor.create_archivo_digital(documento_soporte, "FacilidadesPago")
                archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                
                documento_soporte = archivo_creado_instance.id_archivo_digital

            # CREAR BIEN
            bien_data = {
                'id_deudor': data_in['id_deudor'],
                'descripcion': descripcion,
                'direccion': direccion,
                'id_tipo_bien': id_tipo_bien,
                'documento_soporte': documento_soporte,
                'id_ubicacion': id_ubicacion
            }

            bien = instancia_bien.crear_bien(bien_data)

            if not bien:
                raise ValidationError('No se pudo crear el bien')

            # CREAR AVALUO
            avaluo_data = {
                'id_bien': bien.id,
                'id_funcionario_perito': data_in['id_funcionario'],
                'valor': valor
            }
            avaluo = instancia_avaluo.crear_avaluo(avaluo_data)

            if not avaluo:
                raise ValidationError('No se pudo crear el avaluo')
            
            list_id_bienes.append(bien.id)

        if list_id_bienes:
            facilidad_pago, total_plazos = self.crear_facilidad_pago(facilidad_data)
            try:
                id_facilidad_pago = facilidad_pago.id
            except:
                raise ValidationError('No se creo facilidad de pago debido a datos faltantes')
                

            for id_bien in list_id_bienes:
                # CREAR RELACION DE BIEN Y FACILIDAD
                det_bien_facilidad_data = {
                    'id_bien': id_bien,
                    'id_facilidad_pago': id_facilidad_pago
                }
                det_bien_facilidad = instancia_det_bien_facilidad.crear_bienes_facilidad(det_bien_facilidad_data)
            
            # CREAR GARANTIAS FACILIDAD
            if total_plazos > 12:
                instancia_garantias_facilidad = GarantiasFacilidadCreateView()
                documento_garantia = request.FILES.get('documento_garantia')

                # CREAR ARCHIVO EN T238
                if documento_garantia:
                    archivo_creado = UtilsGestor.create_archivo_digital(documento_garantia, "GarantiasFacilidadPago")
                    archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                    
                    data_in['documento_garantia'] = archivo_creado_instance.id_archivo_digital

                garantias_facilidad_data = {
                    'id_rol': data_in['id_rol'],
                    'id_facilidad_pago': id_facilidad_pago,
                    'documento_garantia': data_in['documento_garantia']
                }
                garantias_facilidad = instancia_garantias_facilidad.crear_garantias_facilidad(garantias_facilidad_data)

                if not garantias_facilidad:
                    raise ValidationError('No se pudo crear la solicitud por falta de datos en las garantias')
                
        documentos_deudor = request.FILES.getlist('documento_deudor')
        requisitos = RequisitosActuacion.objects.filter(id_tipo_actuacion=data_in['id_tipo_actuacion'])
        print("requisitos = ", len(requisitos), "Documentos = ", len(documentos_deudor))

        if len(documentos_deudor) != len(requisitos):
            raise ValidationError('No se pudo crear la solicitud por falta de documentos del deudor')
        
        instancia_cumplimiento = CumplimientoRequisitosCreateView()
        for documento, requisito in zip(documentos_deudor, requisitos):
            # CREAR ARCHIVO EN T238
            if documento:
                archivo_creado = UtilsGestor.create_archivo_digital(documento, "FacilidadesPago")
                archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
                
                documento = archivo_creado_instance.id_archivo_digital

            cumplimiento_data = {
                'id_facilidad_pago': id_facilidad_pago,
                'id_requisito_actuacion': requisito.id,
                'documento': documento
            }

            cumplimiento = instancia_cumplimiento.crear_cumplimiento_requisitos(cumplimiento_data)

            if not cumplimiento:
                raise ValidationError('No se pudo crear la solicitud por falta de datos del deudor en los requisitos')
            
        instancia_cartera = DetallesFacilidadPagoCreateView()
        ids_param = data_in['ids_obligaciones']
        ids_cartera = [int(id_str) for id_str in ids_param.strip('[]').split(',') if id_str]
        for id_cartera in ids_cartera:
            cartera_data = {
                'id_facilidad_pago': id_facilidad_pago,
                'id_cartera': id_cartera
            }

            cartera_detalle = instancia_cartera.crear_cartera_facilidad(cartera_data)

            if not cartera_detalle:
                raise ValidationError('No se pudo crear la solicitud por falta de datos de las obligaciones del deudor')
        
        if not facilidad_pago:
            raise ValidationError('No se pudo crear la facilidad de pago')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes mediante garantías', 'data':self.serializer_class(facilidad_pago).data}, status=status.HTTP_201_CREATED)


### ASIGNACION DE FUNCIONARIOS

class ListadoFacilidadesPagoViews(generics.ListAPIView):
    serializer_class = ListadoFacilidadesPagoSerializer

    def lista_facilidades(self, data):
        facilidades_pago = FacilidadesPago.objects.all()
        identificacion = data['identificacion']
        nombre_de_usuario = data['nombre_de_usuario']


        deudores = None
        deudores = get_info_deudor(None, identificacion, nombre_de_usuario)
        deudor_ids = [deudor['id_deudor'] for deudor in deudores] if deudores else None


        if deudor_ids:
            facilidades_pago = facilidades_pago.filter(id_deudor__in=deudor_ids)   
               

        return facilidades_pago.order_by('-fecha_generacion')
    

class FuncionariosView(generics.ListAPIView):
    serializer_class = FuncionariosSerializer
    queryset = Personas.objects.all()

    def get(self, request):
        funcionarios = ClasesTerceroPersona.objects.filter(id_clase_tercero=2)
        funcionarios = [funcionario.id_persona for funcionario in funcionarios]
        serializer = self.serializer_class(funcionarios, many=True)
        return Response({'success': True, 'detail':'Se muestra los funcionarios para facilidades de pago', 'data':serializer.data}, status=status.HTTP_200_OK)

    
class ListadoFacilidadesPagoAdminViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListadoFacilidadesPagoSerializer

    def list(self, request):
        data = {
            'identificacion':self.request.query_params.get('identificacion', ''),
            'nombre_de_usuario' : self.request.query_params.get('nombre_de_usuario', ''),
        }
        instancia_facilidad = ListadoFacilidadesPagoViews()
        facilidades_pago = instancia_facilidad.lista_facilidades(data)

        if not facilidades_pago.exists():
            raise NotFound("Los datos ingresados con coinciden con las facilidades de pagos existentes")

        serializer = self.serializer_class(facilidades_pago, many=True)
        id_user = request.user.persona
        #asignar = [id_user == facilidad.id_funcionario for facilidad in facilidades_pago]
        data = serializer.data

        # for i in range(len(data)):
        #     data[i]['asignar'] = asignar[i]
        
        return Response({'success': True, 'detail': 'Se muestra las facilidades de pago de los deudores', 'data':data}, status=status.HTTP_200_OK)


class ListadoFacilidadesPagoFuncionarioViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListadoFacilidadesPagoSerializer

    def list(self, request):
        data = {
            'identificacion':self.request.query_params.get('identificacion', ''),
            'nombre_de_usuario' : self.request.query_params.get('nombre_de_usuario', ''),
        }
        instancia_facilidad = ListadoFacilidadesPagoViews()
        facilidades_pago = instancia_facilidad.lista_facilidades(data)

        if not facilidades_pago.exists():
            raise NotFound("Los datos ingresados con coinciden con las facilidades de pagos existentes")

        id_user = request.user.persona.id_persona
        data = [facilidad for facilidad in facilidades_pago if facilidad.id_funcionario.id_persona==id_user]

        serializer = self.serializer_class(data, many=True)
        
        return Response({'success': True, 'detail': 'Se muestra las facilidades de pago de los deudores', 'data':serializer.data}, status=status.HTTP_200_OK)


class FacilidadPagoFuncionarioUpdateView(generics.UpdateAPIView):
    serializer_class = FacilidadesPagoFuncionarioPutSerializer
    permission_classes = [IsAuthenticated, PermisoActualizarSolicitudFacilidadPago]

    def update_funcionario(self, serializer):
        id_funcionario = serializer.validated_data.get('id_funcionario')
        id_funcionario = ClasesTerceroPersona.objects.filter(id_persona=id_funcionario, id_clase_tercero=2).first()

        if id_funcionario:
            serializer.save(update_fields=['id_funcionario'])
            return True
        return False

    def put(self, request, id):
        data = request.data
        facilidad_de_pago = FacilidadesPago.objects.filter(id=id).first()

        if not facilidad_de_pago:
            raise NotFound('No existe facilidad de pago relacionada con la informacion ingresada')
    
        serializer = self.serializer_class(facilidad_de_pago, data=data)
        serializer.is_valid(raise_exception=True)

        if self.update_funcionario(serializer):
            return Response({'success': True, 'detail': 'Se le asigna el funcionario a la facilidad de pago', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied('El funcionario ingresado no tiene permisos')


### MOSTRAR LA FACILIDAD DE PAGO
class CumplimientoRequisitosGetView(generics.ListAPIView):
    serializer_class = CumplimientoRequisitosGetSerializer

    def get_documentos_requisitos(self, id_facilidad_pago):
        documentos_deudor = CumplimientoRequisitos.objects.filter(id_facilidad_pago=id_facilidad_pago)
        if not documentos_deudor:
            raise NotFound('No se encontró ningún registro en cumplimiento de requisitos con el parámetro ingresado')
        serializer = self.serializer_class(documentos_deudor, many=True)
        return serializer.data
    
    def get(self, request, id_facilidad_pago):
        documentos_deudor = self.get_documentos_requisitos(id_facilidad_pago)
        return Response({'success': True, 'detail':'Se muestra los datos del deudor', 'data':documentos_deudor}, status=status.HTTP_200_OK)  


class GarantiasFacilidadGetView(generics.ListAPIView):
    serializer_class = GarantiasFacilidadGetSerializer

    def get_documento_garantia(self, id_facilidad_pago):
        documento_garantia = GarantiasFacilidad.objects.filter(id_facilidad_pago=id_facilidad_pago).first()
        if not documento_garantia:
            raise NotFound('No se encontró ningún registro en garantias de facilidad con el parámetro ingresado')
        serializer = self.serializer_class(documento_garantia, many=False)
        return serializer.data
    
    def get(self, request, id_facilidad_pago):
        documento_garantia = self.get_documento_garantia(id_facilidad_pago)
        return Response({'success': True, 'detail':'Se muestra los datos del deudor', 'data':documento_garantia}, status=status.HTTP_200_OK) 
    

class ListaBienesDeudorView(generics.ListAPIView):
    serializer_class = BienesDeudorSerializer

    def get_bienes_deudor(self, id_deudor):
        bienes_deudor = Bienes.objects.filter(id_deudor=id_deudor)
        if not bienes_deudor:
            raise NotFound('No se encontró ningún registro en los bienes con el parámetro ingresado')
        serializer = self.serializer_class(bienes_deudor, many=True)
        return serializer.data

    def get(self, request, id_deudor):
        bienes_deudor = self.get_bienes_deudor(id_deudor)
        return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': bienes_deudor}, status=status.HTTP_200_OK) 


class ListaBienesFacilidadView(generics.ListAPIView):
    serializer_class = BienesDeudorSerializer

    def get_bienes_deudor(self, id_facilidad_pago):

        facilidad_pago = FacilidadesPago.objects.filter(id=id_facilidad_pago).first()

        if not facilidad_pago:
            raise NotFound('No se encontró ningún registro en facilidades de pago con el parámetro ingresado')
        
        bienes_deudor = Bienes.objects.filter(id_deudor=facilidad_pago.id_deudor)

        if not bienes_deudor:
            raise NotFound('No se encontró ningún registro en los bienes con el parámetro ingresado')
        
        detalles_bienes = DetallesBienFacilidadPago.objects.filter(id_facilidad_pago=facilidad_pago.id)
        bienes_ids = [detalle_bien.id_bien.id for detalle_bien in detalles_bienes if detalle_bien.id_bien]

        bienes_deudor = bienes_deudor.filter(id__in=bienes_ids)

        serializer = self.serializer_class(bienes_deudor, many=True)
        return serializer.data

    def get(self, request, id_facilidad_pago):
        bienes_deudor = self.get_bienes_deudor(id_facilidad_pago)
        return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': bienes_deudor}, status=status.HTTP_200_OK) 
    

class FacilidadPagoGetByIdView(generics.ListAPIView):
    serializer_class = FacilidadPagoGetByIdSerializer

    def get_facilidad_pago_by_id(self, id):
        facilidad_pago = FacilidadesPago.objects.filter(id=id).first()
        if not facilidad_pago:
            raise NotFound('No se encontró ningún registro en facilidades de pago con el parámetro ingresado')
        serializer = self.serializer_class(facilidad_pago, many=False)
        return serializer.data
    
    def get(self, request, id):
        facilidad_pago = self.get_facilidad_pago_by_id(id)
        instancia_deudor = DatosDeudorView()
        deudor = instancia_deudor.get_datos_deudor(facilidad_pago['id_deudor'])
        obligaciones = DetallesFacilidadPago.objects.filter(id_facilidad_pago=facilidad_pago['id'])
        ids_cartera = [obligacion.id_cartera.id for obligacion in obligaciones if obligacion.id_cartera]
        instancia_obligaciones = ListaCarteraDeudorSeleccionadasIds()
        obligaciones_seleccionadas = instancia_obligaciones.get_obligaciones(ids_cartera)
        instancia_documentos_deudor = CumplimientoRequisitosGetView()
        documentos_deudor_actuacion = instancia_documentos_deudor.get_documentos_requisitos(facilidad_pago['id'])
        instancia_deudor_actuacion = DatosContactoDeudorView()
        datos_deudor_actuacion = instancia_deudor_actuacion.get_datos_deudor(facilidad_pago['id_deudor'])
        documento_garanta = None
        if (facilidad_pago['periodicidad']*facilidad_pago['cuotas']) > 12:
            instancia_garantia = GarantiasFacilidadGetView()
            documento_garanta = instancia_garantia.get_documento_garantia(facilidad_pago['id'])
        instancia_bienes = ListaBienesFacilidadView()
        bienes = instancia_bienes.get_bienes_deudor(facilidad_pago['id'])

        result_data = {
            'facilidad_pago': facilidad_pago,
            'deudor': deudor,
            'obligaciones_seleccionadas': obligaciones_seleccionadas,
            'documentos_deudor_actuacion': documentos_deudor_actuacion,
            'datos_deudor_actuacion': datos_deudor_actuacion,
            'documento_garantia': documento_garanta,
            'bienes': bienes
        }

        return Response({'success': True, 'detail':'Se muestra los datos la facilidad de pago', 'data': result_data}, status=status.HTTP_200_OK)   
        

class RespuestaSolicitudFacilidadView(generics.CreateAPIView):
    serializer_class = RespuestaSolicitudSerializer

    def crear_respuesta_solicitud(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        respuesta_solicitud_creada = serializer.save()
        return respuesta_solicitud_creada

    def post(self, request):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('informe_dbme')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "RespuestaSolicitudFacilidadPago")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['informe_dbme'] = archivo_creado_instance.id_archivo_digital

        # CREAR RESPUESTA SOLICITUD
        respuesta_solicitud = self.crear_respuesta_solicitud(data)

        if not respuesta_solicitud:
            raise ValidationError('No se pudo crear el bien')

        return Response({'success': True, 'detail': 'Se registra la respuesta la respuesta dada por el funcionario', 'data': self.serializer_class(respuesta_solicitud).data}, status=status.HTTP_201_CREATED)


class RespuestaSolicitudFacilidadGetView(generics.ListAPIView):
    serializer_class = RespuestaSolicitudGetSerializer

    def get_respuesta_solicitud(self, id_facilidad_pago):
        facilidad_pago = FacilidadesPago.objects.get(id=id_facilidad_pago)

        if not facilidad_pago:
            raise NotFound('No se encontró ningún registro en facilidades de pago con el parámetro ingresado')
        
        respuesta = RespuestaSolicitud.objects.filter(id_facilidad_pago=facilidad_pago.id).first()
        serializer = self.serializer_class(respuesta, many=False)
        return serializer.data
    
    def get(self, request, id_facilidad_pago):
        respuesta_solicitud = self.get_respuesta_solicitud(id_facilidad_pago)
        return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': respuesta_solicitud}, status=status.HTTP_200_OK) 


class FacilidadesPagosSeguimientoListView(generics.ListAPIView):
    serializer_class = ListadoFacilidadesSeguimientoSerializer

    def get_valor_total(self, carteras):
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        valor_total = monto_total + intereses_total
        return valor_total

    def get(self, request):
        user = request.user
        data = []

        deudor = get_info_deudor(None, user.persona.numero_documento, None)
        deudor = deudor[0] if deudor and len(deudor) == 1 else None
        deudor = Deudores.objects.get(id=deudor['id_deudor'])

        facilidades_pago = FacilidadesPago.objects.filter(id_deudor=deudor.id)

        if not facilidades_pago.exists():
            raise NotFound('No se encontró ningún registro en facilidades de pago con el parámetro ingresado')
        
        for facilidad_pago in facilidades_pago:
            cartera_ids = DetallesFacilidadPago.objects.filter(id_facilidad_pago=facilidad_pago.id)
            ids_cartera = [cartera_id.id_cartera.id for cartera_id in cartera_ids if cartera_id]
            cartera_seleccion = Cartera.objects.filter(id__in=ids_cartera)
            valor_total = self.get_valor_total(cartera_seleccion)
            facilidad_data = self.serializer_class(facilidad_pago).data
            facilidad_data['valor_total'] = valor_total
            data.append(facilidad_data)
        
        return Response({'success': True, 'detail':'Se registra la respuesta dada por el funcionario', 'data': data}, status=status.HTTP_201_CREATED)


