from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from almacen.models import UnidadesOrganizacionales, NivelesOrganigrama
from seguridad.models import Personas, User
from rest_framework.decorators import api_view

class SearchVisibleBySolicitud(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien']:
                filter[key+'__icontains']=value
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['visible_solicitudes']= True
        bien=CatalogoBienes.objects.filter(**filter)
        serializador=self.serializer_class(bien,many=True)
        if bien:
            return Response({'success':True,'detail':'se encontró elementos','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'no se econtrò elementos','data':bien},status=status.HTTP_404_NOT_FOUND)


def id_responsable(request):
    data = request.data
    id_responsable = data['id_responsable']
    try:
        responsable = Personas.objects.get(id_persona=id_responsable)   
    except:
        return Response({'Success':False,'detail':'no existe ninguna persona correspondiente al id del funcionario responsable de la unidad'})
    try:
        unidad_org_responsable = UnidadesOrganizacionales.objects.get(id_unidad_org=responsable.id_unidad_org)
    except:
        return Response({'Success':False, 'Detail':'la persona responsable no tiene esta unidad organizacional asignada'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        solicitante = Personas.objects.get(id_persona=data['id_PersonaSolicita'])   
    except:
        return Response({'Success':False,'detail':'no existe ninguna persona correspondiente al id del funcionario solicitante de la unidad'})
    try:
        unidad_org_solicitante = UnidadesOrganizacionales.objects.get(id_unidad_org=solicitante.id_unidad_org)
    except:
        return Response({'Success':False, 'Detail':'la persona solicitante no tiene esta unidad organizacional asignada'},status=status.HTTP_400_BAD_REQUEST)
    if unidad_org_responsable.id_nivel_organigrama < unidad_org_solicitante.id_nivel_organigrama:
        pass
        lista_de_jerarquia = []
        nivel =unidad_org_solicitante
        for i in range(unidad_org_responsable.orden_nivel,unidad_org_solicitante.orden_nivel):

            nivel = UnidadesOrganizacionales.objects.get(id_unidad_org_padre=nivel.id_unidad_org_padre)
          

    else:
        return Response({'Success':False,'Detail':'el nivel de organigrama del responsable es mayor o igual el solicitante'})


@api_view(['GET'])
def get_orgchart_tree(request,pk):
    
    persona = Personas.objects.get(id_persona=int(pk))
    
    try:
        user = User.objects.get(persona=pk)
    except:
        return Response({'Success':False,'Detail':'no existe usuario asignado a esta persona'}, status=status.HTTP_400_BAD_REQUEST)
    if user.tipo_usuario != 'I':
        return Response({'Success':False,'Detail':'su tipo de usuario no corresponde con el esperado para esta consulta'},status=status.HTTP_400_BAD_REQUEST)
    try:
        unidad_organizacional = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=persona.id_unidad_organizacional_actual)
    except:
        return Response({'Success':False,'Detail':'la persona no tiene ninguna unidad organizacional asignada'})
    
    nivel = NivelesOrganigrama.objects.get(id_nivel_organigrama=unidad_organizacional.id_nivel_organigrama).orden_nivel


    