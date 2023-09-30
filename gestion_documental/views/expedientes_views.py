from datetime import datetime
import hashlib
import os
import secrets
from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from gestion_documental.models.trd_models import TablaRetencionDocumental, TipologiasDoc
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguridad.utils import Util
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import  AgregarArchivoSoporteCreateSerializer, ArchivosDigitalesSerializer, ExpedienteGetOrdenSerializer, ExpedienteSearchSerializer, ExpedientesDocumentalesGetSerializer, ListarTRDSerializer, ListarTipologiasSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


########################## CRUD DE CIERRE DE EXPEDIENTES DOCUMENTALES ##########################

#BUSCAR UN EXPEDIENTE
class ExpedienteSearch(generics.ListAPIView):
    serializer_class = ExpedienteSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        titulo_expediente = self.request.query_params.get('titulo_expediente', '').strip()
        codigo_exp_und_serie_subserie = self.request.query_params.get('codigo_exp_und_serie_subserie', '').strip()
        fecha_apertura_expediente = self.request.query_params.get('fecha_apertura_expediente', '').strip()
        nombre_serie_origen = self.request.query_params.get('id_serie_origen', '').strip()
        nombre_subserie_origen = self.request.query_params.get('id_subserie_origen', '').strip()
        palabras_clave_expediente = self.request.query_params.get('palabras_clave_expediente', '').strip()
        codigos_uni_serie_subserie = self.request.query_params.get('codigos_uni_serie_subserie', '').strip()
        trd_nombre = self.request.query_params.get('trd_nombre', '').strip()



        # Filtrar por atributos específicos referentes a un expediente (unión de parámetros)
        queryset = ExpedientesDocumentales.objects.filter(estado='A')  # Filtrar por estado 'A'
        if titulo_expediente:
            queryset = queryset.filter(titulo_expediente__icontains=titulo_expediente)

        if codigo_exp_und_serie_subserie:
            queryset = queryset.filter(codigo_exp_und_serie_subserie=codigo_exp_und_serie_subserie)

        if fecha_apertura_expediente:
            queryset = queryset.filter(fecha_apertura_expediente__icontains=fecha_apertura_expediente)

        if nombre_serie_origen:
            queryset = queryset.filter(id_serie_origen__nombre__icontains=nombre_serie_origen)

        if nombre_subserie_origen:
            queryset = queryset.filter(id_subserie_origen__nombre__icontains=nombre_subserie_origen)
   
        if codigos_uni_serie_subserie:
            queryset = queryset.filter(codigo_exp_und_serie_subserie__startswith=codigos_uni_serie_subserie)

        if trd_nombre:
            queries = []
            
            if trd_nombre.lower() == 'actual':
                queries.append(queryset.filter(id_trd_origen__nombre__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__fecha_retiro_produccion__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__actual=True))
            elif trd_nombre.lower() == 'no actual':
                queries.append(queryset.filter(id_trd_origen__nombre__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__fecha_retiro_produccion__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__actual=False))
            else:
                queries.append(queryset.filter(id_trd_origen__nombre__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__fecha_retiro_produccion__icontains=trd_nombre))
                queries.append(queryset.filter(id_trd_origen__actual__icontains=trd_nombre))
            
            # Combinamos todas las consultas utilizando comas
            queryset = queries[0]
            for query in queries[1:]:
                queryset = queryset | query
            
            
        if palabras_clave_expediente:
            search_vector = SearchVector('palabras_clave_expediente')
            search_query = SearchQuery(palabras_clave_expediente)
            queryset = queryset.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gt=0)

        return queryset

        # queryset = queryset.order_by('orden_ubicacion_por_entidad')  # Ordenar de forma ascendente

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpedienteSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)



#LISTAR_DATOS_TRD
class TrdDateGet(generics.ListAPIView):
    serializer_class = ListarTRDSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de expedientes documentales registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes resultados',
            'data': serializer.data
        })

#LISTAR_EXPEDIENTES    
class ListaExpedientesDocumentales(generics.ListAPIView):
    queryset = ExpedientesDocumentales.objects.all()
    serializer_class = ExpedientesDocumentalesGetSerializer    
    permission_classes = [IsAuthenticated]

        
########################## CRUD DE ARCHIVO DE SOPORTE ##########################
class AgregarArchivoSoporte(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Procesa los datos del archivo adjunto
        uploaded_file = request.data.get('file')

        if not uploaded_file:
            return Response({'success': False,'detail': 'No se ha proporcionado ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtiene el año actual para determinar la carpeta de destino
            current_year = datetime.now().year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in uploaded_file.chunks():
                md5_hash.update(chunk)

            # Obtiene el valor hash MD5
            md5_value = md5_hash.hexdigest()

            # Crea el archivo digital y obtiene su ID
            data_archivo = {
                'es_Doc_elec_archivo': False,
                'ruta': ruta,
                'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
            }

            que_tal = ArchivosDgitalesCreate()
            respuesta = que_tal.crear_archivo(data_archivo, uploaded_file)

            if respuesta.status_code != status.HTTP_201_CREATED:
                return respuesta

            archivo_digital_id = respuesta.data.get('id_archivo_digital')

            # Procesa los datos para agregar un documento de archivo expediente
            data_in = request.data

            persona_logueada = request.user.persona
            data_in['id_persona_que_crea'] = persona_logueada.id_persona

            if not persona_logueada.id_unidad_organizacional_actual:
                raise ValidationError("No tiene permiso para realizar esta acción")

            data_in['id_und_org_oficina_creadora'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
            data_in['id_und_org_oficina_respon_actual'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
            data_in['sub_sistema_incorporacion'] = 'GEST'

            # Determina el último orden en la base de datos y suma 1
            last_order = DocumentosDeArchivoExpediente.objects.order_by('-orden_en_expediente').first()
            if last_order is not None:
                data_in['orden_en_expediente'] = last_order.orden_en_expediente + 1
            else:
                data_in['orden_en_expediente'] = 1

            # Asegúrate de que 'id_expediente_documental' sea una instancia válida de ExpedientesDocumentales
            id_expediente_documental_id = data_in.get('id_expediente_documental')
            if id_expediente_documental_id:
                try:
                    id_expediente_documental = ExpedientesDocumentales.objects.get(pk=id_expediente_documental_id)
                except ExpedientesDocumentales.DoesNotExist:
                    raise ValidationError("El expediente documental especificado no existe.")
                
                # Ahora puedes acceder a los atributos de 'id_expediente_documental'
                if id_expediente_documental.cod_tipo_expediente == 'S':
                    # Para Expedientes Simples (T236codTipoExpediente = S)
                    data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}S{data_in['orden_en_expediente']:010d}"
                elif id_expediente_documental.cod_tipo_expediente == 'C':
                    # Para Expedientes Complejos (T236codTipoExpediente = C)
                    data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}C{id_expediente_documental.codigo_exp_consec_por_agno:<04d}{data_in['orden_en_expediente']:06d}"
                
            serializer = AgregarArchivoSoporteCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            
            # Establece la fecha de incorporación como la fecha actual
            serializer.validated_data['fecha_incorporacion_doc_a_Exp'] = datetime.now()
            
            # Asigna el ID del archivo digital al campo 'id_archivo_sistema'
            serializer.validated_data['id_archivo_sistema'] = archivo_digital_id
            
            # Guarda el archivo de soporte
            archivo_soporte = serializer.save()
            
            # Retornar el hash MD5 y el archivo de soporte
            response_data = {
                "mensaje": "Archivo subido exitosamente",
                "md5_hash": md5_value,
                "archivo_soporte": serializer.data,
                "archivo_digital": respuesta.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
# class AgregarArchivoSoporte(generics.CreateAPIView):
#     serializer_class = AgregarArchivoSoporteCreateSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = DocumentosDeArchivoExpediente.objects.all()
    
#     def post(self, request, format=None):
#         data_in = request.data

#         persona_logueada = request.user.persona
#         data_in['id_persona_que_crea'] = persona_logueada.id_persona

#         if not persona_logueada.id_unidad_organizacional_actual:
#             raise ValidationError("No tiene permiso para realizar esta acción")

        
#         data_in['id_und_org_oficina_creadora'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
#         data_in['id_und_org_oficina_respon_actual'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
#         data_in['sub_sistema_incorporacion'] = 'GEST'

#         # Determina el último orden en la base de datos y suma 1
#         last_order = DocumentosDeArchivoExpediente.objects.order_by('-orden_en_expediente').first()
#         if last_order is not None:
#             data_in['orden_en_expediente'] = last_order.orden_en_expediente + 1
#         else:
#             data_in['orden_en_expediente'] = 1

#         # Asegúrate de que 'id_expediente_documental' sea una instancia válida de ExpedientesDocumentales
#         id_expediente_documental_id = data_in.get('id_expediente_documental')
#         if id_expediente_documental_id:
#             try:
#                 id_expediente_documental = ExpedientesDocumentales.objects.get(pk=id_expediente_documental_id)
#             except ExpedientesDocumentales.DoesNotExist:
#                 raise ValidationError("El expediente documental especificado no existe.")
            
#             # Ahora puedes acceder a los atributos de 'id_expediente_documental'
#             if id_expediente_documental.cod_tipo_expediente == 'S':
#                 # Para Expedientes Simples (T236codTipoExpediente = S)
#                 data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}S{data_in['orden_en_expediente']:010d}"
#             elif id_expediente_documental.cod_tipo_expediente == 'C':
#                 # Para Expedientes Complejos (T236codTipoExpediente = C)
#                 # data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}C{id_expediente_documental.codigo_exp_consec_por_agno:04d}{data_in['orden_en_expedient]e']:06d}"
#                 data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}C{id_expediente_documental.codigo_exp_consec_por_agno:<04d}{data_in['orden_en_expediente']:06d}"
               
#         serializer = self.serializer_class(data=data_in)
#         serializer.is_valid(raise_exception=True)
        
#         # Establece la fecha de incorporación como la fecha actual
#         serializer.validated_data['fecha_incorporacion_doc_a_Exp'] = datetime.now()
        
#         expediente = serializer.save()

      

#         return Response({'success': True, 'detail': 'Se crearon los registros correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)


    
#ORDEN_EXPEDIENTE_SIGUIENTE
class ExpedienteGetOrden(generics.ListAPIView):
    serializer_class = ExpedienteGetOrdenSerializer
    queryset = DocumentosDeArchivoExpediente.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = DocumentosDeArchivoExpediente.objects.aggregate(max_orden=Max('orden_en_expediente'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_en_expediente': orden_siguiente}, status=status.HTTP_200_OK)
    
#ORDEN_EXPEDIENTE_ACTUAL
class ExpedienteGetOrdenActual(generics.ListAPIView):
    serializer_class = ExpedienteGetOrdenSerializer
    queryset = DocumentosDeArchivoExpediente.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = DocumentosDeArchivoExpediente.objects.aggregate(max_orden=Max('orden_en_expediente'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden']
        
        return Response({'success': True, 'orden_actual': orden_siguiente}, status=status.HTTP_200_OK)
    

#LISTAR_TIPOLOGIAS
class ListarTipologias(generics.ListAPIView):
    serializer_class = ListarTipologiasSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de tipologias registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes tipologias',
            'data': serializer.data
        })
    
########################## CRUD DE ARCHIVOS DIGITALES  ##########################




# class UploadPDFView(generics.CreateAPIView):
#     queryset = ArchivosDigitales.objects.all()
#     serializer_class = ArchivosDigitalesSerializer
#     permission_classes = [IsAuthenticated]
#     #parser_classes = (FileUploadParser,)
#     def create(self, request, *args, **kwargs):
#         uploaded_file = request.data.get('file')

#         #archivo=request.data.get('archivo')
#         if uploaded_file:
#              # Obtiene el año actual para determinar la carpeta de destino
#             current_year = datetime.now().year
            
#             ruta = os.path.join("home", "BIA", "Otros", "GDEA",str(current_year))
#             ruta="home,BIA,Otros,GDEA,"+str(current_year)
#             data_archivo={
#             'es_Doc_elec_archivo':False,
#             'ruta':ruta
#             }
#             que_tal=ArchivosDgitalesCreate()
#             respuesta=que_tal.crear_archivo(data_archivo,uploaded_file)

#             if respuesta.status_code!=status.HTTP_201_CREATED:
#                 return respuesta  
#             return respuesta
#         else:
#                 return Response({"error": "No se ha proporcionado ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)
        

class UploadPDFView(generics.CreateAPIView):
    queryset = ArchivosDigitales.objects.all()
    serializer_class = ArchivosDigitalesSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        uploaded_file = request.data.get('file')

        if not uploaded_file:
            return Response({"error": "No se ha proporcionado ningún archivo"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtiene el año actual para determinar la carpeta de destino
            current_year = datetime.now().year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in uploaded_file.chunks():
                md5_hash.update(chunk)

            # Obtiene el valor hash MD5
            md5_value = md5_hash.hexdigest()

            # A continuación, puedes utilizar md5_value según tus necesidades
            # Por ejemplo, puedes agregarlo al diccionario data_archivo
            data_archivo = {
                'es_Doc_elec_archivo': False,
                'ruta': ruta,
                'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
            }

            que_tal = ArchivosDgitalesCreate()
            respuesta = que_tal.crear_archivo(data_archivo, uploaded_file)

            if respuesta.status_code != status.HTTP_201_CREATED:
                return respuesta

            # Retornar el hash MD5 junto con "respuesta"
            response_data = {
                "mensaje": "Archivo subido exitosamente",
                "md5_hash": md5_value,
                "respuesta": respuesta.data  # Agregamos la respuesta de "que_tal"
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






        
        
class ListarArchivosDigitales(generics.ListAPIView):
    queryset = ArchivosDigitales.objects.all()
    serializer_class = ArchivosDigitalesSerializer    
    permission_classes = [IsAuthenticated]
