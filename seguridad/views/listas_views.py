from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.serializers.listas_serializers import (
    MunicipiosSerializer,
    DepartamentosSerializer
)
from rest_framework.views import APIView
from seguridad.models import Municipio, Departamento
from rest_framework.permissions import IsAuthenticated

# IMPORT LISTS
from seguridad.lists.tipo_persona_list import tipo_persona_LIST

class GetListMunicipios(generics.ListAPIView):
    serializer_class = MunicipiosSerializer
    queryset = Municipio.objects.all()
    
    def get(self,request):
        cod_departamento = request.query_params.get('cod_departamento', '')
        
        municipios = self.queryset.all().filter(cod_departamento__icontains=cod_departamento)
        serializador = self.serializer_class(municipios,many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes municipios', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class GetListDepartamentos(generics.ListAPIView):
    serializer_class = DepartamentosSerializer
    queryset = Departamento.objects.all()
    
    def get(self,request):
        pais = request.query_params.get('pais', '')
        
        departamentos = self.queryset.all().filter(pais__icontains=pais)
        serializador = self.serializer_class(departamentos,many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes departamentos', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class GetListTipoPersona(APIView):
    def get(self,request):
        return Response({'success':True, 'detail':'Los tipos de persona son los siguientes', 'data':tipo_persona_LIST}, status=status.HTTP_200_OK)