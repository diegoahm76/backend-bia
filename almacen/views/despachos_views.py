from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date
import copy
from almacen.serializers.despachos_serializers import (
    CerrarSolicitudDebidoInexistenciaSerializer,
    SerializersDespachoConsumo,
    SerializersItemDespachoConsumo,
    SerializersSolicitudesConsumibles,
    SerializersItemsSolicitudConsumible
)
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles, 
    DespachoConsumo, 
    ItemDespachoConsumo, 
    SolicitudesConsumibles, 
    ItemsSolicitudConsumible
)
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
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer

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


class CerrarSolicitudDebidoInexistenciaView(generics.RetrieveUpdateAPIView):
    serializer_class = CerrarSolicitudDebidoInexistenciaSerializer
    queryset = SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data
        
        #VALIDACIÓN SI EXISTE LA SOLICITUD ENVIADA
        solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=id_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No se encontró ninguna solicitud con los parámetros enviados'}, status=status.HTTP_404_NOT_FOUND)
        
        if solicitud.fecha_cierre_no_dispo_alm:
            return Response({'success': False, 'detail': 'No se cerrar una solicitud que ya está cerrada'}, status=status.HTTP_403_FORBIDDEN)
        #SUSTITUIR INFORMACIÓN A LA DATA
        data['fecha_cierre_no_dispo_alm'] = datetime.now()
        data['id_persona_cierre_no_dispo_alm'] = request.user.persona.id_persona
        data['solicitud_abierta'] = False
        data['fecha_cierre_solicitud'] = datetime.now()
        data['gestionada_almacen'] = True

        serializer = self.serializer_class(solicitud, data=data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save
        
        #Auditoria Cerrar Solicitud
        usuario = request.user.id_usuario
        descripcion = {"Codigo bien": str(), "Numero elemento bien": str()}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 18,
            "cod_permiso": "BO",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': False, 'detail': 'Se cerró la solicitud correctamente'}, status=status.HTTP_201_CREATED)
        
