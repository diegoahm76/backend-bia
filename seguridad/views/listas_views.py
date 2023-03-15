from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.serializers.listas_serializers import (
    MunicipiosSerializer,
    DepartamentosSerializer
)
from seguridad.models import Municipio, Departamento
from rest_framework.permissions import IsAuthenticated

class GetListMunicipios(generics.ListAPIView):
    serializer_class = MunicipiosSerializer
    queryset = Municipio.objects.all()
    
    def get(self,request):
        cod_departamento = request.query_params.get('cod_departamento')
        cod_departamento = cod_departamento if cod_departamento else ''
        
        municipios = self.queryset.all().filter(cod_departamento__icontains=cod_departamento)
        serializador = self.serializer_class(municipios,many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes municipios', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class GetListDepartamentos(generics.ListAPIView):
    serializer_class = DepartamentosSerializer
    queryset = Departamento.objects.all()
    
    def get(self,request):
        pais = request.query_params.get('pais')
        pais = pais if pais else ''
        
        departamentos = self.queryset.all().filter(pais__icontains=pais)
        serializador = self.serializer_class(departamentos,many=True)
        
        return Response ({'success':True, 'detail':'Se encontraron los siguientes departamentos', 'data':serializador.data}, status=status.HTTP_200_OK)