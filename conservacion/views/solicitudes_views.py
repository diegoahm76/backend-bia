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
    UnidadesOrganizacionales
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
        nombre = request.query_params['nombre']
        unidades = self.queryset.all().filter(id_organigrama__actual=True).filter(nombre__icontains=nombre)
        serializer = self.serializer_class(unidades, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetFuncionarioResponsableView(generics.GenericAPIView):
    serializer_class = PersonasSerializer
    
    def get(self, request, tipodocumento, numerodocumento):
        persona_logeada = request.user.persona

        #VALIDACIÓN SI EXISTE LA PERSONA ENVIADA
        user = User.objects.filter(persona__tipo_documento=tipodocumento, persona__numero_documento=numerodocumento).first()
        if not user:
            return Response({'success': False, 'detail': 'No existe el funcionario responsable seleccionado o no tiene usuario creado'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EL USUARIO SEA INTERNO
        if user.tipo_usuario != 'I':
            return Response({'success': False, 'detail': 'El funcionario responsable debe ser un usuario interno'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI ESA PERSONA ESTÁ ASOCIADA A UNA UNIDAD ORGANIZACIONAL
        if not user.persona.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona seleccionada no se encuentra relacionada con ninguna unidad organizacional'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI LA PERSONA SE ENCUENTRA EN UNA UNIDAD DE UN ORGANIGRAMA ACTUAL
        if user.persona.id_unidad_organizacional_actual.id_organigrama.actual != True:
            return Response({'success': False, 'detail': 'El responsable seleccionado no pertenece a un organigrama actual'}, status=status.HTTP_400_BAD_REQUEST)

        #ITERACCIÓN PARA CONOCER LAS UNIDADES PADRE
        unidad = persona_logeada.id_unidad_organizacional_actual
        lista_padres = []
        padre_existe = False

        while padre_existe == False:
            if unidad.id_unidad_org_padre:
                unidad_padre = unidad.id_unidad_org_padre
                lista_padres.append(unidad_padre.id_unidad_organizacional)
                unidad = unidad_padre
            else:
                padre_existe = True

        #VALIDACIÓN DE MISMA LINEA JERARQUICA
        lista_unidades_permitidas = []
        lista_unidades_permitidas.extend(lista_padres)
        lista_unidades_permitidas.append(persona_logeada.id_unidad_organizacional_actual.id_unidad_organizacional)

        if user.persona.id_unidad_organizacional_actual.id_unidad_organizacional not in lista_unidades_permitidas:
            return Response({'success': False, 'detail': 'No se puede seleccionar una persona que no sea de la misma linea jerarquica igual o ascendente'}, status=status.HTTP_403_FORBIDDEN)

        persona_serializer = self.serializer_class(user.persona, many=False)
        return Response({'success': True,'data': persona_serializer.data}, status=status.HTTP_200_OK)

class CreateSolicitudViverosView(generics.CreateAPIView):
    serializer_class = CreateSolicitudViverosSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass