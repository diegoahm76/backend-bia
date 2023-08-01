from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from transversal.models. base_models import (
    Municipio,
    Departamento,
    Paises,
    EstadoCivil,
    TipoDocumento
)
from transversal.lists.listas_serializers import (
    MunicipiosSerializer,
    DepartamentosSerializer
)

# IMPORT LISTS
from transversal.lists.direcciones_list import direcciones_LIST
from transversal.lists.indicativo_paises_list import indicativo_paises_LIST
from transversal.lists.sexo_list import sexo_LIST 

class GetListDepartamentos(generics.ListAPIView):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentosSerializer

    def get(self, request):
        pais = request.query_params.get('pais', '')
        departamentos = self.queryset.all().filter(pais__cod_pais__icontains=pais).exclude(cod_departamento='50')
        meta = self.queryset.filter(cod_departamento='50').values(label=F('nombre'),value=F('cod_departamento')).first()
        
        serializer = self.serializer_class(departamentos, many=True)
        
        data = serializer.data
        if data and (pais=='CO' or pais==''):
            data.insert(0, meta)
        
        return Response({'success':True, 'detail':'Se encontraron los siguientes departamentos', 'data': data}, status=status.HTTP_200_OK)

class GetListMunicipios(generics.ListAPIView):
    queryset = Municipio.objects.all()
    serializer_class = MunicipiosSerializer

    def get(self, request):
        cod_departamento = request.query_params.get('cod_departamento', '')

        municipios = self.queryset.all().filter(cod_departamento__cod_departamento__icontains=cod_departamento).exclude(cod_municipio='50001')
        villavicencio = self.queryset.filter(cod_municipio='50001').values(label=F('nombre'),value=F('cod_municipio')).first()

        serializer = self.serializer_class(municipios, many=True)
        
        data = serializer.data
        if data and (cod_departamento=='50' or cod_departamento==''):
            data.insert(0, villavicencio)
        
        return Response({'success':True, 'detail':'Se encontraron los siguientes municipios', 'data':data}, status=status.HTTP_200_OK)
    
class GetListPaises(generics.ListAPIView):
    queryset = Paises.objects.all()

    def get(self, request):
        paises = self.queryset.exclude(cod_pais='CO').values(value=F('cod_pais'), label=F('nombre'))
        colombia = self.queryset.filter(cod_pais='CO').values(value=F('cod_pais'), label=F('nombre')).first()
        
        paises = list(paises)
        paises.insert(0, colombia)
        
        return Response({'success':True, 'detail':'Los paises son los siguientes', 'data': paises}, status=status.HTTP_200_OK)

class GetLisDirecciones(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Las direeciones son las siguientes', 'data': direcciones_LIST}, status=status.HTTP_200_OK)

        
class GetLisIndicativoPais(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los indicativos por pais son los siguientes', 'data': indicativo_paises_LIST}, status=status.HTTP_200_OK)
    

class GetLisSexo(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de sexo son los siguientes', 'data': sexo_LIST}, status=status.HTTP_200_OK)
    

class GetLisEstadoCivil(generics.ListAPIView):
    queryset = EstadoCivil.objects.all()
    
    def get(self, request):
        estados_civil = self.queryset.filter(activo=True).values(value=F('cod_estado_civil'), label=F('nombre'))
        return Response({'success':True, 'detail':'Los tipos de estado civil son los siguientes', 'data': estados_civil}, status=status.HTTP_200_OK)

class GetListTipoDocumento(generics.ListAPIView):
    queryset = TipoDocumento.objects.all()
    
    def get(self, request):
        tipos_documento = self.queryset.filter(activo=True).values(value=F('cod_tipo_documento'), label=F('nombre'))
        return Response({'success':True, 'detail':'Los tipos de documento son los siguientes', 'data': tipos_documento}, status=status.HTTP_200_OK)
