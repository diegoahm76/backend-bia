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
        etapas_lotes_in_vivero = InventarioViveros.objects.filter(id_bien__codigo_bien=id_codigo, id_vivero=id_vivero)
        if not etapas_lotes_in_vivero:
            return Response({'success': False, 'detail': 'El codigo ingresado no existe en una etapa lote'}, status=status.HTTP_400_BAD_REQUEST)
        

        data = []
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': data})