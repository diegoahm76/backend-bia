from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.despachos_serializers import SerializersDespachoConsumo, SerializersItemDespachoConsumo, SerializersSolicitudesConsumibles, SerializersItemsSolicitudConsumible
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from seguridad.models import (
    Personas,
    User,
    ClasesTerceroPersona
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from almacen.models.generics_models import (
    UnidadesMedida
)
from django.db.models import Q
from rest_framework.response import Response
from datetime import datetime, date
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer
import copy
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo, SolicitudesConsumibles, ItemsSolicitudConsumible

class CreateDespachoMaestro(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumo
    queryset = DespachoConsumo
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        #Validaciones primarias
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'data':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=datos_ingresados['id_solicitud_consumo'])
        if datos_ingresados['id_despacho_consumo'] == None:
            bandera_actualizar = False
        else:
            instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=datos_ingresados['id_solicitud_consumibles']).first()
            if not instancia_solicitud:
                return Response({'success':False,'data':'Si desea actualizar una solicitud, ingrese un id de solicitud de consumibles válido'},status=status.HTTP_404_NOT_FOUND)
            else:
                instancia_solicitud_previous = copy.copy(instancia_solicitud)
                bandera_actualizar = True
        
        #return Response({'success': False, 'detail': 'Falló'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'detail': datos_ingresados})
    