from datetime import datetime
import hashlib
import os
from django.db.utils import IntegrityError
from django.core.files.base import ContentFile
import secrets
from rest_framework.parsers import MultiPartParser
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.depositos_models import CarpetaCaja
from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.serializers.conf__tipos_exp_serializers import ConfiguracionTipoExpedienteAgnoGetSerializer
from gestion_documental.serializers.trd_serializers import BusquedaTRDNombreVersionSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from seguridad.utils import Util
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import  AgregarArchivoSoporteCreateSerializer, AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer, ArchivoSoporteSerializer, ArchivosDigitalesCreateSerializer, ArchivosDigitalesSerializer, ArchivosSoporteCierreReaperturaSerializer, ArchivosSoporteGetAllSerializer, CierreExpedienteDetailSerializer, CierreExpedienteSerializer, ConfiguracionTipoExpedienteAperturaGetSerializer, ExpedienteGetOrdenSerializer, ExpedienteSearchSerializer, ExpedientesDocumentalesGetSerializer, ListarTRDSerializer, ListarTipologiasSerializer, SerieSubserieUnidadTRDGetSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

########################## CRUD DE APERTURA DE EXPEDIENTES DOCUMENTALES ##########################

#OBTENER_TRD_ACTUAL
class TrdActualGet(generics.ListAPIView):
    serializer_class = BusquedaTRDNombreVersionSerializer
    queryset = TablaRetencionDocumental.objects.filter(actual=True)
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
        trd_actual = self.queryset.all().first()
        
        if trd_actual:
            serializador = self.serializer_class(trd_actual)
            
            return Response({'success':True,'detail':'Busqueda exitosa','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'Busqueda exitosa, no existe TRD actual'},status=status.HTTP_200_OK)

#OBTENER TRIPLETAS TRD
class SerieSubserieUnidadTRDGetView(generics.ListAPIView):
    serializer_class = SerieSubserieUnidadTRDGetSerializer 
    queryset = CatSeriesUnidadOrgCCDTRD.objects.filter()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        id_trd = request.query_params.get('id_trd', '')
        id_unidad_organizacional = request.query_params.get('id_unidad_organizacional', '')
        
        if id_trd == '' or id_unidad_organizacional == '':
            raise ValidationError('Debe enviar el TRD y la Unidad Organizacional seleccionada')
        
        catalogos_serie_unidad_trd = self.queryset.filter(id_trd=id_trd, id_cat_serie_und__id_unidad_organizacional=id_unidad_organizacional)
        serializador = self.serializer_class(catalogos_serie_unidad_trd, many=True)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)


#OBTENER CONFIGURACION EXPEDIENTE
class ConfiguracionExpedienteGet(generics.ListAPIView):
    serializer_class = ConfiguracionTipoExpedienteAperturaGetSerializer
    queryset = ConfiguracionTipoExpedienteAgno.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self, request, id_catserie_unidadorg):
        current_year = datetime.now().year
        config_expediente = self.queryset.filter(id_cat_serie_undorg_ccd=id_catserie_unidadorg, agno_expediente=current_year).first()
        
        if not config_expediente:
            raise NotFound('La Serie-Subserie-Unidad seleccionada no cuenta con una configuración, debe elegir otra')
        
        serializer = self.serializer_class(config_expediente)
        
        return Response({'success':True, 'detail':'Consulta exitosa', 'data':serializer.data},status=status.HTTP_200_OK)

class AperturaExpedienteCreate(generics.CreateAPIView):
    serializer_class = AperturaExpedienteSimpleSerializer
    serializer_class_complejo = AperturaExpedienteComplejoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data
        
        # Crear codigo expediente
        tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=data['id_cat_serie_und_org_ccd_trd_prop']).first()
        
        if not tripleta_trd:
            raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
        
        cod_unidad = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.codigo
        cod_serie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        cod_subserie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        
        current_date = datetime.now()
        instances_carpetas = None
        
        if data.get('carpetas_caja'):
            instances_carpetas = CarpetaCaja.objects.filter(id_carpeta_caja__in=set(data.get('carpetas_caja')))
            instances_expediente_asociado = instances_carpetas.exclude(id_expediente=None)
            
            if len(set(data.get('carpetas_caja'))) != len(instances_carpetas):
                raise ValidationError('Debe enviar carpetas existentes en el sistema')
            
            if instances_expediente_asociado:
                raise ValidationError('Alguna(s) de las carpetas seleccionadas ya poseen expedientes asociados. Debe seleccionar carpetas sin expedientes')
        
        data['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie
        data['codigo_exp_Agno'] = current_date.year
        
        # VALIDAR DESPUÉS
        data['codigo_exp_consec_por_agno'] = None if data['cod_tipo_expediente'] == 'C' else None # TEMPORAL
            
        data['estado'] = 'A'
        data['fecha_folio_inicial'] = current_date
        data['cod_etapa_de_archivo_actual_exped'] = 'G'
        data['tiene_carpeta_fisica'] = True if data.get('carpetas_caja') else False
        data['ubicacion_fisica_esta_actualizada'] = True
        data['fecha_creacion_manual'] = current_date
        data['id_persona_crea_manual'] = request.user.persona.id_persona
        
        if data['cod_tipo_expediente'] == 'S':
            serializer = self.serializer_class(data=data, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        elif data['cod_tipo_expediente'] == 'C':
            serializer = self.serializer_class_complejo(data=data, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        
        if data.get('carpetas_caja'):
            for carpeta in data.get('carpetas_caja'):
                instance_carpeta = instances_carpetas.filter(id_carpeta_caja=carpeta).first()
                instance_carpeta.id_expediente = expediente_creado
                instance_carpeta.save()
                
        return Response({'success':True, 'detail':'Apertura realizada de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        

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
            raise NotFound('No se encontraron datos que coincidan con los criterios de búsqueda.')

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
            raise NotFound('No se encontraron datos que coincidan con los criterios de búsqueda.')

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

    @transaction.atomic
    def post(self, request, format=None):
        # Procesa los datos del archivo adjunto
        uploaded_file = request.data.get('file')

        if not uploaded_file:
            return Response({'success': False, 'detail': 'No se ha proporcionado ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

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

            archivo_digital_id = respuesta.data.get('data').get('id_archivo_digital')

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

            # Establece la fecha de incorporación como la fecha actual
            data_in['fecha_incorporacion_doc_a_Exp'] = datetime.now()

            # Asigna el ID del archivo digital al campo 'id_archivo_sistema'
            data_in['id_archivo_sistema'] = archivo_digital_id

            # Guardar el archivo de soporte
            serializer = AgregarArchivoSoporteCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            archivo_soporte = serializer.save()

            # Actualiza 'nombre_original_del_archivo' con el nombre del documento antes de cifrarlo
            archivo_soporte.nombre_original_del_archivo = uploaded_file.name
            archivo_soporte.save()

            # Obtener el índice electrónico del expediente que se está cerrando (debe reemplazar '1' con el ID correcto)
            indice_electronico = IndicesElectronicosExp.objects.get(pk=1)  # Reemplaza 1 con el ID correcto

            # Obtener el número de folios ingresado en el formulario
            nro_folios_del_doc = data_in.get('nro_folios_del_doc')

            # Calcular la página de inicio
            last_index_doc = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico).order_by('-pagina_fin').first()
            if last_index_doc:
                pagina_inicio = last_index_doc.pagina_fin + 1
            else:
                pagina_inicio = 1

            # Calcular la página final
            pagina_inicio = int(pagina_inicio)
            nro_folios_del_doc = int(nro_folios_del_doc)
            pagina_fin = pagina_inicio + nro_folios_del_doc - 1

            # Crear un registro en T240Docs_IndiceElectronicoExp
            Docs_IndiceElectronicoExp.objects.create(
                id_indice_electronico_exp=indice_electronico,
                id_doc_archivo_exp=archivo_soporte,
                identificación_doc_exped=archivo_soporte.identificacion_doc_en_expediente,
                nombre_documento=archivo_soporte.nombre_asignado_documento,
                id_tipologia_documental=archivo_soporte.id_tipologia_documental,
                fecha_creacion_doc=archivo_soporte.fecha_creacion_doc,
                fecha_incorporacion_exp=archivo_soporte.fecha_incorporacion_doc_a_Exp,
                valor_huella=md5_value,
                funcion_resumen="MD5",
                orden_doc_expediente=archivo_soporte.orden_en_expediente,
                pagina_inicio=pagina_inicio,
                pagina_fin=pagina_fin,
                formato=archivo_soporte.id_archivo_sistema.formato,
                tamagno_kb=archivo_soporte.id_archivo_sistema.tamagno_kb,
                cod_origen_archivo=archivo_soporte.cod_origen_archivo,
                es_un_archivo_anexo=archivo_soporte.es_un_archivo_anexo,
            )

            # Retornar el hash MD5 y el archivo de soporte
            response_data = {
                'success': True,
                "mensaje": "Archivo subido exitosamente",
                "md5_hash": md5_value,
                "archivo_soporte": serializer.data,
                "archivo_digital": respuesta.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise ValidationError(str(e))
# class AgregarArchivoSoporte(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, format=None):
#         # Procesa los datos del archivo adjunto
#         uploaded_file = request.data.get('file')

#         if not uploaded_file:
#             return Response({'success': False,'detail': 'No se ha proporcionado ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Obtiene el año actual para determinar la carpeta de destino
#             current_year = datetime.now().year
#             ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

#             # Calcula el hash MD5 del archivo
#             md5_hash = hashlib.md5()
#             for chunk in uploaded_file.chunks():
#                 md5_hash.update(chunk)

#             # Obtiene el valor hash MD5
#             md5_value = md5_hash.hexdigest()

#             # Crea el archivo digital y obtiene su ID
#             data_archivo = {
#                 'es_Doc_elec_archivo': False,
#                 'ruta': ruta,
#                 'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
#             }

#             que_tal = ArchivosDgitalesCreate()
#             respuesta = que_tal.crear_archivo(data_archivo, uploaded_file)

#             if respuesta.status_code != status.HTTP_201_CREATED:
#                 return respuesta

#             archivo_digital_id = respuesta.data.get('data').get('id_archivo_digital')

#             # Procesa los datos para agregar un documento de archivo expediente
#             data_in = request.data

#             persona_logueada = request.user.persona
#             data_in['id_persona_que_crea'] = persona_logueada.id_persona

#             if not persona_logueada.id_unidad_organizacional_actual:
#                 raise ValidationError("No tiene permiso para realizar esta acción")

#             data_in['id_und_org_oficina_creadora'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
#             data_in['id_und_org_oficina_respon_actual'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
#             data_in['sub_sistema_incorporacion'] = 'GEST'

#             # Determina el último orden en la base de datos y suma 1
#             last_order = DocumentosDeArchivoExpediente.objects.order_by('-orden_en_expediente').first()
#             if last_order is not None:
#                 data_in['orden_en_expediente'] = last_order.orden_en_expediente + 1
#             else:
#                 data_in['orden_en_expediente'] = 1

#             # Asegúrate de que 'id_expediente_documental' sea una instancia válida de ExpedientesDocumentales
#             id_expediente_documental_id = data_in.get('id_expediente_documental')
#             if id_expediente_documental_id:
#                 try:
#                     id_expediente_documental = ExpedientesDocumentales.objects.get(pk=id_expediente_documental_id)
#                 except ExpedientesDocumentales.DoesNotExist:
#                     raise ValidationError("El expediente documental especificado no existe.")
                
#                 # Ahora puedes acceder a los atributos de 'id_expediente_documental'
#                 if id_expediente_documental.cod_tipo_expediente == 'S':
#                     # Para Expedientes Simples (T236codTipoExpediente = S)
#                     data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}S{data_in['orden_en_expediente']:010d}"
#                 elif id_expediente_documental.cod_tipo_expediente == 'C':
#                     # Para Expedientes Complejos (T236codTipoExpediente = C)
#                     data_in['identificacion_doc_en_expediente'] = f"{id_expediente_documental.codigo_exp_Agno}C{id_expediente_documental.codigo_exp_consec_por_agno:<04d}{data_in['orden_en_expediente']:06d}"

#             # Establece la fecha de incorporación como la fecha actual
#             data_in['fecha_incorporacion_doc_a_Exp'] = datetime.now()
            
#             # Asigna el ID del archivo digital al campo 'id_archivo_sistema'
#             data_in['id_archivo_sistema'] = archivo_digital_id

#             # Obtener el índice electrónico del expediente que se está cerrando (debe reemplazar '1' con el ID correcto)
#             indice_electronico = IndicesElectronicosExp.objects.get(pk=1)  # Reemplaza 1 con el ID correcto

#             # Obtener el número de folios ingresado en el formulario
#             nro_folios_del_doc = data_in.get('nro_folios_del_doc')

#             # Calcular la página de inicio
#             last_index_doc = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico).order_by('-pagina_fin').first()
#             if last_index_doc:
#                 pagina_inicio = last_index_doc.pagina_fin + 1
#             else:
#                 pagina_inicio = 1

#             # Calcular la página final
#             pagina_inicio = int(pagina_inicio)
#             nro_folios_del_doc = int(nro_folios_del_doc)
#             pagina_fin = pagina_inicio + nro_folios_del_doc - 1

#             # Guardar el archivo de soporte
#             serializer = AgregarArchivoSoporteCreateSerializer(data=data_in)
#             serializer.is_valid(raise_exception=True)
#             archivo_soporte = serializer.save()

#             # Crear un registro en T240Docs_IndiceElectronicoExp
#             Docs_IndiceElectronicoExp.objects.create(
#                 id_indice_electronico_exp=indice_electronico,
#                 id_doc_archivo_exp=archivo_soporte,
#                 identificación_doc_exped=archivo_soporte.identificacion_doc_en_expediente,
#                 nombre_documento=archivo_soporte.nombre_asignado_documento,
#                 id_tipologia_documental=archivo_soporte.id_tipologia_documental,
#                 fecha_creacion_doc=archivo_soporte.fecha_creacion_doc,
#                 fecha_incorporacion_exp=archivo_soporte.fecha_incorporacion_doc_a_Exp,
#                 valor_huella=md5_value,
#                 funcion_resumen="MD5",
#                 orden_doc_expediente=archivo_soporte.orden_en_expediente,
#                 pagina_inicio=pagina_inicio,
#                 pagina_fin=pagina_fin,
#                 formato = archivo_soporte.id_archivo_sistema.formato,
#                 tamagno_kb=archivo_soporte.id_archivo_sistema.tamagno_kb,
#                 cod_origen_archivo=archivo_soporte.cod_origen_archivo,
#                 es_un_archivo_anexo=archivo_soporte.es_un_archivo_anexo,
#             )

#             # Retornar el hash MD5 y el archivo de soporte
#             response_data = {
#                 'success': True,
#                 "mensaje": "Archivo subido exitosamente",
#                 "md5_hash": md5_value,
#                 "archivo_soporte": serializer.data,
#                 "archivo_digital": respuesta.data
#             }

#             return Response(response_data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'success': False, 'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)



    
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
            raise NotFound('No se encontraron datos que coincidan con los criterios de búsqueda.')

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes tipologias',
            'data': serializer.data
        })
    

class CierreExpediente(generics.CreateAPIView):
    serializer_class = CierreExpedienteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            id_expediente_doc = request.data.get('id_expediente_doc')
            justificacion_cierre_reapertura = request.data.get('justificacion_cierre_reapertura')
            user = request.user
            expediente = ExpedientesDocumentales.objects.get(pk=id_expediente_doc)
            DocumentoArchivo = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente_doc)

            # Verifica si el expediente ya está cerrado
            if expediente.estado == 'C':
                raise ValidationError('El expediente ya está cerrado.')

            persona = user.persona

            if not DocumentoArchivo.exists():
                raise PermissionDenied('No puede realizar el cierre del expediente sin adjuntar mínimo un archivo de soporte')
            
            # Crea el registro de cierre de expediente
            cierre_expediente = CierresReaperturasExpediente.objects.create(
                id_expediente_doc=expediente,
                cod_operacion='C',  # Siempre 'C' para cierre
                fecha_cierre_reapertura=datetime.now(),
                justificacion_cierre_reapertura=justificacion_cierre_reapertura,
                id_persona_cierra_reabre=persona,  # Asignar la instancia de Personas
                cod_etapa_archivo_pre_reapertura=None
            )

            # Actualizar el estado del expediente a "C" (cerrado)
            expediente.fecha_folio_final = datetime.now()
            expediente.estado = 'C'
            expediente.fecha_cierre_reapertura_actual = datetime.now()
            
            # Guardar los cambios en el expediente
            expediente.save()

            for archivo_soporte in DocumentoArchivo:
                # Reemplaza 'tu_id_de_archivo_soporte' con el ID correcto del archivo de soporte
                ArchivosSoporte_CierreReapertura.objects.create(
                    id_cierre_reapertura_exp=cierre_expediente,
                    id_doc_archivo_exp_soporte=archivo_soporte,
                )

            # Obtener el nombre de la persona que realiza el cierre
            nombre_persona_cierra = ""
            if persona.primer_nombre:
                nombre_persona_cierra += persona.primer_nombre

            if persona.segundo_nombre:
                nombre_persona_cierra += " " + persona.segundo_nombre

            if persona.primer_apellido:
                nombre_persona_cierra += " " + persona.primer_apellido

            if persona.segundo_apellido:
                nombre_persona_cierra += " " + persona.segundo_apellido
                
            # Auditoria cierre_expediente
            usuario = request.user.id_usuario
            descripcion = {"IDExpediente": str(id_expediente_doc), "CodigoOperacion": "Cierre", "ConsecutivoExpediente": str(expediente.codigo_exp_consec_por_agno), "TituloExpediente": str(expediente.titulo_expediente)}

           
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 146,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)

            serializer = CierreExpedienteSerializer(cierre_expediente)

            return Response({'success': True, 'detail': 'Cierre de expediente realizado con éxito', 
                             'data': serializer.data,"persona_cierra":nombre_persona_cierra}, status=status.HTTP_201_CREATED)
        except ExpedientesDocumentales.DoesNotExist:
            raise NotFound('El expediente especificado no existe.')
        except Exception as e:
            raise ValidationError((e.args))

# class CierreExpediente(generics.CreateAPIView):
#     serializer_class = CierreExpedienteSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         try:
#             id_expediente_doc = request.data.get('id_expediente_doc')
#             justificacion_cierre_reapertura = request.data.get('justificacion_cierre_reapertura')
#             user = request.user
#             expediente = ExpedientesDocumentales.objects.get(pk=id_expediente_doc)
#             DocumentoArchivo = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente_doc)

#             # Verifica si el expediente ya está cerrado
#             if expediente.estado == 'C':
#                 raise ValidationError('El expediente ya está cerrado.')

#             persona = user.persona

#             if not DocumentoArchivo.exists():
#                 raise PermissionDenied('No puede realizar el cierre del expediente sin adjuntar mínimo un archivo de soporte')
            
#             # Crea el registro de cierre de expediente
#             cierre_expediente = CierresReaperturasExpediente.objects.create(
#                 id_expediente_doc=expediente,
#                 cod_operacion='C',  # Siempre 'C' para cierre
#                 fecha_cierre_reapertura=datetime.now(),
#                 justificacion_cierre_reapertura=justificacion_cierre_reapertura,
#                 id_persona_cierra_reabre=persona,  # Asignar la instancia de Personas
#             )

#             # Actualizar el estado del expediente a "C" (cerrado)
#             expediente.fecha_folio_final = datetime.now()
#             expediente.estado = 'C'
#             expediente.fecha_cierre_reapertura_actual = datetime.now()
            
#             # Guardar los cambios en el expediente
#             expediente.save()

#             for archivo_soporte in DocumentoArchivo:
#                 # Reemplaza 'tu_id_de_archivo_soporte' con el ID correcto del archivo de soporte
#                 ArchivosSoporte_CierreReapertura.objects.create(
#                     id_cierre_reapertura_exp=cierre_expediente,
#                     id_doc_archivo_exp_soporte=archivo_soporte,
#                 )

#             # Serializar el objeto cierre_expediente
#             serializer = CierreExpedienteSerializer(cierre_expediente)

#             # Auditoria cierre_expediente
#             usuario = request.user.id_usuario
#             descripcion = {"IDExpediente": str(id_expediente_doc), "CodigoOperacion": "Cierre", "ConsecutivoExpediente": str(expediente.codigo_exp_consec_por_agno), "TituloExpediente": str(expediente.titulo_expediente)}
#             direccion=Util.get_client_ip(request)
#             auditoria_data = {
#                 "id_usuario" : usuario,
#                 "id_modulo" : 146,
#                 "cod_permiso": "CR",
#                 "subsistema": 'GEST',
#                 "dirip": direccion,
#                 "descripcion": descripcion,
#             }
#             Util.save_auditoria(auditoria_data)

#             return Response({'success': True, 'message': 'Cierre de expediente realizado con éxito', 'data': serializer.data}, status=status.HTTP_201_CREATED)

#         except ExpedientesDocumentales.DoesNotExist:
#             raise NotFound('El expediente especificado no existe.')
#         except Exception as e:
#             raise ValidationError(str(e))




class EliminarArchivoSoporte(generics.DestroyAPIView):
    queryset = DocumentosDeArchivoExpediente.objects.all()
    serializer_class = AgregarArchivoSoporteCreateSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = 'id_documento_de_archivo_exped'

    def destroy(self, request, *args, **kwargs):
        try:
            # instance = self.get_object()
            # Obtener el id_documento_de_archivo_exped de la solicitud
            id_documento_de_archivo_exped = kwargs.get('id_documento_de_archivo_exped')

            # Verificar si el archivo de soporte existe
            archivo_soporte = DocumentosDeArchivoExpediente.objects.get(id_documento_de_archivo_exped=id_documento_de_archivo_exped)

            # Obtener el archivo de sistema asociado
            archivo_digital = archivo_soporte.id_archivo_sistema

            # Eliminar el archivo de soporte
            archivo_soporte.delete()

            # Verificar si hay más archivos de soporte con el mismo archivo de sistema
            otros_soportes = DocumentosDeArchivoExpediente.objects.filter(id_archivo_sistema=archivo_digital)

            if not otros_soportes.exists():
                # Si no hay más archivos de soporte con el mismo archivo de sistema, eliminar el archivo de sistema
                archivo_digital.delete()

            return Response({'success': True, 'detail': 'Archivo de soporte y su archivo de sistema asociado eliminados con éxito'}, status=status.HTTP_200_OK)
        except DocumentosDeArchivoExpediente.DoesNotExist:
            raise NotFound('El archivo de soporte especificado no existe.')
        

#LISTAR_ARCHIVOS_SOPORTE_X_ID
class ArchivosSoporteGetId(generics.ListAPIView):
    serializer_class = ArchivosSoporteGetAllSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtén el ID del expediente desde la URL
        id_expediente = self.kwargs.get('id_expediente')

        # Filtra los archivos de soporte asociados al expediente
        return DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente).order_by('orden_en_expediente')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_expediente = self.kwargs.get('id_expediente')  # Obtén el ID del expediente de la URL

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': f'No se encontraron archivos de soporte registrados para el expediente con ID {id_expediente}.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': f'Se encontraron los siguientes archivos de soporte para el expediente con ID {id_expediente}.',
            'data': serializer.data
        })

# class UpdateArchivoSoporte(generics.UpdateAPIView):
#     queryset = DocumentosDeArchivoExpediente.objects.all()
#     serializer_class = AgregarArchivoSoporteCreateSerializer
#     lookup_field = 'id_documento_de_archivo_exped'  # Campo utilizado para buscar el archivo de soporte

#     def update(self, request, *args, **kwargs):
#         try:
#             # Obtener el archivo de soporte por su id_documento_de_archivo_exped
#             archivo_soporte = self.get_object()
            
#             # Validar que los datos de entrada sean válidos
#             serializer = self.get_serializer(archivo_soporte, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
            
#             # Guardar los cambios en el archivo de soporte
#             serializer.save()
            
#             return Response({'success': True, 'detail': 'Archivo de soporte actualizado con éxito'}, status=status.HTTP_200_OK)
#         except DocumentosDeArchivoExpediente.DoesNotExist:
#             return Response({'success': False, 'detail': 'El archivo de soporte especificado no existe.'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateArchivoSoporte(generics.UpdateAPIView):
    queryset = DocumentosDeArchivoExpediente.objects.all()
    serializer_class = AgregarArchivoSoporteCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id_documento_de_archivo_exped'  # Campo utilizado para buscar el archivo de soporte

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        uploaded_file = request.data.get('file')

        try:
            if uploaded_file:
                # Obtiene el año actual para determinar la carpeta de destino
                current_year = datetime.now().year
                ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

                # Calcula el hash MD5 del nuevo archivo
                md5_hash = hashlib.md5()
                for chunk in uploaded_file.chunks():
                    md5_hash.update(chunk)

                # Obtiene el valor hash MD5
                md5_value = md5_hash.hexdigest()

                # Elimina el archivo digital anterior asociado a este archivo de soporte
                if instance.id_archivo_sistema:
                    instance.id_archivo_sistema.delete()

                # Crea un nuevo archivo digital y asócialo al archivo de soporte
                data_archivo = {
                    'es_Doc_elec_archivo': False,
                    'ruta': ruta,
                    'md5_hash': md5_value
                }

                que_tal = ArchivosDgitalesCreate()
                respuesta = que_tal.crear_archivo(data_archivo, uploaded_file)

                if respuesta.status_code != status.HTTP_201_CREATED:
                    return respuesta

                archivo_digital_id = respuesta.data.get('data').get('id_archivo_digital')

                # Actualiza 'nombre_original_del_archivo' con el nombre del documento antes de cifrarlo
                instance.nombre_original_del_archivo = uploaded_file.name

                # Actualiza el archivo de soporte con la nueva información
                instance.file = uploaded_file  # Si también deseas actualizar el archivo de soporte
                instance.id_archivo_sistema = ArchivosDigitales.objects.get(pk=archivo_digital_id)

            # Validar que los datos de entrada sean válidos
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # Guardar los cambios en el archivo de soporte
            serializer.save()

            # Retornar el hash MD5 junto con "respuesta"
            response_data = {
                "mensaje": "Archivo subido o actualizado exitosamente",
                "md5_hash": md5_value if uploaded_file else None,  # Devuelve el hash solo si se subió un nuevo archivo
                "respuesta": respuesta.data if uploaded_file else None,  # Devuelve la respuesta solo si se subió un nuevo archivo
            }

            # return Response(response_data, status=status.HTTP_200_OK)
            return Response({ 'success': True,'detail': 'Se Actualizo correctamente el archivo de soporte.','data': response_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DetalleArchivoSoporte(generics.RetrieveAPIView):
    queryset = DocumentosDeArchivoExpediente.objects.all()
    serializer_class = ArchivoSoporteSerializer
    lookup_field = 'id_documento_de_archivo_exped'  # Campo utilizado para buscar el archivo de soporte

    def retrieve(self, request, id_documento_de_archivo_exped, *args, **kwargs):
        try:
            archivo_soporte = self.queryset.get(id_documento_de_archivo_exped=id_documento_de_archivo_exped)
            serializer = self.get_serializer(archivo_soporte)

            return Response({ 'success': True,'detail': 'Se encontraron los siguientes registros.','data': serializer.data}, status=status.HTTP_200_OK)
        except DocumentosDeArchivoExpediente.DoesNotExist:
            raise NotFound('El archivo soporte especificado no existe.')
        except Exception as e:
            raise ValidationError((e.args))

########################## CRUD DE ARCHIVOS DIGITALES  ##########################


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


############################################  REAPERTURA DE EXPEDIENTES  #################################################################

#BUSCAR_EXPEDIENTES_CERRADOS
class ExpedienteSearchCerrado(generics.ListAPIView):
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
        queryset = ExpedientesDocumentales.objects.filter(estado='C')  # Filtrar por estado 'A'
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
            raise NotFound('No se encontraron datos que coincidan con los criterios de búsqueda.')

        serializer = ExpedienteSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

#INFORMACION_EXPEDIENTE_CERRADO
# class CierresReaperturasExpedienteDetailView(generics.RetrieveAPIView):
#     serializer_class = CierreExpedienteSerializer
#     queryset = CierresReaperturasExpediente.objects.all()

#     def retrieve(self, request, id_expediente, *args, **kwargs):
#         # Obtiene el expediente por su ID o devuelve un 404 si no existe
#         expediente = get_object_or_404(ExpedientesDocumentales, pk=id_expediente)

#         # Si el expediente está cerrado (estado 'C'), filtra los cierres relacionados
#         if expediente.estado == 'C':
#             queryset = self.queryset.filter(id_expediente_doc=id_expediente)

#             # Obtén el último registro de cierre por fecha
#             ultimo_cierre = queryset.order_by('-fecha_cierre_reapertura').first()

#             if ultimo_cierre:
#                 titulo_expediente = expediente.titulo_expediente

#                 # Obtener el nombre de la persona que realiza el cierre
#                 nombre_persona_cierra = ""
#                 persona = ultimo_cierre.id_persona_cierra_reabre

#                 if persona.primer_nombre:
#                     nombre_persona_cierra += persona.primer_nombre

#                 if persona.segundo_nombre:
#                     nombre_persona_cierra += " " + persona.segundo_nombre

#                 if persona.primer_apellido:
#                     nombre_persona_cierra += " " + persona.primer_apellido

#                 if persona.segundo_apellido:
#                     nombre_persona_cierra += " " + persona.segundo_apellido

#                 # Obtener la fecha de cierre
#                 fecha_cierre = ultimo_cierre.fecha_cierre_reapertura.strftime("%Y-%m-%d")

#                 # Crear la cadena de texto
#                 cierre_realizado_por = f"El expediente fue cerrado el dia {fecha_cierre} por {nombre_persona_cierra}."

#                 serializer = self.get_serializer(ultimo_cierre)
#                 response_data = {
#                     'titulo_expediente': titulo_expediente,
#                     'nombre_persona_cierra': cierre_realizado_por,
#                     'cierre_expediente': serializer.data
#                 }
#                 return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': response_data,}, status=status.HTTP_200_OK)

#             else:
#                 raise NotFound('No se encontraron cierres para el expediente')
#         else:
#             raise NotFound('El expediente no está cerrado')
class CierresReaperturasExpedienteDetailView(generics.RetrieveAPIView):
    serializer_class = CierreExpedienteDetailSerializer
    queryset = CierresReaperturasExpediente.objects.all()

    def retrieve(self, request, id_expediente, *args, **kwargs):
        # Obtiene el expediente por su ID o devuelve un 404 si no existe
        expediente = get_object_or_404(ExpedientesDocumentales, pk=id_expediente)

        # Si el expediente está cerrado (estado 'C'), filtra los cierres relacionados
        if expediente.estado == 'C':
            queryset = self.queryset.filter(id_expediente_doc=id_expediente)

            # Obtén el último registro de cierre por fecha
            ultimo_cierre = queryset.order_by('-fecha_cierre_reapertura').first()

            if ultimo_cierre:
                titulo_expediente = expediente.titulo_expediente

                # Obtener el nombre de la persona que realiza el cierre
                nombre_persona_cierra = ""
                persona = ultimo_cierre.id_persona_cierra_reabre

                if persona.primer_nombre:
                    nombre_persona_cierra += persona.primer_nombre

                if persona.segundo_nombre:
                    nombre_persona_cierra += " " + persona.segundo_nombre

                if persona.primer_apellido:
                    nombre_persona_cierra += " " + persona.primer_apellido

                if persona.segundo_apellido:
                    nombre_persona_cierra += " " + persona.segundo_apellido

                # Obtener la fecha de cierre
                fecha_cierre = ultimo_cierre.fecha_cierre_reapertura.strftime("%Y-%m-%d")

                # Crear la cadena de texto
                cierre_realizado_por = f"El expediente fue cerrado el día {fecha_cierre} por {nombre_persona_cierra}."

                serializer = self.get_serializer(ultimo_cierre)
                response_data = {
                    'titulo_expediente': titulo_expediente,
                    'nombre_persona_cierra': cierre_realizado_por,
                    'cierre_expediente': serializer.data
                }
                return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': response_data}, status=status.HTTP_200_OK)

            else:
                raise NotFound('No se encontraron cierres para el expediente')
        else:
            raise NotFound('El expediente no está cerrado')


class ReaperturaExpediente(generics.CreateAPIView):
    serializer_class = CierreExpedienteSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            id_expediente_doc = request.data.get('id_expediente_doc')
            justificacion_reapertura = request.data.get('justificacion_reapertura')
            user = request.user
            expediente = get_object_or_404(ExpedientesDocumentales, pk=id_expediente_doc)

            # Verificar si el expediente está cerrado (estado 'C')
            if expediente.estado != 'C':
                raise ValidationError('El expediente no está cerrado, por lo que no se puede reabrir.')

            persona = user.persona

            DocumentoArchivo = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente_doc)
            # Obtener el código de la etapa actual antes de la reapertura
            etapa_actual_anterior = expediente.cod_etapa_de_archivo_actual_exped

            # Crear el registro de reapertura de expediente
            reapertura_expediente = CierresReaperturasExpediente.objects.create(
                id_expediente_doc=expediente,
                cod_operacion='R',  # 'R' para reapertura
                fecha_cierre_reapertura=datetime.now(),
                justificacion_cierre_reapertura=justificacion_reapertura,
                id_persona_cierra_reabre=persona,
                cod_etapa_archivo_pre_reapertura=etapa_actual_anterior
            )


            # Actualizar los campos de ExpedientesDocumentales
            expediente.estado = 'A'  # 'A' para abierto
            expediente.fecha_folio_final = None
            expediente.fecha_cierre_reapertura_actual = datetime.now()
            expediente.fecha_firma_cierre_indice_elec = None
            expediente.fecha_paso_a_archivo_central = None
            expediente.fecha_paso_a_archivo_historico = None
            expediente.fecha_eliminacion_x_dispo_final = None
            if expediente.cod_etapa_de_archivo_actual_exped != 'G':
                expediente.cod_etapa_de_archivo_actual_exped = 'G'
                expediente.ubicacion_fisica_esta_actualizada = False

            # Guardar los cambios en el expediente
            expediente.save()

            # Crear registros de archivos de soporte para la reapertura
            for archivo_soporte in DocumentoArchivo:
                ArchivosSoporte_CierreReapertura.objects.create(
                    id_cierre_reapertura_exp=reapertura_expediente,
                    id_doc_archivo_exp_soporte=archivo_soporte,
                )

            # Auditoria reapertura_expediente
            usuario = request.user.id_usuario
            descripcion = {"IDExpediente": str(id_expediente_doc), "CodigoOperacion": "Reapertura", "ConsecutivoExpediente": str(expediente.codigo_exp_consec_por_agno), "TituloExpediente": str(expediente.titulo_expediente)}

           
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 149,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)

            serializer = CierreExpedienteSerializer(reapertura_expediente)

            return Response({
                'success': True,
                'detail': 'Reapertura de expediente realizada con éxito',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except ExpedientesDocumentales.DoesNotExist:
            raise NotFound('El expediente especificado no existe.')
        except Exception as e:
            raise ValidationError((e.args))        