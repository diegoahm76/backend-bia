from conservacion.utils import UtilConservacion
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

from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from conservacion.serializers.solicitudes_serializers import (
    GetNumeroConsecutivoSolicitudSerializer,
    GetSolicitudByNumeroSolicitudSerializer,
    GetUnidadOrganizacionalSerializer,
    CreateSolicitudViverosSerializer
)
from conservacion.models.viveros_models import (
    Vivero
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from seguridad.serializers.personas_serializers import (
    PersonasSerializer
)
from seguridad.models import (
    Personas,
    User
)

class GetNumeroConsecutivoSolicitudView(generics.RetrieveAPIView):
    serializer_class = GetNumeroConsecutivoSolicitudSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        solicitud_vivero = SolicitudesViveros.objects.all().order_by('-nro_solicitud').first()
        numero_inicial = 0
        if solicitud_vivero:
            numero_inicial = solicitud_vivero.nro_solicitud
        numero_consecutivo = numero_inicial + 1

        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': numero_consecutivo}, status=status.HTTP_200_OK)


class GetSolicitudByNumeroSolicitudView(generics.RetrieveAPIView):
    serializer_class = GetSolicitudByNumeroSolicitudSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, nro_solicitud):
        solicitud = SolicitudesViveros.objects.filter(nro_solicitud=nro_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No existe ninguna solicitud con el numero ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(solicitud, many=False)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetUnidadOrganizacionalView(generics.RetrieveAPIView):
    serializer_class = GetUnidadOrganizacionalSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        persona_logeada = request.user.persona
        linea_jerarquica = UtilConservacion.get_linea_jerarquica(persona_logeada)
        serializer = self.serializer_class(linea_jerarquica, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetFuncionarioResponsableView(generics.GenericAPIView):
    serializer_class = PersonasSerializer
    
    def get(self, request, id_unidad_organizacional, tipodocumento, numerodocumento):
        persona_logeada = request.user.persona

        #VALIDACIÓN SI EXISTE LA PERSONA ENVIADA
        user = User.objects.filter(persona__tipo_documento=tipodocumento, persona__numero_documento=numerodocumento).first()
        if not user:
            return Response({'success': False, 'detail': 'No existe o no tiene usuario creado el funcionario responsable seleccionado'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EL USUARIO SEA INTERNO
        if user.tipo_usuario != 'I':
            return Response({'success': False, 'detail': 'El funcionario responsable debe ser un usuario interno'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI ESA PERSONA ESTÁ ASOCIADA A UNA UNIDAD ORGANIZACIONAL
        if not user.persona.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona seleccionada no se encuentra relacionada con ninguna unidad organizacional'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI LA PERSONA SE ENCUENTRA EN UNA UNIDAD DE UN ORGANIGRAMA ACTUAL
        if user.persona.id_unidad_organizacional_actual.id_organigrama.actual != True:
            return Response({'success': False, 'detail': 'El responsable seleccionado no pertenece a un organigrama actual'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE LINEA JERARQUICA SUPERIOR O IGUAL
        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
        print(linea_jerarquica)

        lista_unidades_permitidas = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        print(lista_unidades_permitidas)

        if user.persona.id_unidad_organizacional_actual.id_unidad_organizacional not in lista_unidades_permitidas:
            return Response({'success': False, 'detail': 'No se puede seleccionar una persona que no esté al mismo nivel o superior en la linea jerarquica'}, status=status.HTTP_403_FORBIDDEN)

        persona_serializer = self.serializer_class(user.persona, many=False)
        return Response({'success': True,'data': persona_serializer.data}, status=status.HTTP_200_OK)

class CreateSolicitudViverosView(generics.CreateAPIView):
    serializer_class = CreateSolicitudViverosSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        persona_logeada = request.user.persona

        #ASIGNACIÓN DE INFORMACIÓN EN JSON Y EN VARIABLES CORRESPONDIENTES
        data_solicitud = json.loads(request.data['data_solicitud'])
        data_items_solicitud = json.loads(request.data['data_items_solicitados'])
        data_solicitud['ruta_archivo_info_tecnico'] = request.FILES.get('ruta_archivo_tecnico')
        data_solicitud['id_persona_solicita'] = persona_logeada.id_persona
        data_solicitud['id_unidad_org_del_solicitante'] = persona_logeada.id_unidad_organizacional_actual.id_unidad_organizacional
        data_solicitud['fecha_solicitud'] = datetime.now()

        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD ESTÉ ASOCIADA A UNA UNIDAD Y QUE SEA ACTUAL
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'succcess': False, 'detail': 'La persona que hace la solicitud debe pertenecer a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        if persona_logeada.id_unidad_organizacional_actual.id_organigrama.actual != True:
            return Response({'succcess': False, 'detail': 'La unidad organizacional de la persona que hace la solicitud debe pertenecer a un organigrama actual'}, status=status.HTTP_400_BAD_REQUEST)
        
        #ASIGNACIÓN NÚMERO CONSECUTIVO
        ultima_solicitud = SolicitudesViveros.objects.all().order_by('-nro_solicitud').first()
        auxiliar = 0
        if ultima_solicitud:
            auxiliar = ultima_solicitud.nro_solicitud
        consecutivo = auxiliar + 1
        data_solicitud['nro_solicitud'] = consecutivo

        #VALIDACIÓN QUE EL VIVERO SELECCIONADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=data_solicitud['id_vivero_solicitud']).first()
        if not vivero:
            return Response({'success': False, 'detail': 'El vivero seleccionado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        if vivero.fecha_cierre_actual != None:
            return Response({'success': False, 'detail': 'El vivero seleccionado no puede estar cerrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE LA UNIDAD PARA LA QUE SOLICITA ESTÉ DENTRO DE LA LINEA JERARQUICA DE LA PERSONA LOGEADA
        linea_jerarquica = UtilConservacion.get_linea_jerarquica(persona_logeada)
        linea_jerarquica_id = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        if data_solicitud['id_unidad_para_la_que_solicita'] not in linea_jerarquica_id:
            return Response({'success': False, 'detail': 'La unidad seleccionada debe hacer parte de su linea jerarquica'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN PARA QUE LA UNIDAD DEL RESPONSABLE SEA DE MISMA O SUPERIOR NIVEL EN LA LINEA JERARQUICA
        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
        linea_jerarquica_id = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        if data_solicitud['id_unidad_org_del_responsable'] not in linea_jerarquica_id:
            return Response({'success': False, 'detail': 'La unidad del responsable debe hacer parte de su linea jerarquica superior o igual'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data_solicitud, many=False)
        serializer.is_valid(raise_exception=True)
        solicitud_maestro = serializer.save()

        for item in data_items_solicitud:
            item['id_solicitud_viveros'] = solicitud_maestro.id_solicitud_vivero

        # AUDITORIA SOLICITUDES A VIVEROS
        valores_creados_detalles = []
        for bien in data_items_solicitud:
            valores_creados_detalles.append({'':''})

        descripcion = {"nombre_bien_sembrado": str(solicitud_maestro.nro_solicitud)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 60,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Creación de solicitud exitosa', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    


