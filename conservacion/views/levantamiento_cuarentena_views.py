import copy
from conservacion.models.cuarentena_models import ItemsLevantaCuarentena, CuarentenaMatVegetal
from conservacion.models.inventario_models import InventarioViveros
from conservacion.serializers.levantamiento_cuarentena_serializers import (
    MaterialVegetalCuarentenaSerializer,
    ItemsLevantamientoCuarentenaSerializer,CuarentenaMaterialVegetalSerializer,
    AnulacionGetCuarentenaMaterialVegetalSerializer
)
from seguridad.utils import Util
from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.serializers.viveros_serializers import ViveroSerializer
from conservacion.models.inventario_models import Vivero
from django.db.models import Q
from datetime import datetime,date,timedelta
from rest_framework.permissions import IsAuthenticated
from conservacion.utils import UtilConservacion


class GetViveroActivo (generics.ListAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != "cod_municipio":
                    filter[key+"__icontains"] = value
                else:
                    filter[key] = value
                    
        filter['activo'] = True
        filter['fecha_cierre_actual'] = None
        filter['id_persona_cierra'] = None
        filter['justificacion_cierre'] = None
        
        viveros = self.queryset.all().filter(**filter).filter(~Q(fecha_ultima_apertura = None))
        if viveros:
            serializador = self.serializer_class(viveros, many=True)
            return Response ({'success':True,'detail':'Se encontraron viveros','data':serializador.data},status=status.HTTP_200_OK)
        return Response ({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)
    
class GetMaterialVegetalByCodigo(generics.ListAPIView):
    serializer_class = MaterialVegetalCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response ({'success':False,'detail':'No existe vivero'},status=status.HTTP_403_FORBIDDEN)
        codigo_bien = request.query_params.get('codigo_bien')
        
        
        fecha_hoy=datetime.now()
        material_vegetal = self.queryset.all().filter(id_bien__codigo_bien=codigo_bien,cuarentena_anulada=False,fecha_cuarentena__lte=fecha_hoy,cuarentena_abierta=True,id_vivero__id_vivero=id_vivero)    
        list_siembra_cerrada = [] 
        
        for material in material_vegetal:
            if material.cod_etapa_lote == 'G':
                inventario_vivero = InventarioViveros.objects.filter(id_bien=material.id_bien.id_bien,agno_lote=material.agno_lote,nro_lote=material.nro_lote,cod_etapa_lote=material.cod_etapa_lote,id_vivero=material.id_vivero.id_vivero,siembra_lote_cerrada=True).first()
                if inventario_vivero:
                    list_siembra_cerrada.append(material.id_cuarentena_mat_vegetal)
    
        
        material_vegetal = material_vegetal.exclude(id_cuarentena_mat_vegetal__in=list_siembra_cerrada)
        
        serializador = self.serializer_class(material_vegetal,many=True)
        
        return Response({'success':True,'detail':'se encontraron elementos','data':serializador.data},status=status.HTTP_200_OK)
    
class GetCuarentenaMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class = MaterialVegetalCuarentenaSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response ({'success':False,'detail':'No existe vivero'},status=status.HTTP_403_FORBIDDEN)
        filtro = {}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote','agno_lote']:
                if key != 'cod_etapa_lote' and key != 'agno_lote':
                    filtro["id_bien__"+key+"__startswith"] = value
                else: 
                    filtro[key] = value
                    
        filtro['cuarentena_anulada'] = False
        filtro['cuarentena_abierta'] = True
    
        fecha_hoy = datetime.now()
        material_vegetal = self.queryset.all().filter(fecha_cuarentena__lte=fecha_hoy,id_vivero__id_vivero=vivero.id_vivero).filter(**filtro)
        list_siembra_cerrada = [] 
        
        for material in material_vegetal:
            if material.cod_etapa_lote == 'G':
                inventario_vivero = InventarioViveros.objects.filter(id_bien=material.id_bien.id_bien,agno_lote=material.agno_lote,nro_lote=material.nro_lote,cod_etapa_lote=material.cod_etapa_lote,id_vivero=material.id_vivero.id_vivero,siembra_lote_cerrada=True).first()
                if inventario_vivero:
                    list_siembra_cerrada.append(material.id_cuarentena_mat_vegetal)
    
        
        material_vegetal = material_vegetal.exclude(id_cuarentena_mat_vegetal__in=list_siembra_cerrada)

        serializador = self.serializer_class(material_vegetal,many=True)
        
        return Response({'success':True,'detail':'se encontraron elementos','data':serializador.data},status=status.HTTP_200_OK)
    
class GetCuarentenaMaterialVegetalById(generics.ListAPIView):
    serializer_class = CuarentenaMaterialVegetalSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request,id_cuarentena_mat_vegetal):
        cuarentena_material_v = self.queryset.all().filter(id_cuarentena_mat_vegetal=id_cuarentena_mat_vegetal).first()
        if cuarentena_material_v:
            serializador = self.serializer_class (cuarentena_material_v, many= False)
            return Response ({'success':True,'detail':'Se encontraron elementos','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response ({'success':False,'detail':'No se encontraron elementos'},status=status.HTTP_200_OK)
        
class GuardarLevantamientoCuarentena(generics.CreateAPIView):
    serializer_class= ItemsLevantamientoCuarentenaSerializer
    queryset = ItemsLevantaCuarentena.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post (self,request):
        data = request.data
        persona = request.user.persona.id_persona
        
        #VALIDACIÓN PENDIENTE
    
        # serializador = self.serializer_class(data=data)
        # serializador.is_valid(raise_exception=True)
        data._mutable = True
        
        #VALIDACION DE OBSERVACION, FECHA_LEVANTAMIENTO Y  ID_CUARENTENA
        
        if not data['observaciones'] or not data['fecha_levantamiento'] or not data['id_cuarentena_mat_vegetal']:
            return Response ({'success':False,'detail':'Debe de enviar los campos: observación, fecha de levantamiento y la id del registro de cuarentena'},status=status.HTTP_400_BAD_REQUEST)
        
        cuarentena = CuarentenaMatVegetal.objects.filter(id_cuarentena_mat_vegetal=data['id_cuarentena_mat_vegetal']).first()
        
        #VALIDACIÓN DEL REGISTRO DE CUARENTENA
        if not cuarentena:
            return Response ({'success':False,'detail':'No existe el registro de cuarentena seleccionado'},status=status.HTTP_403_FORBIDDEN)
        
        if cuarentena.cuarentena_anulada == True:
            return Response ({'success':False,'detail':'El registro de cuarentena se encuentra anulado'},status=status.HTTP_403_FORBIDDEN)
            
        items = self.queryset.all().filter(id_cuarentena_mat_vegetal = cuarentena.id_cuarentena_mat_vegetal).last()
        
        #CREACIÓN DEL CONSECUTIVO
        consec_levan_por_cuaren = items.consec_levan_por_cuaren + 1 if items and items.consec_levan_por_cuaren else 1
            
        data['consec_levan_por_cuaren'] = consec_levan_por_cuaren

        #FILTRO PARA USARLO EN LA VALIDACIÓN DE FECHAS
        items_no_anulados = self.queryset.all().filter(id_cuarentena_mat_vegetal = cuarentena.id_cuarentena_mat_vegetal, id_cuarentena_mat_vegetal__cuarentena_anulada=False).last()
    
        #VALIDACION DE LAS FECHAS
        fecha_levantamiento = data['fecha_levantamiento']
        fecha_levantamiento_strptime = datetime.strptime(fecha_levantamiento, '%Y-%m-%d %H:%M:%S')  
        
        if items_no_anulados:
            if fecha_levantamiento_strptime < items_no_anulados.fecha_levantamiento:
                return Response ({'success':False,'detail':'La fecha del levantamiento ingresado es menor a la fecha del último registro de levantamiento para la cuarentena elegida ('+str(items_no_anulados.fecha_levantamiento)+')'},status=status.HTTP_403_FORBIDDEN)
        
        elif fecha_levantamiento_strptime < cuarentena.fecha_registro:
            return Response ({'success':False,'detail':'La fecha de levantamiento ingresado es menor a la fecha del registro de cuarentena seleccionado ('+str(cuarentena.fecha_registro)+')'},status=status.HTTP_403_FORBIDDEN)
        
        #PERSONA QUE LEVANTA
        data['id_persona_levanta'] = persona
        
        #VALIDACIÓN DE CANTIDAD A LEVANTAR
        
        cantidad_por_levantar = UtilConservacion.get_saldo_por_levantar(cuarentena)
        
        if int(data['cantidad_a_levantar']) <= 0:
            return Response({'success':False,'detail':'La cantidad a levantar debe ser mayor a cero'},status=status.HTTP_403_FORBIDDEN)
        if int(data['cantidad_a_levantar']) > cantidad_por_levantar:
            return Response({'success':False,'detail':'La cantidad a levantar no puede ser mayor a la cantidad por levantar (' + str(cantidad_por_levantar)+')'},status=status.HTTP_403_FORBIDDEN)
    
        # GUARDADO
        serializador = self.serializer_class(data = data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        serializador_data = serializador.data
        serializador_data['cantidad_por_levantar'] = cantidad_por_levantar - int(data['cantidad_a_levantar'])
        
        #ACTUALIZACIÓN DE LA CANTIDAD LEVANTADA DE LA TABLA DE CUARENTENA
        cuarentena.cantidad_levantada += int(data['cantidad_a_levantar'])
        cuarentena.save()    
        
        #ACTUALIZACIÓN DE LA TABLA VIVERO
        
        inventario_vivero = InventarioViveros.objects.filter(id_bien=cuarentena.id_bien.id_bien,agno_lote=cuarentena.agno_lote,nro_lote=cuarentena.nro_lote,cod_etapa_lote=cuarentena.cod_etapa_lote,id_vivero=cuarentena.id_vivero.id_vivero).first()
        print('INVENTARIO',inventario_vivero)
        if inventario_vivero.cod_etapa_lote == 'G':
            inventario_vivero.porc_cuarentena_lote_germinacion -= int(data['cantidad_a_levantar'])
            inventario_vivero.save()
        else:
            inventario_vivero.cantidad_lote_cuarentena -= int(data['cantidad_a_levantar'])
            inventario_vivero.save()
            
        #CIERRE DE CUARENTENA POR NO TENER CANTIDAD POR LEVANTAR
    
        if (int(data['cantidad_a_levantar']) - cantidad_por_levantar) == 0:
            cuarentena.cuarentena_abierta = False
            cuarentena.save()
            

        #AUDITORIA DEL SERVICIO DE GUARDADO
        descripcion = {"nombre_vivero": cuarentena.id_vivero.nombre,
                       'nombre_bien': cuarentena.id_bien.nombre,
                       'numero_lote': str(cuarentena.nro_lote),
                       'agno_lote': str(cuarentena.agno_lote),
                       'etapa_lote': cuarentena.cod_etapa_lote,
                       'fecha_cuarentena':str(cuarentena.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        valores_creados_detalles= [{'fecha_levantamiento':data['fecha_levantamiento']}]
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles":valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True,'detail':'Guardado correctamente', 'data':serializador_data},status=status.HTTP_200_OK) 
            
class GetHistorialLevantamientoCuarentena (generics.ListAPIView):
    
    serializer_class = ItemsLevantamientoCuarentenaSerializer
    queryset = ItemsLevantaCuarentena
    
    def get (self,request,id_cuarentena_mat_vegetal):
        
        cuarentena = CuarentenaMatVegetal.objects.filter(id_cuarentena_mat_vegetal=id_cuarentena_mat_vegetal).first()
        
        print ('cuarentena',cuarentena)
        if not  cuarentena:
            return Response({'success':False,'detail':'No existe la cuarentena de material vegetal enviada o fue anulada'},status=status.HTTP_403_FORBIDDEN
                            )
        levantamientos = ItemsLevantaCuarentena.objects.filter(id_cuarentena_mat_vegetal=cuarentena.id_cuarentena_mat_vegetal,levantamiento_anulado=False)
        
        if levantamientos:
            serializador = self.serializer_class(levantamientos,many=True)
            return Response ({'success':True,'detail':'Se encontraron levantamientos de cuarentena para el registro de cuarentena seleccionado','data':serializador.data},status=status.HTTP_200_OK)
        return Response ({'success':True,'detail':'No se encontraron levantamientos de cuarentena para el registro de cuarentena seleccionado'},status=status.HTTP_200_OK)

class GetAnulacionCuarentenaMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class = AnulacionGetCuarentenaMaterialVegetalSerializer
    queryset = CuarentenaMatVegetal.objects.all()
    
    def get(self,request,id_vivero):
        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response ({'success':False,'detail':'No existe vivero'},status=status.HTTP_403_FORBIDDEN)
        filtro = {}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote','agno_lote']:
                if key == 'codigo_bien':
                    filtro["id_bien__"+key+"__startswith"] = value
                elif key == 'nombre':
                    filtro["id_bien__"+key+"__icontains"] = value
                else: 
                    filtro[key] = value
                    
        filtro['cuarentena_anulada'] = False
        
        material_vegetal = self.queryset.all().filter(id_vivero__id_vivero=vivero.id_vivero).filter(**filtro)
        list_siembra_cerrada = [] 
        
        for material in material_vegetal:
            if material.cod_etapa_lote == 'G':
                inventario_vivero = InventarioViveros.objects.filter(id_bien=material.id_bien.id_bien,agno_lote=material.agno_lote,nro_lote=material.nro_lote,cod_etapa_lote=material.cod_etapa_lote,id_vivero=material.id_vivero.id_vivero,siembra_lote_cerrada=True).first()
                if inventario_vivero:
                    list_siembra_cerrada.append(material.id_cuarentena_mat_vegetal)
    
        material_vegetal = material_vegetal.exclude(id_cuarentena_mat_vegetal__in=list_siembra_cerrada)

        serializador = self.serializer_class(material_vegetal,many=True)
        serializador = [cuarentena for cuarentena in serializador.data if cuarentena['ultimo_item_levantamiento_cuarentena']]
        
        return Response({'success':True,'detail':'se encontraron elementos','data':serializador},status=status.HTTP_200_OK)

class UpdateLevantamientoCuarentena (generics.UpdateAPIView):
    
    serializer_class = ItemsLevantamientoCuarentenaSerializer
    queryset = ItemsLevantaCuarentena.objects.all()
    
    def put(self,request,id_item_levanta_cuarentena):
        
        data = request.data
        
        item_levantamiento_cuarentena = self.queryset.all().filter(id_item_levanta_cuarentena=id_item_levanta_cuarentena,levantamiento_anulado=False).last()
        
        if not item_levantamiento_cuarentena:
            return Response ({'success':False,'detail':'No existe el levantamiento de cuarentena enviado'},status=status.HTTP_403_FORBIDDEN)
        
        item_levantamiento_cuarentena_previous=copy.copy(item_levantamiento_cuarentena)
        
        inventario_vivero = InventarioViveros.objects.filter(id_bien=item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.id_bien.id_bien,agno_lote=item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.agno_lote,nro_lote=item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.nro_lote,cod_etapa_lote=item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote,id_vivero=item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.id_vivero.id_vivero).first()
        
        fecha_hoy = datetime.now()
        cuarenta_ocho_horas_después = item_levantamiento_cuarentena.fecha_levantamiento + timedelta(days=2) 
        fecha_hace_un_mes = item_levantamiento_cuarentena.fecha_levantamiento +  timedelta(days=30) 
        
        #ACTUALIZACION DE LA CANTIDAD A ACTUALIZAR 
        if item_levantamiento_cuarentena:
            
            if int(data['cantidad_a_levantar']) != item_levantamiento_cuarentena.cantidad_a_levantar:
                if fecha_hoy > cuarenta_ocho_horas_después:
                    return Response ({'success':False,'detail':'No se puede actualizar la cantidad a levantar porque el levantamiento a actualizar ya superó las 48 horas permitidas para esta acción.'},status=status.HTTP_403_FORBIDDEN)
            
            if data['observaciones'] != item_levantamiento_cuarentena.observaciones:
                if fecha_hoy > fecha_hace_un_mes:
                    return Response ({'success':True,'detail':'No se puede actualizar el campo observación porque el levantamiento a actualizar ya superó el mes permitido para esta acción.'},status=status.HTTP_403_FORBIDDEN)
            
            
            #ACTUALIZACION CUANDO LA CANTIDAD DISMINUYE
            saldo_disponible = 0
            cantidad_disminuida = 0
            if int(data['cantidad_a_levantar']) < item_levantamiento_cuarentena.cantidad_a_levantar:
                
                if item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'G':
                    saldo_disponible = 100 - inventario_vivero.porc_cuarentena_lote_germinacion
                elif item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'P':
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
                else:
                    saldo_disponible = inventario_vivero.cantidad_entrante - inventario_vivero.cantidad_bajas - inventario_vivero.cantidad_salidas - inventario_vivero.cantidad_lote_cuarentena
                
                cantidad_disminuida = item_levantamiento_cuarentena.cantidad_a_levantar - int(data['cantidad_a_levantar']) 
                
                if int(data['cantidad_a_levantar']) < 1:
                    return Response ({'success':False,'detail':'La cantidad a levantar no puede ser menor a 1'})
                
                if cantidad_disminuida > saldo_disponible:
                    return Response ({'success':False,'detail':'La cantidad a levantar no puede ser mayor al saldo disponible ('+saldo_disponible+')'},status=status.HTTP_403_FORBIDDEN)
                
                if item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cuarentena_abierta == False:
                    item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cuarentena_abierta = True
                
                #DISMINUCIÓN DE CANTIDAD A LEVANTAR
        
                item_levantamiento_cuarentena.cantidad_a_levantar -= cantidad_disminuida
                
                #DISMINUCIÓN DE CANTIDAD LEVANTADA
                item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cantidad_levantada  -= cantidad_disminuida
                
                #DISMINUCIÓN AUMENTO EN LA TABLA INVENTARIO VIVERO
                if item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'G':
                    inventario_vivero.porc_cuarentena_lote_germinacion += cantidad_disminuida
                
                else:
                    inventario_vivero.cantidad_lote_cuarentena += cantidad_disminuida
                
            ## ACTUALIZACIÓN CUANDO LA CANTIDAD AUMENTA
            
            if int(data['cantidad_a_levantar']) > item_levantamiento_cuarentena.cantidad_a_levantar:
                valor_por_levantar = item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cantidad_cuarentena - item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cantidad_bajas - item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cantidad_levantada
                
                cantidad_aumentada = int(data['cantidad_a_levantar']) - item_levantamiento_cuarentena.cantidad_a_levantar
                
                if cantidad_aumentada > valor_por_levantar:
                    return Response ({'success':False,'detail':'La cantidad a levantar es mayor a la cantidad por levantar ('+str(valor_por_levantar)+')'},status=status.HTTP_403_FORBIDDEN)
                    
                ## VALIDACIÓN PENDIENTE INCIDENCIAS
                
                if cantidad_aumentada == valor_por_levantar:
                    item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cuarentena_abierta = False
                
                #AUMENTO DE CANTIDAD A LEVANTAR
                item_levantamiento_cuarentena.cantidad_a_levantar += cantidad_aumentada
                
                #AUMENTO DE CANTIDAD LEVANTADA
                item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cantidad_levantada += cantidad_aumentada
        
                #DISMINUCIÓN EN LA TABLA INVENTARIO VIVERO
                if item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'G':
                    inventario_vivero.porc_cuarentena_lote_germinacion -= cantidad_aumentada
                
                else:
                    inventario_vivero.cantidad_lote_cuarentena -= cantidad_aumentada
                    
        item_levantamiento_cuarentena.observaciones = data['observaciones']
        item_levantamiento_cuarentena.save()
        item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.save()
        inventario_vivero.save()
        
       #AUDITORIA DEL SERVICIO DE GUARDADO
        descripcion = {"nombre_vivero": item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.id_vivero.nombre,
                       'nombre_bien': item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.id_bien.nombre,
                       'numero_lote': str(item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.nro_lote),
                       'agno_lote': str(item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.agno_lote),
                       'etapa_lote': item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote,
                       'fecha_cuarentena':str(item_levantamiento_cuarentena.id_cuarentena_mat_vegetal.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        valores_actualizados_detalles= [{'previous':item_levantamiento_cuarentena_previous,'current':item_levantamiento_cuarentena,'descripcion':{'fecha_levantamiento':str(item_levantamiento_cuarentena.fecha_levantamiento)}}]
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles":valores_actualizados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True,'detail':'Actualización exitosa'})
    
class AnularLevantamientoCuarentena (generics.UpdateAPIView):
    serializer_class = ItemsLevantamientoCuarentenaSerializer
    queryset = ItemsLevantaCuarentena.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put (self,request,id_item_levanta_cuarentena):
        
        data=request.data
        
        if not data['justificacion_anulacion']:
            return Response ({'success':False,'detail':'Debe enviar la justificación de la anulación'},status=status.HTTP_403_FORBIDDEN)
        
        items_levanta_cuarentena = self.queryset.all().filter(id_item_levanta_cuarentena=id_item_levanta_cuarentena,levantamiento_anulado=False).last() 
        if not items_levanta_cuarentena:
            return Response ({'success':False,'detail':'No existe el registro de levantamiento o ya fue anulado'},status=status.HTTP_403_FORBIDDEN)
        
        items_levanta_cuarentena_previous=copy.copy(items_levanta_cuarentena)
        
        inventario_vivero = InventarioViveros.objects.filter(
            id_bien=items_levanta_cuarentena.id_cuarentena_mat_vegetal.id_bien.id_bien,
            agno_lote=items_levanta_cuarentena.id_cuarentena_mat_vegetal.agno_lote,
            nro_lote=items_levanta_cuarentena.id_cuarentena_mat_vegetal.nro_lote,
            cod_etapa_lote=items_levanta_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote,
            id_vivero=items_levanta_cuarentena.id_cuarentena_mat_vegetal.id_vivero.id_vivero
        ).first()
        
        #VALIDACION DE 48 HORAS PERMITIDAS PARA ANULAR
        fecha_hoy = datetime.now()
        cuarenta_ocho_horas_después = items_levanta_cuarentena.fecha_levantamiento + timedelta(days=2) 
        
        if fecha_hoy > cuarenta_ocho_horas_después:
            return Response ({'success':False,'detail':'No se puede anular el registro de levantamiento de cuarentena debido a que ya superó las 48 horas permitidas para hacer esta acción'},status=status.HTTP_403_FORBIDDEN)
        
        #OBTENER SALDO DISPONIBLE
        saldo_disponible = 0
        if items_levanta_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'G':
            saldo_disponible = 100 - inventario_vivero.porc_cuarentena_lote_germinacion
        elif items_levanta_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'P':
            saldo_disponible = UtilConservacion.get_cantidad_disponible_etapa(inventario_vivero)
        else:
            saldo_disponible = UtilConservacion.get_cantidad_disponible_levantamiento(inventario_vivero)
        
        #VALIDACIÓN DE CANTIDAD A LEVANTAR CON CANTIDAD DISPONIBLE
        
        if items_levanta_cuarentena.cantidad_a_levantar > saldo_disponible:
            return Response ({'success':False, 'detail':'No se puede anular debido a que la cantidad a levantar ('+str(items_levanta_cuarentena.cantidad_a_levantar)+') es mayor a la cantidad disponible ('+str(saldo_disponible)+')'},status=status.HTTP_403_FORBIDDEN)
        
        #VALIDACION DE CUARENTENA SI ESTÁ CERRADA
        if items_levanta_cuarentena.id_cuarentena_mat_vegetal.cuarentena_abierta == False:
            items_levanta_cuarentena.id_cuarentena_mat_vegetal.cuarentena_abierta = True
            items_levanta_cuarentena.id_cuarentena_mat_vegetal.save()
            
        #RESTARLE LA CANTIDAD LEVANTADA A LA TABLA DE CUARENTENA MV
        items_levanta_cuarentena.id_cuarentena_mat_vegetal.cantidad_levantada -= items_levanta_cuarentena.cantidad_a_levantar
        
        #AUMENTO EN LA TABLA INVENTARIO VIVERO
        if items_levanta_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote == 'G':
            inventario_vivero.porc_cuarentena_lote_germinacion += items_levanta_cuarentena.cantidad_a_levantar
        
        else:
            inventario_vivero.cantidad_lote_cuarentena += items_levanta_cuarentena.cantidad_a_levantar

        #GUARDADO 
        persona_anulada = request.user.persona
        items_levanta_cuarentena.levantamiento_anulado = True
        items_levanta_cuarentena.fecha_anulacion = datetime.now()
        items_levanta_cuarentena.id_persona_anula = persona_anulada
        items_levanta_cuarentena.justificacion_anulacion = data['justificacion_anulacion']
        
        items_levanta_cuarentena.id_cuarentena_mat_vegetal.save()
        items_levanta_cuarentena.save()
        inventario_vivero.save()
        
       #AUDITORIA DEL SERVICIO DE GUARDADO
        descripcion = {"nombre_vivero": items_levanta_cuarentena.id_cuarentena_mat_vegetal.id_vivero.nombre,
                       'nombre_bien': items_levanta_cuarentena.id_cuarentena_mat_vegetal.id_bien.nombre,
                       'numero_lote': str(items_levanta_cuarentena.id_cuarentena_mat_vegetal.nro_lote),
                       'agno_lote': str(items_levanta_cuarentena.id_cuarentena_mat_vegetal.agno_lote),
                       'etapa_lote': items_levanta_cuarentena.id_cuarentena_mat_vegetal.cod_etapa_lote,
                       'fecha_cuarentena':str(items_levanta_cuarentena.id_cuarentena_mat_vegetal.fecha_cuarentena)}
        direccion=Util.get_client_ip(request)
        valores_actualizados_detalles= [{'previous':items_levanta_cuarentena_previous,'current':items_levanta_cuarentena,'descripcion':{'fecha_levantamiento':str(items_levanta_cuarentena.fecha_levantamiento)}}]
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 53,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles":valores_actualizados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True,'detail':'El levantamiendo de cuarentena de material vegetal fue anulado correctamente'},status=status.HTTP_200_OK)        
        