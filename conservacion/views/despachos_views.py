from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from datetime import timezone
from conservacion.models.inventario_models import InventarioViveros
import copy
import json
from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from almacen.models.solicitudes_models import (
    DespachoConsumo
)
from almacen.models.generics_models import (
    Bodegas
)
from almacen.models.bienes_models import CatalogoBienes
from almacen.models.inventario_models import Inventario

from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.utils import UtilConservacion
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from conservacion.models.despachos_models import (
    DespachoViveros,
    ItemsDespachoViveros,
)
from conservacion.serializers.despachos_serializers import (
    DespachosEntrantesSerializer,
    ItemsDespachosEntrantesSerializer,
    DistribucionesItemDespachoEntranteSerializer,
    DistribucionesItemPreDistribuidoSerializer,
    SolicitudesParaDespachoSerializer,
    DespachosViveroSerializer,
    ItemsDespachoViveroSerializer,
    ItemsSolicitudVieroParaDespachoSerializer,
    GetInsumoSerializer,
    GetPlantaSerializer,
    DespachosParaDespachoSerializer,
)
from conservacion.utils import UtilConservacion

class GetDespachosEntrantes(generics.ListAPIView):
    serializer_class=DespachosEntrantesSerializer
    queryset=DespachoEntrantes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        numero_despacho_consumo = request.query_params.get('numero_despacho')
        despachos_entrantes = self.queryset.all()
        
        if numero_despacho_consumo:
            despacho_consumo = DespachoConsumo.objects.filter(numero_despacho_consumo=numero_despacho_consumo).first()
            despachos_entrantes = despachos_entrantes.filter(id_despacho_consumo_alm=despacho_consumo.id_despacho_consumo) if despacho_consumo else None
        
        serializer=self.serializer_class(despachos_entrantes, many=True)
        if despachos_entrantes:
            return Response({'success':True,'detail':'Se encontraron despachos entrantes','data':serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response({'success':True,'detail':'No se encontraron despachos entrantes', 'data':[]}, status=status.HTTP_200_OK)

class GetItemsDespachosEntrantes(generics.ListAPIView):
    serializer_class=ItemsDespachosEntrantesSerializer
    queryset=ItemsDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        items_despacho = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=pk).values(
            'id_item_despacho_entrante',
            'id_despacho_entrante',
            'id_bien',
            'id_entrada_alm_del_bien',
            'fecha_ingreso',
            'cantidad_entrante',
            'cantidad_distribuida',
            'observacion',
            codigo_bien=F('id_bien__codigo_bien'),
            nombre_bien=F('id_bien__nombre'),
            cod_tipo_elemento_vivero=F('id_bien__cod_tipo_elemento_vivero'),
            es_semilla_vivero=F('id_bien__es_semilla_vivero'),
            unidad_medida=F('id_bien__id_unidad_medida__abreviatura'),
            tipo_documento=F('id_entrada_alm_del_bien__id_tipo_entrada__nombre'),
            numero_documento=F('id_entrada_alm_del_bien__numero_entrada_almacen')
        ).annotate(cantidad_restante=Sum('cantidad_entrante') - Sum('cantidad_distribuida'))
        
        if items_despacho:
            return Response({'success':True,'detail':'Se encontraron items de despachos entrantes','data':items_despacho}, status=status.HTTP_200_OK)
        else: 
            return Response({'success':True,'detail':'No se encontraron items de despachos entrantes', 'data':[]}, status=status.HTTP_200_OK)
        
class GuardarDistribucionBienes(generics.ListAPIView):
    serializer_class=DistribucionesItemDespachoEntranteSerializer
    queryset=DistribucionesItemDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_despacho_entrante):
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        despacho_entrante_previous = copy.copy(despacho_entrante)
        
        response_dict = UtilConservacion.guardar_distribuciones(id_despacho_entrante, request, self.queryset.all())
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        
        # AUDITORIA MAESTRO
        descripcion_maestro = {
            "numero_despacho_consumo": str(despacho_entrante_previous.id_despacho_consumo_alm.numero_despacho_consumo),
            "fecha_ingreso": str(despacho_entrante_previous.fecha_ingreso),
            "distribucion_confirmada": str(despacho_entrante_previous.distribucion_confirmada),
            "fecha_confirmacion_distribucion": str(despacho_entrante_previous.fecha_confirmacion_distribucion),
            "observacion_distribucion": str(despacho_entrante_previous.observacion_distribucion),
            "persona_distribuye": str(despacho_entrante_previous.id_persona_distribuye.primer_nombre + ' ' + despacho_entrante_previous.id_persona_distribuye.primer_apellido if despacho_entrante_previous.id_persona_distribuye.tipo_persona=='N' else despacho_entrante_previous.id_persona_distribuye.razon_social) if despacho_entrante_previous.id_persona_distribuye else 'None'
        }
        valores_actualizados={'previous':despacho_entrante_previous, 'current':despacho_entrante}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 48,
            "cod_permiso": 'AC',
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion_maestro,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':response_dict['success'], 'detail':response_dict['detail']}, status=response_dict['status'])     
       
class ConfirmarDistribucion(generics.UpdateAPIView):
    serializer_class=DistribucionesItemDespachoEntranteSerializer
    queryset=DistribucionesItemDespachoEntrante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_despacho_entrante):
        
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=id_despacho_entrante).first()
        
        if despacho_entrante:
            
            despacho_entrante_previous=copy.copy(despacho_entrante)
            response_dict = UtilConservacion.guardar_distribuciones(id_despacho_entrante, request, self.queryset.all(),True)
            
            if response_dict['success'] != True:
                raise ValidationError(response_dict['detail'])

            despacho_entrante.fecha_confirmacion_distribucion = datetime.now()
            despacho_entrante.observacion_distribucion=despacho_entrante.observacion_distribucion
            despacho_entrante.id_persona_distribuye=request.user.persona
            despacho_entrante.distribucion_confirmada=True
            despacho_entrante.save()
        
            data = request.data
            
            for item in data:
                item_despacho_entrante = ItemsDespachoEntrante.objects.filter(id_item_despacho_entrante=item['id_item_despacho_entrante']).first()
                vivero=Vivero.objects.filter(id_vivero=item['id_vivero']).first()
                bien=CatalogoBienes.objects.filter(id_bien=item_despacho_entrante.id_bien.id_bien).first()
                if despacho_entrante.distribucion_confirmada == True:
                    if item_despacho_entrante.id_bien.cod_tipo_elemento_vivero == "HE" or item_despacho_entrante.id_bien.cod_tipo_elemento_vivero == "IN" or (item_despacho_entrante.id_bien.cod_tipo_elemento_vivero == "MV" and item_despacho_entrante.id_bien.es_semilla_vivero == True):
                        
                        vivero_destino=InventarioViveros.objects.filter(id_vivero=item['id_vivero'],id_bien=item_despacho_entrante.id_bien.id_bien, id_siembra_lote_germinacion=None).first()
                        if vivero_destino:
                            vivero_destino.cantidad_entrante = vivero_destino.cantidad_entrante if vivero_destino.cantidad_entrante else 0
                            vivero_destino.cantidad_entrante += item['cantidad_asignada']
                            vivero_destino.save()
                            
                        else:
                            InventarioViveros.objects.create(
                                id_vivero = vivero,
                                id_bien = bien,
                                cantidad_entrante = item['cantidad_asignada']
                            )
                            
                    elif item_despacho_entrante.id_bien.cod_tipo_elemento_vivero == "MV" and item_despacho_entrante.id_bien.es_semilla_vivero == False:
                            vivero_destino=InventarioViveros.objects.filter(id_vivero=item['id_vivero'],id_bien=item_despacho_entrante.id_bien.id_bien).last()
                            nro_lote = 1
                            if vivero_destino:
                                nro_lote = vivero_destino.nro_lote + 1 if vivero_destino.nro_lote else 1
                                
                            if item["cod_etapa_lote_al_ingresar"] == 'G':
                                raise ValidationError('No puede distribuir un material vegetal no semilla a germinación')
                                
                            InventarioViveros.objects.create(
                                id_vivero = vivero,
                                id_bien = bien,
                                cantidad_entrante = item['cantidad_asignada'],
                                agno_lote = datetime.now().year,
                                nro_lote = nro_lote,
                                cod_etapa_lote = item["cod_etapa_lote_al_ingresar"],
                                es_produccion_propia_lote = False,
                                cod_tipo_entrada_alm_lote = item_despacho_entrante.id_entrada_alm_del_bien.id_tipo_entrada if item_despacho_entrante.id_entrada_alm_del_bien else None,
                                nro_entrada_alm_lote =  item_despacho_entrante.id_entrada_alm_del_bien.numero_entrada_almacen if item_despacho_entrante.id_entrada_alm_del_bien else None,
                                fecha_ingreso_lote_etapa= datetime.now(),
                            )  
            # AUDITORIA MAESTRO
            descripcion_maestro = {
                "numero_despacho_consumo": str(despacho_entrante_previous.id_despacho_consumo_alm.numero_despacho_consumo),
                "fecha_ingreso": str(despacho_entrante_previous.fecha_ingreso),
                "distribucion_confirmada": str(despacho_entrante_previous.distribucion_confirmada),
                "fecha_confirmacion_distribucion": str(despacho_entrante_previous.fecha_confirmacion_distribucion),
                "observacion_distribucion": str(despacho_entrante_previous.observacion_distribucion),
                "persona_distribuye": (str(despacho_entrante_previous.id_persona_distribuye.primer_nombre + ' ' + despacho_entrante_previous.id_persona_distribuye.primer_apellido if despacho_entrante_previous.id_persona_distribuye.tipo_persona=='N' else despacho_entrante_previous.id_persona_distribuye.razon_social)) if despacho_entrante_previous.id_persona_distribuye else None
            }
            valores_actualizados={'previous':despacho_entrante_previous, 'current':despacho_entrante}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario": request.user.id_usuario,
                "id_modulo": 48,
                "cod_permiso": 'AC',
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion_maestro,
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
                       
            return Response({'success':True, 'detail':'Confirmación exitosa'}, status=status.HTTP_200_OK)
        
        raise NotFound('El despacho entrante elegido no existe')

class GetItemsPredistribuidos(generics.ListAPIView):
    serializer_class=DistribucionesItemPreDistribuidoSerializer
    queryset=DistribucionesItemDespachoEntrante
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        despacho_entrante=DespachoEntrantes.objects.filter(id_despacho_entrante=pk).first()
        if despacho_entrante:
            item_despacho_entrante= ItemsDespachoEntrante.objects.filter(id_despacho_entrante=despacho_entrante.id_despacho_entrante)
            list_item_despacho = [item.id_item_despacho_entrante for item in item_despacho_entrante ]
            distribuciones_item_despacho = DistribucionesItemDespachoEntrante.objects.filter(id_item_despacho_entrante__in = list_item_despacho)
            
            serializador=self.serializer_class(distribuciones_item_despacho,many=True)
            return Response ({'success':True,'detail':'Se encontraron items pre-distribuidos: ','data':serializador.data},status=status.HTTP_200_OK)
        
class CreateDespacho(generics.UpdateAPIView):
    serializer_class = DespachosViveroSerializer
    queryset = DespachoViveros.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_items_vivero = ItemsDespachoViveroSerializer
    
    def put(self,request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_con_recibido'] = request.FILES.get('ruta_archivo_con_recibido')
        queryset = self.queryset.all()
        
        #Validaciones de la solicitud
        instancia_solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=info_despacho['id_solicitud_a_viveros'], fecha_aprobacion_coord_viv__lte=info_despacho['fecha_despacho']).first()
        if not instancia_solicitud:
            raise NotFound('Debe ingresar un id de solicitud válido')
        
        if instancia_solicitud.solicitud_abierta == False or instancia_solicitud.estado_aprobacion_responsable != 'A':
            raise NotFound('La solicitud a despachar debe de estar aprobada por el funcionario responsable y no debe de estar cerrada')
        
        # SE ASIGNAN LOS CAMPOS RELACIONADOS CON LA SOLICITUD
        info_despacho['nro_solicitud_a_viveros'] = instancia_solicitud.nro_solicitud
        info_despacho['fecha_solicitud_a_viveros'] = instancia_solicitud.fecha_solicitud
        info_despacho['fecha_solicitud_retiro_material'] = instancia_solicitud.fecha_retiro_material
        info_despacho['id_persona_solicita'] = instancia_solicitud.id_persona_solicita.id_persona
        info_despacho['id_unidad_para_la_que_solicita'] = instancia_solicitud.id_unidad_para_la_que_solicita.id_unidad_organizacional
        info_despacho['id_funcionario_responsable_unidad'] = instancia_solicitud.id_funcionario_responsable_und_destino.id_persona
        
        # SE ASIGNA LA PERSONA QUE REGISTRA LA SOLICITUD
        info_despacho['id_persona_despacha'] = user_logeado.persona.id_persona
        
        # ASIGNACIÓN DE NÚMERO DE DESPACHO VIVEROS
        despachos_existentes = queryset.all()
        if despachos_existentes:
            numero_despachos = [i.nro_despachos_viveros for i in despachos_existentes]
            info_despacho['nro_despachos_viveros'] = max(numero_despachos) + 1
        else:
            info_despacho['nro_despachos_viveros'] = 1
        
        # ASIGNACIÓN DE LA FECHA REGISTRO
        info_despacho['fecha_registro'] = datetime.now()
        
        # SE HACEN VALIDACIONES A LA FECHA
        fecha_despacho = datetime.strptime(info_despacho.get('fecha_despacho'), "%Y-%m-%d %H:%M:%S")
        aux_validacion_fechas = info_despacho['fecha_registro'] - fecha_despacho
        if int(aux_validacion_fechas.days) > 8 or int(aux_validacion_fechas.days) < 0:
            raise NotFound('La fecha ingresada no es permitida dentro de los parametros existentes')
        
        fecha_aprobacion_solicitud = instancia_solicitud.fecha_aprobacion_coord_viv
        if fecha_aprobacion_solicitud == None:
            raise NotFound('La solicitud que desea despachar no tiene registrada fecha de aprobación del responsable')
        if fecha_despacho <= fecha_aprobacion_solicitud:
            raise NotFound('La fecha de despacho debe ser mayor o igual a la fecha de aprobación de la solicitud')
            
        # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=info_despacho['id_solicitud_a_viveros'])
        if not items_solicitud:
            raise NotFound('La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar')
        id_items_solicitud = [i.id_bien.id_bien for i in items_solicitud]
        
        id_bienes_ingresados = [i['id_bien'] for i in items_despacho]
        
        aux_id_bienes_no_ingresados = [i for i in id_items_solicitud if i not in id_bienes_ingresados]
        
        # SE VALIDA QUE EL DESPACHO TENGA ITEMS
        if items_despacho == None:
            raise NotFound('El despacho debe tener por lo menos un item')
        
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items = [i['nro_posicion_en_despacho'] for i in items_despacho]
        if len(nro_posicion_items) != len(set(nro_posicion_items)):
            raise NotFound('El número de posición debe ser único')
        
        # SE VALIDA QUE NO TODOS LOS ITEMS TENGAN CANTIDAD IGUAL A CERO
        validacion_ceros = [i['cantidad_despachada'] for i in items_despacho]
        
        if len(set(validacion_ceros)) <= 1 and len(items_despacho)!=1:
            raise NotFound('No todos las cantidades despachadas de los items pueden estar en cero')
        
        # SE VALIDA QUE EL DESPACHO TENGA AL MENOS UN ITEMS
        if len(items_despacho) == 0:
            raise NotFound('Se debe despachar al menos un item')
        
        # VALIDACIONES EN ITEMS DEL DESPACHO
        aux_cantidad_total = {}
        aux_validacion_bienes_despachados_repetidos = []
        aux_validacion_bienes_despachados_contra_solicitados = []
        axu_validacion_cantidades_despachadas_total = []
        valores_creados_detalles = []
        aux_validacion_bienes_repetidos = {}
        aux_validacion_unidades_dic = {}
        
        for i in items_despacho:
            # SE VALIDA QUE EL BIEN A DESPACHAR SE ENCUENTRE DENTRO DE LA SOLICITUD
            bien_despachado = i.get('id_bien')
            if (bien_despachado not in id_items_solicitud):
                raise NotFound('Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud')
            
            # SE VALIDA LA EXISTENCIA DEL BIEN EN CATÁLOGO DE BIENES
            instancia_bien = CatalogoBienes.objects.filter(id_bien = bien_despachado).first()
            if not instancia_bien:
                raise NotFound('El bien con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe')
            
            instancia_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=info_despacho['id_vivero']).first()

            if not instancia_inventario:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe en el inventario del vivero.')
            
            if ([i['id_bien'], i["agno_lote"], i["nro_lote"], i["cod_etapa_lote"]] in aux_validacion_bienes_despachados_repetidos):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). No se puede ingresar dos veces el mismo bien.')
            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN EN EL INVENTARIO DEL VIVERO SEA MAYOR A CERO
            cantidad_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_inventario)
            if cantidad_disponible <= 0:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no tiene cantidad disponible.')

            # SE VALIDA QUE LA CANTIDAD DE LA SUMA DE LOS BIENES NO SUPERA LA CANTIDAD DESPACHADA
            if str(i['id_bien']) in aux_cantidad_total:
                aux_cantidad_total[str(i['id_bien'])] = aux_cantidad_total[str(i['id_bien'])] + i['cantidad_despachada']
                
            else:
                aux_cantidad_total[str(i['id_bien'])] = i['cantidad_despachada']
            
            if aux_cantidad_total[str(i['id_bien'])] > int(i['cantidad_solicitada']):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La suma de las cantidades despachadas de este bien supera la cantidad solicitada.')
            
            # SE VALDIA QUE EL BIEN ESTE ENTRE EL NIVEL JERARQUICO 2 Y 5
            if instancia_bien.nivel_jerarquico > 5 or instancia_bien.nivel_jerarquico < 2:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). El bien no es de nivel 2 al 5')
            
            # SE VALIDA QUE EL BIEN SEA DE CONSUMO
            if instancia_bien.cod_tipo_bien != 'C':
                raise NotFound('El bien (' + instancia_bien.nombre + ') no es de consumo')
            
            if (instancia_bien.es_semilla_vivero == True and instancia_bien.cod_tipo_elemento_vivero == "MV") or instancia_bien.cod_tipo_elemento_vivero == "HE":
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Solo se pueden despachar plantas que se encuentren en distribución o insumos.')
            
            if instancia_bien.cod_tipo_elemento_vivero == 'IN' and (i['agno_lote'] != None or i['nro_lote'] != None or i['cod_etapa_lote'] != None):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si el bien a despachar es tipo insumo debe dejar los campos (agno_lote), (nro_lote) y (cod_etapa_lote) en null.')
            
            if instancia_bien.cod_tipo_elemento_vivero == 'MV' and instancia_bien.es_semilla_vivero == False and (i['agno_lote'] == None or i['nro_lote'] == None or i['cod_etapa_lote'] == None or i['agno_lote'] == '' or i['nro_lote'] == '' or i['cod_etapa_lote'] == ''):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si el bien a despachar es tipo planta debe ingrasar los campos (agno_lote), (nro_lote) y (cod_etapa_lote)')
            
            # SE VALIDA QUE CUANDO SE INGRESE UNA CANTIDAD DESPACHADA IGUAL A CERO SE CUMPLAN LOS REQUERIMIENTOS EXIGIDOS POR MODELADO
            if i['cantidad_despachada'] == 0:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si la cantidad despachada es igual a cero no debe ingresar ninguna subfila')
            
            # SE VALIDA QUE CUANDO SE INGRESE UNA CANTIDAD DESPACHADA IGUAL A CERO SE CUMPLAN LOS REQUERIMIENTOS EXIGIDOS POR MODELADO
            if i['cantidad_despachada'] >= i['cantidad_solicitada']:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La cantidad despachada debe ser menor a la cantidad solicitada.')
            
            aux_validacion_bienes_despachados_repetidos.append([i['id_bien'], i["agno_lote"], i["nro_lote"], i["cod_etapa_lote"]])
            valores_creados_detalles.append({'nombre' : instancia_inventario.id_bien.nombre})
            
            
        for i in aux_id_bienes_no_ingresados:
            items_despacho.append({
            "id_bien": i,
            "agno_lote": None,
            "nro_lote": None,
            "cod_etapa_lote": None,
            "cantidad_solicitada": 0,
            "cantidad_despachada": 0,
            "observacion_del_despacho": "0",
            "nro_posicion_en_despacho" : None
            })
        
        serializer = self.serializer_class(data=info_despacho)
        serializer.is_valid(raise_exception=True)
        aux_ultimo = serializer.save()
        
        # SE ASIGNA EL ID DEL DESPACHO A LOS ITEMS DEL DESPACHO
        for i in items_despacho:
            i['id_despacho_viveros'] = aux_ultimo.pk
        
        serializer_items = self.serializer_items_vivero(data=items_despacho, many=True)
        serializer_items.is_valid(raise_exception=True)
        serializer_items.save()
        
        # INSERT EN LA TABLA INVENTARIO
        for i in items_despacho:
            bien_despachado = i.get('id_bien')
            instancia_bien = CatalogoBienes.objects.filter(id_bien = bien_despachado).first()
            if instancia_bien.cod_tipo_elemento_vivero == 'IN':
                inventario_instancia = InventarioViveros.objects.filter(Q(id_bien=i['id_bien'])&Q(id_vivero=info_despacho['id_vivero'])).first()
                inventario_instancia.cantidad_salidas = inventario_instancia.cantidad_salidas if inventario_instancia.cantidad_salidas else 0
                inventario_instancia.cantidad_salidas = int(inventario_instancia.cantidad_salidas) + int(i['cantidad_despachada'])
                inventario_instancia.save()
            if instancia_bien.cod_tipo_elemento_vivero == 'MV' and instancia_bien.es_semilla_vivero == False:
                inventario_instancia = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=info_despacho['id_vivero'],agno_lote=i['agno_lote'],nro_lote=i['nro_lote']).first()
                inventario_instancia.cantidad_salidas = inventario_instancia.cantidad_salidas if inventario_instancia.cantidad_salidas else 0
                inventario_instancia.cantidad_salidas = int(inventario_instancia.cantidad_salidas) + int(i['cantidad_despachada'])
                inventario_instancia.save()
        
        # INSERT EN LA TABLA SOLICITUDES DE CONSUMIBLES
        instancia_solicitud.id_despacho_viveros = aux_ultimo.pk
        instancia_solicitud.fecha_cierra_solicitud = info_despacho['fecha_registro']
        instancia_solicitud.gestionada_viveros = True
        instancia_solicitud.solicitud_abierta = False
        instancia_solicitud.save()
        
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"numero_despacho_vivero": str(info_despacho['nro_despachos_viveros']), "fecha_despacho": str(info_despacho['fecha_despacho'])}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 61,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True,'detail':'Despacho creado con éxito', 'Numero despacho' : info_despacho["nro_despachos_viveros"]},status=status.HTTP_200_OK)
    
class UpdatePreparacionMezclas(generics.UpdateAPIView):
    serializer_class = DespachosViveroSerializer
    queryset = DespachoViveros.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_items_vivero = ItemsDespachoViveroSerializer
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_con_recibido'] = request.FILES.get('ruta_archivo_con_recibido')
        queryset = self.queryset.all()
     
        items_nuevos = []
        items_actualizar = []
        items_eliminar = []
        valores_eliminados_detalles = []
        valores_actualizados_detalles = []
        aux_valores_repetidos = []
        aux_nro_posicion = []

        instancia_despacho = DespachoViveros.objects.filter(id_despacho_viveros=info_despacho['id_despacho_viveros']).first()

        if not instancia_despacho:
            raise ValidationError('No se encontró el despacho que desea actualizar.')
        
        
        # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=instancia_despacho.id_solicitud_a_viveros)
        if not items_solicitud:
            raise NotFound('La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar')
        id_items_solicitud = [i.id_bien.id_bien for i in items_solicitud]
        
        id_bienes_ingresados = [i['id_bien'] for i in items_despacho]
        
        aux_id_bienes_no_ingresados = [i for i in id_items_solicitud if i not in id_bienes_ingresados]
        
        # SE VALIDA QUE EL DESPACHO TENGA ITEMS
        if items_despacho == None:
            raise NotFound('El despacho debe tener por lo menos un item')
        
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items = [i['nro_posicion_en_despacho'] for i in items_despacho]
        if len(nro_posicion_items) != len(set(nro_posicion_items)):
            raise NotFound('El número de posición debe ser único')
        
        # SE VALIDA QUE NO TODOS LOS ITEMS TENGAN CANTIDAD IGUAL A CERO
        validacion_ceros = [i['cantidad_despachada'] for i in items_despacho]
        
        if len(set(validacion_ceros)) <= 1 and len(items_despacho)!=1:
            raise NotFound('No todos las cantidades despachadas de los items pueden estar en cero')
        
        # SE VALIDA QUE EL DESPACHO TENGA AL MENOS UN ITEMS
        if len(items_despacho) == 0:
            raise NotFound('Se debe despachar al menos un item')
        
        # SE VALIDA LA FECHA
        fecha_despacho = instancia_despacho.fecha_despacho
        fecha_posible = datetime.now() - timedelta(days=9)
        if fecha_despacho < fecha_posible:
            raise ValidationError('No es posible actualiazar un despacho con más de 9 días de anterioridad.')
    
        # SE OBTIENEN LOS ITEMS ITEMS QUE SE VAN A AÑADIR
        items_nuevos = [i for i in items_despacho if i['id_item_despacho_viveros'] == None]
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ACTUALZIAR
        items_actualizar = [i for i in items_despacho if i['id_item_despacho_viveros'] != None]
        
        # SE OBTIENEN LOS ITEMS QUE SE VAN A ELIMINAR
        items_existentes = ItemsDespachoViveros.objects.filter(id_despacho_viveros=info_despacho['id_despacho_viveros'])
        aux_validacion_eliminar_0 = {}
        for aux_for in items_existentes:
            if aux_for.id_bien.cod_tipo_elemento_vivero == 'MV' and aux_for.id_bien.es_semilla_vivero == False:
                if aux_for.id_bien.id_bien in aux_validacion_eliminar_0:
                    aux_validacion_eliminar_0[aux_for.id_bien.id_bien] = aux_validacion_eliminar_0[aux_for.id_bien.id_bien] + 1
                else:
                    aux_validacion_eliminar_0[aux_for.id_bien.id_bien] = 1
        id_items_existentes = [[i.id_bien.id_bien, i.agno_lote, i.nro_lote] for i in items_existentes]
        id_items_entrantes = [[i['id_bien'], i['agno_lote'], i['nro_lote']] for i in items_despacho if i['id_item_despacho_viveros']!=None]
        id_items_eliminar = [i for i in id_items_existentes if i not in id_items_entrantes]

        items_eliminar = []
        aux_validacion_eliminar = {}
        items_crear_nuevamente = []
        for i in id_items_eliminar:
            aux_for = ItemsDespachoViveros.objects.filter(id_despacho_viveros=instancia_despacho.id_despacho_viveros,id_bien=i[0],nro_lote=i[2],agno_lote=i[1]).first()
            items_eliminar.append(aux_for)
            if aux_for.id_bien.cod_tipo_elemento_vivero == 'IN':
                items_crear_nuevamente.append([aux_for.id_bien.id_bien, aux_for.cantidad_solicitada])
            if aux_for.id_bien.cod_tipo_elemento_vivero == 'MV' and aux_for.id_bien.es_semilla_vivero == False:
                if aux_for.id_bien.id_bien in aux_validacion_eliminar:
                    aux_validacion_eliminar[aux_for.id_bien.id_bien] = aux_validacion_eliminar[aux_for.id_bien.id_bien] + 1
                else:
                    aux_validacion_eliminar[aux_for.id_bien.id_bien] = 1
        # SE VALIDA QUE NO SE BORREN TODOS LOS REGISTROS EXISTENTES DE UNA PLANTA
        for key in aux_validacion_eliminar:
            if aux_validacion_eliminar[key] == aux_validacion_eliminar_0[key]:
                aux_for = ItemsDespachoViveros.objects.filter(id_despacho_viveros=instancia_despacho.id_despacho_viveros,id_bien=key).first()
                items_crear_nuevamente.append([key, aux_for.cantidad_solicitada])
                
        if items_eliminar != []:
            valores_eliminados_detalles = [{'nombre' : i.id_bien.nombre} for i in items_eliminar]
            
        # SE VALIDA QUE NO SE SUPERE LA CANTIDAD SOLICITADA
        aux_cantidad_total = {}
        for i in items_despacho:
            bien_despachado = i.get('id_bien')
             # SE VALIDA LA EXISTENCIA DEL BIEN EN CATÁLOGO DE BIENES
            instancia_bien = CatalogoBienes.objects.filter(id_bien = bien_despachado).first()
            if not instancia_bien:
                raise NotFound('El bien con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe')
            
            instancia_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=instancia_despacho.id_vivero).first()

            if not instancia_inventario:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe en el inventario del vivero.')
            
            if str(i['id_bien']) in aux_cantidad_total:
                aux_cantidad_total[str(i['id_bien'])] = aux_cantidad_total[str(i['id_bien'])] + i['cantidad_despachada']
            else:
                aux_cantidad_total[str(i['id_bien'])] = i['cantidad_despachada']
            
            if aux_cantidad_total[str(i['id_bien'])] > int(i['cantidad_solicitada']):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La suma de las cantidades despachadas de este bien supera la cantidad solicitada.')
                               
#----------------------------------------------------> VALIDACIONES DE LOS ITEMS INSERTADOS USADOS EN LA PREPARACION <----------------------------#
        aux_cantidad_total = {}

        aux_validacion_bienes_despachados_repetidos = [[i.id_bien.id_bien, i.agno_lote, i.nro_lote, i.agno_lote] for i in items_existentes]
        aux_nro_posicion = []
        aux_valores_repetidos = []
        valores_creados_detalles = [] 
        aux_nro_posicion = [i.nro_posicion_en_despacho for i in items_existentes]   
        for i in items_nuevos:
            # SE VALIDA QUE EL BIEN A DESPACHAR SE ENCUENTRE DENTRO DE LA SOLICITUD
            bien_despachado = i.get('id_bien')
            if (bien_despachado not in id_items_solicitud):
                raise NotFound('Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud')
            
            # SE VALIDA LA EXISTENCIA DEL BIEN EN CATÁLOGO DE BIENES
            instancia_bien = CatalogoBienes.objects.filter(id_bien = bien_despachado).first()
            if not instancia_bien:
                raise NotFound('El bien con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe')
            
            instancia_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=instancia_despacho.id_vivero).first()

            if not instancia_inventario:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe en el inventario del vivero.')
            
            if ([i['id_bien'], i["agno_lote"], i["nro_lote"], i["cod_etapa_lote"]] in aux_validacion_bienes_despachados_repetidos):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). No se puede ingresar dos veces el mismo bien.')
            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN EN EL INVENTARIO DEL VIVERO SEA MAYOR A CERO
            cantidad_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_inventario)
            if cantidad_disponible <= 0:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no tiene cantidad disponible.')

            # SE VALIDA QUE LA CANTIDAD DE LA SUMA DE LOS BIENES NO SUPERA LA CANTIDAD DESPACHADA
            if str(i['id_bien']) in aux_cantidad_total:
                aux_cantidad_total[str(i['id_bien'])] = aux_cantidad_total[str(i['id_bien'])] + i['cantidad_despachada']
                
            else:
                aux_cantidad_total[str(i['id_bien'])] = i['cantidad_despachada']
            
            if aux_cantidad_total[str(i['id_bien'])] > int(i['cantidad_solicitada']):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La suma de las cantidades despachadas de este bien supera la cantidad solicitada.')
            
            # SE VALDIA QUE EL BIEN ESTE ENTRE EL NIVEL JERARQUICO 2 Y 5
            if instancia_bien.nivel_jerarquico > 5 or instancia_bien.nivel_jerarquico < 2:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). El bien no es de nivel 2 al 5')
            
            # SE VALIDA QUE EL BIEN SEA DE CONSUMO
            if instancia_bien.cod_tipo_bien != 'C':
                raise NotFound('El bien (' + instancia_bien.nombre + ') no es de consumo')
            
            if (instancia_bien.es_semilla_vivero == True and instancia_bien.cod_tipo_elemento_vivero == "MV") or instancia_bien.cod_tipo_elemento_vivero == "HE":
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Solo se pueden despachar plantas que se encuentren en distribución o insumos.')
            
            if instancia_bien.cod_tipo_elemento_vivero == 'IN' and (i['agno_lote'] != None or i['nro_lote'] != None or i['cod_etapa_lote'] != None):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si el bien a despachar es tipo insumo debe dejar los campos (agno_lote), (nro_lote) y (cod_etapa_lote) en null.')
            
            if instancia_bien.cod_tipo_elemento_vivero == 'MV' and instancia_bien.es_semilla_vivero == False and (i['agno_lote'] == None or i['nro_lote'] == None or i['cod_etapa_lote'] == None or i['agno_lote'] == '' or i['nro_lote'] == '' or i['cod_etapa_lote'] == ''):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si el bien a despachar es tipo planta debe ingrasar los campos (agno_lote), (nro_lote) y (cod_etapa_lote).')
            
            # SE VALIDA QUE CUANDO SE INGRESE UNA CANTIDAD DESPACHADA IGUAL A CERO SE CUMPLAN LOS REQUERIMIENTOS EXIGIDOS POR MODELADO
            if i['cantidad_despachada'] == 0:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). Si la cantidad despachada es igual a cero no debe ingresar ninguna subfila')
            
            # SE VALIDA QUE CUANDO SE INGRESE UNA CANTIDAD DESPACHADA IGUAL A CERO SE CUMPLAN LOS REQUERIMIENTOS EXIGIDOS POR MODELADO
            if i['cantidad_despachada'] >= i['cantidad_solicitada']:
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La cantidad despachada debe ser menor a la cantidad solicitada.')
            
            aux_validacion_bienes_despachados_repetidos.append([i['id_bien'], i["agno_lote"], i["nro_lote"], i["cod_etapa_lote"]])
            valores_creados_detalles.append({'nombre' : instancia_inventario.id_bien.nombre})
            
#----------------------------------------------------> VALIDACIONES DE LOS ITEMS A ACTUALIZAR USADOS EN LA PREPARACION <----------------------------#
        for i in items_actualizar:
            # SE VALIDA LA EXISTENCIA DE LA ITEM USADO EN LA PREPARACIÓN
            instancia_items_despacho = ItemsDespachoViveros.objects.filter(id_despacho_viveros=instancia_despacho.id_despacho_viveros,id_item_despacho_viveros=i['id_item_despacho_viveros']).first()
            if not instancia_items_despacho:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion_en_despacho']) + ' no existe el registro del despacho.')
            
            # SE VALIDA LA EXISTENCIA DEL BIEN USADO EN CATALOGO DE BIENES
            instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_items_despacho.id_bien.id_bien).first()
            if not instancia_bien:
                raise ValidationError('El bien con número de posición ' + str(i['nro_posicion_en_despacho']) + ' no existe registrado en el sistema como bien.')
        
            # SE VALIDA LA EXISTENCIA DEL BIEN USADO EN EL INVENTARIO DEL VIVERO
            instancia_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=instancia_despacho.id_vivero).first()

            if not instancia_inventario:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no existe en el inventario del vivero.')
           
            # SE VALIDA QUE LA CANTIDAD ACTUALIZADA NO SE VALIDE POR CERO
            if i['cantidad_despachada'] <= 0:
                raise ValidationError('El bien ' + str(instancia_bien.nombre) + ' con número de posición ' + str(i['nro_posicion']) + ' tiene cantidad igual a cero, la cantidad debe ser mayor que cero.')
            
            # SE VALIDA QUE LA CANTIDAD DEL BIEN EN EL INVENTARIO DEL VIVERO SEA MAYOR A CERO
            cantidad_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, instancia_inventario)
            if cantidad_disponible <= 0:
                raise NotFound('El bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + ') no tiene cantidad disponible.')

            # SE VALIDA QUE LA CANTIDAD DE LA SUMA DE LOS BIENES NO SUPERA LA CANTIDAD DESPACHADA
            if str(i['id_bien']) in aux_cantidad_total:
                aux_cantidad_total[str(i['id_bien'])] = aux_cantidad_total[str(i['id_bien'])] + i['cantidad_despachada']
                
            else:
                aux_cantidad_total[str(i['id_bien'])] = i['cantidad_despachada']
            
            if aux_cantidad_total[str(i['id_bien'])] > int(i['cantidad_solicitada']):
                raise NotFound('Error en el bien (' + instancia_bien.nombre + ') con número de posición (' + str(i['nro_posicion_en_despacho']) + '). La suma de las cantidades despachadas de este bien supera la cantidad solicitada.')
            
            aux_validacion_bienes_despachados_repetidos.append([instancia_bien.id_bien, i['id_bien'], i["agno_lote"], i["nro_lote"], i["cod_etapa_lote"]])
            

#----------------------------------------------------> ACTUALIZACION DE LOS VALORES DEL INVENTARIO VIVEROS <----------------------------#
        # SE RESTAN LAS CANTIDADES AL INVENTARIO VIVERO DE LOS ITEMS ELIMINADOS
        for i in items_eliminar:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien,id_vivero=instancia_despacho.id_vivero).first()
            instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas if instancia_bien_vivero.cantidad_salidas else 0
            instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas - i.cantidad_despachada
            instancia_bien_vivero.save()    
        
        for i in items_crear_nuevamente:
            items_nuevos.append({
            "id_bien": i[0],
            "agno_lote": None,
            "nro_lote": None,
            "cod_etapa_lote": None,
            "cantidad_solicitada": i[1],
            "cantidad_despachada": 0,
            "observacion_del_despacho": None,
            "nro_posicion_en_despacho" : None
            })
            
        # SE ACTUALIZAN LAS CANTIDADES DE LOS ITEMS USADOS EN EL INVENTARIO VIVERO
        for i in items_despacho:
            if i['id_item_despacho_viveros'] == None:
                bien_despachado = i.get('id_bien')
                instancia_bien = CatalogoBienes.objects.filter(id_bien = bien_despachado).first()
                if instancia_bien.cod_tipo_elemento_vivero == 'IN':
                    inventario_instancia = InventarioViveros.objects.filter(Q(id_bien=i['id_bien'])&Q(id_vivero=instancia_despacho.id_vivero)).first()
                    inventario_instancia.cantidad_salidas = inventario_instancia.cantidad_salidas if inventario_instancia.cantidad_salidas else 0
                    inventario_instancia.cantidad_salidas = int(inventario_instancia.cantidad_salidas) + int(i['cantidad_despachada'])
                    inventario_instancia.save()
                if instancia_bien.cod_tipo_elemento_vivero == 'MV' and instancia_bien.es_semilla_vivero == False:
                    inventario_instancia = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=instancia_despacho.id_vivero,agno_lote=i['agno_lote'],nro_lote=i['nro_lote']).first()
                    inventario_instancia.cantidad_salidas = inventario_instancia.cantidad_salidas if inventario_instancia.cantidad_salidas else 0
                    inventario_instancia.cantidad_salidas = int(inventario_instancia.cantidad_salidas) + int(i['cantidad_despachada'])
                    inventario_instancia.save()
                     
            elif i['id_item_despacho_viveros'] != None:
                if instancia_bien.cod_tipo_elemento_vivero == 'IN':
                    instancia_item_despacho = ItemsDespachoViveros.objects.filter(id_item_despacho_viveros=i['id_item_despacho_viveros']).first()
                    instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_despacho.id_bien.id_bien).first()
                    instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=instancia_item_despacho.id_bien,id_vivero=instancia_despacho.id_vivero).first()
                    instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas if instancia_bien_vivero.cantidad_salidas else 0
                    aux_cantidad = i['cantidad_despachada'] - instancia_item_despacho.cantidad_despachada
                    instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas + aux_cantidad
                    instancia_bien_vivero.save()
                if instancia_bien.cod_tipo_elemento_vivero == 'MV' and instancia_bien.es_semilla_vivero == False:
                    instancia_item_despacho = ItemsDespachoViveros.objects.filter(id_item_despacho_viveros=i['id_item_despacho_viveros']).first()
                    instancia_bien = CatalogoBienes.objects.filter(id_bien=instancia_item_despacho.id_bien.id_bien).first()
                    instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i['id_bien'],id_vivero=instancia_despacho.id_vivero,agno_lote=i['agno_lote'],nro_lote=i['nro_lote']).first()
                    instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas if instancia_bien_vivero.cantidad_salidas else 0
                    aux_cantidad = i['cantidad_despachada'] - instancia_item_despacho.cantidad_despachada
                    instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas + aux_cantidad
                    instancia_bien_vivero.save()

#----------------------------------------------------> SE GUARDAN LOS VALORES DEL MAESTRO Y SE INSERTAN Y/O ACTUALIZAN Y/O ELIMININAN LOS ITEMS <----------------------------#

        # SE GUARDAN LOS DATOS ACTUALIZADOS DEL MAESTRO DE LA PREPARACIÓN
        instancia_despacho.motivo = info_despacho['motivo']
        instancia_despacho.save()
        
        # SE BORRAN LOS ITEMS A ELIMINAR
        for i in items_eliminar:
            i.delete()
        
        for i in items_actualizar:
            i['id_despacho_viveros'] = instancia_despacho.id_despacho_viveros
        # SE ACTUALIZAN LOS ITEMS A ACTUALIZAR
        for i in items_actualizar:
            instancia_item_despacho = ItemsDespachoViveros.objects.filter(id_item_despacho_viveros=i['id_item_despacho_viveros']).first()
            previous_instancia_item = copy.copy(instancia_item_despacho)
            serializer_crear_items = self.serializer_items_vivero(instancia_item_despacho, data=i, many=False)
            serializer_crear_items.is_valid(raise_exception=True)
            serializer_crear_items.save()
            valores_actualizados_detalles.append({'descripcion': {'nombre' : instancia_item_despacho.id_bien.nombre},'previous':previous_instancia_item,'current':previous_instancia_item})
        
        # SE ASIGNA EL ID TRASLADO A LOS ITEMS A TRASLADAR
        for i in items_nuevos:
            i['id_despacho_viveros'] = instancia_despacho.id_despacho_viveros
        
        # SE CREA EL REGISTRO EN LA TABLA ITEM_TRASLADOS
        serializer_crear_items = self.serializer_items_vivero(data=items_nuevos, many=True)
        serializer_crear_items.is_valid(raise_exception=True)
        serializer_crear_items.save()

#----------------------------------------------------> AUDITORIA MAESTRO DETALLE <----------------------------#
        
        # AUDITORIA MAESTRO DETALLE DE LA MEZCLA
        descripcion = {"numero_despacho_vivero": str(instancia_despacho.nro_despachos_viveros), "fecha_despacho": str(instancia_despacho.fecha_despacho)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 61,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True, 'detail':'Despacho actualizado correctamente'}, status=status.HTTP_200_OK)
    
        

class GetSolicitudesVivero(generics.ListAPIView):
    serializer_class = SolicitudesParaDespachoSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        queryset = self.queryset.all()
        id_vivero = request.query_params.get('id_vivero')
        nro_solicitud = request.query_params.get('nro_solicitud')
        fecha_despacho = request.query_params.get('fecha_aprobado')
        
        # SE VALIDA QUE SE INGRESE EL VIVERO Y LA FECHA DE DESPACHO
        if not fecha_despacho or fecha_despacho == '':
            raise NotFound('Es obligatorio ingresar una fecha de despacho.')
        
        fecha_despacho = datetime.strptime(request.query_params.get('fecha_aprobado'), "%Y-%m-%d %H:%M:%S")
        
        if not id_vivero or id_vivero == '':
            raise NotFound('Es obligatorio seleccionar un vivero.')
        
        # SI SE INGRESA NÚMERO DE SOLICITUD SE BUSCA POR EL NÚMERO DE SOLICITUD, EL ID VIVERO Y QUE LA SOLICITUD SEA MENOR LA FECHA DE DESPACHO
        if nro_solicitud:
            instancia_solicitudes = queryset.filter(nro_solicitud=nro_solicitud,estado_aprobacion_responsable='A',solicitud_abierta=True,revisada_coord_viveros=True,estado_aprobacion_coord_viveros='A')
            # if not instancia_solicitudes:
            #     raise NotFound('No se encontraron coincidencias con ese número de solicitud')
            
            instancia_solicitudes = instancia_solicitudes.filter(id_vivero_solicitud=id_vivero) if instancia_solicitudes else []
            # if not instancia_solicitudes:
            #     raise NotFound('El número de solicitud ingresado no está registrada dentro del vivero ingresado')
            
            instancia_solicitudes = instancia_solicitudes.filter(fecha_aprobacion_responsable__lte=fecha_despacho).order_by('-fecha_aprobacion_responsable') if instancia_solicitudes else []
            # if not instancia_solicitudes:
            #     raise NotFound('La fecha del despacho debe ser superior a la fecha de la solicitud')
        
        # SI SE NO INGRESA NÚMERO DE SOLICITUD SE BUSCA POR EL ID VIVERO Y QUE LA SOLICITUD SEA MENOR LA FECHA DE DESPACHO
        else:
            instancia_solicitudes = queryset.filter(id_vivero_solicitud=id_vivero,estado_aprobacion_responsable='A',solicitud_abierta=True,revisada_coord_viveros=True,estado_aprobacion_coord_viveros='A')
            # if not instancia_solicitudes:
            #     raise NotFound('El vivero ingresado no tiene solicitudes registradas o no existe.')
            
            instancia_solicitudes = instancia_solicitudes.filter(fecha_aprobacion_responsable__lte=fecha_despacho).order_by('-fecha_aprobacion_responsable') if instancia_solicitudes else []
            # if not instancia_solicitudes:
            #     raise NotFound('La fecha del despacho debe ser superior a la fecha de la solicitud')
        serializador=self.serializer_class(instancia_solicitudes,many=True)
        
        return Response ({'success':True,'detail':'Datos encontrados','data':serializador.data},status=status.HTTP_200_OK)
    
class GetNroDespachoViveros(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR EL NÚMERO DEL ÚLTIMO DESPACHO DE VIVERO
    serializer_class = DespachosViveroSerializer
    queryset = DespachoViveros.objects.all()
    
    def get(self, request):
        queryset = self.queryset.all()
        nro_solicitud = queryset.all().order_by('nro_despachos_viveros').last()
        salida = 0 if nro_solicitud == None else nro_solicitud.nro_despachos_viveros
        return Response({'success':True,'detail':salida + 1, },status=status.HTTP_200_OK)
    
class GetItemsSolicitud(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR LOS ITEMS DE LA SOLICITUD
    serializer_class = ItemsSolicitudVieroParaDespachoSerializer
    queryset = ItemSolicitudViveros.objects.all()
    
    def get(self, request,id_solicitud_viveros):
        items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=id_solicitud_viveros)
        
        if not items_solicitud:
            raise NotFound('La solicitud seleccionada no tiene items registrados.')
        
        serializer = self.serializer_class(items_solicitud, many=True)
        
        return Response({'success':True,'data':serializer.data},status=status.HTTP_200_OK)
        
class GetInsumo(generics.ListAPIView):
    serializer_class = GetInsumoSerializer
    queryset=InventarioViveros.objects.all()
    
    def get(self,request,id_vivero,codigo_insumo):
        
        instancia_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_insumo, cod_tipo_bien='C', nivel_jerarquico=5, cod_tipo_elemento_vivero='IN').first()
        
        if not instancia_bien:
            raise NotFound('El bien ingresado no es de tipo insumo o no está registrado en Catalogo de bienes.')
        
        bien_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=id_vivero).first()
        if not bien_inventario:
                raise NotFound('El bien ingresado no existe en el inventario del vivero.')
            
        cantidad_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, bien_inventario) 
        
        if cantidad_disponible <= 0:
            raise NotFound('Este insumo no tiene cantidad disponible.')
        
        bien_inventario.cantidad_disponible = cantidad_disponible
    
        serializador = self.serializer_class(bien_inventario, many=False)
        
        return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)

class GetPlanta(generics.ListAPIView):
    serializer_class = GetPlantaSerializer
    queryset=InventarioViveros.objects.all()
    
    def get(self,request):
        id_vivero = request.query_params.get('id_vivero')
        codigo_bien = request.query_params.get('codigo_bien')
        nombre = request.query_params.get('nombre')
                    
         # SE VALIDA QUE SE INGRESE EL VIVERO Y EL CÓDIGO DEL BIEN
        if not id_vivero or id_vivero == '':
            raise NotFound('Es obligatorio ingresar un vivero.')
        
        if not codigo_bien or codigo_bien == '':
            raise NotFound('Es obligatorio ingresar el código del bien.')
        
        if not nombre or nombre == '':
            raise NotFound('Es obligatorio ingresar el nombre del bien un vivero.')
        
          
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['agno_lote','nro_lote']:
                if value != '':
                    filter[key]=value
       
        
        instancia_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, nombre=nombre, cod_tipo_bien='C', nivel_jerarquico=5, cod_tipo_elemento_vivero='MV', es_semilla_vivero=False).first()
        
        if not instancia_bien:
            raise NotFound('El bien ingresado no es una planta o no está registrado en Catalogo de bienes.')
        
        bien_inventario = InventarioViveros.objects.filter(id_bien=instancia_bien.id_bien, id_vivero=id_vivero, cod_etapa_lote='D', **filter)
        
        if not bien_inventario:
            raise NotFound('La planta ingresada no existe en el inventario del vivero o no hay ningún lote en etapa de distribución.')
        
        for i in bien_inventario:
            cantidad_disponible = UtilConservacion.get_cantidad_disponible_F(instancia_bien, i) 
        
            if cantidad_disponible <= 0:
                raise NotFound('Este insumo no tiene cantidad disponible.')
            
            i.cantidad_disponible = cantidad_disponible
    
        serializador = self.serializer_class(bien_inventario, many=True)
        
        return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)

class GetDespachosVivero(generics.ListAPIView):
    serializer_class = DespachosParaDespachoSerializer
    queryset = DespachoViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = self.queryset.all()
        filter = {}
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        id_vivero = request.query_params.get('id_vivero')
        nro_despachos_viveros = request.query_params.get('nro_solicitud')
        if fecha_desde == '' or fecha_desde == None:
            raise NotFound('La fecha desde es obligatoria.')
        if fecha_hasta == '' or fecha_hasta == None:
            raise NotFound('La fecha hasta es obligatoria.')
        if fecha_desde != '':
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
        if fecha_hasta != '':    
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        
        if not fecha_desde or fecha_desde == '':
            fecha_desde = datetime.today() - timedelta(30)
        if not fecha_hasta or fecha_hasta == '':
            fecha_hasta = datetime.today() + timedelta(1)
        else:
            fecha_hasta = fecha_hasta + timedelta(1)
        primer_filtro = DespachoViveros.objects.filter(fecha_despacho__range=[fecha_desde,fecha_hasta])
       
        for key, value in request.query_params.items():
            if key in ['nro_despachos_viveros', 'id_vivero']:
                if value != '':
                    filter[key]=value
        segundo_filtro = primer_filtro.filter(**filter)
        serializer = self.serializer_class(segundo_filtro, many=True)
        
        return Response({'success':True, 'detail':'Ok', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetItemsDespacho(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR LOS ITEMS DE LA SOLICITUD
    serializer_class = ItemsDespachoViveroSerializer
    queryset = ItemsDespachoViveros.objects.all()
    
    def get(self, request,id_despacho_vivero):
        items_despacho = ItemsDespachoViveros.objects.filter(id_despacho_viveros=id_despacho_vivero)
        
        if not items_despacho:
            raise NotFound('El despacho seleccionad0 no tiene items registrados.')
        
        serializer = self.serializer_class(items_despacho, many=True)
        
        return Response({'success':True,'data':serializer.data},status=status.HTTP_200_OK)
    
class AnularPreparacionMezclas(generics.UpdateAPIView):
    serializer_class = DespachosViveroSerializer
    queryset = DespachoViveros.objects.all()
    permission_classes = [IsAuthenticated]
    serializador_items_preparacion_mezclas = ItemsDespachoViveroSerializer
    
    def put(self, request, id_despacho_anular):
        queryset = self.queryset
        datos_ingresados = request.data
        valores_eliminados_detalles = []
        
        despacho_a_anular = queryset.filter(id_despacho_viveros=id_despacho_anular).first()
        if not despacho_a_anular:
            raise ValidationError('No se encontró ningun despacho con el id que ingresó')
        
        if despacho_a_anular.despacho_anulado == True:
            raise ValidationError('Este despacho ya fue anulado.')
        
        items_despacho_a_anular = ItemsDespachoViveros.objects.filter(id_despacho_viveros=despacho_a_anular.id_despacho_viveros)
        if not items_despacho_a_anular:
            raise ValidationError('Este despacho no registra items.')
        
        # SE VALIDA LA FECHA
        fecha_posible = datetime.now() - timedelta(days=9)
        if despacho_a_anular.fecha_despacho < fecha_posible:
            raise NotFound('No es posible anular un despacho que tenga más de 9 días de anterioridad.')
        
        # SE RESTA LA CANTIDAD DE LOS ITEMS DEL DESPACHO AL INVENTARIO DE VIVERO
        for i in items_despacho_a_anular:
            instancia_bien_vivero = InventarioViveros.objects.filter(id_bien=i.id_bien,id_vivero=despacho_a_anular.id_vivero).first()
            instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas if instancia_bien_vivero.cantidad_salidas else 0
            instancia_bien_vivero.cantidad_salidas = instancia_bien_vivero.cantidad_salidas - i.cantidad_despachada
            instancia_bien_vivero.save()    
        
        # SE INSERTAN LOS DATOS CORRESPONDIENTES EN LA TABLA DESPACHOS
        valores_eliminados_detalles = [{'nombre' : i.id_bien.nombre} for i in items_despacho_a_anular]
        items_despacho_a_anular.delete()
        despacho_a_anular.despacho_anulado = True
        despacho_a_anular.fecha_anulacion = datetime.now()
        despacho_a_anular.id_persona_anula = Personas.objects.filter(id_persona=request.user.persona.id_persona).first()
        despacho_a_anular.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        despacho_a_anular.save()
        
        #  SE INSERTAN LOS CAMPOS CORRESPONDIENTES EN LA TABLA SOLICITUDES DE VIVERO
        instancia_solicitud = SolicitudesViveros.objects.filter(id_despacho_viveros=despacho_a_anular.id_despacho_viveros).first()
        if not instancia_solicitud:
            raise ValidationError('No se encontró ninguna solicitud asociada con el despacho ingresado.')
        instancia_solicitud.id_despacho_viveros = None
        instancia_solicitud.solicitud_abierta = True
        instancia_solicitud.fecha_cierra_solicitud = None
        instancia_solicitud.gestionada_viveros = False
        instancia_solicitud.save()
                      
        # AUDITORIA MAESTRO DETALLE DE DESPACHO
        descripcion = {"Despacho": str(despacho_a_anular.id_despacho_viveros), "numero_despacho": str(despacho_a_anular.nro_despachos_viveros)}
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 61,
            "cod_permiso": "AN",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'succes' : True, 'detail' : 'Despacho viveros anualado con éxito'}, status=status.HTTP_200_OK)
    