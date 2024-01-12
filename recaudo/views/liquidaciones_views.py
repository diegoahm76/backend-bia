from recaudo.models.base_models import (
    LeyesLiquidacion
)
from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes,
    CalculosLiquidacionBase
)
from recaudo.serializers.liquidaciones_serializers import (
    OpcionesLiquidacionBaseSerializer,
    OpcionesLiquidacionBasePutSerializer,
    DeudoresSerializer,
    LiquidacionesBaseSerializer,
    LiquidacionesBasePostSerializer,
    DetallesLiquidacionBaseSerializer,
    DetallesLiquidacionBasePostSerializer,
    ExpedientesSerializer,
    CalculosLiquidacionBaseSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import render
from docxtpl import DocxTemplate
from django.conf import settings


class OpcionesLiquidacionBaseView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

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
    #permission_classes = [IsAuthenticated]

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

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LiquidacionesBasePostSerializer(data=request.data)
        if serializer.is_valid():
            id_expediente = request.data['id_expediente']
            if id_expediente is not None:
                expediente = Expedientes.objects.get(pk=id_expediente)
                expediente.estado = 'guardado'
                serializer.save()
                expediente.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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


def liquidacionPdf(request, pk):
    ley = LeyesLiquidacion.objects.all().first()
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()

    context = {
        'rp': liquidacion.id, #referencia pago
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
        'fr': info.calculos['factor_regional'], #factor regional
        'tt': info.calculos['tarifa_tasa'], #tarifa de la tasa

        'numero_cuota': liquidacion.periodo_liquidacion,
        'valor_cuota': liquidacion.valor,

        'codigo_barras': '',

        'factor_costo_oportunidad': info.calculos['factor_costo_oportunidad']
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

def liquidacionPdfpruebaMigueluno(request, pk):
    ley = LeyesLiquidacion.objects.all().first()
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()

    context = {
        'rp': liquidacion.id,  # referencia pago
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
        'fr': info.calculos['factor_regional'],  # factor regional
        'tt': info.calculos['tarifa_tasa'],  # tarifa de la tasa
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


from django.http import JsonResponse
import base64


def liquidacionPdfpruebaMigueldos(request, pk):
    ley = LeyesLiquidacion.objects.all().first()
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    info = CalculosLiquidacionBase.objects.filter(id_liquidacion=liquidacion.id).get()

    context = {
        'rp': liquidacion.id,
        # ... (otros campos del contexto)
    }

    path_to_template = str(settings.BASE_DIR) + '/recaudo/templates/TUA.docx'

    # Crear un objeto BytesIO para almacenar el contenido del documento en memoria
    output = BytesIO()

    # Renderizar y guardar el documento en BytesIO
    doc = DocxTemplate(path_to_template)
    doc.render(context)
    doc.save(output)

    # Convertir el contenido a base64
    encoded_content = base64.b64encode(output.getvalue()).decode('utf-8')

    # Crear un objeto JSON para enviar al frontend
    response_data = {
        'content': encoded_content,
        'filename': 'output.docx',
    }

    # Enviar la respuesta como JSON
    return JsonResponse(response_data)