from conservacion.utils import UtilConservacion
from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
import copy
import json
import operator
import operator, itertools

from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.serializers.solicitudes_funcionario_coordinador_serializer import (
    GetSolicitudesViverosFuncionarioSerializer,
    GestionarSolicitudResponsableSerializer,
    GetSolicitudesViveroResponsableSerializer,
    GestionarSolicitudCoordinadorSerializer
)
from conservacion.serializers.solicitudes_serializers import (
    GetSolicitudesViverosSerializer,
    ListarSolicitudIDSerializer,
)
from conservacion.models.viveros_models import (
    Vivero
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales,
)
from seguridad.serializers.personas_serializers import (
    PersonasSerializer
)
from seguridad.models import (
    Personas,
    User
)

class ListSolicitudesFuncionarioView(generics.ListAPIView):
    serializer_class = GetSolicitudesViverosFuncionarioSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_logeado = request.user.persona.id_persona
        fecha_actual = datetime.now().date()

        solicitudes = self.queryset.filter(id_funcionario_responsable_und_destino=usuario_logeado, fecha_retiro_material__gt=fecha_actual, revisada_responsable=False)
        serializer = self.serializer_class(solicitudes, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ListSolicitudesVencidasFuncionarioView(generics.ListAPIView):
    serializer_class = GetSolicitudesViverosFuncionarioSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_logeado = request.user.persona.id_persona
        fecha_actual = datetime.now().date()

        solicitudes = self.queryset.filter(id_funcionario_responsable_und_destino=usuario_logeado, fecha_retiro_material__lt=fecha_actual, revisada_responsable=False)
        serializer = self.serializer_class(solicitudes, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class DetailSolicitudView(generics.GenericAPIView):
    serializer_class = GetSolicitudesViverosSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_solicitud):
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            raise NotFound ('No existe la solicitud seleccionada')
        items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=solicitud.id_solicitud_vivero)
        
        serializer = self.serializer_class(solicitud)
        data = serializer.data

        serializador = ListarSolicitudIDSerializer(items_solicitud, many=True)
        data['data_items'] = serializador.data
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data_maestro': data}, status=status.HTTP_200_OK)
    
class GestionarSolicitudSupervisorView(generics.RetrieveUpdateAPIView):
    serializer_class = GestionarSolicitudResponsableSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data

        #VALIDAR SI LA SOLICITUD ENVIADA EXISTE
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            raise NotFound ('No existe la solicitud seleccionada')

        solicitud_copy = copy.copy(solicitud)

        #VALIDAR QUE LA SOLICITUD NO HAYA SIDO GESTIONADA ANTES
        if solicitud.revisada_responsable != False:
            raise ValidationError('Esta solicitud ya fue gestionada por el supervisor, no es posible gestionarla nuevamente')

        #ASIGNACIÓN DE DATA SEGÚN CASOS
        if data['estado_aprobacion_responsable'] == 'A':
            data['fecha_aprobacion_responsable'] = datetime.now()
            data['revisada_responsable'] = True
            data['solicitud_abierta'] = True
            data['fecha_cierra_solicitud'] = None

            #GUARDADO DE LA INFORMACIÓN Y SERIALIZACIÓN
            serializer = self.serializer_class(solicitud, data=data)
            serializer.is_valid(raise_exception=True)
            serializador_instance = serializer.save()

            serializador = GetSolicitudesViverosSerializer(solicitud, many=False)
            
        else:
            data['fecha_aprobacion_responsable'] = datetime.now()
            data['revisada_responsable'] = True
            data['solicitud_abierta'] = False
            data['fecha_cierra_solicitud'] = datetime.now()

            #GUARDADO DE LA INFORMACIÓN Y SERIALIZACIÓN
            serializer = self.serializer_class(solicitud, data=data)
            serializer.is_valid(raise_exception=True)
            serializador_instance = serializer.save()

            serializador = GetSolicitudesViverosSerializer(solicitud, many=False)
        
        # AUDITORIA ACTUALIZAR SOLICITUD
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"numero_solicitud": str(solicitud.nro_solicitud)}
        valores_actualizados = {'current': serializador_instance, 'previous': solicitud_copy}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 60,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Solicitud gestionada exitosamente', 'data': serializador.data}, status=status.HTTP_201_CREATED)


class GestionarSolicitudesVencidasSupervisorView(generics.RetrieveUpdateAPIView):
    serializer_class = GestionarSolicitudResponsableSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data
        
        if data['estado_aprobacion_responsable'] != 'R':
            raise NotFound('El estado de aprobación no puede ser diferente a rechazada para una solicitud vencida')

        #VALIDAR SI LA SOLICITUD ENVIADA EXISTE
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            raise NotFound('No existe la solicitud seleccionada')

        solicitud_copy = copy.copy(solicitud)

        #VALIDAR QUE LA SOLICITUD NO HAYA SIDO GESTIONADA ANTES
        if solicitud.revisada_responsable != False:
            raise ValidationError('Esta solicitud ya fue gestionada por el supervisor, no es posible gestionarla nuevamente')
        
        data['fecha_aprobacion_responsable'] = datetime.now()
        data['revisada_responsable'] = True
        data['solicitud_abierta'] = False
        data['fecha_cierra_solicitud'] = datetime.now()

        #GUARDADO DE LA INFORMACIÓN Y SERIALIZACIÓN
        serializer = self.serializer_class(solicitud, data=data)
        serializer.is_valid(raise_exception=True)
        serializador_instance = serializer.save()

        # AUDITORIA ACTUALIZAR SOLICITUD
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"numero_solicitud": str(solicitud.nro_solicitud)}
        valores_actualizados = {'current': serializador_instance, 'previous': solicitud_copy}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 60,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        serializador = GetSolicitudesViverosSerializer(solicitud, many=False)
        return Response({'success': True, 'detail': 'Solicitud gestionada exitosamente', 'data': serializador.data}, status=status.HTTP_201_CREATED)


#----------------------------FUNCIONALIDADES PARA MODULO DE COORDINADOR------------------------


class ListSolicitudesCoordinadorView(generics.ListAPIView):
    serializer_class = GetSolicitudesViveroResponsableSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_logeado = request.user.persona.id_persona

        solicitudes = self.queryset.filter(id_persona_coord_viveros=usuario_logeado, revisada_responsable=True, estado_aprobacion_responsable='A')
        serializer = self.serializer_class(solicitudes, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GestionarSolicitudCoordinadorView(generics.RetrieveUpdateAPIView):
    serializer_class = GestionarSolicitudCoordinadorSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data

        #VALIDAR SI LA SOLICITUD ENVIADA EXISTE
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            raise NotFound('No existe la solicitud seleccionada')

        solicitud_copy = copy.copy(solicitud)

        #VALIDAR QUE LA SOLICITUD NO HAYA SIDO GESTIONADA ANTES
        if solicitud.revisada_coord_viveros != False:
            raise ValidationError('Esta solicitud ya fue gestionada por el supervisor, no es posible gestionarla nuevamente')

        #ASIGNACIÓN DE DATA SEGÚN CASOS
        if data['estado_aprobacion_coord_viveros'] == 'A':
            data['fecha_aprobacion_coord_viv'] = datetime.now()
            data['revisada_coord_viveros'] = True
            data['solicitud_abierta'] = True
            data['fecha_cierra_solicitud'] = None

            #GUARDADO DE LA INFORMACIÓN Y SERIALIZACIÓN
            serializer = self.serializer_class(solicitud, data=data)
            serializer.is_valid(raise_exception=True)
            serializador_instance = serializer.save()

            serializador = GetSolicitudesViverosSerializer(solicitud, many=False)
            
        else:
            data['fecha_aprobacion_coord_viv'] = datetime.now()
            data['revisada_coord_viveros'] = True
            data['solicitud_abierta'] = False
            data['fecha_cierra_solicitud'] = datetime.now()

            #GUARDADO DE LA INFORMACIÓN Y SERIALIZACIÓN
            serializer = self.serializer_class(solicitud, data=data)
            serializer.is_valid(raise_exception=True)
            serializador_instance = serializer.save()

            serializador = GetSolicitudesViverosSerializer(solicitud, many=False)
        
        # AUDITORIA ACTUALIZAR SOLICITUD
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"numero_solicitud": str(solicitud.nro_solicitud)}
        valores_actualizados = {'current': serializador_instance, 'previous': solicitud_copy}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 60,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Solicitud gestionada exitosamente', 'data': serializador.data}, status=status.HTTP_201_CREATED)
