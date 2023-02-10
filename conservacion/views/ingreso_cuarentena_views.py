from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
import copy
import json

from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models.siembras_models import (
    CamasGerminacionVivero,
    Siembras,
    CamasGerminacionViveroSiembra,
    ConsumosSiembra,
)
from conservacion.models.viveros_models import (
    Vivero,
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
)
from conservacion.serializers.ingreso_cuarentena_serializers import (
    GetLotesEtapaSerializer,
    CreateIngresoCuarentenaSerializer
)
from conservacion.serializers.camas_siembras_serializers import (
    CamasGerminacionPost,
    CreateSiembrasSerializer,
    GetNumeroLoteSerializer,
    GetCamasGerminacionSerializer,
    CreateSiembraInventarioViveroSerializer,
    CreateBienesConsumidosSerializer,
    GetSiembraSerializer,
    GetBienesPorConsumirSerializer,
    UpdateSiembraSerializer,
    UpdateBienesConsumidosSerializer,
    DeleteSiembraSerializer,
    GetBienesConsumidosSiembraSerializer,
    GetBienSembradoSerializer,
    DeleteBienesConsumidosSerializer,
    GetSiembrasSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.cuarentena_models import (
    CuarentenaMatVegetal,
    ItemsLevantaCuarentena,
    BajasVivero
)
from conservacion.utils import UtilConservacion

class GetViveroView(generics.ListAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        viveros_habilitados = Vivero.objects.filter(activo=True, fecha_cierre_actual = None, id_persona_cierra = None, justificacion_cierre = None).exclude(fecha_ultima_apertura = None)
        serializer = self.serializer_class(viveros_habilitados, many=True)
        
        return Response({'succes': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class GetLotesEtapaView(generics.ListAPIView):
    serializer_class = GetLotesEtapaSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero, id_codigo):
        data = request.data

        #VALIDACIÓN QUE EL VIVERO SELECCIONADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No existe ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EL CODIGO ENVIADO EXISTA EN ALGÚN BIEN EN INVENTARIO VIVEROS
        etapas_lotes_in_vivero = InventarioViveros.objects.filter(id_bien__codigo_bien=id_codigo, id_vivero=id_vivero, id_siembra_lote_germinacion=None)
        if not etapas_lotes_in_vivero:
            return Response({'success': False, 'detail': 'El codigo ingresado no existe en una etapa lote'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL CODIGO ENVIADO PERTENEZCA A UN BIEN MATERIAL VEGETAL QUE NO SEA SEMILLA
        if etapas_lotes_in_vivero[0].id_bien.cod_tipo_elemento_vivero != 'MV':
            return Response({'success': False, 'detail': 'El código debe pertenecer a un bien de tipo material vegetal'}, status=status.HTTP_403_FORBIDDEN)            
        if etapas_lotes_in_vivero[0].id_bien.cod_tipo_elemento_vivero == 'MV' and etapas_lotes_in_vivero[0].id_bien.es_semilla_vivero != False:
            return Response({'success': False, 'detail': 'El código debe pertenecer a un material vegetal que no sea semilla'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDAR CANTIDADES DISPONIBLES
        for etapa_lote in etapas_lotes_in_vivero:
            porc_cuarentena_lote_germinacion = etapa_lote.porc_cuarentena_lote_germinacion if etapa_lote.porc_cuarentena_lote_germinacion else 0
            cantidad_entrante = etapa_lote.cantidad_entrante if etapa_lote.cantidad_entrante else 0
            cantidad_bajas = etapa_lote.cantidad_bajas if etapa_lote.cantidad_bajas else 0
            cantidad_traslados_lote_produccion_distribucion = etapa_lote.cantidad_traslados_lote_produccion_distribucion if etapa_lote.cantidad_traslados_lote_produccion_distribucion else 0
            cantidad_salidas = etapa_lote.cantidad_salidas if etapa_lote.cantidad_salidas else 0
            cantidad_lote_cuarentena = etapa_lote.cantidad_lote_cuarentena if etapa_lote.cantidad_lote_cuarentena else 0


            if etapa_lote.cod_etapa_lote == 'G':
                etapa_lote.cod_etapa_lote = 'Germinación'
                etapa_lote.saldo_disponible = 100 - porc_cuarentena_lote_germinacion
            if etapa_lote.cod_etapa_lote == 'P':
                etapa_lote.cod_etapa_lote = 'Producción'
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
            if etapa_lote.cod_etapa_lote == 'D':
                etapa_lote.cod_etapa_lote = 'Distribución'
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena

        serializer = self.serializer_class(etapas_lotes_in_vivero, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class GetLotesEtapaLupaView(generics.ListAPIView):
    serializer_class = GetLotesEtapaSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):

        #VALIDACIÓN QUE EL VIVERO SELECCIONADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No existe ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

        #CREACIÓN DE FILTROS SEGÚN QUERYPARAMS
        filter = {}
        for key, value in request.query_params.items():
            if key in ['codigo_bien', 'nombre', 'agno_lote', 'cod_etapa_lote']:
                if key == 'codigo_bien' or key == 'nombre':
                    filter['id_bien__' + key + '__icontains'] = value
                else:
                    filter[key] = value

        #VALIDACIÓN QUE EL CODIGO ENVIADO EXISTA EN ALGÚN BIEN EN INVENTARIO VIVEROS
        etapas_lotes_in_vivero = InventarioViveros.objects.filter(id_vivero=id_vivero, id_siembra_lote_germinacion=None).exclude(~Q(id_bien__cod_tipo_elemento_vivero='MV')).exclude(id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=True).filter(**filter)
        if not etapas_lotes_in_vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún material vegetal disponible'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR CANTIDADES DISPONIBLES
        for etapa_lote in etapas_lotes_in_vivero:
            porc_cuarentena_lote_germinacion = etapa_lote.porc_cuarentena_lote_germinacion if etapa_lote.porc_cuarentena_lote_germinacion else 0
            cantidad_entrante = etapa_lote.cantidad_entrante if etapa_lote.cantidad_entrante else 0
            cantidad_bajas = etapa_lote.cantidad_bajas if etapa_lote.cantidad_bajas else 0
            cantidad_traslados_lote_produccion_distribucion = etapa_lote.cantidad_traslados_lote_produccion_distribucion if etapa_lote.cantidad_traslados_lote_produccion_distribucion else 0
            cantidad_salidas = etapa_lote.cantidad_salidas if etapa_lote.cantidad_salidas else 0
            cantidad_lote_cuarentena = etapa_lote.cantidad_lote_cuarentena if etapa_lote.cantidad_lote_cuarentena else 0


            if etapa_lote.cod_etapa_lote == 'G':
                etapa_lote.cod_etapa_lote = 'Germinación'
                etapa_lote.saldo_disponible = 100 - porc_cuarentena_lote_germinacion
            if etapa_lote.cod_etapa_lote == 'P':
                etapa_lote.cod_etapa_lote = 'Producción'
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
            if etapa_lote.cod_etapa_lote == 'D':
                etapa_lote.cod_etapa_lote = 'Distribución'
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena


        serializer = self.serializer_class(etapas_lotes_in_vivero, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class CreateIngresoCuarentenaView(generics.CreateAPIView):
    serializer_class = CreateIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_cuarentena = json.loads(request.data['data_ingreso_cuarentena'])
        data_cuarentena['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        data_cuarentena['id_persona_cuarentena'] = request.user.persona.id_persona

        #VALIDACIÓN QUE EL VIVERO ENVIADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=data_cuarentena['id_vivero'], activo=True).first()
        if not vivero:
            return Response({'success': False, 'detail': 'El vivero seleccionado no existe'})
        
        #VALIDACIÓN QUE EL ID BIEN SELECCIONADO EXISTA
        bien = CatalogoBienes.objects.filter(id_bien=data_cuarentena['id_bien']).first()
        if not bien:
            return Response({'success': False, 'detail': 'El bien seleccionado no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EL CODIGO ENVIADO PERTENEZCA A UN BIEN MATERIAL VEGETAL QUE NO SEA SEMILLA
        if bien.cod_tipo_elemento_vivero != 'MV':
            return Response({'success': False, 'detail': 'El código debe pertenecer a un bien de tipo material vegetal'}, status=status.HTTP_403_FORBIDDEN)            
        if bien.cod_tipo_elemento_vivero == 'MV' and bien.es_semilla_vivero != False:
            return Response({'success': False, 'detail': 'El código debe pertenecer a un material vegetal que no sea semilla'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN DE FECHA CUARENTENA
        fecha_cuarentena = data_cuarentena['fecha_cuarentena']
        fecha_strptime = datetime.strptime(fecha_cuarentena, '%Y-%m-%d %H:%M:%S')
        if fecha_strptime < (datetime.now() - timedelta(hours=24)):
            return Response({'success': False, 'detail': 'No se puede realizar un ingreso a cuarentena con más de 24 horas de anterioridad'}, status=status.HTTP_400_BAD_REQUEST)

        #ASIGNACIÓN NÚMERO CONSECUTIVO
        ingreso_cuarentena = CuarentenaMatVegetal.objects.filter(id_vivero=data_cuarentena['id_vivero'], id_bien=data_cuarentena['id_bien'], agno_lote=data_cuarentena['agno_lote'], nro_lote=data_cuarentena['nro_lote']).order_by('-consec_cueren_por_lote_etapa').first()
        numero_consecutivo = 0
        if ingreso_cuarentena:
            numero_consecutivo = ingreso_cuarentena.consec_cueren_por_lote_etapa
        data_cuarentena['consec_cueren_por_lote_etapa'] = numero_consecutivo + 1

        #VALIDACIÓN CANTIDAD INGRESADA A CUARENTENA
        if data_cuarentena['cantidad_cuarentena'] <= 0:
            return Response({'success': False, 'detail': 'No se puede realizar un ingreso a cuarentena con cantidad 0'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN QUE LA FECHA SEA SUPERIOR AL ÚLTIMO INGRESO CUARENTENA POR LOTE ETAPA
        if ingreso_cuarentena:
            if fecha_strptime <= ingreso_cuarentena.fecha_cuarentena:
                return Response({'success': False, 'detail': 'La fecha del ingreso a cuarentena debe ser mayor a la fecha de la última cuarentena para este lote'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN QUE LA FECHA SEA SUPERIOR AL INGRESO DEL LOTE EN LA ETAPA
        lote_etapa_inventario = InventarioViveros.objects.filter(id_vivero=data_cuarentena['id_vivero'], id_bien=data_cuarentena['id_bien'], agno_lote=data_cuarentena['agno_lote'], nro_lote=data_cuarentena['nro_lote']).first()
        if fecha_strptime <= lote_etapa_inventario.fecha_ingreso_lote_etapa:
            return Response({'success': False, 'detail': 'La fecha del ingreso a cuarentena debe ser posterior a la fecha de ingreso del lote en la etapa'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDICACIÓN QUE EXISTA CANTIDAD O PORCENTAJE SUFICIENTE PARA PONER EN CUARENTENA
        if lote_etapa_inventario.cod_etapa_lote == 'G':
            porcentaje_actual = lote_etapa_inventario.porc_cuarentena_lote_germinacion if lote_etapa_inventario.porc_cuarentena_lote_germinacion else 0
            if porcentaje_actual == 100:
                return Response({'success': False, 'detail': f'Esta etapa lote ya tiene el 100% en cuarentena'}, status=status.HTTP_400_BAD_REQUEST)
            porcentaje_nuevo = porcentaje_actual + data_cuarentena['cantidad_cuarentena']
            if porcentaje_nuevo > 100:
                return Response({'success': False, 'detail': f'No se puede crear un ingreso a cuarentena con un porcentaje mayor a 100%'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            cantidad_actual = lote_etapa_inventario.cantidad_lote_cuarentena if lote_etapa_inventario.cantidad_lote_cuarentena else 0
            if cantidad_actual == lote_etapa_inventario.cantidad_entrante:
                return Response({'success': False, 'detail': 'Esta etapa lote ya tiene todas sus cantidades en cuarentena'}, status=status.HTTP_400_BAD_REQUEST)
            cantidad_nueva = cantidad_actual + data_cuarentena['cantidad_cuarentena']
            if cantidad_nueva > lote_etapa_inventario.cantidad_entrante:
                return Response({'success': False, 'detail': f'No se puede crear un ingreso a cuarentena con cantidades mayores a las disponibles'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL MOTIVO NO SEA ENVIADO EN NULL
        if data_cuarentena['motivo'] == None or data_cuarentena['motivo'] == '':
            return Response({'success': False, 'detail': 'El motivo del ingreso a cuarentena no debe ser enviado vacío'}, status=status.HTTP_400_BAD_REQUEST)

        #ASIGNACIÓN DE CANTIDAD LEVANTADA Y CANTIDAD BAJAS
        data_cuarentena['cantidad_levantada'] = 0
        data_cuarentena['cantidad_bajas'] = 0

        #VALIDACIÓN DEL PORCENTAJE ENVIADO CUANDO LA ETAPA ES GERMINACIÓN
        if lote_etapa_inventario.cod_etapa_lote == 'G':
            if data_cuarentena['cantidad_cuarentena'] > 100:
                return Response({'success': False, 'detail': 'No se puede enviar un porcentaje superior a 100'}, status=status.HTTP_400_BAD_REQUEST)
            
        #VALIDACIÓN DE LA CANTIDAD ENVIADA CUANDO LA ETAPA ES PRODUCCIÓN O DISTRIBUCIÓN
        if lote_etapa_inventario.cod_etapa_lote == 'P' or lote_etapa_inventario.cod_etapa_lote == 'D':
            if data_cuarentena['cantidad_cuarentena'] > lote_etapa_inventario.cantidad_entrante:
                return Response({'success': False, 'detail': 'No se puede ingresar a cuarentena una cantidad mayor a la existente'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data_cuarentena, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        if lote_etapa_inventario.cod_etapa_lote == 'G':
            porcentaje_actual = lote_etapa_inventario.porc_cuarentena_lote_germinacion if lote_etapa_inventario.porc_cuarentena_lote_germinacion else 0
            lote_etapa_inventario.porc_cuarentena_lote_germinacion = porcentaje_actual + serializador.cantidad_cuarentena
            lote_etapa_inventario.save()

        else:
            cantidad_actual = lote_etapa_inventario.cantidad_lote_cuarentena if lote_etapa_inventario.cantidad_lote_cuarentena else 0
            lote_etapa_inventario.cantidad_lote_cuarentena = cantidad_actual + serializador.cantidad_cuarentena
            lote_etapa_inventario.save()

        

        return Response({'success': True, 'detail': 'Ingreso a cuarentena creado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)