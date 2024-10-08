import copy
from django.urls import path
from rest_framework.response import Response
from conservacion.views import mortalidad_views as views
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from almacen.models import (
    CatalogoBienes
)
from conservacion.models import (
    BajasVivero,
    ItemsBajasVivero,
    InventarioViveros,
    Vivero,
    CuarentenaMatVegetal,
    IncidenciasMatVegetal,
    Siembras
)
from conservacion.serializers.mortalidad_serializers import (
    RegistrarMortalidadSerializer,
    MortalidadMaterialVegetalSerializer,
    RegistrarItemsMortalidadSerializer,
    ActualizarMortalidadSerializer,
    ActualizarItemsMortalidadSerializer,
    GetMortalidadSerializer,
    AnularMortalidadSerializer,
    GetItemsMortalidadSerializer,
    GetHistorialMortalidadSerializer
)
from conservacion.utils import UtilConservacion
from seguridad.permissions.permissions_conservacion import PermisoActualizarMortalidadPlantasPlantulas, PermisoAnularMortalidadPlantasPlantulas, PermisoCrearMortalidadPlantasPlantulas
from seguridad.utils import Util
import json
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

class GetMaterialVegetalByCodigo(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        codigo_bien = request.query_params.get('codigo_bien')
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            raise NotFound('Debe elegir un vivero que exista')
        
        catalogo_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien).first()
        
        # VALIDACIONES DEL CÓDIGO BIEN
        if not catalogo_bien:
            raise ValidationError('El código ingresado no existe')
        
        if catalogo_bien.cod_tipo_elemento_vivero:
            if catalogo_bien.cod_tipo_elemento_vivero != 'MV' or (catalogo_bien.cod_tipo_elemento_vivero == 'MV' and catalogo_bien.es_semilla_vivero):
                raise ValidationError('El código ingresado no es el código de una planta o una plántula')
        else:
            raise ValidationError('El código ingresado no es de consumo o no se encuentra tipificado')
           
        inventarios_viveros = InventarioViveros.objects.filter(id_bien__codigo_bien=codigo_bien, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False, id_vivero=id_vivero)
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        saldos_disponibles_principal = [data['saldo_disponible_busqueda'] for data in data_serializada if data['saldo_disponible_busqueda']]
        
        if data_serializada:
            if len(set(saldos_disponibles_principal)) == 1 and list(set(saldos_disponibles_principal))[0] == 0:
                raise PermissionDenied('El código ingresado es de una planta que no tiene saldo disponible en ningún lote-etapa')
        
        data_serializada = [data for data in data_serializada if data['saldo_disponible_busqueda'] != 0]
        
        for item in data_serializada:
            saldos_disponibles_cuarentena = [data['saldo_por_levantar'] for data in item['registros_cuarentena']] if item['registros_cuarentena'] else [0]
            saldos_disponibles_cuarentena = sum(saldos_disponibles_cuarentena)
            
            item['saldo_disponible_registro'] = item['saldo_disponible_busqueda'] - saldos_disponibles_cuarentena if item['saldo_disponible_busqueda'] else None
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)

class GetMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            raise NotFound('Debe elegir un vivero que exista')
        
        filtro = {}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote']:
                if key == 'codigo_bien':
                    filtro['id_bien__' + key + '__icontains'] = value
                elif key == 'nombre':
                    filtro['id_bien__' + key + '__icontains'] = value
                else:
                    if value != '':
                        filtro[key]=value
        
        inventarios_viveros = InventarioViveros.objects.filter(**filtro).filter(id_vivero=id_vivero, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).exclude(cod_etapa_lote='G')
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        data_serializada = [data for data in data_serializada if data['saldo_disponible_busqueda'] != 0]
        
        for item in data_serializada:
            saldos_disponibles_cuarentena = [data['saldo_por_levantar'] for data in item['registros_cuarentena']] if item['registros_cuarentena'] else [0]
            saldos_disponibles_cuarentena = sum(saldos_disponibles_cuarentena)
            
            item['saldo_disponible_registro'] = item['saldo_disponible_busqueda'] - saldos_disponibles_cuarentena if item['saldo_disponible_busqueda'] else (100 - saldos_disponibles_cuarentena)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)

class GetMortalidadByNro(generics.ListAPIView):
    serializer_class=GetMortalidadSerializer
    queryset=BajasVivero.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        nro_registro_mortalidad = request.query_params.get('nro_registro_mortalidad')
        baja = self.queryset.all().filter(nro_baja_por_tipo=nro_registro_mortalidad, tipo_baja='M').first()
        
        serializer_data = self.serializer_class(baja).data if baja else []
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer_data}, status=status.HTTP_200_OK)

class GetItemsMortalidadByIdBaja(generics.ListAPIView):
    serializer_class=GetItemsMortalidadSerializer
    queryset=ItemsBajasVivero.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_baja):
        items_mortalidad = self.queryset.all().filter(id_baja=id_baja).order_by('nro_posicion')
        
        if items_mortalidad:
            serializer = self.serializer_class(items_mortalidad, many=True)
            
            return Response ({'success':True, 'detail':'Se encontraron los siguientes items de mortalidad', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No se encontraron items de mortalidad para la mortalidad elegida'}, status=status.HTTP_200_OK)
        
class GetUltimoNro(generics.ListAPIView):
    serializer_class=GetMortalidadSerializer
    queryset=BajasVivero.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        baja = self.queryset.all().filter(tipo_baja='M').last()
        
        ultimo_nro_baja = baja.nro_baja_por_tipo + 1 if baja else 1
        
        return Response ({'success':True, 'detail':'El último número de mortalidad es el siguiente', 'data':ultimo_nro_baja}, status=status.HTTP_200_OK)

class GetHistorialMortalidad(generics.ListAPIView):
    serializer_class=GetHistorialMortalidadSerializer
    queryset=ItemsBajasVivero.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_cuarentena_mat_vegetal):
        cuarentena = CuarentenaMatVegetal.objects.filter(id_cuarentena_mat_vegetal=id_cuarentena_mat_vegetal).first()
        
        serializer_data = []
        if cuarentena:
            items_mortalidad = self.queryset.all().filter(
                id_baja__id_vivero=cuarentena.id_vivero,
                id_bien=cuarentena.id_bien,
                agno_lote=cuarentena.agno_lote,
                nro_lote=cuarentena.nro_lote,
                cod_etapa_lote=cuarentena.cod_etapa_lote,
                consec_cuaren_por_lote_etapa=cuarentena.consec_cueren_por_lote_etapa,
                id_baja__tipo_baja='M'
            )
            
            serializer = self.serializer_class(items_mortalidad, many=True)
            serializer_data = serializer.data
        
        return Response ({'success':True, 'detail':'El historial de mortalidades es el siguiente', 'data':serializer_data}, status=status.HTTP_200_OK)

class RegistrarMortalidad(generics.CreateAPIView):
    serializer_class=RegistrarMortalidadSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated, PermisoCrearMortalidadPlantasPlantulas]
    
    def post(self,request):
        data = request.data
        persona = request.user.persona.id_persona
        
        data_mortalidad = json.loads(data['data_mortalidad'])
        data_items_mortalidad = json.loads(data['data_items_mortalidad'])
        
        data_mortalidad['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        data_mortalidad['tipo_baja'] = 'M'
        data_mortalidad['id_persona_baja'] = persona
        
        ultima_mortalidad = BajasVivero.objects.filter(tipo_baja='M').last()
        nro_baja = ultima_mortalidad.nro_baja_por_tipo + 1 if ultima_mortalidad and ultima_mortalidad.nro_baja_por_tipo else 1
        data_mortalidad['nro_baja_por_tipo'] = nro_baja
        
        fecha_baja = datetime.strptime(data_mortalidad['fecha_baja'], "%Y-%m-%d %H:%M:%S")
        fecha_posible = datetime.now() - timedelta(days=1)
    
        cuarentenas = CuarentenaMatVegetal.objects.filter(id_vivero=data_mortalidad['id_vivero'])
        incidencias = IncidenciasMatVegetal.objects.filter(id_vivero=data_mortalidad['id_vivero'])
        siembras = Siembras.objects.filter(id_vivero=data_mortalidad['id_vivero'])
        
        # VALIDACIONES MAESTRO
        serializador_maestro = self.serializer_class(data=data_mortalidad)
        serializador_maestro.is_valid(raise_exception=True)
        
        if fecha_baja < fecha_posible:
            raise ValidationError ('La fecha de baja no puede superar las 24 horas')
        
        if ultima_mortalidad:
            if fecha_baja < ultima_mortalidad.fecha_baja:
                raise ValidationError('La fecha de baja no puede superar la fecha de mortalidad del último registro en el sistema (' + str(ultima_mortalidad.fecha_baja) + ')')
        
        # VALIDACIONES DETALLE
        if not data_items_mortalidad:
            raise ValidationError('No puede guardar un registro de mortalidad sin haber agregado por lo menos un ítem')
            
        for item in data_items_mortalidad:
            # VALIDAR SI ENVIAN ITEMS REPETIDOS
            items_repetidos = [item_data for item_data in data_items_mortalidad if
                                item_data['id_bien']==item['id_bien'] and
                                item_data['agno_lote']==item['agno_lote'] and
                                item_data['nro_lote']==item['nro_lote'] and
                                item_data['cod_etapa_lote']==item['cod_etapa_lote'] and
                                item_data['consec_cuaren_por_lote_etapa']==item['consec_cuaren_por_lote_etapa']]
                
            if len(items_repetidos) > 1:
                raise ValidationError ('El item de la posición ' + str(item['nro_posicion']) + ' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad a registrar de mortalidad de dicho material vegetal, debe borrar el registro y agregarlo nuevamente')
            
            # VALIDAR QUE EL ITEM DE GERMINACION SEA EL PRINCIPAL
            if item['cod_etapa_lote'] == 'G' and item['consec_cuaren_por_lote_etapa']:
                raise ValidationError('No puede seleccionar un registro de cuarentena para registrar una mortalidad a una germinación')
            
            # VALIDACIONES DE CANTIDAD_BAJA (P,D)
            if item['cod_etapa_lote'] != 'G':
                if item['cantidad_baja'] <= 0:
                    raise ValidationError ('Debe ingresar una cantidad de mortalidad mayor a cero en el item de la posición ' + str(item['nro_posicion']))
                    
                saldo_disponible = 0
                
                if item['consec_cuaren_por_lote_etapa']:
                    item_cuarentena = cuarentenas.filter(
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote'],
                        consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                    ).first()
                    
                    saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                else:
                    inventario_vivero = self.queryset.all().filter(
                        id_vivero = data_mortalidad['id_vivero'],
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote']
                    ).first()
                    
                    if item['cod_etapa_lote'] == 'P':
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_produccion(inventario_vivero)
                    else:
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_distribucion(inventario_vivero)
                    
                if item['cantidad_baja'] > saldo_disponible:
                    raise ValidationError ('La cantidad a registrar de mortalidad del item en la posición ' + str(item['nro_posicion']) + ' no puede superar el saldo disponible (' + str(saldo_disponible) + ')')
                
                # VALIDACION DETALLES CON FECHA_INCIDENCIA
                item_incidencia = incidencias.filter(
                    id_bien = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote'],
                    fecha_incidencia__gt = fecha_baja
                ).last()
                
                if item_incidencia:
                    if item['cantidad_baja'] == saldo_disponible:
                        raise ValidationError('No es posible marcar mortalidad de todo el saldo disponible del registro lote-etapa en la posición ' + str(item['nro_posicion']) + ', ya que tiene un registro de incidencia posterior a la fecha de este registro de mortalidad')
            else:
                if item['consec_cuaren_por_lote_etapa']:
                    raise PermissionDenied('No puede elegir un registro de cuarentena para registrar mortalidad de germinación')
                else:
                    item['cantidad_baja'] = 100
        
        # REGISTRO MAESTRO
        response_maestro = serializador_maestro.save()
        
        for item in data_items_mortalidad:
            item['id_baja'] = response_maestro.pk
        
        # REGISTRO DETALLES
        serializador_detalle = RegistrarItemsMortalidadSerializer(data=data_items_mortalidad, many=True)
        serializador_detalle.is_valid(raise_exception=True)
        items_serializados = serializador_detalle.save()
        
        # GUARDAR DESCRIPCIONES DE LOS DETALLES PARA AUDITORIA
        valores_creados_detalles = []
        for detalle in items_serializados:
            descripcion = {
                'nombre_bien':detalle.id_bien.nombre,
                'agno_lote':detalle.agno_lote,
                'nro_lote':detalle.nro_lote,
                'cod_etapa_lote':detalle.cod_etapa_lote,
                'consec_cuaren_por_lote_etapa':detalle.consec_cuaren_por_lote_etapa
            }
            valores_creados_detalles.append(descripcion)
        
        # ACTUALIZACIÓN DE CANTIDADES EN DETALLES
        for item in data_items_mortalidad:
            inventario_vivero = self.queryset.all().filter(
                id_vivero = data_mortalidad['id_vivero'],
                id_bien = item['id_bien'],
                agno_lote = item['agno_lote'],
                nro_lote = item['nro_lote'],
                cod_etapa_lote = item['cod_etapa_lote']
            ).first()
            
            if item['cod_etapa_lote'] != 'G':
                inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + item['cantidad_baja'] if inventario_vivero.cantidad_bajas else item['cantidad_baja']
                
                if item['consec_cuaren_por_lote_etapa']:
                    item_cuarentena = cuarentenas.filter(
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote'],
                        consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                    ).first()
                    
                    inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena - item['cantidad_baja'] if inventario_vivero.cantidad_lote_cuarentena else 0
                    
                    item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas + item['cantidad_baja'] if item_cuarentena.cantidad_bajas else item['cantidad_baja']
                    item_cuarentena.save()
            else:
                siembra = siembras.filter(
                    id_bien_sembrado = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote']
                ).first()
                inventario_vivero.cantidad_bajas = item['cantidad_baja']
                inventario_vivero.siembra_lote_cerrada = True
                if siembra:
                    siembra.siembra_abierta = False
                    siembra.save()
                
            inventario_vivero.save()
        
        # AUDITORIA MAESTRO DETALLE DE MORTALIDAD
        descripcion = {"tipo_baja": 'M', "nro_baja_por_tipo": nro_baja, "fecha_baja": data_mortalidad['fecha_baja']}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 56,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'success':True, 'detail':'Se realizó el registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)

class ActualizarMortalidad(generics.UpdateAPIView):
    serializer_class=ActualizarMortalidadSerializer
    queryset=BajasVivero.objects.all()
    permission_classes=[IsAuthenticated, PermisoActualizarMortalidadPlantasPlantulas]
    
    def put(self,request,id_baja):
        data = request.data
        baja = self.queryset.all().filter(id_baja=id_baja, tipo_baja='M').first()
        
        if baja:
            data_mortalidad = json.loads(data['data_mortalidad'])
            data_items_mortalidad = json.loads(data['data_items_mortalidad'])
            
            data_mortalidad['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
            
            fecha_maxima_maestro = baja.fecha_baja + timedelta(days=30)
            fecha_maxima_detalle_cantidad = baja.fecha_baja + timedelta(days=2)
            fecha_maxima_detalle_observaciones = baja.fecha_baja + timedelta(days=30)
            fecha_actual = datetime.now()
            
            inventarios_viveros = InventarioViveros.objects.filter(id_vivero=baja.id_vivero)
            cuarentenas = CuarentenaMatVegetal.objects.filter(id_vivero=baja.id_vivero)
            incidencias = IncidenciasMatVegetal.objects.filter(id_vivero=baja.id_vivero)
            siembras = Siembras.objects.filter(id_vivero=baja.id_vivero)
            
            if not data_items_mortalidad:
                raise PermissionDenied ('No puede eliminar todos los items, debe dejar por lo menos uno')
            
            if baja.motivo != data_mortalidad['motivo'] or baja.ruta_archivo_soporte != data_mortalidad['ruta_archivo_soporte']:
                if fecha_actual > fecha_maxima_maestro:
                    raise PermissionDenied('No puede actualizar el motivo o el archivo porque ha superado los 30 días después de la fecha de mortalidad')
            
            # REALIZAR VALIDACIONES INICIALES DETALLES
            for item in data_items_mortalidad:
                if item['cantidad_baja'] <= 0:
                    raise PermissionDenied('Debe ingresar una cantidad de mortalidad mayor a cero en el item de la posición ' + str(item['nro_posicion']))
                    
                items_repetidos = [item_data for item_data in data_items_mortalidad if
                                item_data['id_bien']==item['id_bien'] and
                                item_data['agno_lote']==item['agno_lote'] and
                                item_data['nro_lote']==item['nro_lote'] and
                                item_data['cod_etapa_lote']==item['cod_etapa_lote'] and
                                item_data['consec_cuaren_por_lote_etapa']==item['consec_cuaren_por_lote_etapa']]
                
                if len(items_repetidos) > 1:
                    raise ValidationError('El item de la posición ' + str(item['nro_posicion']) + ' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad a registrar de mortalidad de dicho material vegetal, debe borrar el registro y agregarlo nuevamente')
                
                item['id_baja'] = id_baja
            
            items_crear = [item for item in data_items_mortalidad if not item['id_item_baja_viveros']]
            items_actualizar = [item for item in data_items_mortalidad if item['id_item_baja_viveros']!=None]
            
            items_detalle_list = [item['id_item_baja_viveros'] for item in items_actualizar]
            
            items_mortalidad_actual = ItemsBajasVivero.objects.filter(id_baja=id_baja)
            
            # VALIDAR QUE LOS IDs DE LOS ITEMS PERTENEZCAN A LA MORTALIDAD INDICADA
            items_id_list = [item_actualizar['id_item_baja_viveros'] for item_actualizar in items_actualizar]
            items_existentes = items_mortalidad_actual.filter(id_item_baja_viveros__in=items_id_list)
            if len(items_id_list) != len(items_existentes):
                raise ValidationError ('Debe validar que todos los items pertenezcan al mismo registro de mortalidad')
            
            items_cambios_actualizar = []
            
            # VALIDACIONES ACTUALIZACION DE ITEMS
            for item in items_actualizar:
                item_actual = items_mortalidad_actual.filter(id_item_baja_viveros=item['id_item_baja_viveros']).first()
                inventario_vivero = inventarios_viveros.filter(
                    id_bien = item_actual.id_bien.id_bien,
                    agno_lote = item_actual.agno_lote,
                    nro_lote = item_actual.nro_lote,
                    cod_etapa_lote = item_actual.cod_etapa_lote
                ).first()
                item['cantidad_baja'] = item_actual.cantidad_baja if item_actual.cod_etapa_lote == 'G' else item['cantidad_baja']
                # VALIDAR SI ACTUALIZARON CANTIDAD_BAJA U OBSERVACIONES
                if item_actual.cantidad_baja != item['cantidad_baja']:
                    if fecha_actual > fecha_maxima_detalle_cantidad:
                        raise PermissionDenied('No puede actualizar la cantidad de los items porque ha superado las 48 horas')
                    
                    if item['cantidad_baja'] > item_actual.cantidad_baja:
                        cantidad_aumentada = item['cantidad_baja'] - item_actual.cantidad_baja
                        saldo_disponible = 0
                        
                        if not item_actual.consec_cuaren_por_lote_etapa:
                            if item_actual.cod_etapa_lote == 'P':
                                saldo_disponible = UtilConservacion.get_cantidad_disponible_produccion(inventario_vivero)
                                if cantidad_aumentada > saldo_disponible:
                                    raise ValidationError('La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')')
                            else:
                                saldo_disponible = UtilConservacion.get_cantidad_disponible_distribucion(inventario_vivero)
                                if cantidad_aumentada > saldo_disponible:
                                    raise ValidationError('La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')')
                        else:
                            item_cuarentena = cuarentenas.filter(
                                id_bien = item_actual.id_bien,
                                agno_lote = item_actual.agno_lote,
                                nro_lote = item_actual.nro_lote,
                                cod_etapa_lote = item_actual.cod_etapa_lote,
                                consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                            ).first()
                            saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                            if cantidad_aumentada > saldo_disponible:
                                raise ValidationError('La cantidad aumentada del item en la posición ' + str(item_actual.nro_posicion) + ' no puede ser mayor al saldo disponible (' + str(saldo_disponible) + ')')

                        # VALIDACION DETALLES CON FECHA_INCIDENCIA
                        item_incidencia = incidencias.filter(
                            id_bien = item['id_bien'],
                            agno_lote = item['agno_lote'],
                            nro_lote = item['nro_lote'],
                            cod_etapa_lote = item['cod_etapa_lote'],
                            fecha_incidencia__gt = baja.fecha_baja
                        ).last()
                        
                        if item_incidencia:
                            if cantidad_aumentada == saldo_disponible:
                                raise ValidationError('No es posible marcar mortalidad de todo el saldo disponible del registro lote-etapa en la posición ' + str(item['nro_posicion']) + ', ya que tiene un registro de incidencia posterior a la fecha de este registro de mortalidad')
                    
                if item_actual.observaciones != item['observaciones']:
                    if fecha_actual > fecha_maxima_detalle_observaciones:
                        raise PermissionDenied('No puede actualizar la observación de los items porque ha superado los 30 días')
            
                if item_actual.cantidad_baja != item['cantidad_baja'] or item_actual.observaciones != item['observaciones']:
                    items_cambios_actualizar.append(item)

            # VALIDACIONES CREACIÓN DE ITEMS
            for item in items_crear:
                if item['cod_etapa_lote'] != 'G':
                    saldo_disponible = 0
                    if item['consec_cuaren_por_lote_etapa']:
                        item_cuarentena = cuarentenas.filter(
                            id_bien = item['id_bien'],
                            agno_lote = item['agno_lote'],
                            nro_lote = item['nro_lote'],
                            cod_etapa_lote = item['cod_etapa_lote'],
                            consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                        ).first()
                        
                        saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                    else:
                        inventario_vivero = inventarios_viveros.filter(
                            id_bien = item['id_bien'],
                            agno_lote = item['agno_lote'],
                            nro_lote = item['nro_lote'],
                            cod_etapa_lote = item['cod_etapa_lote']
                        ).first()
                        
                        if item['cod_etapa_lote'] == 'P':
                            saldo_disponible = UtilConservacion.get_cantidad_disponible_produccion(inventario_vivero)
                        else:
                            saldo_disponible = UtilConservacion.get_cantidad_disponible_distribucion(inventario_vivero)
                        
                    if item['cantidad_baja'] > saldo_disponible:
                        raise PermissionDenied('La cantidad a registrar de mortalidad del item en la posición ' + str(item['nro_posicion']) + ' no puede superar el saldo disponible (' + str(saldo_disponible) + ')')
                else:
                    if item['consec_cuaren_por_lote_etapa']:
                        raise PermissionDenied('No puede elegir un registro de cuarentena para registrar mortalidad de germinación')
                    else:
                        item['cantidad_baja'] = 100
                    
                # VALIDACION DETALLES CON FECHA_INCIDENCIA
                item_incidencia = incidencias.filter(
                    id_bien = item['id_bien'],
                    agno_lote = item['agno_lote'],
                    nro_lote = item['nro_lote'],
                    cod_etapa_lote = item['cod_etapa_lote'],
                    fecha_incidencia__gt = baja.fecha_baja
                ).last()
                
                if item_incidencia:
                    if item['cantidad_baja'] == saldo_disponible:
                        raise ValidationError('No es posible marcar mortalidad de todo el saldo disponible del registro lote-etapa en la posición ' + str(item['nro_posicion']) + ', ya que tiene un registro de incidencia posterior a la fecha de este registro de mortalidad')
        
            # ACTUALIZAR MAESTRO
            if baja.motivo != data_mortalidad['motivo'] or baja.ruta_archivo_soporte != data_mortalidad['ruta_archivo_soporte']:
                serializer_maestro = self.serializer_class(baja, data=data_mortalidad, context = {'request':request})
                serializer_maestro.is_valid(raise_exception=True)
                serializer_maestro.save()
            
            # ACTUALIZAR DETALLES
            valores_actualizados_detalles = []
            
            if items_cambios_actualizar:
                for item in items_cambios_actualizar:
                    if item['cod_etapa_lote'] != 'G':
                        item_actual = items_mortalidad_actual.filter(id_item_baja_viveros=item['id_item_baja_viveros']).first()
                        inventario_vivero = inventarios_viveros.filter(
                            id_bien = item_actual.id_bien.id_bien,
                            agno_lote = item_actual.agno_lote,
                            nro_lote = item_actual.nro_lote,
                            cod_etapa_lote = item_actual.cod_etapa_lote
                        ).first()
                        
                        # DESCRIPCION Y PREVIOUS PARA LA AUDITORIA
                        item_actual_previous = copy.copy(item_actual)
                        descripcion = {
                            'nombre_bien':item_actual.id_bien.nombre,
                            'agno_lote':item_actual.agno_lote,
                            'nro_lote':item_actual.nro_lote,
                            'cod_etapa_lote':item_actual.cod_etapa_lote,
                            'consec_cuaren_por_lote_etapa':item_actual.consec_cuaren_por_lote_etapa
                        }
                        
                        if item['cantidad_baja'] < item_actual.cantidad_baja:
                            cantidad_disminuida = item_actual.cantidad_baja - item['cantidad_baja']
                            inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas - cantidad_disminuida if inventario_vivero.cantidad_bajas else 0
                            if item_actual.consec_cuaren_por_lote_etapa:
                                item_cuarentena = cuarentenas.filter(
                                    id_bien = item_actual.id_bien,
                                    agno_lote = item_actual.agno_lote,
                                    nro_lote = item_actual.nro_lote,
                                    cod_etapa_lote = item_actual.cod_etapa_lote,
                                    consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                                ).first()
                                
                                inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena - cantidad_disminuida if inventario_vivero.cantidad_lote_cuarentena else 0
                                
                                item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas - cantidad_disminuida if item_cuarentena.cantidad_bajas else 0
                                item_cuarentena.save()
                            inventario_vivero.save()
                        elif item['cantidad_baja'] > item_actual.cantidad_baja:
                            cantidad_aumentada = item['cantidad_baja'] - item_actual.cantidad_baja
                            inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + cantidad_aumentada if inventario_vivero.cantidad_bajas else cantidad_aumentada
                            if item_actual.consec_cuaren_por_lote_etapa:
                                item_cuarentena = cuarentenas.filter(
                                    id_bien = item_actual.id_bien,
                                    agno_lote = item_actual.agno_lote,
                                    nro_lote = item_actual.nro_lote,
                                    cod_etapa_lote = item_actual.cod_etapa_lote,
                                    consec_cueren_por_lote_etapa = item_actual.consec_cuaren_por_lote_etapa
                                ).first()
                                
                                saldo_disponible = UtilConservacion.get_saldo_por_levantar(item_cuarentena)
                                if cantidad_aumentada == saldo_disponible:
                                    item_cuarentena.cuarentena_abierta = False
                                item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas + cantidad_aumentada if item_cuarentena.cantidad_bajas else cantidad_aumentada
                                item_cuarentena.save()
                            inventario_vivero.save()
                    else:
                        siembra = siembras.filter(
                            id_bien_sembrado = item['id_bien'],
                            agno_lote = item['agno_lote'],
                            nro_lote = item['nro_lote']
                        ).first()
                        inventario_vivero.cantidad_bajas = item['cantidad_baja']
                        inventario_vivero.siembra_lote_cerrada = True
                        if siembra:
                            siembra.siembra_abierta = False
                            siembra.save()
                    
                    serializer_detalle = ActualizarItemsMortalidadSerializer(item_actual, data=item)
                    serializer_detalle.is_valid(raise_exception=True)
                    serializer_detalle.save()
                    
                    valores_actualizados_detalles.append({'previous':item_actual_previous, 'current':item_actual, 'descripcion':descripcion})
            
            # ELIMINACIÓN DE ITEMS MORTALIDAD
            valores_eliminados_detalles = []
            items_mortalidad_eliminar = items_mortalidad_actual.exclude(id_item_baja_viveros__in=items_detalle_list)
            
            if items_mortalidad_eliminar:
                for item in items_mortalidad_eliminar:
                    inventario_vivero = inventarios_viveros.filter(
                        id_bien = item.id_bien.id_bien,
                        agno_lote = item.agno_lote,
                        nro_lote = item.nro_lote,
                        cod_etapa_lote = item.cod_etapa_lote
                    ).first()
                    inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas - item.cantidad_baja if inventario_vivero.cantidad_bajas else 0
                    
                    # DESCRIPCION PARA LA AUDITORIA
                    descripcion = {
                        'nombre_bien':item.id_bien.nombre,
                        'agno_lote':item.agno_lote,
                        'nro_lote':item.nro_lote,
                        'cod_etapa_lote':item.cod_etapa_lote,
                        'consec_cuaren_por_lote_etapa':item.consec_cuaren_por_lote_etapa
                    }
                    valores_eliminados_detalles.append(descripcion)
                    
                    if item.consec_cuaren_por_lote_etapa:
                        inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena + item.cantidad_baja if inventario_vivero.cantidad_lote_cuarentena else item.cantidad_baja
                        item_cuarentena = cuarentenas.filter(
                            id_bien = item.id_bien,
                            agno_lote = item.agno_lote,
                            nro_lote = item.nro_lote,
                            cod_etapa_lote = item.cod_etapa_lote,
                            consec_cueren_por_lote_etapa = item.consec_cuaren_por_lote_etapa
                        ).first()
                        item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas - item.cantidad_baja if item_cuarentena.cantidad_bajas else 0
                        item_cuarentena.save()
                    
                    if item.cod_etapa_lote == 'G':
                        siembra = siembras.filter(
                            id_bien_sembrado = item.id_bien,
                            agno_lote = item.agno_lote,
                            nro_lote = item.nro_lote
                        ).first()
                        inventario_vivero.siembra_lote_cerrada = False
                        if siembra:
                            siembra.siembra_abierta = True
                            siembra.save()
                    
                    inventario_vivero.save()
                    
                items_mortalidad_eliminar.delete()
            
            response_serializer_create = []
            
            # CREAR DETALLES
            if items_crear:
                serializer_detalle_crear = RegistrarItemsMortalidadSerializer(data=items_crear, many=True)
                serializer_detalle_crear.is_valid(raise_exception=True)
                response_serializer_create = serializer_detalle_crear.save()
                # items_detalle_list.extend([item_creado.pk for item_creado in response_serializer_create])
                
                # ACTUALIZACIÓN DE CANTIDADES EN DETALLES CREATE
                for item in items_crear:
                    inventario_vivero = inventarios_viveros.filter(
                        id_bien = item['id_bien'],
                        agno_lote = item['agno_lote'],
                        nro_lote = item['nro_lote'],
                        cod_etapa_lote = item['cod_etapa_lote']
                    ).first()
                    
                    inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + item['cantidad_baja'] if inventario_vivero.cantidad_bajas else item['cantidad_baja']
                    
                    if item['consec_cuaren_por_lote_etapa']:
                        item_cuarentena = cuarentenas.filter(
                            id_bien = item['id_bien'],
                            agno_lote = item['agno_lote'],
                            nro_lote = item['nro_lote'],
                            cod_etapa_lote = item['cod_etapa_lote'],
                            consec_cueren_por_lote_etapa = item['consec_cuaren_por_lote_etapa']
                        ).first()
                        
                        inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena - item['cantidad_baja'] if inventario_vivero.cantidad_lote_cuarentena else 0
                        
                        item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas + item['cantidad_baja'] if item_cuarentena.cantidad_bajas else item['cantidad_baja']
                        item_cuarentena.save()
                        
                    inventario_vivero.save()
            
            # GUARDAR DESCRIPCIONES DE LOS DETALLES PARA AUDITORIA
            valores_creados_detalles = []
            
            for detalle in response_serializer_create:
                descripcion = {
                    'nombre_bien':detalle.id_bien.nombre,
                    'agno_lote':detalle.agno_lote,
                    'nro_lote':detalle.nro_lote,
                    'cod_etapa_lote':detalle.cod_etapa_lote,
                    'consec_cuaren_por_lote_etapa':detalle.consec_cuaren_por_lote_etapa
                }
                valores_creados_detalles.append(descripcion)
            
            # AUDITORIA MAESTRO DETALLE DE MORTALIDAD
            descripcion = {"tipo_baja": baja.tipo_baja, "nro_baja_por_tipo": str(baja.nro_baja_por_tipo), "fecha_baja": str(baja.fecha_baja)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 56,
                "cod_permiso": "AC",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_creados_detalles": valores_creados_detalles,
                "valores_actualizados_detalles": valores_actualizados_detalles,
                "valores_eliminados_detalles": valores_eliminados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Se realizó la actualizacón del registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('No existe el registro de mortalidad elegido')

class AnularMortalidad(generics.UpdateAPIView):
    serializer_class=AnularMortalidadSerializer
    queryset=BajasVivero.objects.all()
    permission_classes=[IsAuthenticated, PermisoAnularMortalidadPlantasPlantulas]
    
    def put(self,request,id_baja):
        data = request.data
        persona = request.user.persona.id_persona
        ultima_baja = self.queryset.all().filter(tipo_baja='M', baja_anulado=False).last()
        baja = self.queryset.all().filter(id_baja=id_baja, tipo_baja='M', baja_anulado=False).first()
        
        if baja:
            if baja.id_baja != ultima_baja.id_baja:
                raise PermissionDenied('Solo puede anular el último registro de mortalidad')
            
            fecha_maxima_anular = baja.fecha_baja + timedelta(days=2)
            fecha_actual = datetime.now()
            
            if fecha_actual > fecha_maxima_anular:
                raise PermissionDenied('No puede anular el registro de mortalidad porque ha superado las 48 horas')
            
            items_mortalidad = ItemsBajasVivero.objects.filter(id_baja=id_baja)
            inventarios_viveros = InventarioViveros.objects.filter(id_vivero=baja.id_vivero)
            cuarentenas = CuarentenaMatVegetal.objects.filter(id_vivero=baja.id_vivero)
            
            valores_eliminados_detalles = []
            
            for item in items_mortalidad:
                inventario_vivero = inventarios_viveros.filter(
                    id_bien = item.id_bien.id_bien,
                    agno_lote = item.agno_lote,
                    nro_lote = item.nro_lote,
                    cod_etapa_lote = item.cod_etapa_lote
                ).first()
                inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas - item.cantidad_baja if inventario_vivero.cantidad_bajas else 0
                
                # DESCRIPCION PARA LA AUDITORIA
                descripcion = {
                    'nombre_bien':item.id_bien.nombre,
                    'agno_lote':item.agno_lote,
                    'nro_lote':item.nro_lote,
                    'cod_etapa_lote':item.cod_etapa_lote,
                    'consec_cuaren_por_lote_etapa':item.consec_cuaren_por_lote_etapa
                }
                valores_eliminados_detalles.append(descripcion)
                
                if item.consec_cuaren_por_lote_etapa:
                    inventario_vivero.cantidad_lote_cuarentena = inventario_vivero.cantidad_lote_cuarentena + item.cantidad_baja if inventario_vivero.cantidad_lote_cuarentena else item.cantidad_baja
                    item_cuarentena = cuarentenas.filter(
                        id_bien = item.id_bien,
                        agno_lote = item.agno_lote,
                        nro_lote = item.nro_lote,
                        cod_etapa_lote = item.cod_etapa_lote,
                        consec_cueren_por_lote_etapa = item.consec_cuaren_por_lote_etapa
                    ).first()
                    item_cuarentena.cantidad_bajas = item_cuarentena.cantidad_bajas - item.cantidad_baja if item_cuarentena.cantidad_bajas else 0
                    item_cuarentena.save()
                    
                if item.cod_etapa_lote == 'G':
                    siembra = Siembras.objects.filter(
                        id_bien_sembrado = item.id_bien,
                        agno_lote = item.agno_lote,
                        nro_lote = item.nro_lote,
                        id_vivero = baja.id_vivero
                    ).first()
                    inventario_vivero.siembra_lote_cerrada = False
                    if siembra:
                        siembra.siembra_abierta = True
                        siembra.save()
                
                inventario_vivero.save()
            
            # ELIMINAR REGISTROS DE ITEMS
            items_mortalidad.delete()
            
            # ACTUALIZAR INFO DE ANULACIÓN EN MORTALIDAD
            data['baja_anulado'] = True
            data['fecha_anulacion'] = fecha_actual
            data['id_persona_anula'] = persona
            
            serializer = self.serializer_class(baja, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # AUDITORIA MAESTRO DETALLE DE MORTALIDAD
            descripcion = {"tipo_baja": baja.tipo_baja, "nro_baja_por_tipo": str(baja.nro_baja_por_tipo), "fecha_baja": str(baja.fecha_baja)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 56,
                "cod_permiso": "AN",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Se realizó la anulación del registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe el registro de mortalidad elegido')