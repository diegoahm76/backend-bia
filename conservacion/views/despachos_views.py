from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from almacen.models.solicitudes_models import (
    DespachoConsumo
)
from almacen.models.bienes_models import CatalogoBienes

from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from conservacion.serializers.despachos_serializers import (
    DespachosEntrantesSerializer,
    ItemsDespachosEntrantesSerializer,
    DistribucionesItemDespachoEntranteSerializer,
    DistribucionesItemPreDistribuidoSerializer
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
            "persona_distribuye": str(despacho_entrante_previous.id_persona_distribuye.primer_nombre + ' ' + despacho_entrante_previous.id_persona_distribuye.primer_apellido if despacho_entrante_previous.id_persona_distribuye.tipo_persona=='N' else despacho_entrante_previous.id_persona_distribuye.razon_social)
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
                return Response({'success':response_dict['success'], 'detail':response_dict['detail']}, status=response_dict['status'])

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
        
        return Response({'success':False, 'detail':'El despacho entrante elegido no existe'}, status=status.HTTP_404_NOT_FOUND)

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
            
        