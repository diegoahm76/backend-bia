from datetime import datetime
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.base_models import (
    LeyesLiquidacion
)
from recaudo.models.liquidaciones_models import (
    HistEstadosLiq,
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes,
    CalculosLiquidacionBase
)
from recaudo.serializers.liquidaciones_serializers import (
    HistEstadosLiqGetSerializer,
    HistEstadosLiqPostSerializer,
    LiquidacionesTramitePostSerializer,
    OpcionesLiquidacionBaseSerializer,
    OpcionesLiquidacionBasePutSerializer,
    DeudoresSerializer,
    LiquidacionesBaseSerializer,
    LiquidacionesBasePostSerializer,
    LiquidacionesBasePostMasivoSerializer,
    DetallesLiquidacionBaseSerializer,
    DetallesLiquidacionBasePostSerializer,
    ExpedientesSerializer,
    CalculosLiquidacionBaseSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.db.models.functions import Lower
from django.shortcuts import render
from docxtpl import DocxTemplate
from django.conf import settings
import calendar
import json
import hashlib
import os

from seguridad.permissions.permissions_recaudo import PermisoActualizarConstructorFormulas, PermisoActualizarGeneradorLiquidacionesRecaudo, PermisoBorrarConstructorFormulas, PermisoCrearConstructorFormulas, PermisoCrearGeneradorLiquidacionesRecaudo

class OpcionesLiquidacionBaseView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'POST':
            permissions.append(PermisoCrearConstructorFormulas())
        return permissions

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetalleOpcionesLiquidacionBaseView(generics.GenericAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'PUT':
            permissions.append(PermisoActualizarConstructorFormulas())
        return permissions

    def get(self, request, pk):
        queryset = OpcionesLiquidacionBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        opcion = OpcionesLiquidacionBase.objects.filter(pk=pk).get()
        serializer = OpcionesLiquidacionBasePutSerializer(opcion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EliminarOpcionesLiquidacionBaseView(generics.GenericAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    permission_classes = [IsAuthenticated, PermisoBorrarConstructorFormulas]

    def get(self, request, pk):
        opcion_liquidacion = OpcionesLiquidacionBase.objects.filter(pk=pk).first()
        if opcion_liquidacion:
            opcion_liquidacion.delete()
            return Response({'success': True, 'detail': 'La opción de liquidación ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la opción de liquidación')


class DeudoresView(generics.GenericAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeudoresIdentificacionView(generics.GenericAPIView):
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, identificacion):
        queryset = Deudores.objects.filter(identificacion=identificacion).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun deudor con la identificación ingresada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class LiquidacionBaseView(generics.ListAPIView):
    queryset = LiquidacionesBase.objects.all()
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'POST':
            permissions.append(PermisoCrearGeneradorLiquidacionesRecaudo())
        return permissions

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LiquidacionesBasePostSerializer(data=request.data)
        if serializer.is_valid():
            id_expediente = request.data['id_expediente']
            if id_expediente is not None:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LiquidacionesBasePostMasivovista(generics.CreateAPIView):
    serializer_class = LiquidacionesBasePostMasivoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            id_expedientes = serializer.validated_data.get('id_expediente', [])
            print("IDs de expedientes recibidos:", id_expedientes)
            for id_expediente in id_expedientes:
                try:
                    expediente = Expedientes.objects.get(pk=id_expediente)
                    print("Expediente encontrado:", expediente)
                except Expedientes.DoesNotExist:
                    print(f"Expediente con ID {id_expediente} no encontrado")
                    return Response({"error": f"Expediente con ID {id_expediente} no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Errores de validación del serializador:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class ObtenerLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = LiquidacionesBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ninguna liquidación base con el id ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
        serializer = LiquidacionesBasePostSerializer(liquidacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtenerLiquidacionPorIdExpedienteBaseView(generics.GenericAPIView):
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = LiquidacionesBase.objects.filter(id_expediente=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ninguna liquidación base con el id de expediente ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DetallesLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = DetallesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'POST':
            permissions.append(PermisoCrearGeneradorLiquidacionesRecaudo())
        if method == 'PUT':
            permissions.append(PermisoActualizarGeneradorLiquidacionesRecaudo())
        return permissions

    def get(self, request, liquidacion):
        queryset = DetalleLiquidacionBase.objects.filter(id_liquidacion__id=liquidacion)
        if len(queryset) == 0:
            return Response({'success': False, 'detail': 'No se encontró ningun detalle para la liquidación base'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DetallesLiquidacionBasePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, liquidacion):
        detalle = DetalleLiquidacionBase.objects.filter(pk=liquidacion).get()
        serializer = DetallesLiquidacionBasePostSerializer(detalle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LiquidacionTramiteCreateView(generics.CreateAPIView):
    queryset = LiquidacionesBase.objects.all()
    serializer_class = LiquidacionesTramitePostSerializer
    serializer_detalles_class = DetallesLiquidacionBasePostSerializer
    serializer_historico_class = HistEstadosLiqPostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_liquidacion = request.data.get('data_liquidacion')
        data_detalles = request.data.get('data_detalles')
        archivo_liquidacion = request.FILES.get('archivo_liquidacion')
        current_date = datetime.now()

        if not data_liquidacion:
            raise ValidationError('Debe enviar la información de la liquidación')
        
        if not archivo_liquidacion:
            raise ValidationError('Debe enviar el archivo generado para la liquidación')
        
        data_liquidacion = json.loads(data_liquidacion)
        data_detalles = json.loads(data_detalles) if data_detalles else None

        # Guardar archivo
        # VALIDAR FORMATO ARCHIVO 
        archivo_nombre = archivo_liquidacion.name 
        nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        
        formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
        
        if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
            raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
        
        # CREAR ARCHIVO EN T238
        # Obtiene el año actual para determinar la carpeta de destino
        current_year = current_date.year
        ruta = os.path.join("home", "BIA", "Otros", "LiquidacionesTramites", str(current_year))
        
        # Calcula el hash MD5 del archivo
        md5_hash = hashlib.md5()
        for chunk in archivo_liquidacion.chunks():
            md5_hash.update(chunk)

        # Obtiene el valor hash MD5
        md5_value = md5_hash.hexdigest()

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': True,
            'ruta': ruta,
            'md5_hash': md5_value  
        }
        
        archivo_class = ArchivosDgitalesCreate()
        respuesta = archivo_class.crear_archivo(data_archivo, archivo_liquidacion)

        # Validar que la fecha de vencimiento sea 
        fecha_vencimiento = datetime.strptime(data_liquidacion['vencimiento'], "%Y-%m-%d")
        fecha_actual = datetime.now()
        if fecha_vencimiento.date() < fecha_actual.date():
            raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha actual')

        # Asociar archivo creado a liquidación
        data_liquidacion['id_persona_liquida'] = request.user.persona.id_persona
        data_liquidacion['id_archivo'] = respuesta.data.get('data').get('id_archivo_digital')
        data_liquidacion['estado'] = 'PENDIENTE'

        serializer = self.serializer_class(data=data_liquidacion)
        serializer.is_valid(raise_exception=True)
        liquidacion_creada = serializer.save()

        data_output = serializer.data
        data_output['id_archivo_ruta'] = liquidacion_creada.id_archivo.ruta_archivo.url
        data_output['detalles'] = []

        if data_detalles:
            for detalle in data_detalles:
                detalle['id_liquidacion'] = liquidacion_creada.id
                serializer_detalle = self.serializer_detalles_class(data=detalle)
                serializer_detalle.is_valid(raise_exception=True)
                serializer_detalle.save()

                data_output['detalles'].append(serializer_detalle.data)

        # Guardar historico
        data_historico = {
            'id_liquidacion_base': liquidacion_creada.id,
            'estado_liq': 'PENDIENTE',
            'fecha_estado': datetime.now()
        }
        serializer_historico = self.serializer_historico_class(data=data_historico)
        serializer_historico.is_valid(raise_exception=True)
        serializer_historico.save()

        return Response({'success': True, 'detail': 'Se ha creado la liquidación para el trámite correctamente', 'data': data_output}, status=status.HTTP_201_CREATED)

class HistLiquidacionTramiteGetView(generics.ListAPIView):
    queryset = HistEstadosLiq.objects.all()
    serializer_class = HistEstadosLiqGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key in ['num_liquidacion', 'id_solicitud_tramite', 'id_liquidacion_base', 'nombre_proyecto_tramite', 'fecha_inicio', 'fecha_fin', 'estado_liq'] and value != '':
                if key == 'num_liquidacion':
                    filter['id_liquidacion_base__'+key+'__icontains'] = value
                elif key == 'id_solicitud_tramite':
                    filter['id_liquidacion_base__'+key] = value
                elif key == 'nombre_proyecto_tramite':
                    filter['id_liquidacion_base__id_solicitud_tramite__nombre_proyecto__icontains'] = value
                elif key == 'fecha_inicio':
                    filter['fecha_estado__date__gte'] = value
                elif key == 'fecha_fin':
                    filter['fecha_estado__date__lte'] = value
                else:
                    filter[key] = value

        queryset = self.queryset.filter(**filter)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'message': 'Se encontraron los siguientes resultados', 'data': serializer.data}, status=status.HTTP_200_OK)

class ExpedientesView(generics.ListAPIView):
    queryset = Expedientes.objects.filter(id_deudor__isnull=False)
    serializer_class = ExpedientesSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ExpedienteEspecificoView(generics.ListAPIView):
    queryset = Expedientes.objects.all()
    serializer_class = ExpedientesSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = Expedientes.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun expendiente con el id ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ClonarOpcionLiquidacionView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        opcion = OpcionesLiquidacionBase.objects.filter(pk=pk)
        if len(opcion) == 0:
            return Response({'success': False, 'detail': 'No existen opción de liquidación para clonar'}, status=status.HTTP_200_OK)
        else:
            opcion_actual = opcion.get()
            opcion_nueva = OpcionesLiquidacionBase(
                nombre='Copia ' + opcion_actual.nombre,
                estado=opcion_actual.estado,
                version=opcion_actual.version,
                funcion=opcion_actual.funcion,
                variables=opcion_actual.variables,
                bloques=opcion_actual.bloques
            )
            opcion_nueva.save()
            serializer = self.serializer_class(opcion_nueva, many=False)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ExpedientesDeudorGetView(generics.ListAPIView):
    serializer_class = ExpedientesSerializer

    def get_expedientes_deudor(self, id_deudor):
        expedientes = Expedientes.objects.filter(id_deudor=id_deudor)
        if not expedientes:
            raise NotFound('No se encontró ningún registro en expedientes con el parámetro ingresado')
        serializer = self.serializer_class(expedientes, many=True)
        return serializer.data

    def get(self, request, id_deudor):
        expedientes = self.get_expedientes_deudor(id_deudor)
        return Response({'success': True, 'detail':'Se muestra los expedientes del deudor', 'data':expedientes}, status=status.HTTP_200_OK)


def obtener_dias_por_mes(anio):
    #TODO: Aqui se modifica la cantidad de dias por mes
    dias_por_mes = {}
    for mes in range(1, 13):
        dias_por_mes[mes] = calendar.monthrange(anio, mes)[1]
    return dias_por_mes


def liquidacionPdf(request, pk):
    ley = LeyesLiquidacion.objects.all().first()
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()
    anio = liquidacion.fecha_liquidacion.year
    tua = info.calculos['tarifa_tasa']
    caudalc = float(info.calculos['caudal_consecionado'])
    fop = float(info.calculos['factor_costo_oportunidad'])

    volumenMeses = []
    montopagarMeses = []
    totalliquidacion = 0
    liquidacionuno = 0
    liquidaciondos = 0

    dias_por_mes_actual = obtener_dias_por_mes(anio)

    for mes, dias in dias_por_mes_actual.items():
        volumen = round(float(caudalc * dias), 2)
        volumenMeses.append(volumen)
        valorPagar = round(float(tua * volumen * fop), 2)
        montopagarMeses.append(valorPagar)
        if mes < 7:
            liquidacionuno += valorPagar
        else:
            liquidaciondos += valorPagar
    totalliquidacion = liquidacionuno + liquidaciondos

    nombres = liquidacion.id_deudor.nombres.upper() if liquidacion.id_deudor.nombres is not None else ''
    apellidos = liquidacion.id_deudor.apellidos.upper() if liquidacion.id_deudor.apellidos is not None else ''

    context = {
        'rp': liquidacion.id, #referencia pago
        'limite_pago': liquidacion.vencimiento,
        'doc_cobro': '',
        'ley': ley.ley if ley.ley is not None else '',
        'fecha_impresion': liquidacion.fecha_liquidacion,
        'anio': anio,
        'cedula': liquidacion.id_deudor.identificacion,
        'titular': nombres + ' ' + apellidos,
        'representante_legal': '',
        'direccion': liquidacion.id_deudor.ubicacion_id.nombre.upper(),
        'telefono': liquidacion.id_deudor.telefono,
        'expediente': liquidacion.id_expediente.cod_expediente,
        'exp_resolucion': liquidacion.id_expediente.numero_resolucion,
        'nombre_fuente': str(info.calculos['nombre_fuente']).upper(),
        'predio': str(info.calculos['predio']).upper(),
        'municipio': str(info.calculos['municipio']).upper(),
        'caudal_consecionado': caudalc,
        'uso': str(info.calculos['uso']).upper(),
        'fr': info.calculos['factor_regional'], #factor regional
        'tt': tua, #tarifa de la tasa
        'numero_cuota': liquidacion.periodo_liquidacion,
        'valor_cuota': liquidacion.valor,
        'liquidacionuno': liquidacionuno,
        'liquidaciondos': liquidaciondos,
        'liquidaciontotal': totalliquidacion,
        'volumenMeses': volumenMeses,
        'montopagarMeses': montopagarMeses,
        'fco': fop,
        'codigo_barras': ''
    }

    pathToTemplate = str(settings.BASE_DIR) + '/recaudo/templates/TUA.docx'
    outputPath = str(settings.BASE_DIR) + '/recaudo/templates/output.docx'

    doc = DocxTemplate(pathToTemplate)
    doc.render(context)
    doc.save(outputPath)

    return render(request, 'liquidacion.html', context=context)


class CalculosLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = CalculosLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




#------------------------------stiven prueba--------------------------------------------
    

from io import BytesIO
from django.http import HttpResponse

class liquidacionPdfpruebaMigueluno(generics.ListAPIView):
    def get(self, request, pk):
        # Obtener los datos necesarios de la base de datos
        ley = LeyesLiquidacion.objects.all().first()
        liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
        info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()

        # Calcular los datos necesarios
        nombres = liquidacion.id_deudor.nombres.upper() if liquidacion.id_deudor.nombres else ''
        apellidos = liquidacion.id_deudor.apellidos.upper() if liquidacion.id_deudor.apellidos else ''
        anio = liquidacion.fecha_liquidacion.year
        tua = info.calculos['tarifa_tasa']
        caudalc = float(info.calculos['caudal_consecionado'])
        fop = float(info.calculos['factor_costo_oportunidad'])
        volumenMeses = []
        montopagarMeses = []
        totalliquidacion = 0
        liquidacionuno = 0
        liquidaciondos = 0
        dias_por_mes_actual = obtener_dias_por_mes(anio)

        for mes, dias in dias_por_mes_actual.items():
            volumen = round(float(caudalc * dias), 2)
            volumenMeses.append(volumen)
            valorPagar = round(float(tua * volumen * fop), 2)
            montopagarMeses.append(valorPagar)
            if mes < 7:
                liquidacionuno += valorPagar
            else:
                liquidaciondos += valorPagar
        totalliquidacion = liquidacionuno + liquidaciondos

        # Crear el contexto para el documento PDF
        context = {
            'rp': liquidacion.id,  # referencia pago
            'limite_pago': liquidacion.vencimiento,
            'doc_cobro': '',
            'ley': ley.ley if ley.ley else '',
            'fecha_impresion': liquidacion.fecha_liquidacion,
            'anio': anio,
            'cedula': liquidacion.id_deudor.identificacion,
            'titular': nombres + ' ' + apellidos,
            'representante_legal': '',
            'direccion': liquidacion.id_deudor.ubicacion_id.nombre.upper(),
            'telefono': liquidacion.id_deudor.telefono,
            'expediente': liquidacion.id_expediente.cod_expediente,
            'exp_resolucion': liquidacion.id_expediente.numero_resolucion,
            'nombre_fuente': str(info.calculos['nombre_fuente']).upper(),
            'predio': str(info.calculos['predio']).upper(),
            'municipio': str(info.calculos['municipio']).upper(),
            'caudal_consecionado': caudalc,
            'uso': str(info.calculos['uso']).upper(),
            'fr': info.calculos['factor_regional'],  # factor regional
            'tt': tua,  # tarifa de la tasa
            'numero_cuota': liquidacion.periodo_liquidacion,
            'valor_cuota': liquidacion.valor,
            'codigo_barras': '',
            'factor_costo_oportunidad': fop,
            'volumenMeses': volumenMeses,
            'montopagarMeses': montopagarMeses,
            'liquidacionuno': liquidacionuno,
            'liquidaciondos': liquidaciondos,
            'liquidaciontotal': totalliquidacion,
        }

        # Crear un documento Word
        # doc = Document()

        # # Agregar contenido al documento
        # doc.add_paragraph('Liquidación de prueba')
        # doc.add_paragraph('RP: {}'.format(context['rp']))
        # doc.add_paragraph('Fecha de impresión: {}'.format(context['fecha_impresion']))
        # doc.add_paragraph('Año: {}'.format(context['anio']))
        # doc.add_paragraph('Titular: {}'.format(context['titular']))
        # doc.add_paragraph('Dirección: {}'.format(context['direccion']))
        # # Agregar más contenido según sea necesario

        # # Guardar el documento en BytesIO
        # output = BytesIO()
        # doc.save(output)

        # Crear una respuesta HTTP con el contenido del BytesIO
        # response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        # response['Content-Disposition'] = 'attachment; filename=output.docx'
        # response.write(output.getvalue())

        return Response({'success': True, 'detail':'Se mostraron los datos', 'data':context}, status=status.HTTP_200_OK)


from django.http import JsonResponse
import base64

def liquidacionPdfpruebaMigueldos(request, pk):
    ley = LeyesLiquidacion.objects.all().first()
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()

    context = {
        'rp': liquidacion.id,
        'limite_pago': liquidacion.vencimiento,
        'doc_cobro': '',
        'ley': ley.ley if ley.ley is not None else '',
        'fecha_impresion': liquidacion.fecha_liquidacion,
        'anio': liquidacion.fecha_liquidacion.year,
        'cedula': liquidacion.id_deudor.identificacion,
        'titular': liquidacion.id_deudor.nombres.upper() + ' ' + liquidacion.id_deudor.apellidos.upper(),
        'representante_legal': '',
        'direccion': liquidacion.id_deudor.ubicacion_id.nombre.upper(),
        'telefono': liquidacion.id_deudor.telefono,
        'expediente': liquidacion.id_expediente.cod_expediente,
        'exp_resolucion': liquidacion.id_expediente.numero_resolucion,
        'nombre_fuente': str(info.calculos['nombre_fuente']).upper(),
        'predio': str(info.calculos['predio']).upper(),
        'municipio': str(info.calculos['municipio']).upper(),
        'caudal_consecionado': info.calculos['caudal_consecionado'],
        'uso': str(info.calculos['uso']).upper(),
        'fr': info.calculos['factor_regional'],
        'tt': info.calculos['tarifa_tasa'],
        'numero_cuota': liquidacion.periodo_liquidacion,
        'valor_cuota': liquidacion.valor,
        'codigo_barras': '',
        'factor_costo_oportunidad': info.calculos['factor_costo_oportunidad']
    }

    pathToTemplate = str(settings.BASE_DIR) + '/recaudo/templates/TUA.docx'
    outputPath = str(settings.BASE_DIR) + '/recaudo/templates/output.docx'

    doc = DocxTemplate(pathToTemplate)
    doc.render(context)

    # Crear un objeto BytesIO para almacenar el contenido del documento en memoria
    output = BytesIO()

    # Guardar el documento renderizado en el objeto BytesIO
    doc.save(output)

    # Crear una respuesta HTTP con el contenido del BytesIO
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=output.docx'
    response.write(output.getvalue())

    # Devolver la respuesta HTTP
    return response




class  LiquidacionPdfpruebaMiguelUpdate(generics.UpdateAPIView):
   
    def put(self,request,pk):
        data=request.data
        liquidacion = LiquidacionesBase.objects.filter(pk=pk).first()
        if not liquidacion : 
            raise NotFound("no se encontro la liquidacion buscada")
        info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).first()
        if not info : 
              raise NotFound("Aun no se ha creado el calculo")
        info.calculos['caudal_consecionado']=data.get('caudal_consecionado')
        info.save()
        return Response({'success': True, 'detail': 'Se actualizo la liquidacion'}, status=status.HTTP_200_OK)

