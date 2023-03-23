from rest_framework import generics, status
from rest_framework.response import Response
from seguridad.serializers.listas_serializers import (
    MunicipiosSerializer,
    DepartamentosSerializer,
    PaisSerializer
)
from rest_framework.views import APIView
from seguridad.models import Municipio, Departamento, Paises
from rest_framework.permissions import IsAuthenticated

# IMPORT LISTS
from seguridad.lists.tipo_persona_list import tipo_persona_LIST
from seguridad.lists.tipo_documento_list import tipo_documento_LIST
from seguridad.lists.tipo_usuario_list import tipo_usuario_LIST
from seguridad.lists.clase_tercero_list import clase_tercero_LIST
from seguridad.lists.cod_permiso_list import cod_permiso_LIST
from seguridad.lists.estado_civil_list import estado_civil_LIST  
from seguridad.lists.opciones_usuario_list import opciones_usuario_LIST
from seguridad.lists.sexo_list import sexo_LIST 
from seguridad.lists.subsistemas_list import subsistemas_LIST
from seguridad.lists.tipo_direccion_list import tipo_direccion_LIST
from seguridad.lists.direcciones_list import direcciones_LIST 
from seguridad.lists.indicativo_paises_list import indicativo_paises_LIST

class GetListMunicipios(generics.ListAPIView):
    serializer_class = MunicipiosSerializer
    queryset = Municipio.objects.all()

    def get(self, request):
        cod_departamento = request.query_params.get('cod_departamento', '')

        municipios = self.queryset.all().filter(
            cod_departamento__icontains=cod_departamento)
        serializador = self.serializer_class(municipios, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes municipios', 'data': serializador.data}, status=status.HTTP_200_OK)


class GetListDepartamentos(generics.ListAPIView):
    serializer_class = DepartamentosSerializer
    queryset = Departamento.objects.all()

    def get(self, request):
        pais = request.query_params.get('pais', '')

        departamentos = self.queryset.all().filter(pais__icontains=pais)
        serializador = self.serializer_class(departamentos, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes departamentos', 'data': serializador.data}, status=status.HTTP_200_OK)


class GetListPaises(generics.ListAPIView):
    serializer_class = PaisSerializer
    queryset = Paises.objects.all()

    def get(self, request):

        pais = self.queryset.all()
        serializador = self.serializer_class(pais, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes paises', 'data': serializador.data}, status=status.HTTP_200_OK)


class GetListTipoDocumento(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de documento son los siguientes', 'data': tipo_documento_LIST}, status=status.HTTP_200_OK)


class GetListTipoPersona(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de persona son los siguientes', 'data': tipo_persona_LIST}, status=status.HTTP_200_OK)
    
class GetListTipoUsuario(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de usuarios son los siguientes', 'data': tipo_usuario_LIST}, status=status.HTTP_200_OK)

class GetLisClaseTercero(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de clase tercero son los siguientes', 'data': clase_tercero_LIST}, status=status.HTTP_200_OK)
    
class GetLisCodPermiso(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de codigo permiso son los siguientes', 'data': cod_permiso_LIST}, status=status.HTTP_200_OK)
    
class GetLisEstadoCivil(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de estado civil son los siguientes', 'data': estado_civil_LIST}, status=status.HTTP_200_OK) 

class GetLisOpcUsuario(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de opciones de usuario son los siguientes', 'data': opciones_usuario_LIST}, status=status.HTTP_200_OK) 

class GetLisSexo(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de sexo son los siguientes', 'data': sexo_LIST}, status=status.HTTP_200_OK) 

class GetLisSubsistema(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de subsistema son los siguientes', 'data': subsistemas_LIST}, status=status.HTTP_200_OK)
    
class GetLisTipoDireccion(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los tipos de direccion son las siguientes', 'data': tipo_direccion_LIST}, status=status.HTTP_200_OK)

class GetLisDirecciones(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Las direeciones son las siguientes', 'data': direcciones_LIST}, status=status.HTTP_200_OK) 
        
class GetLisIndicativoPais(APIView):
    def get(self, request):
        return Response({'success': True, 'detail': 'Los indicativos por pais son los siguientes', 'data': indicativo_paises_LIST}, status=status.HTTP_200_OK)