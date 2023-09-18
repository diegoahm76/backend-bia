from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, F
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Cast
from django.db.models import BigIntegerField
from gestion_documental.serializers.ccd_serializers import (
    CCDPostSerializer,
    CCDPutSerializer,
    CCDActivarSerializer,
    CCDSerializer,
    CatalogoSerieSubserieSerializer,
    SeriesDocPostSerializer,
    SeriesDocPutSerializer,
    SubseriesDocPostSerializer,
    SubseriesDocPutSerializer,
    CatalogosSeriesUnidadSerializer,
    AsignacionesCatalogosOrgSerializer,
    BusquedaCCDSerializer
)
from transversal.models.organigrama_models import Organigramas
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)

import copy

from transversal.serializers.organigrama_serializers import UnidadesGetSerializer

class BusquedaCCDPermisosGetView(generics.ListAPIView):
    serializer_class = BusquedaCCDSerializer 
    queryset = CuadrosClasificacionDocumental.objects.filter(Q(actual=True) | (Q(actual=False) & ~Q(fecha_retiro_produccion=None)))
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
        
        ccd = self.queryset.filter(**filter).order_by('fecha_terminado')
        serializador = self.serializer_class(ccd, many=True, context = {'request':request})
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class UnidadesCCDGetView(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer 
    queryset = UnidadesOrganizacionales.objects.filter()
    permission_classes = [IsAuthenticated]

    def get (self, request, id_organigrama):
        nombre = request.query_params.get('nombre', '')
        unidades_org = self.queryset.filter(nombre__icontains=nombre, id_organigrama=id_organigrama, activo=True).exclude(cod_agrupacion_documental=None)
        serializador = self.serializer_class(unidades_org, many=True)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class SerieSubserieUnidadCCDGetView(generics.ListAPIView):
    serializer_class = SerieSubserieUnidadCCDGetSerializer 
    queryset = CatalogosSeriesUnidad.objects.filter()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        id_ccd = request.query_params.get('id_ccd', '')
        id_unidad_organizacional = request.query_params.get('id_unidad_organizacional', '')
        
        if id_ccd == '' or id_unidad_organizacional == '':
            raise ValidationError('Debe enviar el CCD y la Unidad Organizacional seleccionada')
        
        catalogos_serie_unidad = self.queryset.filter(id_catalogo_serie__id_serie_doc__id_ccd=id_ccd, id_unidad_organizacional=id_unidad_organizacional)
        serializador = self.serializer_class(catalogos_serie_unidad, many=True)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)

class UnidadesPermisosGetView(generics.ListAPIView):
    serializer_class = PermisosGetSerializer 
    queryset = UnidadesOrganizacionales.objects.filter()
    permission_classes = [IsAuthenticated]
    
    def get_family(self, unidades_hijas):
        unidades_family = []
        for unidad in unidades_hijas:
            hijas = self.queryset.filter(id_unidad_org_padre=unidad['id_und_organizacional_actual']).values(
                'activo',
                'cod_agrupacion_documental',
                id_und_organizacional_actual = F('id_unidad_organizacional'),
                nombre_und_organizacional_actual = F('nombre'),
                codigo_und_organizacional_actual = F('codigo')
            )
            if hijas:
                unidades_family = unidades_family + list(hijas)
                unidades_inner = self.get_family(hijas)
                unidades_family = unidades_family + unidades_inner
        return unidades_family

    def get(self, request, id_cat_serie_und):
        cat_serie_und = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=id_cat_serie_und).first()
        if not cat_serie_und:
            raise NotFound('El registro del Catalogo Serie Subserie Unidad ingresado no existe')
        
        id_unidad_org_actual_admin_series = cat_serie_und.id_unidad_organizacional.id_unidad_org_actual_admin_series
        unidades_permisos = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, pertenece_seccion_actual_admin_serie=True)
        
        # OBTENER UNIDAD ADMIN Y FAMILIA
        unidades_data = [
            {
                'activo':id_unidad_org_actual_admin_series.activo,
                'cod_agrupacion_documental':id_unidad_org_actual_admin_series.cod_agrupacion_documental,
                'id_und_organizacional_actual':id_unidad_org_actual_admin_series.id_unidad_organizacional,
                'nombre_und_organizacional_actual':id_unidad_org_actual_admin_series.nombre,
                'codigo_und_organizacional_actual':id_unidad_org_actual_admin_series.codigo,
            }
        ]
        unidades_org = self.queryset.filter(id_unidad_org_padre=id_unidad_org_actual_admin_series.id_unidad_organizacional).values(
            'activo',
            'cod_agrupacion_documental',
            id_und_organizacional_actual = F('id_unidad_organizacional'),
            nombre_und_organizacional_actual = F('nombre'),
            codigo_und_organizacional_actual = F('codigo')
        )
        unidades_org = [unidad for unidad in unidades_org if unidad['activo'] and not unidad['cod_agrupacion_documental']]
        
        unidades_family = self.get_family(unidades_org)
        unidades_family = [unidad for unidad in unidades_family if unidad['activo'] and not unidad['cod_agrupacion_documental']]
        unidades_family = unidades_data + unidades_org + unidades_family
        
        for unidad in unidades_family:
            unidad['id_permisos_und_org_actual_serie_exp_ccd'] = None
            unidad['id_cat_serie_und_org_ccd'] = id_cat_serie_und
            unidad['pertenece_seccion_actual_admin_serie'] = False
            unidad['crear_expedientes'] = False
            unidad['crear_documentos_exps_no_propios'] = False
            unidad['anular_documentos_exps_no_propios'] = False
            unidad['borrar_documentos_exps_no_propios'] = False
            unidad['conceder_acceso_documentos_exps_no_propios'] = False
            unidad['conceder_acceso_expedientes_no_propios'] = False
            unidad['consultar_expedientes_no_propios'] = False
            unidad['descargar_expedientes_no_propios'] = False
            unidad['mostrar'] = True
        
        data = []
        
        if unidades_permisos:
            serializador = self.serializer_class(unidades_permisos, many=True)
            serializador_data = serializador.data
            
            serializador_data_id = [unidad['id_und_organizacional_actual'] for unidad in serializador_data]
            unidades_propias = [unidad for unidad in unidades_family if unidad['id_und_organizacional_actual'] not in serializador_data_id]
            for unidad in unidades_propias:
                unidad['mostrar'] = False
            
            data = serializador_data + unidades_propias
        else:
            data = unidades_family
            
        # PENDIENTE VALIDACION SI TIENEN PERMISOS
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)

class UnidadesExternasPermisosGetView(generics.ListAPIView):
    serializer_class = PermisosGetSerializer 
    queryset = UnidadesOrganizacionales.objects.filter()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_cat_serie_und):
        cat_serie_und = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=id_cat_serie_und).first()
        if not cat_serie_und:
            raise NotFound('El registro del Catalogo Serie Subserie Unidad ingresado no existe')
        
        id_unidad_org_actual_admin_series = cat_serie_und.id_unidad_organizacional.id_unidad_org_actual_admin_series
        
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        unidades_organigrama_actual = organigrama_actual.unidadesorganizacionales_set.filter(activo=True)
        unidades_permisos_clasificadas = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, pertenece_seccion_actual_admin_serie=False)
        unidades_permisos_clasificadas_list = list(unidades_permisos_clasificadas.values_list('id_und_organizacional_actual', flat=True)) if unidades_permisos_clasificadas else []
        
        unidades_permisos_clasificadas_list.append(id_unidad_org_actual_admin_series.id_unidad_organizacional) 
        
        unidades_org_admin_hijas = self.queryset.filter(id_unidad_org_padre=id_unidad_org_actual_admin_series.id_unidad_organizacional).values(
            'activo',
            'cod_agrupacion_documental',
            id_und_organizacional_actual = F('id_unidad_organizacional'),
            nombre_und_organizacional_actual = F('nombre'),
            codigo_und_organizacional_actual = F('codigo')
        )
        
        unidades_primera_seccion = UnidadesPermisosGetView()
        unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_admin_hijas)
        
        unidades_permisos_clasificadas_list = unidades_permisos_clasificadas_list + [unidad['id_und_organizacional_actual'] for unidad in list(unidades_org_admin_hijas) if unidad['activo'] and not unidad['cod_agrupacion_documental']] + [unidad['id_und_organizacional_actual'] for unidad in unidades_primera_seccion_family if unidad['activo'] and not unidad['cod_agrupacion_documental']]
        
        unidades_organigrama_actual = unidades_organigrama_actual.exclude(id_unidad_organizacional__in=unidades_permisos_clasificadas_list)
        
        # OBTENER UNIDADES
        unidades_organigrama_actual_data = unidades_organigrama_actual.values(
            'activo',
            'cod_agrupacion_documental',
            id_und_organizacional_actual = F('id_unidad_organizacional'),
            nombre_und_organizacional_actual = F('nombre'),
            codigo_und_organizacional_actual = F('codigo')
        )
        
        for unidad in unidades_organigrama_actual_data:
            unidad['id_permisos_und_org_actual_serie_exp_ccd'] = None
            unidad['id_cat_serie_und_org_ccd'] = id_cat_serie_und
            unidad['pertenece_seccion_actual_admin_serie'] = False
            unidad['crear_expedientes'] = False
            unidad['crear_documentos_exps_no_propios'] = False
            unidad['anular_documentos_exps_no_propios'] = False
            unidad['borrar_documentos_exps_no_propios'] = False
            unidad['conceder_acceso_documentos_exps_no_propios'] = False
            unidad['conceder_acceso_expedientes_no_propios'] = False
            unidad['consultar_expedientes_no_propios'] = False
            unidad['descargar_expedientes_no_propios'] = False
            unidad['mostrar'] = True
            
        if unidades_permisos_clasificadas:
            serializador = self.serializer_class(unidades_permisos_clasificadas, many=True)
            serializador_data = serializador.data
            
            serializador_data_id = [unidad['id_und_organizacional_actual'] for unidad in serializador_data]
            unidades_propias = [unidad for unidad in unidades_organigrama_actual_data if unidad['id_und_organizacional_actual'] not in serializador_data_id]
            for unidad in unidades_propias:
                unidad['mostrar'] = False
            
            data = serializador_data + unidades_propias
        else:
            data = unidades_organigrama_actual_data
            
        # PENDIENTE VALIDACION SI TIENEN PERMISOS
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)

class DenegacionPermisosGetView(generics.ListAPIView):
    serializer_class = DenegacionPermisosGetSerializer 
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_cat_serie_und):
        denegacion_permisos = self.queryset.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, id_und_organizacional_actual=None).first()
        serializador = self.serializer_class(denegacion_permisos)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)

class UnidadesPermisosPutView(generics.UpdateAPIView):
    serializer_class_post = PermisosPostSerializer
    serializer_class_put = PermisosPutSerializer
    serializer_class_post_denegacion = PermisosPostDenegacionSerializer
    serializer_class_put_denegacion = PermisosPutDenegacionSerializer
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]
    
    def put_restricciones(self, request, id_cat_serie_und):
        data = request.data['restricciones']
        instance = self.queryset.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, id_und_organizacional_actual=None).first()
        
        restricciones_list = [
            data['denegar_anulacion_docs'],
            data['denegar_borrado_docs'],
            data['excluir_und_actual_respon_series_doc_restriccion'],
            data['denegar_conceder_acceso_doc_na_resp_series'],
            data['denegar_conceder_acceso_exp_na_resp_series']
        ]
        
        if data['excluir_und_actual_respon_series_doc_restriccion']:
            if not data['denegar_borrado_docs'] and not data['denegar_anulacion_docs']:
                raise ValidationError('No puede marcar "Excluir a Sección o Subsección Actual Responsable de la Serie Documental, de las Restricciones de Anulación y Borrado" sin marcar por lo menos uno de los siguientes: "Denegar Borrar Documentos", "Denegar Anular Documentos"')
        else:
            if data['denegar_borrado_docs'] or data['denegar_anulacion_docs']:
                raise ValidationError('No puede dejar desmarcado "Excluir a Sección o Subsección Actual Responsable de la Serie Documental, de las Restricciones de Anulación y Borrado" sin desmarcar los siguientes: "Denegar Borrar Documentos", "Denegar Anular Documentos"')
        
        serializer = None
        
        if instance:
            if True in restricciones_list:
                serializer = self.serializer_class_put_denegacion(instance, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                instance.delete()
        else:
            if True in restricciones_list:
                serializer = self.serializer_class_post_denegacion(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        
        serializer_data = serializer.data if serializer else serializer
        
        return serializer_data

    def put(self, request, id_cat_serie_und):
        data = request.data['unidades_permisos']
        unidades_permisos_crear = [item for item in data if not item['id_permisos_und_org_actual_serie_exp_ccd']]
        unidades_permisos_actualizar = [item for item in data if item['id_permisos_und_org_actual_serie_exp_ccd']]
        
        unidad_permiso_list = []
        
        for unidad_permiso in data:
            unidad_permiso_list = [
                unidad_permiso['crear_expedientes'],
                unidad_permiso['crear_documentos_exps_no_propios'],
                unidad_permiso['anular_documentos_exps_no_propios'],
                unidad_permiso['borrar_documentos_exps_no_propios'],
                unidad_permiso['conceder_acceso_documentos_exps_no_propios'],
                unidad_permiso['conceder_acceso_expedientes_no_propios'],
                unidad_permiso['consultar_expedientes_no_propios'],
                unidad_permiso['descargar_expedientes_no_propios']
            ]
            
            if unidad_permiso['consultar_expedientes_no_propios']:
                if not unidad_permiso['anular_documentos_exps_no_propios'] and not unidad_permiso['borrar_documentos_exps_no_propios'] and not unidad_permiso['conceder_acceso_documentos_exps_no_propios'] and not unidad_permiso['conceder_acceso_expedientes_no_propios']:
                    raise ValidationError('No puede marcar "Consultar Expediente" sin marcar por lo menos uno de los siguientes: "Anular Documento", "Borrar Documento", "Conceder Acceso a Docs", "Conceder Acceso a Exps"')
            else:
                if unidad_permiso['anular_documentos_exps_no_propios'] or unidad_permiso['borrar_documentos_exps_no_propios'] or unidad_permiso['conceder_acceso_documentos_exps_no_propios'] or unidad_permiso['conceder_acceso_expedientes_no_propios']:
                    raise ValidationError('No puede dejar desmarcado "Consultar Expediente" sin desmarcar los siguientes: "Anular Documento", "Borrar Documento", "Conceder Acceso a Docs", "Conceder Acceso a Exps"')
                
        if unidades_permisos_crear:
            # PENDIENTE VALIDAR QUE NO CREE PERMISOS CON TODO EN FALSE
            if True in unidad_permiso_list:
                unidades_permisos_crear_serializer = self.serializer_class_post(data=unidades_permisos_crear, many=True)
                unidades_permisos_crear_serializer.is_valid(raise_exception=True)
                unidades_permisos_crear_serializer.save()
        
        if unidades_permisos_actualizar:
            for unidad_permiso in unidades_permisos_actualizar:
                unidad_permiso_instance = self.queryset.filter(id_permisos_und_org_actual_serie_exp_ccd=unidad_permiso['id_permisos_und_org_actual_serie_exp_ccd']).first()
                
                if True in unidad_permiso_list:
                    unidad_permiso_serializer = self.serializer_class_put(unidad_permiso_instance, data=unidad_permiso)
                    unidad_permiso_serializer.is_valid(raise_exception=True)
                    unidad_permiso_serializer.save()
                else:
                    unidad_permiso_instance.delete()
                
        if request.data.get('restricciones'):
            self.put_restricciones(request, id_cat_serie_und)
        
        # PENDIENTE VALIDACION SI TIENEN PERMISOS
        
        # PENDIENTE AUDITORIAS
        return Response({'succes': True, 'detail':'Se realizó el guardado correctamente'}, status=status.HTTP_200_OK)