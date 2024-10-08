from rest_framework import generics, status
from rest_framework.views import APIView
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from seguridad.permissions.permissions_conservacion import PermisoActualizarIngresoCuarentenaMaterialVegetal, PermisoAnularIngresoCuarentenaMaterialVegetal, PermisoCrearIngresoCuarentenaMaterialVegetal
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
from conservacion.utils import UtilConservacion
import copy
import json

from transversal.models.personas_models import Personas
from conservacion.models.viveros_models import (
    Vivero,
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
)
from conservacion.serializers.ingreso_cuarentena_serializers import (
    GetLotesEtapaSerializer,
    CreateIngresoCuarentenaSerializer,
    AnularIngresoCuarentenaSerializer,
    UpdateIngresoCuarentenaSerializer,
    GetIngresoCuarentenaSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.cuarentena_models import (
    CuarentenaMatVegetal,
)

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
            raise NotFound('No existe ningún vivero con el parámetro ingresado')
        
        #VALIDACIÓN QUE EL CODIGO ENVIADO EXISTA EN ALGÚN BIEN EN INVENTARIO VIVEROS
        etapas_lotes_in_vivero = InventarioViveros.objects.filter(id_bien__codigo_bien=id_codigo, id_vivero=id_vivero, id_siembra_lote_germinacion=None)
        if not etapas_lotes_in_vivero:
            raise ValidationError('El codigo ingresado no existe en una etapa lote')

        #VALIDACIÓN QUE EL CODIGO ENVIADO PERTENEZCA A UN BIEN MATERIAL VEGETAL QUE NO SEA SEMILLA
        if etapas_lotes_in_vivero[0].id_bien.cod_tipo_elemento_vivero != 'MV':
            raise PermissionDenied('El código debe pertenecer a un bien de tipo material vegetal')            
        if etapas_lotes_in_vivero[0].id_bien.cod_tipo_elemento_vivero == 'MV' and etapas_lotes_in_vivero[0].id_bien.es_semilla_vivero != False:
            raise PermissionDenied('El código debe pertenecer a un material vegetal que no sea semilla')

        #VALIDAR CANTIDADES DISPONIBLES
        for etapa_lote in etapas_lotes_in_vivero:
            porc_cuarentena_lote_germinacion = etapa_lote.porc_cuarentena_lote_germinacion if etapa_lote.porc_cuarentena_lote_germinacion else 0
            cantidad_entrante = etapa_lote.cantidad_entrante if etapa_lote.cantidad_entrante else 0
            cantidad_bajas = etapa_lote.cantidad_bajas if etapa_lote.cantidad_bajas else 0
            cantidad_traslados_lote_produccion_distribucion = etapa_lote.cantidad_traslados_lote_produccion_distribucion if etapa_lote.cantidad_traslados_lote_produccion_distribucion else 0
            cantidad_salidas = etapa_lote.cantidad_salidas if etapa_lote.cantidad_salidas else 0
            cantidad_lote_cuarentena = etapa_lote.cantidad_lote_cuarentena if etapa_lote.cantidad_lote_cuarentena else 0


            if etapa_lote.cod_etapa_lote == 'G':
                etapa_lote.saldo_disponible = 100 - porc_cuarentena_lote_germinacion
            if etapa_lote.cod_etapa_lote == 'P':
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
            if etapa_lote.cod_etapa_lote == 'D':
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
            raise NotFound ('No existe ningún vivero con el parámetro ingresado')

        #CREACIÓN DE FILTROS SEGÚN QUERYPARAMS
        filter = {}
        for key, value in request.query_params.items():
            if key in ['codigo_bien', 'nombre', 'agno_lote', 'cod_etapa_lote']:
                if key == 'codigo_bien' or key == 'nombre':
                    if value != '':
                        filter['id_bien__' + key + '__icontains'] = value
                else:
                    if value != '':
                        filter[key] = value

        #VALIDACIÓN QUE EL CODIGO ENVIADO EXISTA EN ALGÚN BIEN EN INVENTARIO VIVEROS
        etapas_lotes_in_vivero = InventarioViveros.objects.filter(id_vivero=id_vivero, id_siembra_lote_germinacion=None).exclude(~Q(id_bien__cod_tipo_elemento_vivero='MV')).exclude(id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=True).filter(**filter)
        if not etapas_lotes_in_vivero:
            raise ValidationError('No se encontró ningún material vegetal disponible')
        
        #VALIDAR CANTIDADES DISPONIBLES
        for etapa_lote in etapas_lotes_in_vivero:
            porc_cuarentena_lote_germinacion = etapa_lote.porc_cuarentena_lote_germinacion if etapa_lote.porc_cuarentena_lote_germinacion else 0
            cantidad_entrante = etapa_lote.cantidad_entrante if etapa_lote.cantidad_entrante else 0
            cantidad_bajas = etapa_lote.cantidad_bajas if etapa_lote.cantidad_bajas else 0
            cantidad_traslados_lote_produccion_distribucion = etapa_lote.cantidad_traslados_lote_produccion_distribucion if etapa_lote.cantidad_traslados_lote_produccion_distribucion else 0
            cantidad_salidas = etapa_lote.cantidad_salidas if etapa_lote.cantidad_salidas else 0
            cantidad_lote_cuarentena = etapa_lote.cantidad_lote_cuarentena if etapa_lote.cantidad_lote_cuarentena else 0


            if etapa_lote.cod_etapa_lote == 'G':
                etapa_lote.saldo_disponible = 100 - porc_cuarentena_lote_germinacion
            if etapa_lote.cod_etapa_lote == 'P':
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_traslados_lote_produccion_distribucion - cantidad_salidas - cantidad_lote_cuarentena
            if etapa_lote.cod_etapa_lote == 'D':
                etapa_lote.saldo_disponible = cantidad_entrante - cantidad_bajas - cantidad_salidas - cantidad_lote_cuarentena


        serializer = self.serializer_class(etapas_lotes_in_vivero, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class CreateIngresoCuarentenaView(generics.CreateAPIView):
    serializer_class = CreateIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated, PermisoCrearIngresoCuarentenaMaterialVegetal]

    def post(self, request):
        data_cuarentena = json.loads(request.data['data_ingreso_cuarentena'])
        archivo_soporte = request.FILES.get('ruta_archivo_soporte')
        data_cuarentena['id_persona_cuarentena'] = request.user.persona.id_persona

        #VALIDACIÓN QUE EL VIVERO ENVIADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=data_cuarentena['id_vivero'], activo=True).first()
        if not vivero:
            raise ValidationError('El vivero seleccionado no existe')
        
        #VALIDACIÓN QUE EL ID BIEN SELECCIONADO EXISTA
        bien = CatalogoBienes.objects.filter(id_bien=data_cuarentena['id_bien']).first()
        if not bien:
            raise NotFound('El bien seleccionado no existe')
        
        #VALIDACIÓN QUE EL CODIGO ENVIADO PERTENEZCA A UN BIEN MATERIAL VEGETAL QUE NO SEA SEMILLA
        if bien.cod_tipo_elemento_vivero != 'MV':
            raise PermissionDenied('El código debe pertenecer a un bien de tipo material vegetal')            
        if bien.cod_tipo_elemento_vivero == 'MV' and bien.es_semilla_vivero != False:
            raise PermissionDenied('El código debe pertenecer a un material vegetal que no sea semilla')

        #VALIDACIÓN DE FECHA CUARENTENA
        fecha_cuarentena = data_cuarentena['fecha_cuarentena']
        fecha_strptime = datetime.strptime(fecha_cuarentena, '%Y-%m-%d %H:%M:%S')
        if fecha_strptime < (datetime.now() - timedelta(hours=24)):
            raise ValidationError('No se puede realizar un ingreso a cuarentena con más de 24 horas de anterioridad')

        #ASIGNACIÓN NÚMERO CONSECUTIVO
        ingreso_cuarentena_instance = CuarentenaMatVegetal.objects.filter(id_vivero=data_cuarentena['id_vivero'], id_bien=data_cuarentena['id_bien'], agno_lote=data_cuarentena['agno_lote'], nro_lote=data_cuarentena['nro_lote']).order_by('-consec_cueren_por_lote_etapa')
        ingreso_cuarentena = ingreso_cuarentena_instance.first()
        ultimo_cuarentena_no_anulado = ingreso_cuarentena_instance.exclude(cuarentena_anulada=True).first()
        numero_consecutivo = 0
        if ingreso_cuarentena:
            numero_consecutivo = ingreso_cuarentena.consec_cueren_por_lote_etapa
        data_cuarentena['consec_cueren_por_lote_etapa'] = numero_consecutivo + 1

        #VALIDACIÓN CANTIDAD INGRESADA A CUARENTENA
        if data_cuarentena['cantidad_cuarentena'] <= 0:
            raise PermissionDenied('No se puede realizar un ingreso a cuarentena con cantidad 0')

        #VALIDACIÓN QUE LA FECHA SEA SUPERIOR AL ÚLTIMO INGRESO CUARENTENA POR LOTE ETAPA
        if ultimo_cuarentena_no_anulado:
            if fecha_strptime <= ultimo_cuarentena_no_anulado.fecha_cuarentena:
                raise PermissionDenied('La fecha del ingreso a cuarentena debe ser mayor a la fecha de la última cuarentena para este lote')

        #VALIDACIÓN QUE LA FECHA SEA SUPERIOR AL INGRESO DEL LOTE EN LA ETAPA
        lote_etapa_inventario = InventarioViveros.objects.filter(id_vivero=data_cuarentena['id_vivero'], id_bien=data_cuarentena['id_bien'], agno_lote=data_cuarentena['agno_lote'], nro_lote=data_cuarentena['nro_lote'], cod_etapa_lote=data_cuarentena['cod_etapa_lote']).first()
        if fecha_strptime <= lote_etapa_inventario.fecha_ingreso_lote_etapa:
            raise PermissionDenied('La fecha del ingreso a cuarentena debe ser posterior a la fecha de ingreso del lote en la etapa')

        #VALIDICACIÓN QUE EXISTA CANTIDAD O PORCENTAJE SUFICIENTE PARA PONER EN CUARENTENA
        if lote_etapa_inventario.cod_etapa_lote == 'G':
            porcentaje_actual = lote_etapa_inventario.porc_cuarentena_lote_germinacion if lote_etapa_inventario.porc_cuarentena_lote_germinacion else 0
            if porcentaje_actual == 100:
                raise ValidationError (f'Esta etapa lote ya tiene el 100% en cuarentena')
            porcentaje_nuevo = porcentaje_actual + data_cuarentena['cantidad_cuarentena']
            if porcentaje_nuevo > 100:
                raise ValidationError (f'No se puede crear un ingreso a cuarentena con un porcentaje mayor a 100%')

        else:
            cantidad_actual = lote_etapa_inventario.cantidad_lote_cuarentena if lote_etapa_inventario.cantidad_lote_cuarentena else 0
            if cantidad_actual == lote_etapa_inventario.cantidad_entrante:
                raise ValidationError('Esta etapa lote ya tiene todas sus cantidades en cuarentena')
            cantidad_nueva = cantidad_actual + data_cuarentena['cantidad_cuarentena']
            if cantidad_nueva > lote_etapa_inventario.cantidad_entrante:
                raise ValidationError (f'No se puede crear un ingreso a cuarentena con cantidades mayores a las disponibles')

        #VALIDACIÓN QUE EL MOTIVO NO SEA ENVIADO EN NULL
        if data_cuarentena['motivo'] == None or data_cuarentena['motivo'] == '':
            raise ValidationError('El motivo del ingreso a cuarentena no debe ser enviado vacío')

        #ASIGNACIÓN DE CANTIDAD LEVANTADA Y CANTIDAD BAJAS
        data_cuarentena['cantidad_levantada'] = 0
        data_cuarentena['cantidad_bajas'] = 0

        #VALIDACIÓN DEL PORCENTAJE ENVIADO CUANDO LA ETAPA ES GERMINACIÓN
        if lote_etapa_inventario.cod_etapa_lote == 'G':
            if data_cuarentena['cantidad_cuarentena'] > 100:
                raise ValidationError ('No se puede enviar un porcentaje superior a 100')
            
        #VALIDACIÓN DE LA CANTIDAD ENVIADA CUANDO LA ETAPA ES PRODUCCIÓN O DISTRIBUCIÓN
        if lote_etapa_inventario.cod_etapa_lote == 'P' or lote_etapa_inventario.cod_etapa_lote == 'D':
            if data_cuarentena['cantidad_cuarentena'] > lote_etapa_inventario.cantidad_entrante:
                raise ValidationError ('No se puede ingresar a cuarentena una cantidad mayor a la existente')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "IngresoCuarentena")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data_cuarentena['ruta_archivo_soporte'] = archivo_creado_instance.id_archivo_digital

        serializer = self.serializer_class(data=data_cuarentena, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()
        
        if lote_etapa_inventario.cod_etapa_lote == 'G':
            porcentaje_actual = lote_etapa_inventario.porc_cuarentena_lote_germinacion if lote_etapa_inventario.porc_cuarentena_lote_germinacion else 0
            lote_etapa_inventario.porc_cuarentena_lote_germinacion = porcentaje_actual + serializador.cantidad_cuarentena

        else:
            cantidad_actual = lote_etapa_inventario.cantidad_lote_cuarentena if lote_etapa_inventario.cantidad_lote_cuarentena else 0
            lote_etapa_inventario.cantidad_lote_cuarentena = cantidad_actual + serializador.cantidad_cuarentena
        
        lote_etapa_inventario.save()

        # AUDITORIA ELIMINACIÓN DE CREAR CUARENTENA
        descripcion = {"nombre_vivero": str(serializador.id_bien.nombre), "nombre_bien": str(serializador.id_vivero.id_vivero), "agno": str(serializador.agno_lote), "nro_lote": str(serializador.nro_lote), "etapa_lote": str(serializador.cod_etapa_lote), "fecha_hora_cuarentena": str(serializador.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Ingreso a cuarentena creado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    

class AnularIngresoCuarentenaView(generics.RetrieveUpdateAPIView):
    serializer_class = AnularIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated, PermisoAnularIngresoCuarentenaMaterialVegetal]

    def put(self, request, id_ingreso_cuarentena):
        data = request.data
        data['fecha_anulacion'] = datetime.now()
        data['id_persona_anula'] = request.user.persona.id_persona

        #VALIDACIÓN SI EXISTE LA CUARENTENA SELECCIONADA
        cuarentena = CuarentenaMatVegetal.objects.filter(id_cuarentena_mat_vegetal=id_ingreso_cuarentena).first()
        if not cuarentena:
            raise ValidationError ('No existe ninguna cuarentena con el parámetro ingresado')

        #VALIDACIÓN SI LA CUARENTENA YA HA SIDO ANULADA
        if cuarentena.cuarentena_anulada != False:
            raise ValidationError ('No se puede anular una entrada que ya ha sido anulada')

        #VALIDACIÓN SI LA CUARENTENA HA TENIDO LEVANTAMIENTOS
        if cuarentena.cantidad_levantada != 0:
            raise PermissionDenied('No se puede anular un ingreso a cuarentena que ha tenido levantamientos')
        
        #VALIDACIÓN SI LA CUARENTENA HA TENIDO MORTALIDAD
        if cuarentena.cantidad_bajas != 0:
            raise PermissionDenied('No se puede anular un ingreso a cuarentena si ha tenido mortalidad')
        
        #PENDIENTE VALIDACIÓN EN TABLA 171

        #VALIDACIÓN QUE LA FECHA NO PUEDE SER MAYOR A 48 HORAS DESPUES DE LA CREACIÓN
        if data['fecha_anulacion'] > (cuarentena.fecha_cuarentena + timedelta(hours=48)):
            raise PermissionDenied('No se puede anular un ingreso a cuarentena despues de 48 horas de la creación')
        
        serializer = self.serializer_class(cuarentena, data=data, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #ACCIONES EN INVENTARIO VIVEROS SEGÚN EL LOTE ETAPA
        lote_etapa_in_inventario = InventarioViveros.objects.filter(id_vivero=cuarentena.id_vivero.id_vivero, id_bien=cuarentena.id_bien.id_bien, agno_lote=cuarentena.agno_lote, nro_lote=cuarentena.nro_lote, cod_etapa_lote=cuarentena.cod_etapa_lote).first()
        if lote_etapa_in_inventario.cod_etapa_lote == 'G':
            porcentaje_actual = lote_etapa_in_inventario.porc_cuarentena_lote_germinacion if lote_etapa_in_inventario.porc_cuarentena_lote_germinacion else 0
            lote_etapa_in_inventario.porc_cuarentena_lote_germinacion = porcentaje_actual - cuarentena.cantidad_cuarentena
            lote_etapa_in_inventario.save()
        
        else:
            cantidad_actual = lote_etapa_in_inventario.cantidad_lote_cuarentena if lote_etapa_in_inventario.cantidad_lote_cuarentena else 0
            lote_etapa_in_inventario.cantidad_lote_cuarentena = cantidad_actual - cuarentena.cantidad_cuarentena
            lote_etapa_in_inventario.save()

        # AUDITORIA ELIMINACIÓN DE ANULAR CUARENTENA
        descripcion = {"nombre_vivero": str(cuarentena.id_bien.nombre), "nombre_bien": str(cuarentena.id_vivero.id_vivero), "agno": str(cuarentena.agno_lote), "nro_lote": str(cuarentena.nro_lote), "etapa_lote": str(cuarentena.cod_etapa_lote), "fecha_hora_cuarentena": str(cuarentena.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "AN",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Ingreso a cuarentena anulado exitosamente'}, status=status.HTTP_201_CREATED)

class UpdateIngresoCuarentenaView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarIngresoCuarentenaMaterialVegetal]


    def put(self, request, id_ingreso_cuarentena):

        data = json.loads(request.data['data'])
        archivo_soporte = request.FILES.get('ruta_archivo_soporte')
        data._mutable=True
        
        data['fecha_actualizacion'] = datetime.now()

        #VALIDACIÓN SI EXISTE LA CUARENTENA SELECCIONADA
        cuarentena = CuarentenaMatVegetal.objects.filter(id_cuarentena_mat_vegetal=id_ingreso_cuarentena).first()
        cuarentena_copy = copy.copy(cuarentena)
        if not cuarentena:
            raise ValidationError ('No existe ninguna cuarentena con el parámetro ingresado')

        #VALIDACIÓN SI LA CUARENTENA YA HA SIDO ANULADA
        if cuarentena.cuarentena_anulada != False:
            raise ValidationError ('No se puede actualizar una entrada que ya ha sido anulada')

        #VALIDACIÓN SI LA CUARENTENA HA TENIDO LEVANTAMIENTOS
        if cuarentena.cantidad_levantada != 0:
            raise PermissionDenied('No se puede actualizar un ingreso a cuarentena que ha tenido levantamientos')
        
        #VALIDACIÓN SI LA CUARENTENA HA TENIDO MORTALIDAD
        if cuarentena.cantidad_bajas != 0:
            raise PermissionDenied('No se puede actualizar un ingreso a cuarentena si ha tenido mortalidad')
        
        #VALIDACIÓN SI ACTUALIZAN CANTIDADES O NO
        lote_etapa_in_inventario_viveros = InventarioViveros.objects.filter(id_vivero=cuarentena.id_vivero.id_vivero, id_bien=cuarentena.id_bien.id_bien, agno_lote=cuarentena.agno_lote, nro_lote=cuarentena.nro_lote, cod_etapa_lote=cuarentena.cod_etapa_lote, id_siembra_lote_germinacion=None).first()
        if data['cantidad_cuarentena'] != cuarentena.cantidad_cuarentena:
            if data['fecha_actualizacion'] > (cuarentena.fecha_cuarentena + timedelta(hours=48)):
                raise ValidationError('La cantidad en cuarentena solo se puede modificar hasta 48 horas despues de la creación')
                
            if data['cantidad_cuarentena'] > cuarentena.cantidad_cuarentena:
                if cuarentena.cod_etapa_lote == 'G':
                    if data['cantidad_cuarentena'] > 100:
                        raise ValidationError (f'La cantidad actualizada debe ser maximo del 100% de la cuarentena')
                    if (data['cantidad_cuarentena'] + lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion - cuarentena.cantidad_cuarentena) > 100:
                        raise ValidationError (f'La cantidad actualizada debe ser maximo del 100% de la cuarentena')
                else:
                    if data['cantidad_cuarentena'] > lote_etapa_in_inventario_viveros.cantidad_entrante:
                        raise ValidationError ('La cantidad actualizada debe ser menor a la disponible por ingresar en cuarentena')
        
            else:
                if data['cantidad_cuarentena'] < 1:
                    raise PermissionDenied('No se puede actualizar un ingreso a cuarentena con 0 cantidades o porcentaje')
        else:
            if data['fecha_actualizacion'] > (cuarentena.fecha_cuarentena + timedelta(days=30)):
                raise ValidationError ('Estos datos solo se pueden modificar hasta 30 días despues del ingreso en cuarentena')

        # ACTUALIZAR ARCHIVO
        if archivo_soporte:
            if cuarentena.ruta_archivo_soporte:
                cuarentena.ruta_archivo_soporte.ruta_archivo.delete()
                cuarentena.ruta_archivo_soporte.delete()

            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "IngresoCuarentena")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['ruta_archivo_soporte'] = archivo_creado_instance.id_archivo_digital
        # elif not archivo_soporte and cuarentena.ruta_archivo_soporte:
        #     cuarentena.ruta_archivo_soporte.ruta_archivo.delete()
        #     cuarentena.ruta_archivo_soporte.delete()

        if data['cantidad_cuarentena'] != cuarentena.cantidad_cuarentena:
            if data['cantidad_cuarentena'] > cuarentena.cantidad_cuarentena:
                if cuarentena.cod_etapa_lote == 'G':
                    cantidad_existente = lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion if lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion else 0
                    lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion = cantidad_existente - cuarentena.cantidad_cuarentena + data['cantidad_cuarentena']
                    lote_etapa_in_inventario_viveros.save()
                else:
                    cantidad_existente = lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena if lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena else 0
                    lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena = cantidad_existente - cuarentena.cantidad_cuarentena + data['cantidad_cuarentena']
                    lote_etapa_in_inventario_viveros.save()

            elif data['cantidad_cuarentena'] < cuarentena.cantidad_cuarentena:
                if cuarentena.cod_etapa_lote == 'G':
                    cantidad_existente = lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion if lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion else 0
                    lote_etapa_in_inventario_viveros.porc_cuarentena_lote_germinacion = cantidad_existente - cuarentena.cantidad_cuarentena + data['cantidad_cuarentena']
                    lote_etapa_in_inventario_viveros.save()
                else:
                    cantidad_existente = lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena if lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena else 0
                    lote_etapa_in_inventario_viveros.cantidad_lote_cuarentena = cantidad_existente - cuarentena.cantidad_cuarentena + data['cantidad_cuarentena']
                    lote_etapa_in_inventario_viveros.save()
            serializer = self.serializer_class(cuarentena, data=data, many=False)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()
        else:
            serializer = self.serializer_class(cuarentena, data=data, many=False)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()

        # AUDITORIA ELIMINACIÓN DE ANULAR CUARENTENA
        valores_actualizados = {'previous': cuarentena_copy,'current': serializador}
        descripcion = {"nombre_vivero": str(cuarentena.id_bien.nombre), "nombre_bien": str(cuarentena.id_vivero.id_vivero), "agno": str(cuarentena.agno_lote), "nro_lote": str(cuarentena.nro_lote), "etapa_lote": str(cuarentena.cod_etapa_lote), "fecha_hora_cuarentena": str(cuarentena.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Ingreso a cuarentena actualizado exitosamente'}, status=status.HTTP_201_CREATED)
    

class GetIngresoCuarentenaView(generics.ListAPIView):
    serializer_class = GetIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuarentenas = self.queryset.all()
        serializer = self.serializer_class(cuarentenas, many=True, context = {'request':request})
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetCuarentenasByLoteEtapa(generics.ListAPIView):
    serializer_class = GetIngresoCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        
        for key, value in request.query_params.items():
            if key in ['codigo_bien','agno_lote', 'cod_etapa_lote', 'nombre']:
                if key == 'codigo_bien' or key == 'nombre':
                    if value != '':
                        filter['id_bien__' + key + '__icontains'] = value
                else:
                    if value != '':
                        filter[key] = value
                        
        cuarentenas = self.queryset.all().filter(**filter)
        
        if cuarentenas: 
            serializer = self.serializer_class(cuarentenas, many=True, context = {'request':request} )
            data = serializer.data
        else:
            data = []
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': data}, status=status.HTTP_200_OK)