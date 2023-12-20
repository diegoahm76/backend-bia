
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.trd_models import FormatosTiposMedio, TipologiasDoc
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, AccesoUndsOrg_PlantillaDocGetSerializer, OtrasTipologiasSerializerGetSerializer, PlantillasDocBusquedaAvanzadaDetalleSerializer, PlantillasDocBusquedaAvanzadaSerializer, PlantillasDocCreateSerializer, PlantillasDocGetSeriallizer, PlantillasDocSerializer, PlantillasDocUpdateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
import json
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
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
        data_in['id_persona_crea_plantilla'] = usuario
        #CONFIGURACION TEMPORAL PARA HACER PRUEBAS
        if 'ruta_temporal' in data_in and data_in['ruta_temporal']:

            ruta_temporal = data_in['ruta_temporal']
        else:
            ruta_temporal = ''
        elementos = ruta_temporal.split(",")
        ruta = os.path.join(*elementos)
       
        #FIN PRUEBAS
        #ruta = os.path.join("home", "BIA", "Otros", "Plantillas")
       
        #print(ruta)
    
        #raise ValidationError(ruta)
        #archivo = request.FILES['archivo']
        if not 'archivo' in data_in:
            raise ValidationError("No se ha proporcionado ningún archivo.")
        archivo = request.data.get('archivo')
        data_archivo={
            'es_Doc_elec_archivo':False,
            'ruta':ruta
        }
                
        if not archivo:
            raise ValidationError("No se ha proporcionado ningún archivo.")

        #Validacion para tipos de archivo:
        nombre=archivo.name
            
        nombre_sin_extension, extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        if not extension_sin_punto:
            raise ValidationError("No fue posible registrar el archivo")
        
        formatos=FormatosTiposMedio.objects.filter(nombre=extension_sin_punto,activo=True).first()
        data_in['id_formato_tipo_medio']=formatos.id_formato_tipo_medio
        if not formatos:
            raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")
       
        que_tal=ArchivosDgitalesCreate()
        respuesta=que_tal.crear_archivo(data_archivo,archivo)

 
        if respuesta.status_code!=status.HTTP_201_CREATED:
            return respuesta   

        data_archivo_digital= respuesta.data['data']      
        di_archivo=data_archivo_digital['id_archivo_digital']
        data_in['id_archivo_digital'] =  di_archivo              
        
        
        if data_in['asociada_a_tipologia_doc_trd']=='True':
                if 'id_tipologia_doc_trd' in data_in:
                    if not data_in['id_tipologia_doc_trd']:
                        raise ValidationError("Se requiere asociar una tipologia")
                else:
                    raise ValidationError("Se requiere asociar una tipologia.")
                
        else:
            if 'otras_tipologias' in data_in:
                if not data_in['otras_tipologias']:
                    raise ValidationError('Debe asociar otra tiplogia tipologia.')

            else: 
              
                raise ValidationError('Debe asociar otra tiplogia tipologia.')
            
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



            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':{**serializer.data,"acceso_unidades":data_acceso,'archivo_digital':data_archivo_digital}},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
        

class PlantillasDocDelete(generics.DestroyAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocCreateSerializer
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        intance_accesos_plantilla=AccesoUndsOrg_PlantillaDoc.objects.filter(id_plantilla_doc=instance.id_plantilla_doc)
        if intance_accesos_plantilla:
            intance_accesos_plantilla.delete()
        
        if instance.id_archivo_digital:
            instance_archivo=ArchivosDigitales.objects.filter(id_archivo_digital=instance.id_archivo_digital.id_archivo_digital)
            if instance_archivo:
                instance_archivo.delete()

        instance.delete()


        return Response({
            "success": True,
            "detail": "Se eliminó el registro correctamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
class TipologiasDocGetActivo(generics.ListAPIView):
    serializer_class = TipologiasDocSerializerGetSerializer
    queryset =TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
        }, status=status.HTTP_200_OK)
    def delete(self, request,pk):
        response=self.eliminar(pk)
        return response
    

class PlantillasDocUpdateUpdate(generics.UpdateAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocUpdateSerializer
    permission_classes = [IsAuthenticated]

    def comparar_arreglos(self,base,json):
                arregloBase = base
                    
                arregloJson = json
                # Convertimos los arreglos en conjuntos
                set_arregloBase = set(arregloBase)
                set_arregloJson = set(arregloJson)

                # Obtenemos los elementos en arregloBase pero no en arregloJson
                elementos_en_arregloBase_no_en_arregloJson = set_arregloBase.difference(set_arregloJson)

                # Obtenemos los elementos en arregloJson pero no en arregloBase
                elementos_en_arregloJson_no_en_arregloBase = set_arregloJson.difference(set_arregloBase)

                # Convertimos los resultados de nuevo a listas para mostrarlos
                elementos_en_arregloBase_no_en_arregloJson = list(elementos_en_arregloBase_no_en_arregloJson)
                elementos_en_arregloJson_no_en_arregloBase = list(elementos_en_arregloJson_no_en_arregloBase)

                print("Elementos en arregloBase pero no en arregloJson:", elementos_en_arregloBase_no_en_arregloJson)
                print("Elementos en arregloJson pero no en arregloBase:", elementos_en_arregloJson_no_en_arregloBase)
                return elementos_en_arregloJson_no_en_arregloBase,elementos_en_arregloBase_no_en_arregloJson
    
    def put(self, request, *args, **kwargs):

        data_in=request.data
        instance = self.get_object()
        data_eliminada=[]
        data_acceso_nueva=[]
        data_archivo_digital={}
        if not instance:
            raise NotFound("No existe un dato  asociada a esta id")
        try:

            #Actualizar archivo
            if 'archivo' in data_in:
                ruta = os.path.join("home", "BIA", "Otros", "Plantillas")
            
                print(ruta)
            
                if not 'archivo' in data_in:
                    raise ValidationError("No se ha proporcionado ningún archivo.")
                archivo = request.data.get('archivo')
                data_archivo={
                    'es_Doc_elec_archivo':False,
                    'ruta':ruta
                }
                nombre=archivo.name
                nombre_sin_extension, extension = os.path.splitext(nombre)
                extension_sin_punto = extension[1:] if extension.startswith('.') else extension
                if not extension_sin_punto:
                    raise ValidationError("No fue posible registrar el archivo")
                
                formatos=FormatosTiposMedio.objects.filter(nombre=extension_sin_punto,activo=True)

                if not formatos:
                    raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")
            
                que_tal=ArchivosDgitalesCreate()
                respuesta=que_tal.crear_archivo(data_archivo,archivo)

        
                if respuesta.status_code!=status.HTTP_201_CREATED:
                    return respuesta   

                data_archivo_digital= respuesta.data['data']      
                di_archivo=data_archivo_digital['id_archivo_digital']
                data_in['id_archivo_digital'] =  di_archivo     

                instance.id_archivo_digital.delete()

            serializer = self.get_serializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()




            
            id_planilla=instance.id_plantilla_doc
            if 'acceso_unidades' in data_in and data_in['acceso_unidades']:
                crear_acceso=AccesoUndsOrg_PlantillaDocCreate()
                data_json = request.data.get('acceso_unidades')
                data_dict={}
                try:
                
                    data_dict = json.loads(data_json)
                except json.JSONDecodeError:
                    return Response({'error': 'El campo "data_json" debe ser un JSON válido.'}, status=status.HTTP_400_BAD_REQUEST)
      

                unidades_acceso_query=AccesoUndsOrg_PlantillaDoc.objects.filter(id_plantilla_doc=instance.id_plantilla_doc).values_list('id_unidad_organizacional', flat=True)
                unidades_acceso=[]
                unidades_acceso_json=[]
                for acceso in unidades_acceso_query:
                    unidades_acceso.append(acceso)
                    #unidades_acceso.append(acceso.id_unidad_organizacional)
                print(unidades_acceso)

                for acceso in data_dict:
                    unidades_acceso_json.append(acceso['id_unidad_organizacional'])
                print(unidades_acceso_json)

 
                elementos_crear,elementos_eliminar=self.comparar_arreglos(unidades_acceso,unidades_acceso_json)
                ##
                #Crea los que no estan en base de datos
                for acceso in elementos_crear:
                    
                    response=crear_acceso.crear_acceso({'id_unidad_organizacional':acceso,"id_plantilla_doc":id_planilla})
                    if response.status_code!=status.HTTP_201_CREATED:
                            return response   
                    data_acceso_nueva.append(response.data['data'])
                
                eliminar_acceso=AccesoUndsOrg_PlantillaDocDelete()
                unidades_acceso_query_delete=AccesoUndsOrg_PlantillaDoc.objects.filter(id_unidad_organizacional__in=elementos_eliminar)
                for dato in unidades_acceso_query_delete:
                    
                        respuesta=eliminar_acceso.eliminar(dato.id_acceso_und_org_plantilla_doc)
            
                        if respuesta.status_code!=status.HTTP_200_OK:
                                return respuesta   
                        data_eliminada.append(respuesta.data['data'])
   
                
            response_data=serializer.data
            response_data['eliminar_acceso']=data_eliminada
            response_data['data_acceso_nueva']=data_acceso_nueva
            response_data['data_archivo_digital']=data_archivo_digital
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
        usuario = request.user.persona

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
                
        filter['activa']=True


        
       
        if 'RT' in request.query_params.getlist('disponibilidad'):
            unidad_organizacional=usuario.id_unidad_organizacional_actual
            if not unidad_organizacional:
                raise NotFound("No se encuentra vinculado a ninguna unidad organizacional.")
            
            plantilla_ids = AccesoUndsOrg_PlantillaDoc.objects.filter(id_unidad_organizacional=unidad_organizacional.id_unidad_organizacional).values_list('id_plantilla_doc', flat=True)
            #print(plantilla_ids)
            filter['id_plantilla_doc__in'] = plantilla_ids
        else:
            filter['cod_tipo_acceso__icontains']='TC'
        plantilla = self.queryset.all().filter(**filter)


        serializador = self.serializer_class(plantilla,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        
class BusquedaAvanzadaPlantillasAdmin(generics.ListAPIView):
    #serializer_class = PlantillasDocBusquedaAvanzadaDetalleSerializer
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
                
        
        #activas=PlantillasDoc.objects.filter(activa=True)
        plantilla = self.queryset.all().filter(**filter)
        ids_de_plantillas = list(plantilla.values_list('id_archivo_digital', flat=True))
        #print(ids_de_plantillas)
        
        archivos_digitales=ArchivosDigitales.objects.filter(id_archivo_digital__in=ids_de_plantillas)
        # for a in archivos_digitales:
        #     print (a)
        #raise ValidationError(ids_de_plantillas)

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
        


class OtrasTipologiasDocGetActivo(generics.ListAPIView):
    serializer_class = OtrasTipologiasSerializerGetSerializer
    queryset =PlantillasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        #instance = PlantillasDoc.objects.filter(activo=True)
        instance = PlantillasDoc.objects.filter(activa=True).values('otras_tipologias').distinct()
        # for x in instance:
        #     print(x)
    
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
