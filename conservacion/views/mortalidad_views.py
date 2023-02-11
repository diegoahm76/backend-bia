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
    CuarentenaMatVegetal
)
from conservacion.serializers.mortalidad_serializers import (
    RegistrarMortalidadSerializer,
    MortalidadMaterialVegetalSerializer,
    RegistrarItemsMortalidadSerializer,
    ActualizarMortalidadSerializer,
    ActualizarItemsMortalidadSerializer
)
from conservacion.utils import UtilConservacion
import json

class RegistrarMortalidad(generics.CreateAPIView):
    serializer_class=RegistrarMortalidadSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
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
        
        # VALIDACIONES MAESTRO
        serializador_maestro = self.serializer_class(data=data_mortalidad)
        serializador_maestro.is_valid(raise_exception=True)
        
        if fecha_baja < fecha_posible:
            return Response({'success':False, 'detail':'La fecha de baja no puede superar las 24 horas'}, status=status.HTTP_400_BAD_REQUEST)
        
        if ultima_mortalidad:
            if fecha_baja < ultima_mortalidad.fecha_baja:
                return Response({'success':False, 'detail':'La fecha de baja no puede superar la fecha de mortalidad del último registro en el sistema (' + str(ultima_mortalidad.fecha_baja) + ')'}, status=status.HTTP_400_BAD_REQUEST)
        
        # VALIDACIONES DETALLE
        if not data_items_mortalidad:
            return Response({'success':False, 'detail':'No puede guardar un registro de mortalidad sin haber agregado por lo menos un ítem'}, status=status.HTTP_400_BAD_REQUEST)
            
        for item in data_items_mortalidad:
            if item['cantidad_baja'] <= 0:
                return Response({'success':False, 'detail':'Debe ingresar una cantidad de mortalidad mayor a cero en el item de la posición ' + str(item['nro_posicion'])})
                
            items_repetidos = [item_data for item_data in data_items_mortalidad if
                               item_data['id_bien']==item['id_bien'] and
                               item_data['agno_lote']==item['agno_lote'] and
                               item_data['nro_lote']==item['nro_lote'] and
                               item_data['cod_etapa_lote']==item['cod_etapa_lote'] and
                               item_data['consec_cuaren_por_lote_etapa']==item['consec_cuaren_por_lote_etapa']]
            
            if len(items_repetidos) > 1:
                return Response({'success':False, 'detail':'El item de la posición ' + str(item['nro_posicion']) + ' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad a registrar de mortalidad de dicho material vegetal, debe borrar el registro y agregarlo nuevamente'}, status=status.HTTP_400_BAD_REQUEST)
            
            saldo_disponible = 0
            
            if item['consec_cuaren_por_lote_etapa']:
                item_cuarentena = CuarentenaMatVegetal.objects.filter(
                    id_vivero = data_mortalidad['id_vivero'],
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
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa_produccion(inventario_vivero)
                else:
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
                
            if item['cantidad_baja'] > saldo_disponible:
                return Response({'success':False, 'detail':'La cantidad a registrar de mortalidad del item en la posición ' + str(item['nro_posicion']) + ' no puede superar el saldo disponible (' + str(saldo_disponible) + ')'})
            
        # PENDIENTE VALIDACION DETALLES CON FECHA_INCIDENCIA EN T171
        
        # REGISTRO MAESTRO
        response_maestro = serializador_maestro.save()
        
        for item in data_items_mortalidad:
            item['id_baja'] = response_maestro.pk
        
        # REGISTRO DETALLES
        serializador_detalle = RegistrarItemsMortalidadSerializer(data=data_items_mortalidad, many=True)
        serializador_detalle.is_valid(raise_exception=True)
        serializador_detalle.save()
        
        # ACTUALIZACIÓN DE CANTIDADES EN DETALLES
        for item in data_items_mortalidad:
            inventario_vivero = self.queryset.all().filter(
                id_vivero = data_mortalidad['id_vivero'],
                id_bien = item['id_bien'],
                agno_lote = item['agno_lote'],
                nro_lote = item['nro_lote'],
                cod_etapa_lote = item['cod_etapa_lote']
            ).first()
            
            inventario_vivero.cantidad_bajas = inventario_vivero.cantidad_bajas + item['cantidad_baja'] if inventario_vivero.cantidad_bajas else item['cantidad_baja']
            
            if item['consec_cuaren_por_lote_etapa']:
                item_cuarentena = CuarentenaMatVegetal.objects.filter(
                    id_vivero = data_mortalidad['id_vivero'],
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
        
        return Response({'success':True, 'detail':'Se realizó el registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)

# class ActualizarMortalidad(generics.UpdateAPIView):
#     serializer_class=ActualizarMortalidadSerializer
#     queryset=InventarioViveros.objects.all()
#     permission_classes=[IsAuthenticated]
    
#     def put(self,request):
#         data = request.data
#         persona = request.user.persona.id_persona
        
#         data_mortalidad = json.loads(data['data_mortalidad'])
#         data_items_mortalidad = json.loads(data['data_items_mortalidad'])
        
#         data_mortalidad['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        
#         return Response({'success':True, 'detail':'Se realizó el registro de mortalidad correctamente'}, status=status.HTTP_201_CREATED)

class GetMaterialVegetalByCodigo(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        codigo_bien = request.query_params.get('codigo_bien')
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            return Response({'success':False, 'detail':'Debe elegir un vivero que exista'}, status=status.HTTP_404_NOT_FOUND)
        
        catalogo_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien).first()
        
        # VALIDACIONES DEL CÓDIGO BIEN
        if not catalogo_bien:
            return Response({'success':False, 'detail':'El código ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        if catalogo_bien.cod_tipo_elemento_vivero:
            if catalogo_bien.cod_tipo_elemento_vivero != 'MV' or (catalogo_bien.cod_tipo_elemento_vivero == 'MV' and catalogo_bien.es_semilla_vivero):
                return Response({'success':False, 'detail':'El código ingresado no es el código de una planta o una plántula'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success':False, 'detail':'El código ingresado no es de consumo o no se encuentra tipificado'}, status=status.HTTP_400_BAD_REQUEST)
           
        inventarios_viveros = InventarioViveros.objects.filter(id_bien__codigo_bien=codigo_bien, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).exclude(cod_etapa_lote='G')
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        saldos_disponibles = [data['saldo_disponible'] for data in data_serializada]
        
        if data_serializada:
            if len(set(saldos_disponibles)) == 1 and list(set(saldos_disponibles))[0] == 0:
                return Response({'success':False, 'detail':'El código ingresado es de una planta que no tiene saldo disponible en ningún lote-etapa'}, status=status.HTTP_403_FORBIDDEN)
        
        data_serializada = [data for data in data_serializada if data['saldo_disponible'] != 0]
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)

class GetMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class=MortalidadMaterialVegetalSerializer
    queryset=InventarioViveros.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self,request,id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        
        # VALIDAR EXISTENCIA DEL VIVERO
        if not vivero:
            return Response({'success':False, 'detail':'Debe elegir un vivero que exista'}, status=status.HTTP_404_NOT_FOUND)
        
        filtro = {}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote']:
                if key == 'codigo_bien':
                    filtro['id_bien__' + key + '__startswith'] = value
                elif key == 'nombre':
                    filtro['id_bien__' + key + '__icontains'] = value
                else:
                    if value != '':
                        filtro[key]=value
        
        inventarios_viveros = InventarioViveros.objects.filter(**filtro).filter(id_vivero=id_vivero, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).exclude(cod_etapa_lote='G')
        serializador = self.serializer_class(inventarios_viveros, many=True)
        
        data_serializada = serializador.data
        data_serializada = [data for data in data_serializada if data['saldo_disponible'] >= 1]
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':data_serializada}, status=status.HTTP_200_OK)