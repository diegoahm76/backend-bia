from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from almacen.models.solicitudes_models import (
    DespachoConsumo
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante
)
from conservacion.serializers.despachos_serializers import (
    DespachosEntrantesSerializer,
    ItemsDespachosEntrantesSerializer
)

# class DitribucionDespachosViveros(generics.CreateAPIView):
#     serializer_class = DespachosEntrantesSerializer
#     queryset = DespachoEntrantes.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         data = request.data
#         persona = request.user.persona.id_persona
#         data['id_persona_crea'] = persona
        
#         # VALIDAR ASIGNACIÓN VIVERISTA
#         viverista = data.get('id_viverista_actual')
#         if viverista:
#             viverista_existe = Personas.objects.filter(id_persona=viverista)
#             if not viverista_existe:
#                 return Response({'status':False, 'detail':'Debe elegir un viverista que exista'}, status=status.HTTP_400_BAD_REQUEST)
            
#             viveristas_actuales = Vivero.objects.filter(id_viverista_actual = viverista)
            
#             if viveristas_actuales:
#                 return Response({'status':False, 'detail':'Debe elegir un viverista que no tenga ningún vivero asignado'}, status=status.HTTP_403_FORBIDDEN)
            
#             data['fecha_inicio_viverista_actual'] = datetime.now()
        
#         serializador = self.serializer_class(data=data)
#         serializador.is_valid(raise_exception=True)
#         serializador.save()
        
#         # AUDITORIA DE CREATE DE VIVEROS
#         user_logeado = request.user.id_usuario
#         dirip = Util.get_client_ip(request)
#         descripcion = {'nombre':data['nombre']}
#         auditoria_data = {
#             'id_usuario': user_logeado,
#             'id_modulo': 41,
#             'cod_permiso': 'CR',
#             'subsistema': 'CONS',
#             'dirip': dirip,
#             'descripcion': descripcion
#         }
#         Util.save_auditoria(auditoria_data)
        
#         return Response({'success':True, 'detail':'Se ha creado el vivero', 'data':serializador.data}, status=status.HTTP_201_CREATED)

class GetDespachosEntrantes(generics.ListAPIView):
    serializer_class=ItemsDespachosEntrantesSerializer
    queryset=DespachoEntrantes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        numero_despacho_consumo = request.query_params.get('numero_despacho')
        despachos_entrantes = self.queryset.all()
        
        if numero_despacho_consumo:
            despacho_consumo = DespachoConsumo.objects.filter(numero_despacho_consumo=numero_despacho_consumo).first()
            despachos_entrantes = despachos_entrantes.filter(id_despacho_consumo_alm=despacho_consumo.id_despacho_consumo)
        
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
        items_despacho = ItemsDespachoEntrante.objects.filter(id_despacho_entrante=pk)
        
        serializer=self.serializer_class(items_despacho, many=True)
        if items_despacho:
            return Response({'success':True,'detail':'Se encontraron items de despachos entrantes','data':serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response({'success':True,'detail':'No se encontraron items de despachos entrantes', 'data':[]}, status=status.HTTP_200_OK)