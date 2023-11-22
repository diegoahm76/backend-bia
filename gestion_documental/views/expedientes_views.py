from datetime import datetime
import hashlib
import os
import json
import copy
from django.db.utils import IntegrityError
from django.core.files.base import ContentFile
import secrets
from rest_framework.parsers import MultiPartParser
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.depositos_models import CarpetaCaja
from gestion_documental.models.expedientes_models import ConcesionesAccesoAExpsYDocs, DobleVerificacionTmp, ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, FormatosTiposMedio, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.serializers.conf__tipos_exp_serializers import ConfiguracionTipoExpedienteAgnoGetSerializer
from gestion_documental.serializers.trd_serializers import BusquedaTRDNombreVersionSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.conf__tipos_exp_views import ConfiguracionTipoExpedienteAgnoGetConsect
from seguridad.utils import Util
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import  AgregarArchivoSoporteCreateSerializer, AnularExpedienteSerializer, AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer, AperturaExpedienteUpdateAutSerializer, AperturaExpedienteUpdateNoAutSerializer, ArchivoSoporteSerializer, ArchivosDigitalesCreateSerializer, ArchivosDigitalesSerializer, ArchivosSoporteCierreReaperturaSerializer, ArchivosSoporteGetAllSerializer, BorrarExpedienteSerializer, CierreExpedienteDetailSerializer, CierreExpedienteSerializer, ConcesionAccesoDocumentosCreateSerializer, ConcesionAccesoDocumentosGetSerializer, ConcesionAccesoExpedientesCreateSerializer, ConcesionAccesoExpedientesGetSerializer, ConcesionAccesoPersonasFilterSerializer, ConcesionAccesoUpdateSerializer, ConfiguracionTipoExpedienteAperturaGetSerializer, EnvioCodigoSerializer, ExpedienteAperturaSerializer, ExpedienteGetOrdenSerializer, ExpedienteSearchSerializer, ExpedientesDocumentalesGetSerializer, FirmaCierreGetSerializer, IndexarDocumentosAnularSerializer, IndexarDocumentosCreateSerializer, IndexarDocumentosGetSerializer, IndexarDocumentosUpdateAutSerializer, IndexarDocumentosUpdateSerializer, InformacionIndiceGetSerializer, ListExpedientesComplejosSerializer, ListarTRDSerializer, ListarTipologiasSerializer, ReubicacionFisicaExpedienteSerializer, SerieSubserieUnidadTRDGetSerializer
from gestion_documental.serializers.depositos_serializers import  CarpetaCajaGetOrdenSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q, F
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from transversal.models.organigrama_models import Organigramas
from django.db.models.functions import Concat
from django.db.models import Value as V

from transversal.models.personas_models import Personas

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
        
        # OBTENER CONSECUTIVO ACTUAL
        codigo_exp_consec_por_agno = None
        
        if data['cod_tipo_expediente'] == 'C':
            # LLAMAR CLASE PARA GENERAR CONSECUTIVO
            fecha_actual = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            clase_consec = ConfiguracionTipoExpedienteAgnoGetConsect()
            codigo_exp_consec_por_agno = clase_consec.generar_radicado(
                data['id_cat_serie_und_org_ccd_trd_prop'],
                request.user.persona.id_persona,
                fecha_actual
            )
            codigo_exp_consec_por_agno = codigo_exp_consec_por_agno.data.get('data').get('consecutivo_actual')
            
        data['codigo_exp_consec_por_agno'] = codigo_exp_consec_por_agno
        data['estado'] = 'A'
        data['fecha_folio_inicial'] = current_date
        data['cod_etapa_de_archivo_actual_exped'] = 'G'
        data['tiene_carpeta_fisica'] = True if data.get('carpetas_caja') else False
        data['ubicacion_fisica_esta_actualizada'] = True
        data['fecha_creacion_manual'] = current_date
        data['id_persona_crea_manual'] = request.user.persona.id_persona
        data['creado_automaticamente'] = False
        
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
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(data['codigo_exp_Agno'])
        }
        if codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 160,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
            
        return Response({'success':True, 'detail':'Apertura realizada de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class AperturaExpedienteGet(generics.ListAPIView):
    serializer_class = ExpedienteAperturaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_expediente_documental):
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        serializer = self.serializer_class(expediente)
        
        return Response({'success':True, 'detail':'Se encontró el siguiente expediente', 'data':serializer.data}, status=status.HTTP_200_OK)

class AperturaExpedienteUpdate(generics.UpdateAPIView):
    serializer_class = AperturaExpedienteUpdateAutSerializer
    serializer_class_no_aut = AperturaExpedienteUpdateNoAutSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, id_expediente_documental):
        data = request.data
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        
        if not expediente:
            raise NotFound('No se encontró el expediente indicado')
        
        previous_expediente = copy.copy(expediente)
        
        if expediente.creado_automaticamente:
            serializer = self.serializer_class(expediente, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.serializer_class_no_aut(expediente, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
        instances_carpetas_ya_asociadas = CarpetaCaja.objects.filter(id_expediente=id_expediente_documental)
        carpetas_caja = data.get('carpetas_caja')
        
        if carpetas_caja:
            instances_carpetas = CarpetaCaja.objects.filter(id_carpeta_caja__in=set(data.get('carpetas_caja')))
            instances_carpetas_ya_asociadas_list = list(instances_carpetas_ya_asociadas.values_list('id_carpeta_caja', flat=True))
            
            instances_expediente_asociado = instances_carpetas.exclude(id_expediente=None).exclude(id_expediente=id_expediente_documental)
            
            if len(set(data.get('carpetas_caja'))) != len(instances_carpetas):
                raise ValidationError('Debe enviar carpetas existentes en el sistema')
            
            if instances_expediente_asociado:
                raise ValidationError('Alguna(s) de las carpetas seleccionadas ya poseen expedientes asociados distinto al ingresado')
            
            nuevas_carpetas = [carpeta for carpeta in instances_carpetas if carpeta.id_carpeta_caja not in instances_carpetas_ya_asociadas_list]
            
            for nueva_carpeta in nuevas_carpetas:
                nueva_carpeta.id_expediente = expediente
                nueva_carpeta.save()
                
            carpetas_removidas = [carpeta for carpeta in instances_carpetas_ya_asociadas if carpeta.id_carpeta_caja not in list(instances_carpetas.values_list('id_carpeta_caja', flat=True))]

            for carpeta_removida in carpetas_removidas:
                carpeta_removida.id_expediente = None
                carpeta_removida.save()
        elif carpetas_caja == []:
            for carpeta_removida in instances_carpetas_ya_asociadas:
                carpeta_removida.id_expediente = None
                carpeta_removida.save()
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(expediente.codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(expediente.codigo_exp_Agno)
        }
        if expediente.codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(expediente.codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        valores_actualizados = {'previous': previous_expediente, 'current':expediente}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 160,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Expediente actualizado de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class AnularExpediente(generics.UpdateAPIView):
    serializer_class = AnularExpedienteSerializer
    permission_classes = [IsAuthenticated] # PENDIENTE VALIDACIÓN permisos de Creación de Expediente en la Serie Documental elegida y adicionalmente la persona como tal debe tener permisos de Anulación del módulo

    def update(self, request, id_expediente_documental):
        data = request.data
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        
        if not expediente:
            raise NotFound('No se encontró el expediente indicado')
        
        if expediente.creado_automaticamente:
            raise PermissionDenied('No puede anular un expediente creado automaticamente')
        
        if expediente.cod_etapa_de_archivo_actual_exped != 'G':
            raise PermissionDenied('Solo puede anular expedientes en etapa de Gestión')
                    
        if expediente.estado != 'A':
            raise PermissionDenied('No puede anular un expediente cerrado. Debe realizar una reapertura primero')
        
        data['anulado'] = True
        data['fecha_anulacion'] = datetime.now()
        data['id_persona_anula'] = request.user.persona.id_persona
        
        serializer = self.serializer_class(expediente, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(expediente.codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(expediente.codigo_exp_Agno)
        }
        if expediente.codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(expediente.codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 160,
            "cod_permiso": "AN",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Expediente anulado de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class BorrarExpediente(generics.DestroyAPIView):
    serializer_class = BorrarExpedienteSerializer
    permission_classes = [IsAuthenticated] # PENDIENTE VALIDACIÓN permisos de Creación de Expediente en la Serie Documental elegida y adicionalmente la persona como tal debe tener permisos de Anulación del módulo

    def delete(self, request, id_expediente_documental):
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        
        if not expediente:
            raise NotFound('No se encontró el expediente indicado')
        
        if expediente.creado_automaticamente:
            raise PermissionDenied('No puede anular un expediente creado automaticamente')
        
        if expediente.documentosdearchivoexpediente_set.all():
            raise PermissionDenied('No puede borrar un expediente con documentos asociados')
        
        if expediente.cod_tipo_expediente != 'S':
            ultimo_expediente_comp = ExpedientesDocumentales.objects.filter(cod_tipo_expediente='C', codigo_exp_und_serie_subserie=expediente.codigo_exp_und_serie_subserie).order_by('codigo_exp_consec_por_agno').last()
            if expediente.id_expediente_documental != ultimo_expediente_comp.id_expediente_documental:
                raise PermissionDenied('Solo puede borrar el expediente con el último consecutivo')
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(expediente.codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(expediente.codigo_exp_Agno)
        }
        if expediente.codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(expediente.codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 160,
            "cod_permiso": "BO",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
        
        # BORRAR
        expediente.delete()
        
        return Response({'success':True, 'detail':'Expediente borrado de manera exitosa'}, status=status.HTTP_200_OK)

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
        id_persona_titular_exp_complejo = self.request.query_params.get('id_persona_titular_exp_complejo')
        ubicacion_desactualizada = self.request.query_params.get('ubicacion_desactualizada', '').strip()




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

        if id_persona_titular_exp_complejo:
            queryset = queryset.filter(id_persona_titular_exp_complejo=id_persona_titular_exp_complejo)
        
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

        # Nuevo filtro para expedientes con ubicación física desactualizada
        if ubicacion_desactualizada.lower() in ['true', 'false']:
            ubicacion_desactualizada_bool = ubicacion_desactualizada.lower() == 'true'
            queryset = queryset.filter(ubicacion_fisica_esta_actualizada=ubicacion_desactualizada_bool)

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
        
class TrdActualRetiradosGet(generics.ListAPIView):
    serializer_class = BusquedaTRDNombreVersionSerializer 
    queryset = TablaRetencionDocumental.objects.filter(Q(actual=True) | (Q(actual=False) & ~Q(fecha_retiro_produccion=None)))
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
        
        trd = self.queryset.filter(**filter).order_by('-actual')
        serializador = self.serializer_class(trd, many=True, context = {'request':request})
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializador.data}, status=status.HTTP_200_OK)

class ListExpedientesComplejosGet(generics.ListAPIView):
    serializer_class = ListExpedientesComplejosSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_catserie_unidadorg):
        expedientes = ExpedientesDocumentales.objects.filter(id_cat_serie_und_org_ccd_trd_prop=id_catserie_unidadorg)
        if not expedientes:
            raise NotFound("No se encontró expedientes para la tripleta del TRD seleccionado")
        
        serializer = self.serializer_class(expedientes, many=True)
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)

class ExpedientesSimpleGet(generics.ListAPIView):
    serializer_class = ListExpedientesComplejosSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_expediente_documental):
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        if not expediente:
            raise NotFound("No se encontró el expediente seleccionado")
        
        serializer = self.serializer_class(expediente)
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class IndexarDocumentosCreate(generics.CreateAPIView):
    serializer_class = IndexarDocumentosCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_expediente_documental):
        data = request.data
        data_documentos = json.loads(data['data_documentos'])
        archivos = request.FILES.getlist('archivos')
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        indice_electronico = IndicesElectronicosExp.objects.filter(id_expediente_doc=id_expediente_documental).first()
        if not indice_electronico:
            raise NotFound('Debe crear el índice electrónico del expediente elegido antes de continuar')
        
        if len(data_documentos) != len(archivos):
            raise ValidationError('Debe enviar la data para cada archivo subido')
        
        # Hallar identificacion doc
        identificacion_doc = ''
        if expediente.cod_tipo_expediente == 'S':
            identificacion_doc = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}"
        else:
            identificacion_doc = f"{expediente.codigo_exp_Agno}{expediente.cod_tipo_expediente}{expediente.codigo_exp_consec_por_agno:<04d}"
        
        documento_principal = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente_documental, es_un_archivo_anexo=False, orden_en_expediente=1).first()
        if not documento_principal:
            documento_principal = None
        
        for data, archivo in zip(data_documentos, archivos):
            # VALIDAR FORMATO ARCHIVO 
            archivo_nombre = archivo.name
            nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            
            tipologia = TipologiasDoc.objects.filter(id_tipologia_documental=data['id_tipologia_documental']).first()
            if not tipologia:
                raise ValidationError("Debe elegir una tipología válida")
                
            cod_tipo_medio_doc_list = ['E', 'F'] if tipologia.cod_tipo_medio_doc.cod_tipo_medio_doc == 'H' else [tipologia.cod_tipo_medio_doc.cod_tipo_medio_doc]
            
            formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc__in=cod_tipo_medio_doc_list).values_list('nombre', flat=True)
            
            if extension_sin_punto.lower() not in list(formatos_tipos_medio_list) and extension_sin_punto.upper() not in list(formatos_tipos_medio_list):
                raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido para la Tipología Documental elegida')
            
            # CREAR ARCHIVO EN T238
            # Obtiene el año actual para determinar la carpeta de destino
            year_expediente = expediente.fecha_apertura_expediente.year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(year_expediente))

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in archivo.chunks():
                md5_hash.update(chunk)

            # Obtiene el valor hash MD5
            md5_value = md5_hash.hexdigest()

            # Crea el archivo digital y obtiene su ID
            data_archivo = {
                'es_Doc_elec_archivo': True,
                'ruta': ruta,
                'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
            }
            
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, archivo)
            
            # CREAR DOCUMENTO EN T237
            data['id_expediente_documental'] = id_expediente_documental
            data['identificacion_doc_en_expediente'] = f"{identificacion_doc}{data['orden_en_expediente']:010d}" if expediente.cod_tipo_expediente == 'S' else f"{identificacion_doc}{data['orden_en_expediente']:06d}"
            data['nombre_original_del_archivo'] = archivo.name
            data['es_version_original'] = True
            data['es_un_archivo_anexo'] = True if str(data['orden_en_expediente']) != '1' else False
            data['id_doc_de_arch_del_cual_es_anexo'] = None if not documento_principal else documento_principal.id_documento_de_archivo_exped
            data['anexo_corresp_a_lista_chequeo'] = False
            data['id_archivo_sistema'] = respuesta.data.get('data').get('id_archivo_digital')
            data['documento_requiere_rta'] = False
            data['creado_automaticamente'] = False
            data['fecha_indexacion_manual_sistema'] = datetime.now()
            data['id_und_org_oficina_creadora'] = request.user.persona.id_unidad_organizacional_actual.id_unidad_organizacional
            data['id_persona_que_crea'] = request.user.persona.id_persona
            data['id_und_org_oficina_respon_actual'] = request.user.persona.id_unidad_organizacional_actual.id_unidad_organizacional
            
            serializer_documento = self.serializer_class(data=data)
            serializer_documento.is_valid(raise_exception=True)
            doc_creado = serializer_documento.save()
            
            if str(data['orden_en_expediente']) == '1':
                documento_principal = doc_creado
            
            # CREAR REGISTRO EN T240
            
            # Calcular la página de inicio
            last_index_doc = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico).order_by('-pagina_fin').first()
            if last_index_doc:
                pagina_inicio = last_index_doc.pagina_fin + 1
            else:
                pagina_inicio = 1

            # Calcular la página final
            pagina_inicio = int(pagina_inicio)
            nro_folios_del_doc = int(data['nro_folios_del_doc'])
            pagina_fin = pagina_inicio + nro_folios_del_doc - 1
            
            Docs_IndiceElectronicoExp.objects.create(
                id_indice_electronico_exp=indice_electronico,
                id_doc_archivo_exp=doc_creado,
                identificación_doc_exped=doc_creado.identificacion_doc_en_expediente,
                nombre_documento=doc_creado.nombre_asignado_documento,
                id_tipologia_documental=doc_creado.id_tipologia_documental,
                fecha_creacion_doc=doc_creado.fecha_creacion_doc,
                fecha_incorporacion_exp=doc_creado.fecha_incorporacion_doc_a_Exp,
                valor_huella=md5_value,
                funcion_resumen="MD5",
                orden_doc_expediente=doc_creado.orden_en_expediente,
                pagina_inicio=pagina_inicio,
                pagina_fin=pagina_fin,
                formato=doc_creado.id_archivo_sistema.formato,
                tamagno_kb=doc_creado.id_archivo_sistema.tamagno_kb,
                cod_origen_archivo=doc_creado.cod_origen_archivo,
                es_un_archivo_anexo=doc_creado.es_un_archivo_anexo,
            )
        
        return Response({'success':True, 'detail':'Indexación de documentos realizado correctamente'}, status=status.HTTP_201_CREATED)

class IndexarDocumentosGet(generics.ListAPIView):
    serializer_class = IndexarDocumentosGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_documento_de_archivo_exped):
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound("No se encuentra el documento ingresado")
            
        serializer = self.serializer_class(doc_expediente)
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class IndexarDocumentosUpdate(generics.UpdateAPIView):
    serializer_class = IndexarDocumentosUpdateSerializer
    serializer_aut_class = IndexarDocumentosUpdateAutSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_documento_de_archivo_exped):
        data = request.data
        
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound('No se encontró el documento del expediente elegido')
        
        if doc_expediente.creado_automaticamente:
            serializer = self.serializer_aut_class(doc_expediente, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.serializer_class(doc_expediente, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
            if data.get('nro_folios_del_doc'):
                indice_electronico = IndicesElectronicosExp.objects.filter(id_expediente_doc=doc_expediente.id_expediente_documental).first()
                index_doc = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico, id_doc_archivo_exp=doc_expediente.id_documento_de_archivo_exped).first()
                
                # Calcular la página final
                pagina_inicio = index_doc.pagina_inicio
                nro_folios_del_doc = int(data.get('nro_folios_del_doc'))
                pagina_fin = pagina_inicio + nro_folios_del_doc - 1
                
                index_doc.pagina_fin = pagina_fin
                index_doc.save()
                
                pagina_fin_next = pagina_fin
                
                index_doc_next = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico, id_doc_archivo_exp__orden_en_expediente__gt=doc_expediente.orden_en_expediente).order_by('id_doc_archivo_exp__orden_en_expediente')
                if index_doc_next:
                    for index_doc_after in index_doc_next:
                        # Calcular la página de inicio
                        pagina_inicio_next = pagina_fin_next + 1

                        # Calcular la página final
                        nro_folios_del_doc = index_doc_after.id_doc_archivo_exp.nro_folios_del_doc
                        pagina_fin_next = pagina_inicio_next + nro_folios_del_doc - 1
                        
                        index_doc_after.pagina_inicio = pagina_inicio_next
                        index_doc_after.pagina_fin = pagina_fin_next
                        index_doc_after.save()
        
        return Response({'success':True, 'detail':'Actualización de documento realizado correctamente'}, status=status.HTTP_201_CREATED)

class IndexarDocumentosAnular(generics.UpdateAPIView):
    serializer_class = IndexarDocumentosAnularSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_documento_de_archivo_exped):
        data = request.data
        
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound('No se encontró el documento del expediente elegido')
        
        if doc_expediente.id_expediente_documental.estado != 'A':
            raise PermissionDenied('No puede anular el documento elegido porque el expediente se encuentra cerrado')

        data['anulado'] = True
        data['fecha_anulacion'] = datetime.now()
        data['id_persona_anula'] = request.user.persona.id_persona
            
        serializer = self.serializer_class(doc_expediente, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        doc_indice_elect = doc_expediente.docs_indiceelectronicoexp_set.first()
        doc_indice_elect.anulado = True
        doc_indice_elect.save()
        
        if not doc_expediente.es_un_archivo_anexo:
            docs_expedientes_anexos = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=doc_expediente.id_expediente_documental, es_un_archivo_anexo=True)
            
            for doc_expediente_anexo in docs_expedientes_anexos:
                doc_expediente_anexo.anulado = True
                doc_expediente_anexo.fecha_anulacion = data['fecha_anulacion']
                doc_expediente_anexo.observacion_anulacion = 'Anulado debido a que el archivo del cual este es anexo fue anulado.'
                doc_expediente_anexo.id_persona_anula = request.user.persona
                doc_expediente_anexo.save()
                
                doc_indice_elect_anexo = doc_expediente_anexo.docs_indiceelectronicoexp_set.first()
                doc_indice_elect_anexo.anulado = True
                doc_indice_elect_anexo.save()
        
        return Response({'success':True, 'detail':'Anulación de documento realizado correctamente'}, status=status.HTTP_201_CREATED)

class IndexarDocumentosBorrar(generics.DestroyAPIView):
    serializer_class = IndexarDocumentosAnularSerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id_documento_de_archivo_exped):
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound('No se encontró el documento del expediente elegido')
        
        if doc_expediente.id_expediente_documental.estado != 'A':
            raise PermissionDenied('No puede borrar el documento elegido porque el expediente se encuentra cerrado')
        
        descripcion = {
            "NombreAsignadoDocumento": doc_expediente.nombre_asignado_documento,
            "IdentificacionDocEnExpediente": doc_expediente.identificacion_doc_en_expediente
        }
        
        id_expediente_documental = doc_expediente.id_expediente_documental.id_expediente_documental
        orden_en_expediente = doc_expediente.orden_en_expediente
        
        if not doc_expediente.es_un_archivo_anexo:
            docs_expedientes_anexos = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=doc_expediente.id_expediente_documental, es_un_archivo_anexo=True)
            cont = 1
            for doc_expediente_anexo in docs_expedientes_anexos:
                descripcion['NombreAsignadoDocumentoAnexo'+str(cont)] = doc_expediente_anexo.nombre_asignado_documento
                if doc_expediente_anexo.id_archivo_sistema:
                    doc_expediente_anexo.id_archivo_sistema.delete()
                cont += 1
            
            docs_expedientes_anexos.delete()
        
        doc_expediente.id_archivo_sistema.delete()
        doc_expediente.delete()
        
        docs_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=id_expediente_documental)
        if not docs_expediente:
            doc_indice_elect = IndicesElectronicosExp.objects.filter(id_expediente_doc=id_expediente_documental).first()
            if doc_indice_elect:
                doc_indice_elect.delete()
        else:
            indice_electronico = IndicesElectronicosExp.objects.filter(id_expediente_doc=id_expediente_documental).first()
            index_doc_previous = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico, id_doc_archivo_exp__orden_en_expediente__lt=orden_en_expediente).order_by('id_doc_archivo_exp__orden_en_expediente').last()
            
            index_doc_next = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=indice_electronico, id_doc_archivo_exp__orden_en_expediente__gt=orden_en_expediente).order_by('id_doc_archivo_exp__orden_en_expediente')
            if index_doc_next:
                pagina_fin_previous = index_doc_previous.pagina_fin
                for index_doc_after in index_doc_next:
                    # Calcular la página de inicio
                    pagina_inicio_next = pagina_fin_previous + 1

                    # Calcular la página final
                    nro_folios_del_doc = index_doc_after.id_doc_archivo_exp.nro_folios_del_doc
                    pagina_fin_previous = pagina_inicio_next + nro_folios_del_doc - 1
                    
                    index_doc_after.pagina_inicio = pagina_inicio_next
                    index_doc_after.pagina_fin = pagina_fin_previous
                    index_doc_after.save()
        
        # AUDITORIA
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 161,
            "cod_permiso": "BO",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Borrado de documento realizado correctamente'}, status=status.HTTP_201_CREATED)

########################## CRUD DE CIERRE DE EXPEDIENTES DOCUMENTALES ##########################

#BUSCAR UN EXPEDIENTE
class ExpedientesSearchAll(generics.ListAPIView):
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
        id_trd_origen = self.request.query_params.get('id_trd_origen', '')
        id_persona_titular_exp_complejo = self.request.query_params.get('id_persona_titular_exp_complejo')



        # Filtrar por atributos específicos referentes a un expediente (unión de parámetros)
        queryset = ExpedientesDocumentales.objects.all()  # Filtrar por estado 'A'
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

        if id_persona_titular_exp_complejo:
            queryset = queryset.filter(id_persona_titular_exp_complejo=id_persona_titular_exp_complejo)
        
        if id_trd_origen and id_trd_origen != '':
            queryset = queryset.filter(id_trd_origen=id_trd_origen)
            
        if palabras_clave_expediente:
            search_vector = SearchVector('palabras_clave_expediente')
            search_query = SearchQuery(palabras_clave_expediente)
            queryset = queryset.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gt=0)

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
        
class InformacionIndiceGetView(generics.ListAPIView):
    serializer_class = InformacionIndiceGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_expediente_doc):
        indice_electronico_exp = IndicesElectronicosExp.objects.filter(id_expediente_doc=id_expediente_doc).first()
        if not indice_electronico_exp:
            raise NotFound('No se encontró el indice electrónico al expediente elegido')
        
        serializer = self.serializer_class(indice_electronico_exp)
        return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class EnvioCodigoView(generics.CreateAPIView):
    serializer_class = EnvioCodigoSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_indice_electronico_exp):
        persona = request.user.persona
        
        indice_electronico_exp = IndicesElectronicosExp.objects.filter(id_indice_electronico_exp=id_indice_electronico_exp).first()
        if not indice_electronico_exp:
            raise NotFound('No se encontró el indice del expediente ingresado')
        
        if not indice_electronico_exp.abierto:
            raise PermissionDenied('No puede realizar esta acción para un indice que ya se encuentra cerrado')
        
        verification_code = secrets.randbelow(10**6)
        verification_code_str = f'{verification_code:06}'
        
        # GUARDAR O ACTUALIZAR REGISTRO EN T270
        doble_verificacion = DobleVerificacionTmp.objects.filter(id_expediente=indice_electronico_exp.id_expediente_doc, id_persona_firma=persona.id_persona).first()
        
        if doble_verificacion:
            segundos = (datetime.now() - doble_verificacion.fecha_hora_codigo).total_seconds()
            if segundos < 60:
                raise ValidationError('Debe esperar un minuto antes de solicitar otro código')
            doble_verificacion.codigo_generado = verification_code_str
            doble_verificacion.fecha_hora_codigo = datetime.now()
            doble_verificacion.save()
        else:
            DobleVerificacionTmp.objects.create(
                id_persona_firma=persona,
                id_expediente=indice_electronico_exp.id_expediente_doc,
                codigo_generado=verification_code_str,
                fecha_hora_codigo=datetime.now()
            )
        
        # ENVIAR SMS Y/O EMAIL
        
        if persona.telefono_celular:
            sms = f'Ingrese el siguiente código para continuar con el cierre del índice electrónico: {verification_code_str}'
            Util.send_sms(persona.telefono_celular, sms)
        
        if persona.email:
            subject = "Código de Verificación - "
            template = "codigo-cierre-indice.html"
            Util.notificacion(persona,subject,template,nombre_de_usuario=request.user.nombre_de_usuario,verification_code_str=verification_code_str)
        
        # serializer = self.serializer_class(indice_electronico_exp)
        return Response({'success':True, 'detail':'Se ha realizado el envío del código de verificación'}, status=status.HTTP_200_OK)
    
class ValidacionCodigoView(generics.UpdateAPIView):
    serializer_class = EnvioCodigoSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request):
        id_indice_electronico_exp = request.data.get('id_indice_electronico_exp')
        codigo = request.data.get('codigo')
        
        if not id_indice_electronico_exp or not codigo:
            raise ValidationError('Debe enviar el indice del expediente y el código')
        
        persona = request.user.persona
        current_time = datetime.now()
        
        indice_electronico_exp = IndicesElectronicosExp.objects.filter(id_indice_electronico_exp=id_indice_electronico_exp).first()
        if not indice_electronico_exp:
            raise NotFound('No se encontró el indice del expediente ingresado')
        
        if not indice_electronico_exp.abierto:
            raise PermissionDenied('No puede realizar esta acción para un indice que ya se encuentra cerrado')
        
        doble_verificacion = DobleVerificacionTmp.objects.filter(id_expediente=indice_electronico_exp.id_expediente_doc, id_persona_firma=persona.id_persona).first()
        if not doble_verificacion:
            raise ValidationError('No se encuentra un código para el índice ingresado')
        
        minutos = (current_time - doble_verificacion.fecha_hora_codigo).total_seconds() / 60.0
        if minutos > 15:
            raise ValidationError('El código ingresado ha expirado')
        else:
            if doble_verificacion.codigo_generado != codigo:
                raise ValidationError('El código es inválido. Intente nuevamente')
        
        return Response({'success':True, 'detail':'El código es válido'}, status=status.HTTP_200_OK)

class FirmaCierreView(generics.UpdateAPIView):
    serializer_class = EnvioCodigoSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request):
        id_indice_electronico_exp = request.data.get('id_indice_electronico_exp')
        observacion = request.data.get('observacion', '')
        
        if not id_indice_electronico_exp or observacion == '':
            raise ValidationError('Debe enviar el indice del expediente y la observación')
        
        persona = request.user.persona
        current_time = datetime.now()
        
        indice_electronico_exp = IndicesElectronicosExp.objects.filter(id_indice_electronico_exp=id_indice_electronico_exp).first()
        if not indice_electronico_exp:
            raise NotFound('No se encontró el indice del expediente ingresado')
        
        if not indice_electronico_exp.abierto:
            raise PermissionDenied('No puede realizar esta acción para un indice que ya se encuentra cerrado')
        
        doble_verificacion = DobleVerificacionTmp.objects.filter(id_expediente=indice_electronico_exp.id_expediente_doc, id_persona_firma=persona.id_persona).first()
        if not doble_verificacion:
            raise ValidationError('No se ha generado aún código de verificación para el índice ingresado')
        
        # ACTUALIZAR EN T239
        previous_indice_electronico_exp = copy.copy(indice_electronico_exp)
        
        indice_electronico_exp.abierto = False
        indice_electronico_exp.fecha_cierre = current_time
        indice_electronico_exp.id_persona_firma_cierre = persona
        indice_electronico_exp.fecha_envio_cod_verificacion = doble_verificacion.fecha_hora_codigo
        indice_electronico_exp.email_envio_cod_verificacion = doble_verificacion.id_persona_firma.email
        indice_electronico_exp.nro_cel_envio_cod_verificacion = doble_verificacion.id_persona_firma.telefono_celular
        indice_electronico_exp.fecha_intro_cod_verificacion_ok = current_time
        indice_electronico_exp.observacion_firme_cierre = observacion
        indice_electronico_exp.save()
        
        # ACTUALIZAR EN T236
        indice_electronico_exp.id_expediente_doc.fecha_firma_cierre_indice_elec = current_time
        indice_electronico_exp.id_expediente_doc.save()
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "IdExpedienteDoc": str(indice_electronico_exp.id_expediente_doc.id_expediente_documental)
        }
        direccion = Util.get_client_ip(request)
        valores_actualizados = {'previous': previous_indice_electronico_exp, 'current':indice_electronico_exp}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 150,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Se realizó la firma correcta del cierre del índice electrónico'}, status=status.HTTP_200_OK)
    
class FirmaCierreGetView(generics.ListAPIView):
    serializer_class = FirmaCierreGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_indice_electronico_exp):
        indice_electronico_exp = IndicesElectronicosExp.objects.filter(id_indice_electronico_exp=id_indice_electronico_exp).first()
        if not indice_electronico_exp:
            raise NotFound('No se encontró el indice del expediente ingresado')
        
        serializer = self.serializer_class(indice_electronico_exp)
        
        return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializer.data}, status=status.HTTP_200_OK)
    

#REUBICACION_FISICA_EXPEDIENTE
class ExpedienteSearchConUbicacionDesactualizada(generics.ListAPIView):
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
        id_persona_titular_exp_complejo = self.request.query_params.get('id_persona_titular_exp_complejo')
        ubicacion_desactualizada = self.request.query_params.get('ubicacion_desactualizada', '').strip()

        queryset = ExpedientesDocumentales.objects.all() 

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

        if id_persona_titular_exp_complejo:
            queryset = queryset.filter(id_persona_titular_exp_complejo=id_persona_titular_exp_complejo)

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
            
            queryset = queries[0]
            for query in queries[1:]:
                queryset = queryset | query

        if palabras_clave_expediente:
            search_vector = SearchVector('palabras_clave_expediente')
            search_query = SearchQuery(palabras_clave_expediente)
            queryset = queryset.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gt=0)

         # Nuevo filtro para expedientes con ubicación física desactualizada
        if ubicacion_desactualizada.lower() in ['true', 'false']:
            ubicacion_desactualizada_bool = ubicacion_desactualizada.lower() == 'true'
            queryset = queryset.filter(ubicacion_fisica_esta_actualizada=ubicacion_desactualizada_bool)

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
    

class ReubicacionFisicaExpedienteGet(generics.ListAPIView):
    serializer_class = ReubicacionFisicaExpedienteSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_expediente_documental):
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente_documental).first()
        
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        serializer = self.serializer_class(expediente)
        
        return Response({'success':True, 'detail':'Se encontró el siguiente expediente', 'data':serializer.data}, status=status.HTTP_200_OK)
    


class ExpedienteCarpetaAgregarEliminar(generics.UpdateAPIView):
    lookup_field = 'id_expediente_documental'
    queryset = ExpedientesDocumentales.objects.all()
    serializer_class = ExpedientesDocumentalesGetSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # Obtener el ID del expediente desde los parámetros de la URL
        id_expediente_documental = self.kwargs.get(self.lookup_field)

        try:
            # Intentar obtener el expediente
            expediente = ExpedientesDocumentales.objects.get(id_expediente_documental=id_expediente_documental)
        except ExpedientesDocumentales.DoesNotExist:
            # Si no se encuentra el expediente, devolver una respuesta de error
            raise NotFound('No se encontró el expediente ingresado')
        except ValidationError as e:
            # Si ocurre una ValidationError, devolver una respuesta de error
            ValidationError({"error": str(e)})

        carpetas_nuevas_ids = request.data.get('carpetas_cajas_agregar', [])
        carpetas_eliminar_ids = request.data.get('carpetas_cajas_eliminar', [])
        
        # Eliminar la asociación del expediente con las carpetas a eliminar
        carpetas_eliminar = CarpetaCaja.objects.filter(id_carpeta_caja__in=carpetas_eliminar_ids)
        carpetas_eliminadas = []

        for carpeta_eliminar in carpetas_eliminar:
            carpeta_eliminar.id_expediente = None
            carpeta_eliminar.save()
            carpetas_eliminadas.append(carpeta_eliminar)

        # Asociar el expediente con las nuevas carpetas
        carpetas_actualizadas = []

        for carpeta_id in carpetas_nuevas_ids:
            try:
                carpeta_nueva = CarpetaCaja.objects.get(id_carpeta_caja=carpeta_id)
                carpeta_nueva.id_expediente = expediente
                carpeta_nueva.save()
                carpetas_actualizadas.append(carpeta_nueva)
            except CarpetaCaja.DoesNotExist:
                return Response({"error": f"Carpeta con ID {carpeta_id} no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar atributos en el expediente
        expediente_actualizado = False

        if not expediente.ubicacion_fisica_esta_actualizada:
            expediente.ubicacion_fisica_esta_actualizada = True
            expediente_actualizado = True

        if not expediente.tiene_carpeta_fisica:
            expediente.tiene_carpeta_fisica = True
            expediente_actualizado = True

        if expediente_actualizado:
            expediente.save()

        # Construir manualmente la respuesta
        carpetas_agregadas_serializer = CarpetaCajaGetOrdenSerializer(carpetas_actualizadas, many=True)
        carpetas_agregadas_data = carpetas_agregadas_serializer.data

        carpetas_eliminadas_serializer = CarpetaCajaGetOrdenSerializer(carpetas_eliminadas, many=True)
        carpetas_eliminadas_data = carpetas_eliminadas_serializer.data

        return Response({
            'success': True,
            'detail': 'Se actualizaron los siguientes registros.',
            "carpetas_agregadas": carpetas_agregadas_data,
            "carpetas_eliminadas": carpetas_eliminadas_data,
        })

class ConcesionAccesoPermisoGetView(generics.ListAPIView):
    serializer_class = FirmaCierreGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_expediente):
        id_unidad_organizacional_actual = request.user.persona.id_unidad_organizacional_actual
        if not id_unidad_organizacional_actual:
            raise NotFound('La persona logueada no se encuentra vinculada como colaborador')
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        id_cat_serie_und = expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_cat_serie_und
        
        permiso_und_ord_ccd = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, id_und_organizacional_actual=id_unidad_organizacional_actual.id_unidad_organizacional, conceder_acceso_expedientes_no_propios=True).first()
        if not permiso_und_ord_ccd:
            raise PermissionDenied('No tiene permiso para acceder a este módulo')
        
        if expediente.id_und_org_oficina_respon_actual.id_unidad_organizacional == id_unidad_organizacional_actual.id_unidad_organizacional:
            if permiso_und_ord_ccd.denegar_conceder_acceso_exp_na_resp_series:
                raise PermissionDenied('No tiene permiso para acceder a este módulo')
        
        return Response({'success':True, 'detail':'Se encontró el permiso para acceder a este módulo'}, status=status.HTTP_200_OK)

class ConcesionAccesoPersonasDocumentoView(generics.ListAPIView):
    serializer_class = ConcesionAccesoPersonasFilterSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter = {}
        numero_documento = request.query_params.get('numero_documento')
        tipo_documento = request.query_params.get('tipo_documento')
        
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        if not organigrama_actual:
            raise ValidationError('No existe organigrama actual en el sistema')
        
        if not numero_documento or not tipo_documento:
            raise PermissionDenied('Debe de seleccionar el tipo de documento y digitar el número de documento')

        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento']:
                filter[key]=value
        
        persona = Personas.objects.filter(**filter).filter(~Q(id_cargo=None) and ~Q(id_unidad_organizacional_actual=None) and Q(es_unidad_organizacional_actual=True)).filter(id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama)

        if persona: 
            serializador = self.serializer_class(persona,many=True)
            return Response ({'success':True,'detail':'Se encontraron personas: ','data':serializador.data},status=status.HTTP_200_OK) 
        
        else:
            return Response ({'success':True,'detail':'No existe la persona, o no está en una unidad organizacional actual','data':[]},status=status.HTTP_200_OK) 

class ConcesionAccesoPersonasFiltroView(generics.ListAPIView):
    serializer_class = ConcesionAccesoPersonasFilterSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter={}
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        if not organigrama_actual:
            raise ValidationError('No existe organigrama actual en el sistema')
        
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido','id_unidad_organizacional_actual']:
                if key == 'numero_documento':
                    if value != '':
                        filter[key+'__icontains']=value
                elif key == 'tipo_documento':
                    if value != '':
                        filter[key]=value
                elif key == 'id_unidad_organizacional_actual':
                    if value != '':
                        filter[key]=value
                else:
                    if value != '':
                        filter[key+'__icontains']=value
                
        personas = Personas.objects.filter(**filter).filter(~Q(id_cargo=None) & ~Q(id_unidad_organizacional_actual=None) & Q(es_unidad_organizacional_actual=True)).filter(id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama)

        if personas:
            serializador = self.serializer_class(personas, many=True)
            return Response ({'success':True,'detail':'Se encontraron personas: ','data':serializador.data},status=status.HTTP_200_OK) 
        
        else:
            return Response ({'success':True,'detail':'No se encontraron personas','data':[]},status=status.HTTP_200_OK) 

class ConcesionAccesoExpedientesCreateView(generics.CreateAPIView):
    serializer_class = ConcesionAccesoExpedientesCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_expediente):
        data = request.data
        persona_logueada = request.user.persona.id_persona
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        configuracion_tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=8).first()
        nro_max_dias = configuracion_tiempo_respuesta.tiempo_respuesta_en_dias
        if not nro_max_dias:
            raise ValidationError('Se debe configurar primero el Tiempo máximo de Concesión de Acceso a Expedientes y Documentos en el módulo de Configuración de Tiempos de Respuesta y Plazos de Acción')
        
        for item in data:
            item['id_persona_concede_acceso'] = persona_logueada
            item['id_expediente'] = id_expediente
            
            fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
            fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
            
            if fecha_acceso_inicia > fecha_acceso_termina:
                raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
            
            if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
        
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        instancias_creadas = serializer.save()
        
        valores_creados_detalles = []
        for item in instancias_creadas:
            descripcion = {
                'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
                'NombreRecibeAcceso': f'{str(item.id_persona_recibe_acceso.primer_nombre)} {str(item.id_persona_recibe_acceso.primer_apellido)}',
                'IDExpediente': id_expediente
            }
            valores_creados_detalles.append(descripcion)
        
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = {
            'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
            'IDExpediente': id_expediente
        }
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 170,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'success':True, 'detail':'Se concedió acceso correctamente a las personas elegidas', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class ConcesionAccesoExpedientesUpdateView(generics.UpdateAPIView):
    serializer_class = ConcesionAccesoUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def delete_concesiones(self, list_eliminar):
        concesiones_eliminar = ConcesionesAccesoAExpsYDocs.objects.filter(id_concesion_acc__in=list_eliminar).annotate(
            NombreDaAcceso=Concat('id_persona_concede_acceso__primer_nombre', V(' '), 'id_persona_concede_acceso__primer_apellido'),
            NombreRecibeAcceso=Concat('id_persona_recibe_acceso__primer_nombre', V(' '), 'id_persona_recibe_acceso__primer_apellido')
        )
        description_eliminar = concesiones_eliminar.values(
            'NombreDaAcceso',
            'NombreRecibeAcceso',
            IDExpediente=F('id_expediente')
        )
        description_eliminar = list(description_eliminar)
        concesiones_eliminar.delete()
        
        return description_eliminar
    
    def create_concesiones(self, data, id_expediente, persona_logueada, nro_max_dias):
        for item in data:
            item['id_persona_concede_acceso'] = persona_logueada
            item['id_expediente'] = id_expediente
            
            fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
            fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
            
            if fecha_acceso_inicia > fecha_acceso_termina:
                raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
            
            if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
        
        serializer = ConcesionAccesoExpedientesCreateSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        instancias_creadas = serializer.save()
        
        description_creados = []
        for item in instancias_creadas:
            descripcion = {
                'NombreDaAcceso': f'{str(item.id_persona_concede_acceso.primer_nombre)} {str(item.id_persona_concede_acceso.primer_apellido)}',
                'NombreRecibeAcceso': f'{str(item.id_persona_recibe_acceso.primer_nombre)} {str(item.id_persona_recibe_acceso.primer_apellido)}',
                'IDExpediente': id_expediente
            }
            description_creados.append(descripcion)
        
        return description_creados
    
    def update(self, request, id_expediente):
        data_concesiones_propias = request.data.get('concesiones_propias')
        data_concesiones_otros = request.data.get('concesiones_otros')
        persona_logueada = request.user.persona.id_persona
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
        if not expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        configuracion_tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=8).first()
        nro_max_dias = configuracion_tiempo_respuesta.tiempo_respuesta_en_dias
        if not nro_max_dias:
            raise ValidationError('Se debe configurar primero el Tiempo máximo de Concesión de Acceso a Expedientes y Documentos en el módulo de Configuración de Tiempos de Respuesta y Plazos de Acción')
        
        concesiones_actuales = ConcesionesAccesoAExpsYDocs.objects.filter(id_expediente=id_expediente, id_persona_concede_acceso=persona_logueada)
        
        concesiones_crear = [concesion for concesion in data_concesiones_propias if not concesion['id_concesion_acc']]
        concesiones_actualizar = [concesion for concesion in data_concesiones_propias if concesion['id_concesion_acc']]
        concesiones_eliminar = concesiones_actuales.exclude(id_concesion_acc__in=[concesion['id_concesion_acc'] for concesion in concesiones_actualizar]).values_list('id_concesion_acc', flat=True)
        concesiones_eliminar = list(concesiones_eliminar) + data_concesiones_otros if data_concesiones_otros else list(concesiones_eliminar)
        
        valores_eliminados_detalles = self.delete_concesiones(concesiones_eliminar)
        valores_creados_detalles = self.create_concesiones(concesiones_crear, id_expediente, persona_logueada, nro_max_dias)
        valores_actualizados_detalles = []
        
        for item in concesiones_actualizar:
            instancia = concesiones_actuales.filter(id_concesion_acc=item['id_concesion_acc']).first()
            if instancia:
                previous_instancia = copy.copy(instancia)
                
                fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
                fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
                
                if fecha_acceso_inicia > fecha_acceso_termina:
                    raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
                
                if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                    raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
                
                serializer = self.serializer_class(instancia, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                descripcion_update = {
                    'NombreDaAcceso': f'{str(instancia.id_persona_concede_acceso.primer_nombre)} {str(instancia.id_persona_concede_acceso.primer_apellido)}',
                    'NombreRecibeAcceso': f'{str(instancia.id_persona_recibe_acceso.primer_nombre)} {str(instancia.id_persona_recibe_acceso.primer_apellido)}',
                    'IDExpediente': id_expediente
                }
                
                valores_actualizados_detalles.append({'descripcion':descripcion_update, 'previous':previous_instancia, 'current':instancia})
        
        # AUDITORIAS
        direccion = Util.get_client_ip(request)
        descripcion = {
            'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
            'IDExpediente': id_expediente
        }
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 170,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        # SERIALIZER DESPUÉS DE CAMBIOS
        concesiones_actuales = ConcesionesAccesoAExpsYDocs.objects.filter(id_expediente=id_expediente, id_persona_concede_acceso=persona_logueada)
        serializer_actuales = ConcesionAccesoExpedientesGetSerializer(concesiones_actuales, many=True)
        
        return Response({'success':True, 'detail':'Se ha realizado las modificaciones correctamente', 'data':serializer_actuales.data}, status=status.HTTP_201_CREATED)

class ConcesionAccesoDocumentosCreateView(generics.CreateAPIView):
    serializer_class = ConcesionAccesoDocumentosCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, id_documento_de_archivo_exped):
        data = request.data
        persona_logueada = request.user.persona.id_persona
        
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        configuracion_tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=8).first()
        nro_max_dias = configuracion_tiempo_respuesta.tiempo_respuesta_en_dias
        if not nro_max_dias:
            raise ValidationError('Se debe configurar primero el Tiempo máximo de Concesión de Acceso a Expedientes y Documentos en el módulo de Configuración de Tiempos de Respuesta y Plazos de Acción')
        
        for item in data:
            item['id_persona_concede_acceso'] = persona_logueada
            item['id_documento_exp'] = id_documento_de_archivo_exped
            
            fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
            fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
            
            if fecha_acceso_inicia > fecha_acceso_termina:
                raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
            
            if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
        
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        instancias_creadas = serializer.save()
        
        valores_creados_detalles = []
        for item in instancias_creadas:
            descripcion = {
                'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
                'NombreRecibeAcceso': f'{str(item.id_persona_recibe_acceso.primer_nombre)} {str(item.id_persona_recibe_acceso.primer_apellido)}',
                'IDDocumentoExp': id_documento_de_archivo_exped
            }
            valores_creados_detalles.append(descripcion)
        
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = {
            'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
            'IDDocumentoExp': id_documento_de_archivo_exped
        }
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 170,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'success':True, 'detail':'Se concedió acceso correctamente a las personas elegidas', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class ConcesionAccesoDocumentosUpdateView(generics.UpdateAPIView):
    serializer_class = ConcesionAccesoUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def delete_concesiones(self, list_eliminar):
        concesiones_eliminar = ConcesionesAccesoAExpsYDocs.objects.filter(id_concesion_acc__in=list_eliminar).annotate(
            NombreDaAcceso=Concat('id_persona_concede_acceso__primer_nombre', V(' '), 'id_persona_concede_acceso__primer_apellido'),
            NombreRecibeAcceso=Concat('id_persona_recibe_acceso__primer_nombre', V(' '), 'id_persona_recibe_acceso__primer_apellido')
        )
        description_eliminar = concesiones_eliminar.values(
            'NombreDaAcceso',
            'NombreRecibeAcceso',
            IDDocumentoExp=F('id_documento_exp')
        )
        description_eliminar = list(description_eliminar)
        concesiones_eliminar.delete()
        
        return description_eliminar
    
    def create_concesiones(self, data, id_documento_de_archivo_exped, persona_logueada, nro_max_dias):
        for item in data:
            item['id_persona_concede_acceso'] = persona_logueada
            item['id_documento_exp'] = id_documento_de_archivo_exped
            
            fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
            fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
            
            if fecha_acceso_inicia > fecha_acceso_termina:
                raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
            
            if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
        
        serializer = ConcesionAccesoDocumentosCreateSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        instancias_creadas = serializer.save()
        
        description_creados = []
        for item in instancias_creadas:
            descripcion = {
                'NombreDaAcceso': f'{str(item.id_persona_concede_acceso.primer_nombre)} {str(item.id_persona_concede_acceso.primer_apellido)}',
                'NombreRecibeAcceso': f'{str(item.id_persona_recibe_acceso.primer_nombre)} {str(item.id_persona_recibe_acceso.primer_apellido)}',
                'IDDocumentoExp': id_documento_de_archivo_exped
            }
            description_creados.append(descripcion)
        
        return description_creados
    
    def update(self, request, id_documento_de_archivo_exped):
        data_concesiones_propias = request.data.get('concesiones_propias')
        data_concesiones_otros = request.data.get('concesiones_otros')
        persona_logueada = request.user.persona.id_persona
        
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        if not doc_expediente:
            raise NotFound('No se encontró el expediente ingresado')
        
        configuracion_tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=8).first()
        nro_max_dias = configuracion_tiempo_respuesta.tiempo_respuesta_en_dias
        if not nro_max_dias:
            raise ValidationError('Se debe configurar primero el Tiempo máximo de Concesión de Acceso a Expedientes y Documentos en el módulo de Configuración de Tiempos de Respuesta y Plazos de Acción')
        
        concesiones_actuales = ConcesionesAccesoAExpsYDocs.objects.filter(id_documento_exp=id_documento_de_archivo_exped, id_persona_concede_acceso=persona_logueada)
        
        concesiones_crear = [concesion for concesion in data_concesiones_propias if not concesion['id_concesion_acc']]
        concesiones_actualizar = [concesion for concesion in data_concesiones_propias if concesion['id_concesion_acc']]
        concesiones_eliminar = concesiones_actuales.exclude(id_concesion_acc__in=[concesion['id_concesion_acc'] for concesion in concesiones_actualizar]).values_list('id_concesion_acc', flat=True)
        concesiones_eliminar = list(concesiones_eliminar) + data_concesiones_otros if data_concesiones_otros else list(concesiones_eliminar)
        
        valores_eliminados_detalles = self.delete_concesiones(concesiones_eliminar)
        valores_creados_detalles = self.create_concesiones(concesiones_crear, id_documento_de_archivo_exped, persona_logueada, nro_max_dias)
        valores_actualizados_detalles = []
        
        for item in concesiones_actualizar:
            instancia = concesiones_actuales.filter(id_concesion_acc=item['id_concesion_acc']).first()
            if instancia:
                previous_instancia = copy.copy(instancia)
                
                fecha_acceso_inicia = datetime.strptime(item['fecha_acceso_inicia'], '%Y-%m-%d')
                fecha_acceso_termina = datetime.strptime(item['fecha_acceso_termina'], '%Y-%m-%d')
                
                if fecha_acceso_inicia > fecha_acceso_termina:
                    raise ValidationError('La fecha desde de la concesión no puede ser mayor a la fecha hasta')
                
                if (fecha_acceso_termina - fecha_acceso_inicia).days > nro_max_dias:
                    raise ValidationError(f'El número de días entre ambas fechas elegidas no puede superar el Tiempo máximo de Concesión de Acceso a Expedientes ya configurado ({str(nro_max_dias)})')
            
                serializer = self.serializer_class(instancia, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                descripcion_update = {
                    'NombreDaAcceso': f'{str(instancia.id_persona_concede_acceso.primer_nombre)} {str(instancia.id_persona_concede_acceso.primer_apellido)}',
                    'NombreRecibeAcceso': f'{str(instancia.id_persona_recibe_acceso.primer_nombre)} {str(instancia.id_persona_recibe_acceso.primer_apellido)}',
                    'IDDocumentoExp': id_documento_de_archivo_exped
                }
                
                valores_actualizados_detalles.append({'descripcion': descripcion_update, 'previous':previous_instancia, 'current':instancia})
        
        # AUDITORIAS
        direccion = Util.get_client_ip(request)
        descripcion = {
            'NombreDaAcceso': f'{str(request.user.persona.primer_nombre)} {str(request.user.persona.primer_apellido)}',
            'IDDocumentoExp': id_documento_de_archivo_exped
        }
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 170,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        # SERIALIZER DESPUÉS DE CAMBIOS
        concesiones_actuales = ConcesionesAccesoAExpsYDocs.objects.filter(id_documento_exp=id_documento_de_archivo_exped, id_persona_concede_acceso=persona_logueada)
        serializer_actuales = ConcesionAccesoDocumentosGetSerializer(concesiones_actuales, many=True)
        
        return Response({'success':True, 'detail':'Se ha realizado las modificaciones correctamente', 'data':serializer_actuales.data}, status=status.HTTP_201_CREATED)

class ConcesionAccesoExpedientesGetView(generics.ListAPIView):
    serializer_class = ConcesionAccesoExpedientesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_expediente):
        propios = request.query_params.get('propios', '')
        if propios != '':
            propios = True if propios.lower() == 'true' else False
            
        persona_logueada = request.user.persona
            
        concesiones = ConcesionesAccesoAExpsYDocs.objects.filter(id_expediente=id_expediente)
        concesiones = concesiones.filter(id_persona_concede_acceso=persona_logueada.id_persona) if propios else concesiones.exclude(id_persona_concede_acceso=persona_logueada.id_persona)
        if not concesiones:
            raise NotFound('No se han encontrado concesiones de expedientes')
        
        expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
        actual_responsable = True if expediente.id_und_org_oficina_respon_actual.id_unidad_organizacional == persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional else False
        
        serializer = self.serializer_class(concesiones, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes concesiones realizadas', 'actual_responsable':actual_responsable, 'data': serializer.data}, status=status.HTTP_200_OK)
    
class ConcesionAccesoDocumentosGetView(generics.ListAPIView):
    serializer_class = ConcesionAccesoDocumentosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_documento_de_archivo_exped):
        propios = request.query_params.get('propios', '')
        if propios != '':
            propios = True if propios.lower() == 'true' else False
            
        persona_logueada = request.user.persona
            
        concesiones = ConcesionesAccesoAExpsYDocs.objects.filter(id_documento_exp=id_documento_de_archivo_exped)
        concesiones = concesiones.filter(id_persona_concede_acceso=persona_logueada.id_persona) if propios else concesiones.exclude(id_persona_concede_acceso=persona_logueada.id_persona)
        if not concesiones:
            raise NotFound('No se han encontrado concesiones de documentos de expedientes')
        
        doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_documento_de_archivo_exped=id_documento_de_archivo_exped).first()
        actual_responsable = True if doc_expediente.id_expediente_documental.id_und_org_oficina_respon_actual.id_unidad_organizacional == persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional else False
        
        serializer = self.serializer_class(concesiones, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes concesiones realizadas', 'actual_responsable':actual_responsable, 'data': serializer.data}, status=status.HTTP_200_OK)

class ConcesionAccesoExpedientesUserGetView(generics.ListAPIView):
    serializer_class = ConcesionAccesoExpedientesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        persona_logueada = request.user.persona
            
        concesiones = ConcesionesAccesoAExpsYDocs.objects.filter(id_persona_recibe_acceso=persona_logueada)
        if not concesiones:
            raise NotFound('No se han encontrado concesiones de expedientes')
        
        serializer = self.serializer_class(concesiones, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes concesiones', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class ConcesionAccesoDocumentosUserGetView(generics.ListAPIView):
    serializer_class = ConcesionAccesoDocumentosGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        persona_logueada = request.user.persona.id_persona
            
        concesiones = ConcesionesAccesoAExpsYDocs.objects.filter(id_persona_recibe_acceso=persona_logueada)
        if not concesiones:
            raise NotFound('No se han encontrado concesiones de documentos de expedientes')
        
        serializer = self.serializer_class(concesiones, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes concesiones', 'data': serializer.data}, status=status.HTTP_200_OK)