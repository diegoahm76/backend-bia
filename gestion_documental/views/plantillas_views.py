
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, AccesoUndsOrg_PlantillaDocGetSerializer, PlantillasDocBusquedaAvanzadaSerializer, PlantillasDocCreateSerializer, PlantillasDocGetSeriallizer, PlantillasDocSerializer, PlantillasDocUpdateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
import json
from transversal.models.organigrama_models import UnidadesOrganizacionales
class PlantillasDocCreate(generics.CreateAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocCreateSerializer
    permission_classes = [IsAuthenticated]
    def obtener_extension_archivo(self,archivo):
        _, extension = os.path.splitext(archivo.name)
        return extension

    def post(self,request):
        
        usuario = request.user.persona.id_persona
        data_acceso=[]
        data_in = request.data.copy()
        data_in['id_persona_crea_plantilla']=usuario

        archivo = request.FILES.get('archivo')
        nombre_archivo = request.data.get('nombre_archivo')
                
        if not archivo:
            raise ValidationError("No se ha proporcionado ningún archivo.")

        if not nombre_archivo:
            raise ValidationError("El archivo debe tener un nombre.")
        #FUNCION GENERADORA DE RUTAS DE ARCHIVOS
        
    
       
        try:
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            id_planilla=instance.id_plantilla_doc
            if 'acceso_unidades' in data_in and data_in['acceso_unidades']:
                crear_acceso=AccesoUndsOrg_PlantillaDocCreate()
                data_json = request.data.get('acceso_unidades')
                data_dict={}
                try:
                
                    data_dict = json.loads(data_json)
                except json.JSONDecodeError:
                    return Response({'error': 'El campo "data_json" debe ser un JSON válido.'}, status=status.HTTP_400_BAD_REQUEST)
                #print(data_dict)
                for acceso in data_dict:
                    response=crear_acceso.crear_acceso({**acceso,"id_plantilla_doc":id_planilla})
                    if response.status_code!=status.HTTP_201_CREATED:
                            return response   
                    data_acceso.append(response.data['data'])



            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':{**serializer.data,"acceso_unidades":data_acceso}},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
        

class PlantillasDocDelete(generics.DestroyAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocCreateSerializer
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "detail": "Se eliminó el registro correctamente",
            "data": serializer.data
        }, status=status.HTTP_204_NO_CONTENT)
class TipologiasDocGetActivo(generics.ListAPIView):
    serializer_class = TipologiasDocSerializerGetSerializer
    queryset =TipologiasDoc.objects.all()

    def get (self, request):
        instance = TipologiasDoc.objects.filter(activo=True)

        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    

class AccesoUndsOrg_PlantillaDocCreate(generics.CreateAPIView):
    serializer_class = AccesoUndsOrg_PlantillaDocCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = AccesoUndsOrg_PlantillaDoc.objects.all()
    
    def crear_acceso(self,data):
        try:
           

            data_in=data
            if 'id_und_organizacional' in data_in:
                unidad= UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_und_organizacional']).first()
                if not unidad:
                    raise NotFound("No existe unidad asociada a esta id.")
            if 'id_plantilla_doc' in data_in:
                plantilla= PlantillasDoc.objects.filter(id_plantilla_doc=data_in['id_plantilla_doc'])
                if not plantilla:
                    raise NotFound("No existe plantilla asociada a esta id.")
            serializer = AccesoUndsOrg_PlantillaDocCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_acceso(data_in)
        return response
    

class AccesoUndsOrg_PlantillaDocGetByPlantilla(generics.ListAPIView):
    serializer_class = AccesoUndsOrg_PlantillaDocGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = AccesoUndsOrg_PlantillaDoc.objects.all()
    def get (self, request,pk):


        instance=AccesoUndsOrg_PlantillaDoc.objects.filter(id_plantilla_doc=pk)

        if not instance:
            raise NotFound("No existen registros asociados.")
        
        serializador=self.serializer_class(instance, many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    


class AccesoUndsOrg_PlantillaDocDelete(generics.DestroyAPIView):
    queryset = AccesoUndsOrg_PlantillaDoc.objects.all()
    serializer_class = AccesoUndsOrg_PlantillaDocCreateSerializer

    def eliminar(self,pk):
        instance = AccesoUndsOrg_PlantillaDoc.objects.filter(id_acceso_und_org_plantilla_doc=pk).first()
        if not instance:
            raise NotFound("No existe relacion asociada a esta id.")
        serializer =AccesoUndsOrg_PlantillaDocCreateSerializer(instance)
        instance.delete()
        return Response({
            "success": True,
            "detail": "Se eliminó la pregunta correctamente",
            "data": serializer.data
        }, status=status.HTTP_204_NO_CONTENT)
    def delete(self, request,pk):
        response=self.eliminar(pk)
        return response
    

class PlantillasDocUpdateUpdate(generics.UpdateAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocUpdateSerializer


    def put(self, request, *args, **kwargs):

        data_in=request.data
        instance = self.get_object()
        data_eliminada=[]
        if not instance:
            raise NotFound("No existe un dato  asociada a esta id")
        try:

            serializer = self.get_serializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            if 'eliminar_acceso' in data_in and data_in['eliminar_acceso']:
                data_json = request.data.get('eliminar_acceso')
                data_dict={}
                try:
                
                    data_dict = json.loads(data_json)
                except json.JSONDecodeError:
                    return Response({'error': 'El campo "data_json" debe ser un JSON válido.'}, status=status.HTTP_400_BAD_REQUEST)
                print(data_dict)
                

                eliminar_acceso=AccesoUndsOrg_PlantillaDocDelete()
                for dato in data_dict:
                    if 'id_acceso_und_org_plantilla_doc' in dato and  dato['id_acceso_und_org_plantilla_doc']:
                        respuesta=eliminar_acceso.eliminar(dato['id_acceso_und_org_plantilla_doc'])
            
                        if respuesta.status_code!=status.HTTP_204_NO_CONTENT:
                                return respuesta   
                        data_eliminada.append(respuesta.data['data'])
   
            response_data=serializer.data
            response_data['eliminar_acceso']=data_eliminada
            #response_data['preguntas']=data_response_pregunta
            return Response({
                "success": True,
                "detail": "Se actualizó correctamente",
                "data": response_data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:       
            raise ValidationError(e.detail)
        


class BusquedaAvanzadaPlantillas(generics.ListAPIView):
    serializer_class = PlantillasDocBusquedaAvanzadaSerializer
    queryset = PlantillasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        
        for key, value in request.query_params.items():

            if key == 'nombre':
                if value !='':
                    filter['nombre__icontains'] = value
            if key =='descripcion':
                if value != '':
                    filter['descripcion__icontains'] = value    
            if key =='tipologia':
                if value != '':
                    filter['id_tipologia_doc_trd__nombre__icontains'] = value
            if key =='disponibilidad':
                if value != '':
                    filter['cod_tipo_acceso__icontains'] = value

                    
            if key =='extension':
                if value != '':
                    filter['id_archivo_digital__formato__icontains'] = value                 
                
        plantilla = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(plantilla,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        

class PlantillasDocGetById(generics.ListAPIView):
    serializer_class = PlantillasDocGetSeriallizer
    queryset = PlantillasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
                
        plantilla = self.queryset.all().filter(id_plantilla_doc=pk)

        if not plantilla:
            raise NotFound("No existe registro.")
        serializador = self.serializer_class(plantilla,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        

class PlantillasDocGetDetalleById(generics.ListAPIView):
    
    serializer_class = PlantillasDocSerializer
    queryset = PlantillasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
                
        plantilla = self.queryset.all().filter(id_plantilla_doc=pk).first()

        if not plantilla:
            raise NotFound("No existe registro.")
        
        accesos=AccesoUndsOrg_PlantillaDoc.objects.filter(id_plantilla_doc=pk)
        
        
        data_acceso = AccesoUndsOrg_PlantillaDocGetSerializer(accesos, many=True)
        serializador = self.serializer_class(plantilla).data
        
        serializador['acceso_unidades']=data_acceso.data
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador},status=status.HTTP_200_OK)
        