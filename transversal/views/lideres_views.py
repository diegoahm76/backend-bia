import copy
from django.db.models import Max
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from seguridad.models import Personas
from seguridad.serializers.personas_serializers import PersonasFilterSerializer
from seguridad.utils import Util
from transversal.models.organigrama_models import Organigramas
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.serializers.lideres_serializers import BusquedaAvanzadaOrganigramasSerializer, GetListLideresAsignadosSerializer

class BusquedaAvanzadaOrganigramasView(generics.ListAPIView):
    serializer_class = BusquedaAvanzadaOrganigramasSerializer
    queryset = Organigramas.objects.exclude(fecha_terminado=None)
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
            if key == 'actual':
                if value != '':
                    if value in ['true','false']:
                        filter[key] = True if value == 'true' else False
        
        organigramas = self.queryset.filter(**filter)
        serializer = self.serializer_class(organigramas, many=True)
        
        return Response({'success':True,'detail':"Se encontraron los siguientes organigramas",'data':serializer.data}, status=status.HTTP_200_OK)
            
class GetListLideresAsignadosView(generics.ListAPIView):
    serializer_class = GetListLideresAsignadosSerializer
    queryset = LideresUnidadesOrg.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_organigrama):
        organigramas = self.queryset.filter(id_unidad_organizacional__id_organigrama=id_organigrama)
        serializer = self.serializer_class(organigramas, many=True)
        
        return Response({'success':True,'detail':"Se encontraron los siguientes lideres asignados",'data':serializer.data}, status=status.HTTP_200_OK)

class BuscarLideresAsignadosFilterView(generics.ListAPIView):
    serializer_class = GetListLideresAsignadosSerializer
    queryset = LideresUnidadesOrg.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre_organigrama','version_organigrama','codigo_unidad_org','nombre_unidad_org','tipo_documento','numero_documento','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido']:
                if key in ['nombre_organigrama', 'version_organigrama']:
                    if value != '':
                        key = key.split('_')
                        filter['id_unidad_organizacional__id_organigrama__' + key[0] + '__icontains']=value
                elif key in ['codigo_unidad_org', 'nombre_unidad_org']:
                    if value != '':
                        key = key.split('_')
                        filter['id_unidad_organizacional__' + key[0] + '__icontains']=value
                elif key in ['tipo_documento','numero_documento','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido']:
                    if value != '':
                        filter['id_persona__' + key + '__icontains']=value
                else:
                    if value != '':
                        filter[key+'__icontains']=value
        
        lideres = self.queryset.filter(**filter)
        serializer = self.serializer_class(lideres, many=True)
        
        return Response({'success':True,'detail':"Se encontraron los siguientes lideres asignados",'data':serializer.data}, status=status.HTTP_200_OK)

class GetPersonaLiderByNumeroDocumento(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self,request):
        filter = {}
        numero_documento = request.query_params.get('numero_documento')
        tipo_documento = request.query_params.get('tipo_documento')
        
        if not numero_documento or not tipo_documento:
            raise PermissionDenied('Debe de seleccionar el tipo de documento y digitar el número de documento')

        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento']:
                filter[key]=value
        
        current_date = datetime.now()
        persona = Personas.objects.filter(**filter, es_unidad_organizacional_actual=True, fecha_a_finalizar_cargo_actual__gt=current_date).exclude(id_cargo=None, id_unidad_organizacional_actual=None).first()

        if persona: 
            serializador = self.serializer_class(persona)
            return Response({'success':True,'detail':'Se encontró la persona','data':serializador.data}, status=status.HTTP_200_OK) 
        else:
            raise NotFound('No existe la persona, o no se encuentra actualmente vinculada')

class GetPersonaLiderFiltro(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido', 'id_unidad_organizacional_actual']:
                if key in ['tipo_documento', 'id_unidad_organizacional_actual']:
                    if value != '':
                        filter[key]=value
                else:
                    if value != '':
                        filter[key+'__icontains']=value
                
        current_date = datetime.now()
        personas = Personas.objects.filter(**filter, es_unidad_organizacional_actual=True, fecha_a_finalizar_cargo_actual__gt=current_date).exclude(id_cargo=None, id_unidad_organizacional_actual=None)

        serializador = self.serializer_class(personas, many=True)
        
        return Response ({'success':True,'detail':'Se encontraron las siguientes personas','data':serializador.data}, status=status.HTTP_200_OK)