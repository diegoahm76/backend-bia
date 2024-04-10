import hashlib
import os
import json
#from wsgiref.types import FileWrapper
from django.core.files.base import ContentFile
from django.db.models import F
import base64 
from django.db.models import Count
from django.db.models import Max
from pyexpat import model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from seguridad.models import Personas
from rest_framework.permissions import IsAuthenticated
from transversal.models.organigrama_models import UnidadesOrganizacionales
from datetime import datetime, date, timedelta, timezone
from rest_framework.response import Response
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from almacen.models.generics_models import Marcas, UnidadesMedida
from django.db import transaction
from rest_framework import status
from django.db.models import Q, Max
from django.db.models.functions import Lower
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen, EstadosArticulo
from almacen.serializers.activos_serializer import ActivosDespachadosDevolucionSerializer, ActivosDevolucionadosSerializer, AlmacenistaLogueadoSerializer, AnexoSerializer, AnexosDocsAlmaSerializer, AnexosOpcionalesDocsAlmaSerializer, ArchivosDigitalesSerializer, AsignacionActivosSerializer, BajaActivosSerializer, BodegasSerializer, BusquedaArticuloSubSerializer, BusquedaSolicitudActivoSerializer, CatalogoBienesSerializer, ClasesTerceroPersonaSerializer, DespachoActivosCreateSerializer, DespachoActivosSerializer, DespachoSinSolicitudSerializer, DetalleSolicitudActivosSerializer, DevolucionActivosSerializer, EntradasAlmacenSerializer, EstadosArticuloSerializer, InventarioSerializer, ItemEntradaAlmacenSerializer, ItemSolicitudActivosSerializer, ItemsBajaActivosSerializer, ItemsDespachoActivosSerializer, ItemsSolicitudActivosSerializer, RegistrarBajaAnexosCreateSerializer, RegistrarBajaBienesCreateSerializer, RegistrarBajaCreateSerializer, SalidasEspecialesArticulosSerializer, SalidasEspecialesSerializer, SolicitudesActivosSerializer, UnidadesMedidaSerializer
from almacen.models.inventario_models import Inventario
from seguridad.models import Personas
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, Bodegas
from almacen.models.activos_models import ActivosDevolucionados, AnexosDocsAlma, AsignacionActivos, BajaActivos, DespachoActivos, DevolucionActivos, ItemsBajaActivos, ItemsDespachoActivos, ItemsSolicitudActivos, SalidasEspecialesArticulos, SolicitudesActivos
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate, ArchivosDigitales
from transversal.models.base_models import ClasesTerceroPersona

from copy import copy


class BuscarBien(generics.ListAPIView):
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Filtrar los registros de inventario según las validaciones requeridas
        queryset = Inventario.objects.filter(
            id_bien__isnull=False,
            id_bodega__isnull=False,
            realizo_baja=False,
            realizo_salida=False,
            
        ).select_related('id_bodega')  # Realizar una sola consulta a la tabla de bodegas

        # Filtrar las bodegas activas
        queryset = queryset.filter(id_bodega__activo=True)

        # Excluir los bienes incluidos en salidas o bajas previas
        queryset = queryset.exclude(realizo_baja=True).exclude(realizo_salida=True)

        # Validar que el campo id_bien tenga un nivel jerárquico de 5
        queryset = queryset.annotate(
            nivel_jerarquico=F('id_bien__nivel_jerarquico')
        ).filter(nivel_jerarquico=5)

        # Validar que el campo cod_tipo_bien sea igual a "A"
        queryset = queryset.filter(id_bien__cod_tipo_bien='A')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Aplicar filtros adicionales según los parámetros de consulta recibidos en la URL
        codigo_bien = self.request.query_params.get('codigo_bien')
        nombre_bien = self.request.query_params.get('nombre_bien')
        nombre_marca = self.request.query_params.get('nombre_marca')
        identificador_bien = self.request.query_params.get('identificador_bien')
        valor_unitario = self.request.query_params.get('valor_unitario')

        if codigo_bien:
            queryset = queryset.filter(id_bien__codigo_bien__icontains=codigo_bien)

        if nombre_bien:
            queryset = queryset.filter(id_bien__nombre__icontains=nombre_bien)

        if nombre_marca:
            queryset = queryset.filter(id_bien__id_marca__nombre__icontains=nombre_marca)

        if identificador_bien:
            queryset = queryset.filter(id_bien__doc_identificador_nro__icontains=identificador_bien)

        if valor_unitario:
            # Filtrar por valor unitario
            items_entrada_ids = ItemEntradaAlmacen.objects.filter(id_bien_id__in=queryset.values_list('id_bien', flat=True), valor_unitario=valor_unitario).values_list('id_bien', flat=True)
            queryset = queryset.filter(id_bien__in=items_entrada_ids)

        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Bienes obtenidos exitosamente', 'data': serializer.data})
    
class RegistrarBajaCreateView(generics.CreateAPIView):
    serializer_class = RegistrarBajaCreateSerializer
    serializer_bienes_class = RegistrarBajaBienesCreateSerializer
    serializer_anexos_class = RegistrarBajaAnexosCreateSerializer
    permission_classes = [IsAuthenticated]


    @transaction.atomic
    def create(self, request):
        data = request.data
        anexo = request.FILES.get('anexo')
        current_date = datetime.now()
        persona_logueada = request.user.persona

        bienes = json.loads(data.get('bienes'))

        if not bienes:
            raise ValidationError('Debe seleccionar mínimo un activo al cual desea darle de baja')

        ultimo_consecutivo = BajaActivos.objects.aggregate(Max('consecutivo_por_baja'))
        ultimo_consecutivo = ultimo_consecutivo['consecutivo_por_baja__max'] if ultimo_consecutivo['consecutivo_por_baja__max'] else 0

        # Insertar baja en T086
        data_baja = {}
        data_baja['consecutivo_por_baja'] = ultimo_consecutivo + 1
        data_baja['concepto'] = data.get('concepto')
        data_baja['fecha_baja'] = current_date
        data_baja['cantidad_activos_baja'] = len(bienes)
        data_baja['id_persona_registro_baja'] = persona_logueada.id_persona
        data_baja['id_uni_org_registro_baja'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
        
        serializer_baja = self.serializer_class(data=data_baja)
        serializer_baja.is_valid(raise_exception=True)
        baja_creada = serializer_baja.save()

        # Insertar bienes
        bienes_id_list = [bien['id_bien'] for bien in bienes]
        bienes_instances = CatalogoBienes.objects.filter(id_bien__in=bienes_id_list)

        item_entrada_instances = ItemEntradaAlmacen.objects.filter(id_bien__in=bienes_id_list)

        for bien in bienes:
            bien_instance = bienes_instances.filter(id_bien=bien['id_bien']).first()

            item_entrada_instance = item_entrada_instances.filter(id_bien=bien['id_bien']).first()
            valor_unitario_correcto = item_entrada_instance.valor_unitario if item_entrada_instance else None
            
            bien['id_baja_activo'] = baja_creada.id_baja_activo
            bien['codigo_bien'] = bien_instance.codigo_bien
            bien['nombre'] = bien_instance.nombre
            bien['nombre_marca'] = bien_instance.id_marca.nombre
            bien['doc_identificador_nro'] = bien_instance.doc_identificador_nro
            bien['valor_unitario'] = valor_unitario_correcto

            # Agregar registro al inventario
            inventario = Inventario.objects.filter(id_bien=bien['id_bien']).first()
            if inventario:
                inventario.realizo_baja = True
                inventario.ubicacion_en_bodega = False
                inventario.fecha_ultimo_movimiento = current_date
                inventario.tipo_doc_ultimo_movimiento = 'BAJA'
                inventario.id_registro_doc_ultimo_movimiento = baja_creada.id_baja_activo
                inventario.save()

        serializer_bienes = self.serializer_bienes_class(data=bienes, many=True)
        serializer_bienes.is_valid(raise_exception=True)
        serializer_bienes.save()

        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO 
        nombre_anexo = "Resolución aprobada por el comité"
        archivo_nombre = anexo.name 
        nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        
        formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
        
        if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
            raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
        
        # CREAR ARCHIVO EN T238
        # Obtiene el año actual para determinar la carpeta de destino
        current_year = current_date.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year)) # VALIDAR RUTA

        # Calcula el hash MD5 del archivo
        md5_hash = hashlib.md5()
        for chunk in anexo.chunks():
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
        anexo.name = nombre_anexo + extension
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        # Insertar anexo en T094
        data_anexo = {}
        data_anexo['id_baja_activo'] = baja_creada.id_baja_activo
        data_anexo['nombre_anexo'] = nombre_anexo # PONER NOMBRE FIJO ANEXO
        data_anexo['nro_folios'] = data.get('nro_folios')
        data_anexo['descripcion_anexo'] = data.get('descripcion_anexo')
        data_anexo['fecha_creacion_anexo'] = current_date
        data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
        
        serializer_anexo = self.serializer_anexos_class(data=data_anexo)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        return Response({'success': True, 'detail': 'Se realizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)

class ActualizarBajaActivosView(generics.UpdateAPIView):
    serializer_class = RegistrarBajaCreateSerializer
    serializer_bienes_class = RegistrarBajaBienesCreateSerializer
    serializer_anexos_class = RegistrarBajaAnexosCreateSerializer
    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def update(self, request, pk):
        data = request.data
        anexo = request.FILES.get('anexo')
        current_date = datetime.now()
        persona_logueada = request.user.persona

        bienes = json.loads(data.get('bienes'))

        baja_activo = BajaActivos.objects.filter(id_baja_activo=pk).first()
        if not baja_activo:
            raise NotFound('No se encontró la baja ingresada')

        if not bienes:
            raise ValidationError('Debe seleccionar mínimo un activo al cual desea darle de baja')

        # Actualizar baja en T086
        data_baja = {}
        data_baja['concepto'] = data.get('concepto')
        data_baja['fecha_baja'] = current_date # VALIDAR SI SE PUEDE ACTUALIZAR
        data_baja['cantidad_activos_baja'] = len(bienes)
        data_baja['id_persona_registro_baja'] = persona_logueada.id_persona # VALIDAR SI SE PUEDE ACTUALIZAR
        data_baja['id_uni_org_registro_baja'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional # VALIDAR SI SE PUEDE ACTUALIZAR
        
        serializer_baja = self.serializer_class(baja_activo, data=data_baja, partial=True)
        serializer_baja.is_valid(raise_exception=True)
        serializer_baja.save()

        # Insertar bienes
        bienes_id_list = [bien['id_bien'] for bien in bienes]
        items_bienes_bajas = ItemsBajaActivos.objects.filter(id_baja_activo=pk)
        items_bienes_bajas_list = list(items_bienes_bajas.values_list('id_bien', flat=True))

        items_bienes_actualizar = items_bienes_bajas.filter(id_bien__in=bienes_id_list)
        items_bienes_crear = [bien for bien in bienes if bien['id_bien'] not in items_bienes_bajas_list]
        items_bienes_crear_list = [bien['id_bien'] for bien in items_bienes_crear]
        items_bienes_eliminar = items_bienes_bajas.exclude(id_bien__in=bienes_id_list)
        items_bienes_crear_instances = CatalogoBienes.objects.filter(id_bien__in=items_bienes_crear_list)

        item_entrada_instances = ItemEntradaAlmacen.objects.filter(id_bien__in=items_bienes_crear_list)

        # ELIMINAR BIENES BAJA
        if items_bienes_eliminar:
            items_bienes_eliminar.delete()

        # CREAR BIENES DE BAJAS NUEVOS
        if items_bienes_crear:
            for bien in items_bienes_crear:
                bien_instance = items_bienes_crear_instances.filter(id_bien=bien['id_bien']).first()

                item_entrada_instance = item_entrada_instances.filter(id_bien=bien['id_bien']).first()
                valor_unitario_correcto = item_entrada_instance.valor_unitario if item_entrada_instance else None
                
                bien['id_baja_activo'] = pk
                bien['codigo_bien'] = bien_instance.codigo_bien
                bien['nombre'] = bien_instance.nombre
                bien['nombre_marca'] = bien_instance.id_marca.nombre
                bien['doc_identificador_nro'] = bien_instance.doc_identificador_nro
                bien['valor_unitario'] = valor_unitario_correcto

                # Agregar registro al inventario
                inventario = Inventario.objects.filter(id_bien=bien['id_bien']).first()
                if inventario:
                    inventario.realizo_baja = True
                    inventario.ubicacion_en_bodega = False
                    inventario.fecha_ultimo_movimiento = current_date # VALIDAR FECHA QUE DEBERIA TOMAR (CREACION O ACTUALIZACION)
                    inventario.tipo_doc_ultimo_movimiento = 'BAJA'
                    inventario.id_registro_doc_ultimo_movimiento = pk
                    inventario.save()

            serializer_bienes = self.serializer_bienes_class(data=items_bienes_crear, many=True)
            serializer_bienes.is_valid(raise_exception=True)
            serializer_bienes.save()

        # ACTUALIZAR JUSTIFICACION BIENES BAJA
        if items_bienes_actualizar:
            for bien_actualizar in items_bienes_actualizar:
                bien_actualizar.justificacion_baja_activo = [bien['justificacion_baja_activo'] for bien in bienes if bien['id_bien'] == bien_actualizar.id_bien.id_bien][0]
                bien_actualizar.save()

        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO
        anexo_instance = AnexosDocsAlma.objects.filter(id_anexo_doc_alma=data['id_anexo_doc_alma']).first()
        if anexo:
            nombre_anexo = "Resolución aprobada por el comité"
            old_archivo_digital = copy(anexo_instance.id_archivo_digital)

            archivo_nombre = anexo.name 
            nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            
            formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
            
            if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
                raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
            
            # CREAR ARCHIVO EN T238
            # Obtiene el año actual para determinar la carpeta de destino
            current_year = current_date.year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year)) # VALIDAR RUTA

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in anexo.chunks():
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
            anexo.name = nombre_anexo + extension
            respuesta = archivo_class.crear_archivo(data_archivo, anexo)
            data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')

            # ELIMINAR ARCHIVO DIGITAL
            old_archivo_digital.delete()
            

        # Actualizar anexo en T094
        data_anexo = {}
        data_anexo['nro_folios'] = data.get('nro_folios')
        data_anexo['descripcion_anexo'] = data.get('descripcion_anexo')
        data_anexo['fecha_creacion_anexo'] = current_date # SE VA GUADAR FECHA ACTUALZIACION????
        
        serializer_anexo = self.serializer_anexos_class(anexo_instance, data=data_anexo, partial=True)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        

        return Response({'success': True, 'detail': 'Se actualizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)

#Retorna_consecutivo_Siguiente
class UltimoConsecutivoView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] 
    def list(self, request, *args, **kwargs):
        # Obtener el último consecutivo más 1
        ultimo_consecutivo = BajaActivos.objects.aggregate(max_consecutivo=Max('consecutivo_por_baja'))
        proximo_consecutivo = ultimo_consecutivo['max_consecutivo'] + 1 if ultimo_consecutivo['max_consecutivo'] is not None else 1
        data = {'success': True, 'detail': 'El ultimo consecutivo actual es:', 'data': {'consecutivo_por_baja': proximo_consecutivo}}
        return Response(data)
    

#ELIMINAR_REGISTROS
class BorrarBajaActivosView(generics.DestroyAPIView):
    queryset = BajaActivos.objects.all()
    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def destroy(self, request, pk):
        instance = self.get_object()
        
        # Validar si es posible eliminar el registro de baja de activos
        if not self.puede_eliminar_registro(instance):
            raise ValidationError('No es posible eliminar el registro de baja de activos debido a movimientos posteriores.')

        # Proceder con la eliminación del registro de baja de activos

        # Paso 1: Eliminar los registros correspondientes en la tabla T094ItemsBajaActivos
        items_baja_activos = ItemsBajaActivos.objects.filter(id_baja_activo=instance.id_baja_activo)
        for item in items_baja_activos:
            # Paso 2: Obtener el bien y actualizar el inventario
            inventario = Inventario.objects.get(id_bien=item.id_bien.id_bien)
            inventario.realizo_baja = False
            inventario.fecha_ultimo_movimiento = None
            inventario.tipo_doc_ultimo_movimiento = None
            inventario.id_registro_doc_ultimo_movimiento = None
            inventario.save()

            # Paso 3: Eliminar el item de baja de activos
            item.delete()

        # Paso 4: Eliminar los registros correspondientes en la tabla T087AnexosDocsAlma
        anexos_baja_activos = AnexosDocsAlma.objects.filter(id_baja_activo=instance.id_baja_activo)
        for anexo in anexos_baja_activos:
            # Paso 5: Obtener el archivo digital y eliminarlo
            archivo_digital = anexo.id_archivo_digital
            archivo_digital.delete()
            anexo.delete()

        # Paso 6: Finalmente, eliminar el registro correspondiente en la tabla T086BajaActivos
        instance.delete()

        return Response({'success': True, 'detail': 'Se eliminó el registro de baja de activos correctamente.'}, status=status.HTTP_200_OK)

    def puede_eliminar_registro(self, instance):
        # Recuperar todos los activos incluidos en el registro de baja
        activos_baja = ItemsBajaActivos.objects.filter(id_baja_activo=instance.id_baja_activo)

        # Verificar si los activos tienen movimientos posteriores a la fecha de la baja
        for activo in activos_baja:
            # Obtener el registro de inventario correspondiente al activo
            inventario_activo = Inventario.objects.get(id_bien=activo.id_bien.id_bien)

            # Verificar si el activo tiene un movimiento posterior a la fecha de la baja
            if inventario_activo.fecha_ultimo_movimiento and inventario_activo.fecha_ultimo_movimiento > instance.fecha_baja:
                return False  # Si hay algún movimiento posterior, no se puede eliminar el registro de baja

        return True  # Si no hay movimientos posteriores para ningún activo, se puede eliminar el registro de baja
    


class BajaActivosPorConsecutivo(generics.ListAPIView):
    queryset = BajaActivos.objects.all()
    serializer_class = BajaActivosSerializer
    permission_classes = [IsAuthenticated] 

    def list(self, request, *args, **kwargs):
        consecutivo = self.kwargs.get('consecutivo')  # Obtener el consecutivo desde los argumentos de la URL
        baja_activos = self.get_queryset().filter(consecutivo_por_baja=consecutivo).first()  # Filtrar por consecutivo
        if not baja_activos:
            return Response({"success": False, "detail": "No se encontró la baja de activos asociada al consecutivo proporcionado"}, status=404)
        
        # Serializar la baja de activos
        serializer = self.get_serializer(baja_activos)
        data = serializer.data

        # Obtener los anexos relacionados con la baja de activos
        anexos = AnexosDocsAlma.objects.filter(id_baja_activo=baja_activos.id_baja_activo)
        anexos_serializer = AnexosDocsAlmaSerializer(anexos, many=True)
        
        # Agregar los anexos serializados al objeto de la respuesta
        data['anexos'] = anexos_serializer.data

        # Obtener los items de baja de activos asociados a la baja de activos
        items_baja_activos = ItemsBajaActivos.objects.filter(id_baja_activo=baja_activos.id_baja_activo)
        items_serializer = ItemsBajaActivosSerializer(items_baja_activos, many=True)
        
        # Agregar los items serializados al objeto de la respuesta
        data['items'] = items_serializer.data

        return Response({"success": True, "detail": "Baja de activos encontrada", "data": data})
    

class ListarBajasActivosView(generics.ListAPIView):
    queryset = BajaActivos.objects.all()
    serializer_class = BajaActivosSerializer
    permission_classes = [IsAuthenticated] 

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "detail": "Bajas de activos listadas correctamente", "data": serializer.data})
    
class ListarUnidadesMedidaActivas(generics.ListAPIView):
    serializer_class = UnidadesMedidaSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return UnidadesMedida.objects.filter(activo=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Unidades de medida activas obtenidas correctamente', 'data': serializer.data})
    

class CrearSolicitudActivosView(generics.CreateAPIView):
    serializer_class = SolicitudesActivosSerializer
    items_serializer_class = ItemsSolicitudActivosSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        data = request.data
        current_date = datetime.now()
        persona_logueada = request.user.persona

        # Obtener ID de unidad organizacional del solicitante
        id_unidad_org_solicitante = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional

        # Obtener ID de la persona operario y su unidad organizacional
        id_persona_operario = data.get('id_persona_operario')
        try:
            persona_operario = Personas.objects.get(id_persona=id_persona_operario)
            id_uni_org_operario = persona_operario.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario operario especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener ID de la persona responsable y su unidad organizacional
        id_funcionario_resp_unidad = data.get('id_funcionario_resp_unidad')
        try:
            persona_responsable = Personas.objects.get(id_persona=id_funcionario_resp_unidad)
            id_uni_org_responsable = persona_responsable.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario responsable especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si la solicitud es de préstamo y ajustar la fecha de devolución
        solicitud_prestamo = data.get('solicitud_prestamo', False)
        if solicitud_prestamo:
            fecha_devolucion = current_date
        else:
            fecha_devolucion = None

        # Guardar información de la solicitud
        solicitud_data = {
            'fecha_solicitud': current_date,
            'motivo': data.get('motivo'),
            'observacion': data.get('observacion'),
            'id_persona_solicita': persona_logueada.id_persona,
            'id_uni_org_solicitante': id_unidad_org_solicitante,
            'id_funcionario_resp_unidad': id_funcionario_resp_unidad,
            'id_uni_org_responsable': id_uni_org_responsable,
            'id_persona_operario': id_persona_operario,
            'id_uni_org_operario': id_uni_org_operario,
            'estado_solicitud': 'S',
            'solicitud_prestamo': solicitud_prestamo,
            'revisada_responsable': False,
            'estado_aprobacion_resp': 'Ep',
            'gestionada_alma': False,
            'rechazada_almacen': False,
            'solicitud_anulada_solicitante': False,
        }

        solicitud_serializer = self.serializer_class(data=solicitud_data)
        solicitud_serializer.is_valid(raise_exception=True)
        solicitud = solicitud_serializer.save()

        # Guardar información de los items de la solicitud
        items_data = data.get('items', [])
        for index, item_data in enumerate(items_data, start=1):
            # Asignar el ID de la solicitud y el número de posición al item
            item_data['id_solicitud_activo'] = solicitud.id_solicitud_activo
            item_data['nro_posicion'] = index
            item_serializer = self.items_serializer_class(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()

        return Response({'success': True, 'detail': 'Solicitud de activos creada correctamente', 'data': solicitud_serializer.data}, status=status.HTTP_201_CREATED)
    


class EditarSolicitudActivosView(generics.UpdateAPIView):
    serializer_class = SolicitudesActivosSerializer
    queryset = SolicitudesActivos.objects.filter(estado_solicitud__in=["SR","S"])
    items_serializer_class = ItemsSolicitudActivosSerializer
    permission_classes = [IsAuthenticated] 

    def update(self, request, pk):
        instance = self.queryset.filter(id_solicitud_activo=pk).first()
        if not instance:
            raise NotFound ("No se encontro la solicitud activo.")
        data = request.data
        current_date = datetime.now()


        # try:
        with transaction.atomic():
                # Actualizar los campos de la solicitud
                instance.fecha_solicitud = current_date
                instance.estado_solicitud = 'S'
                instance.motivo = data.get('motivo', instance.motivo)
                instance.observacion = data.get('observacion', instance.observacion)
                instance.solicitud_prestamo = data.get('solicitud_prestamo', instance.solicitud_prestamo)
                instance.save()

                # Actualizar la fecha de devolución si es un préstamo
                if instance.solicitud_prestamo:
                    instance.fecha_devolucion = current_date
                else:
                    instance.fecha_devolucion = None

                # Eliminar los items que no se envían en la solicitud
                items_data = data.get('items', [])
                item_ids_to_keep = [item['id_item_solicitud_activo'] for item in items_data if 'id_item_solicitud_activo' in item]
                instance.itemssolicitudactivos_set.exclude(id_item_solicitud_activo__in=item_ids_to_keep).delete()

                # Guardar o actualizar los items enviados en la solicitud
                for item_data in items_data:
                    item_id = item_data.get('id_item_solicitud_activo')
                    if item_id:
                        # Si el ID del item existe, actualizar el item
                        item_instance = instance.itemssolicitudactivos_set.get(id_item_solicitud_activo=item_id)
                        item_instance.descripcion = item_data.get('descripcion', item_instance.descripcion)
                        item_instance.cantidad = item_data.get('cantidad', item_instance.cantidad)
                        item_instance.save()
                    else:
                        # Si el ID del item no existe, crear un nuevo item asociado a la solicitud
                        item_data['id_solicitud_activo'] = instance.id_solicitud_activo
                        item_serializer = self.items_serializer_class(data=item_data)
                        item_serializer.is_valid(raise_exception=True)
                        item_serializer.save()

        return Response({'success': True, 'detail': 'Solicitud de activos editada correctamente'}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     return Response({'success': False, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DetalleSolicitudActivosView(generics.RetrieveAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    lookup_field = 'id_solicitud_activo'
    permission_classes = [IsAuthenticated] 

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Obtener los items asociados a la solicitud de activos
        items_queryset = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance.id_solicitud_activo)
        items_serializer = ItemSolicitudActivosSerializer(items_queryset, many=True)

        # Agregar el nombre de la unidad de medida en los items
        for item_data in items_serializer.data:
            unidad_medida_id = item_data.get('id_unidad_medida')
            unidad_medida_nombre = None
            if unidad_medida_id:
                unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=unidad_medida_id).first()
                if unidad_medida:
                    unidad_medida_nombre = unidad_medida.nombre
            item_data['nombre_unidad_medida'] = unidad_medida_nombre

        # Agregar los items al resultado de la serialización
        serialized_data = serializer.data
        serialized_data['items'] = items_serializer.data

        return Response({'success': True, 'detail': 'Solicitud de activos recuperada correctamente', 'data': serialized_data}, status=status.HTTP_200_OK)
    
class ResumenSolicitudGeneralActivosView(generics.RetrieveAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = None  # No necesitamos un serializador para esta vista
    lookup_field = 'id_solicitud_activo'  # Especifica el campo utilizado como PK en la URL
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        solicitud_data = {
            'id_solicitud_activo': instance.id_solicitud_activo,
            'fecha_solicitud': instance.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S'),
            'motivo': instance.motivo,
            'observacion': instance.observacion,
            #Persona_Solicitante
            'id_persona_solicita': instance.id_persona_solicita.id_persona if instance.id_persona_solicita else None,
            'primer_nombre_persona_solicitante': instance.id_persona_solicita.primer_nombre if instance.id_persona_solicita else None,
            'primer_apellido_persona_solicitante': instance.id_persona_solicita.primer_apellido if instance.id_persona_solicita else None,
            'tipo_documento_persona_solicitante': instance.id_persona_solicita.tipo_documento.cod_tipo_documento if instance.id_persona_solicita else None,
            'numero_documento_persona_solicitante': instance.id_persona_solicita.numero_documento if instance.id_persona_solicita else None,
            'id_uni_org_solicitante': instance.id_uni_org_solicitante.id_unidad_organizacional,
            #Persona_Funcionario_Responsable_Unidad
            'id_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.id_persona if instance.id_funcionario_resp_unidad else None,
            'primer_nombre_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.primer_nombre if instance.id_funcionario_resp_unidad else None,
            'primer_apellido_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.primer_apellido if instance.id_funcionario_resp_unidad else None,
            'tipo_documento_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.tipo_documento.cod_tipo_documento if instance.id_funcionario_resp_unidad else None,
            'numero_documento_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.numero_documento if instance.id_funcionario_resp_unidad else None,
            'id_uni_org_responsable': instance.id_uni_org_responsable.id_unidad_organizacional,
            #Persona_Operario
            'id_persona_operario': instance.id_persona_operario.id_persona if instance.id_persona_operario else None,
            'primer_nombre_persona_operario': instance.id_persona_operario.primer_nombre if instance.id_persona_operario else None,
            'primer_apellido_persona_operario': instance.id_persona_operario.primer_apellido if instance.id_persona_operario else None,
            'tipo_documento_persona_operario': instance.id_persona_operario.tipo_documento.cod_tipo_documento if instance.id_persona_operario else None,
            'numero_documento_persona_operario': instance.id_persona_operario.numero_documento if instance.id_persona_operario else None,
            'id_uni_org_operario': instance.id_uni_org_operario.id_unidad_organizacional,
            #Resumen_Solcitiud
            'estado_solicitud': instance.estado_solicitud,
            'solicitud_prestamo': instance.solicitud_prestamo,
            'fecha_cierra_solicitud': instance.fecha_cierra_solicitud.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_cierra_solicitud else None,
            'revisada_responsable': instance.revisada_responsable,
            'estado_aprobacion_resp': instance.estado_aprobacion_resp,
            'justificacion_rechazo_resp': instance.justificacion_rechazo_resp,
            'fecha_aprobacion_resp': instance.fecha_aprobacion_resp.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_aprobacion_resp else None,
            'gestionada_alma': instance.gestionada_alma,
            'obser_cierre_no_dispo_alma': instance.obser_cierre_no_dispo_alma,
            'fecha_cierre_no_dispo_alma': instance.fecha_cierre_no_dispo_alma.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_cierre_no_dispo_alma else None,
            #Persona_cierra_no_dispo_alma
            'id_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.id_persona if instance.id_persona_cierra_no_dispo_alma else None,
            'primer_nombre_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.primer_nombre if instance.id_persona_cierra_no_dispo_alma else None,
            'primer_apellido_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.primer_apellido if instance.id_persona_cierra_no_dispo_alma else None,
            'tipo_documento_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.tipo_documento.cod_tipo_documento if instance.id_persona_cierra_no_dispo_alma else None,
            'numero_documento_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.numero_documento if instance.id_persona_cierra_no_dispo_alma else None,
            #//////////////////////////////////////////////////////////////////////////////////////////////////////////////
            'rechazada_almacen': instance.rechazada_almacen,
            'fecha_rechazo_almacen': instance.fecha_rechazo_almacen.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_rechazo_almacen else None,
            'justificacion_rechazo_almacen': instance.justificacion_rechazo_almacen,
            #persona_alma_rechaza
            'id_persona_alma_rechaza': instance.id_persona_alma_rechaza.id_persona if instance.id_persona_alma_rechaza else None,
            'primer_nombre_persona_alma_rechaza': instance.id_persona_alma_rechaza.primer_nombre if instance.id_persona_alma_rechaza else None,
            'primer_apellido_persona_alma_rechaza': instance.id_persona_alma_rechaza.primer_apellido if instance.id_persona_alma_rechaza else None,
            'tipo_documento_persona_alma_rechaza': instance.id_persona_alma_rechaza.tipo_documento.cod_tipo_documento if instance.id_persona_alma_rechaza else None,
            'numero_documento_persona_alma_rechaza': instance.id_persona_alma_rechaza.numero_documento if instance.id_persona_alma_rechaza else None,
            'solicitud_anulada_solicitante': instance.solicitud_anulada_solicitante,
            'fecha_anulacion_solicitante': instance.fecha_anulacion_solicitante.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_anulacion_solicitante else None,
        }
        
        # Recuperar los items de solicitud activos relacionados
        items_solicitud = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance)
        items_data = []
        for item in items_solicitud:
            item_data = {
                'id_item_solicitud_activo': item.id_item_solicitud_activo,
                'id_solicitud_activo': item.id_solicitud_activo.id_solicitud_activo,
                'id_bien': item.id_bien.id_bien,  
                'nombre_bien': item.id_bien.nombre,  
                'codigo_bien': item.id_bien.codigo_bien,  
                'cantidad': item.cantidad,
                'id_unidad_medida': item.id_unidad_medida.id_unidad_medida,  
                'abreviatura_unidad_medida': item.id_unidad_medida.abreviatura,  
                'nombre_unidad_medida': item.id_unidad_medida.nombre,
                'observacion': item.observacion,
                'nro_posicion': item.nro_posicion
            }
            items_data.append(item_data)
        
        # Recuperar los items de despacho activos relacionados
        items_despacho = ItemsDespachoActivos.objects.filter(id_despacho_activo__id_solicitud_activo=instance)
        items_despacho_data = []
        for item_despacho in items_despacho:
            item_despacho_data = {
                'id_item_despacho_activo': item_despacho.id_item_despacho_activo,
                'id_despacho_activo': item_despacho.id_despacho_activo.id_despacho_activo,
                'id_bien_solicitado': item_despacho.id_bien_solicitado.id_bien if item_despacho.id_bien_solicitado else None,
                'nombre_bien_solicitado': item_despacho.id_bien_solicitado.nombre if item_despacho.id_bien_solicitado else None,
                'id_bien_despachado': item_despacho.id_bien_despachado.id_bien if item_despacho.id_bien_despachado else None,
                'nombre_bien_despachado': item_despacho.id_bien_despachado.nombre if item_despacho.id_bien_despachado else None,
                'id_entrada_alma': item_despacho.id_entrada_alma.id_entrada_almacen if item_despacho.id_entrada_alma else None,
                'id_bodega': item_despacho.id_bodega.id_bodega if item_despacho.id_bodega else None,
                'nombre_bodega': item_despacho.id_bodega.nombre if item_despacho.id_bodega else None,
                'cantidad_solicitada': item_despacho.cantidad_solicitada,
                'fecha_devolucion': item_despacho.fecha_devolucion.strftime('%Y-%m-%d %H:%M:%S') if item_despacho.fecha_devolucion else None,
                'se_devolvio': item_despacho.se_devolvio,
                'id_uni_medida_solicitada': item_despacho.id_uni_medida_solicitada.id_unidad_medida if item_despacho.id_uni_medida_solicitada else None,
                'nombre_uni_medida_solicitada': item_despacho.id_uni_medida_solicitada.nombre if item_despacho.id_uni_medida_solicitada else None,
                'abreviatura_uni_medida_solicitada': item_despacho.id_uni_medida_solicitada.abreviatura if item_despacho.id_uni_medida_solicitada else None,
                'cantidad_despachada': item_despacho.cantidad_despachada,
                'observacion': item_despacho.observacion,
                'nro_posicion_despacho': item_despacho.nro_posicion_despacho
            }
            items_despacho_data.append(item_despacho_data)

        
        # Recuperar los despachos activos relacionados
        despachos = DespachoActivos.objects.filter(id_solicitud_activo=instance)
        despachos_data = []
        for despacho in despachos:
            despacho_data = {
                'id_despacho_activo': despacho.id_despacho_activo,
                'despacho_sin_solicitud': despacho.despacho_sin_solicitud,
                'estado_despacho': despacho.estado_despacho,
                'fecha_autorizacion_resp': despacho.fecha_autorizacion_resp.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_autorizacion_resp else None,
                'justificacion_rechazo_resp': despacho.justificacion_rechazo_resp,
                'fecha_solicitud': despacho.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_solicitud else None,
                'fecha_despacho': despacho.fecha_despacho.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_despacho else None,
                #persona_despacha
                'id_persona_despacha': despacho.id_persona_despacha.id_persona,
                'primer_nombre_persona_despacha': despacho.id_persona_despacha.primer_nombre if despacho.id_persona_solicita else None,
                'primer_apellido_persona_despacha': despacho.id_persona_despacha.primer_apellido if despacho.id_persona_solicita else None,
                'tipo_documento_persona_despacha': despacho.id_persona_despacha.tipo_documento.cod_tipo_documento if despacho.id_persona_despacha else None,
                'numero_documento_persona_despacha': despacho.id_persona_despacha.numero_documento if despacho.id_persona_despacha else None,
                #/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                'observacion': despacho.observacion,
                #persona_solicita
                'id_persona_solicita': despacho.id_persona_solicita.id_persona if despacho.id_persona_solicita else None,
                'primer_nombre_persona_solicitante': despacho.id_persona_solicita.primer_nombre if despacho.id_persona_solicita else None,
                'primer_apellido_persona_solicitante': despacho.id_persona_solicita.primer_apellido if despacho.id_persona_solicita else None,
                'tipo_documento_persona_solicitante': despacho.id_persona_solicita.tipo_documento.cod_tipo_documento if despacho.id_persona_solicita else None,
                'numero_documento_persona_solicitante': despacho.id_persona_solicita.numero_documento if despacho.id_persona_solicita else None,
                'id_uni_org_solicitante': despacho.id_uni_org_solicitante.id_unidad_organizacional if despacho.id_uni_org_solicitante else None,
                #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                'id_bodega': despacho.id_bodega.id_bodega if despacho.id_bodega else None,
                'nombre_bodega': despacho.id_bodega.nombre if despacho.id_bodega else None,
                'despacho_anulado': despacho.despacho_anulado,
                'justificacion_anulacion': despacho.justificacion_anulacion,
                'fecha_anulacion': despacho.fecha_anulacion.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_anulacion else None,
                #Persona_Anula
                'id_persona_anula': despacho.id_persona_anula.id_persona if despacho.id_persona_anula else None,
                'primer_nombre_persona_anula': despacho.id_persona_anula.primer_nombre if despacho.id_persona_anula else None,
                'primer_apellido_persona_anula': despacho.id_persona_anula.primer_apellido if despacho.id_persona_anula else None,
                'tipo_documento_persona_anula': despacho.id_persona_anula.tipo_documento.cod_tipo_documento if despacho.id_persona_anula else None,
                'numero_documento_persona_anula': despacho.id_persona_anula.numero_documento if despacho.id_persona_anula else None,
                'id_archivo_doc_recibido': despacho.id_archivo_doc_recibido.id_archivo_digital if despacho.id_archivo_doc_recibido else None
            }
            despachos_data.append(despacho_data)
        
        # Agregar los datos de los items de solicitud y despacho activos al resultado final
        solicitud_data['items_solicitud'] = items_data
        solicitud_data['despachos'] = despachos_data
        solicitud_data['items_despacho'] = items_despacho_data

        return Response({'success': True, 'detail': 'Solicitud de activos recuperada correctamente', 'data': solicitud_data}, status=status.HTTP_200_OK)
    

class CancelarSolicitudActivos(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]   
  
    lookup_field = 'id_solicitud_activo'  # Especifica el campo utilizado como PK en la URL

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verificar si la solicitud puede ser cancelada
        if instance.gestionada_alma:
            return Response({'error': 'No se puede cancelar una solicitud gestionada por el almacén.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener los datos de la solicitud
        justificacion_anulacion = request.data.get('justificacion_anulacion')
        fecha_actual = datetime.now()
        
        # Actualizar los campos de la solicitud
        instance.solicitud_anulada_solicitante = True
        instance.justificacion_anulacion = justificacion_anulacion
        instance.fecha_anulacion_solicitante = fecha_actual
        instance.estado_solicitud = 'C'
        instance.fecha_cierra_solicitud = fecha_actual
        
        # Guardar los cambios en la base de datos
        instance.save()
        
        # Serializar la instancia actualizada
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        return Response({'success': True, 'detail': 'Solicitud cancelada correctamente.', 'data': data}, status=status.HTTP_200_OK)
    

class BusquedaAvanzadaSolicitudesActivos(generics.ListAPIView):
    serializer_class = BusquedaSolicitudActivoSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Obtener parámetros de consulta
        estado_solicitud = self.request.query_params.get('estado_solicitud')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        # Filtrar las solicitudes por estado
        queryset = SolicitudesActivos.objects.all()
        if estado_solicitud:
            queryset = queryset.filter(estado_solicitud=estado_solicitud)

        # Filtrar las solicitudes por rango de fechas
        if fecha_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_hasta)

        # Anotar el número de activos relacionados a cada solicitud
        queryset = queryset.annotate(numero_activos=Count('itemssolicitudactivos'))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Solicitudes obtenidas correctamente.',
            'data': serializer.data
        }
        return Response(data)
    


class CrearArchivosOpcionales(generics.CreateAPIView):
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    def create(self,request, id_baja_activo):
        data = request.data
        anexo = request.FILES.get('anexo_opcional')
        current_date = datetime.now()
        baja = BajaActivos.objects.filter(id_baja_activo=id_baja_activo).first()

        if not baja:
            raise NotFound("La Baja Activo no ha sido encontrada.")
        
        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO 
        archivo_nombre = anexo.name 
        nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        
        formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
        
        if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
            raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
        
        # CREAR ARCHIVO EN T238
        # Obtiene el año actual para determinar la carpeta de destino
        current_year = current_date.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year)) # VALIDAR RUTA

        # Calcula el hash MD5 del archivo
        md5_hash = hashlib.md5()
        for chunk in anexo.chunks():
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
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        # Insertar anexo en T094
        data['id_baja_activo'] = baja.id_baja_activo
        data['fecha_creacion_anexo'] = current_date
        data['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
        data.pop('anexo_opcional')
        serializer_anexo = self.serializer_class(data=data)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        return Response({'success': True, 'detail': 'Archivo opcional creado exitosamente.', 'data': serializer_anexo.data}, status=status.HTTP_200_OK)



class ActualizarAnexoOpcional(generics.UpdateAPIView):
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    # Insertar archivo digital

    # VALIDAR FORMATO ARCHIVO

    def update(self, request,id_baja_activo):

        data = request.data
        data._mutable=True
        anexo = request.FILES.get('anexo_opcional')
        current_date = datetime.now()

        anexo_instance = AnexosDocsAlma.objects.filter(id_anexo_doc_alma=data['id_anexo_doc_alma'],id_baja_activo = id_baja_activo ).first()
        if not anexo_instance:
            raise NotFound("No se encontro el anexo opcional para la baja de activos requerida.")


        if anexo:
            old_archivo_digital = copy(anexo_instance.id_archivo_digital)

            archivo_nombre = anexo.name 
            nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            
            formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
            
            if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
                raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
            
            # CREAR ARCHIVO EN T238
            # Obtiene el año actual para determinar la carpeta de destino
            current_year = current_date.year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year)) # VALIDAR RUTA

            # Calcula el hash MD5 del archivo
            md5_hash = hashlib.md5()
            for chunk in anexo.chunks():
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
            respuesta = archivo_class.crear_archivo(data_archivo, anexo)

            # Actualizar anexo en T094
            data['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
            
            # ELIMINAR ARCHIVO DIGITAL
            old_archivo_digital.delete()
            data.pop('anexo_opcional')

        data['fecha_creacion_anexo'] = current_date
        serializer_anexo = self.serializer_class(anexo_instance, data=data, partial=True)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        

        return Response({'success': True, 'detail': 'Se actualizó el registro de la baja correctamente', 'data': serializer_anexo.data}, status=status.HTTP_200_OK)


class EliminarAnexoOpcional(generics.DestroyAPIView):
    queryset = AnexosDocsAlma.objects.all()
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, id_baja_activo):
        id_anexo_doc_alma = request.query_params.get('id_anexo_doc_alma')

        # Obtener el anexo opcional
        anexo_opcional = get_object_or_404(AnexosDocsAlma, id_anexo_doc_alma=id_anexo_doc_alma, id_baja_activo=id_baja_activo)

        # Serializar el anexo opcional para incluir todos los datos
        serializer = self.serializer_class(anexo_opcional)

        # Eliminar el anexo opcional
        anexo_opcional.id_archivo_digital.ruta_archivo.delete()
        anexo_opcional.id_archivo_digital.delete()
        anexo_opcional.delete()

        return Response({'success': True, 'detail': 'Anexo opcional eliminado exitosamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class ListarAnexoOpcional(generics.ListAPIView):
    queryset = AnexosDocsAlma.objects.all()
    serializer_class = AnexosDocsAlmaSerializer

    def get_queryset(self):
        id_baja_activo = self.kwargs.get('id_baja_activo')
        return AnexosDocsAlma.objects.filter(id_baja_activo=id_baja_activo)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Anexos opcionales obtenidos exitosamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class BusquedaAvanzadaSolicitudesProcesos(generics.ListAPIView):
    serializer_class = BusquedaSolicitudActivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener parámetros de consulta
        estado_solicitud = self.request.query_params.get('estado_solicitud')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        id_persona_solicita = self.request.query_params.get('id_persona_solicita') 
        # Obtener el ID de la persona logueada
        persona_logueada = self.request.user.persona

        # Filtrar las solicitudes por estado y por persona responsable de la unidad
        queryset = SolicitudesActivos.objects.filter(id_funcionario_resp_unidad=persona_logueada)

        if estado_solicitud:
            queryset = queryset.filter(estado_solicitud=estado_solicitud)

        # Filtrar por id_persona_solicita si se proporciona
        if id_persona_solicita:
            queryset = queryset.filter(id_persona_solicita=id_persona_solicita)

        # Filtrar las solicitudes por rango de fechas
        if fecha_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_hasta)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Solicitudes obtenidas correctamente.',
            'data': serializer.data
        }
        return Response(data)




class RechazarSolicitud(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si la solicitud puede ser rechazada
        if instance.estado_solicitud != 'S':
            return Response({'success': False, 'detail': 'No se puede rechazar una solicitud que no esté en estado "S".'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtener la justificación de rechazo y la fecha actual
        justificacion_rechazo = request.data.get('justificacion_rechazo')
        fecha_actual = datetime.now()

        # Actualizar los campos de la solicitud
        instance.estado_aprobacion_resp = 'Re'
        instance.fecha_aprobacion_resp = fecha_actual
        instance.justificacion_rechazo_resp = justificacion_rechazo
        instance.revisada_responsable = True
        instance.estado_solicitud = 'SR'

        # Guardar los cambios en la base de datos
        instance.save()

        # Serializar y retornar la información actualizada
        serializer = self.serializer_class(instance)
        return Response({'success': True, 'detail': 'Solicitud rechazada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    


class AprobarSolicitud(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si la solicitud puede ser rechazada
        if instance.estado_solicitud != 'S':
            return Response({'success': False, 'detail': 'No se puede rechazar una solicitud que no esté en estado "S".'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtener la justificación de rechazo y la fecha actual
        justificacion_rechazo = request.data.get('justificacion_rechazo')
        fecha_actual = datetime.now()

        # Actualizar los campos de la solicitud
        instance.estado_aprobacion_resp = 'Ac'
        instance.fecha_aprobacion_resp = fecha_actual
        instance.revisada_responsable = True
        instance.estado_solicitud = 'SA'

        # Guardar los cambios en la base de datos
        instance.save()

        # Serializar y retornar la información actualizada
        serializer = self.serializer_class(instance)


        #generacion de alerta

        
        return Response({'success': True, 'detail': 'Solicitud aceptada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    


class ClasesTerceroPersonaSearchView(generics.ListAPIView):
    serializer_class = ClasesTerceroPersonaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ClasesTerceroPersona.objects.all()
        
        # Filtrar por tipo de documento
        tipo_documento = self.request.query_params.get('tipo_documento')
        # Filtrar por nombre
        nombre = self.request.query_params.get('nombre')
        # Filtrar por apellido
        apellido = self.request.query_params.get('apellido')
        # Filtrar por id_clase_tercero
        id_clase_tercero = self.request.query_params.get('id_clase_tercero')
        # Filtrar por id_clase_tercero
        numero_documento = self.request.query_params.get('numero_documento')


        if tipo_documento:
            queryset = queryset.filter(id_persona__tipo_documento=tipo_documento)
        
        
        if nombre:
            queryset = queryset.filter(id_persona__primer_nombre__icontains=nombre) | \
                       queryset.filter(id_persona__segundo_nombre__icontains=nombre)
            
        if apellido:
            queryset = queryset.filter(id_persona__primer_apellido__icontains=apellido) | \
                       queryset.filter(id_persona__segundo_apellido__icontains=apellido)
        
        if id_clase_tercero:
            queryset = queryset.filter(id_clase_tercero=id_clase_tercero)

        if numero_documento:
            queryset = queryset.filter(id_persona__numero_documento__icontains=numero_documento)
        
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Búsqueda exitosa', 'data': serializer.data})
    

class EntradasRelacionadasAlmacenListView(generics.ListAPIView):
    serializer_class = EntradasAlmacenSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        id_persona = self.kwargs['id_persona']  # Obtener el id_persona de los parámetros de la URL

        # Filtrar las entradas del almacén según las condiciones dadas
        queryset = EntradasAlmacen.objects.filter(
            Q(id_proveedor=id_persona) &  # El proveedor es igual al id_persona
            Q(id_tipo_entrada__in=[5, 6, 7, 8]) &  # El tipo de entrada está en la lista dada
            ~Q(id_bodega=None)  # La bodega no es NULL
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = serializer.data
        return Response({'success': True, 'detail': 'Información de entradas de almacén obtenida correctamente', 'data': data})
    


class ActivosAsociadosDetailView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_entrada_almacen):
        try:
            # Filtrar los registros en el modelo ItemEntradaAlmacen
            items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada_almacen)

            # Lista para almacenar los datos serializados de los registros encontrados
            serialized_data = []

            for item in items_entrada:
                # Filtrar el inventario por id_bien y realizo_salida=True
                inventario = Inventario.objects.filter(id_bien=item.id_bien.id_bien, realizo_salida=False).first()
                if inventario:
                    # Consultar el registro en el modelo CatalogoBienes
                    bien = item.id_bien

                    # Obtener el nombre de la marca
                    marca_nombre = None
                    if bien.id_marca:
                        marca_nombre = bien.id_marca.nombre

                    # Crear un diccionario con la información necesaria
                    data = {
                        'id_item_entrada_almacen': item.id_item_entrada_almacen,  # Pk de ItemEntradaAlmacen
                        'id_entrada_almacen': item.id_entrada_almacen.id_entrada_almacen,  # Fk de EntradaAlmacen
                        'id_bien': bien.id_bien,  # Pk de CatalogoBienes
                        'codigo': bien.codigo_bien,
                        'serial_placa': bien.doc_identificador_nro,
                        'nombre': bien.nombre,
                        'marca': marca_nombre,
                    }

                    # Agregar el diccionario a la lista de datos serializados
                    serialized_data.append(data)

            # Devolver la respuesta con los datos serializados y un mensaje de éxito
            return Response({'success': True, 'detail': 'Datos encontrados correctamente', 'data': serialized_data}, status=status.HTTP_200_OK)

        except ItemEntradaAlmacen.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron elementos'}, status=status.HTTP_404_NOT_FOUND)
        

        

class CrearSalidaEspecialView(generics.CreateAPIView):
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data
        anexos = request.FILES.getlist('anexo_opcional')
        anexos_data = data.get('anexos')
        current_date = datetime.now()


        # Crear registro en T088SalidasEspeciales_Articulos
        consecutivo_salida = SalidasEspecialesArticulos.objects.count() + 1
        referencia_salida = data.get('referencia_salida')
        concepto_salida = data.get('concepto_salida')
        id_entrada_almacen = data.get('id_entrada_almacen')

        salida_especial_data = {
            'consecutivo_por_salida': consecutivo_salida,
            'fecha_salida': current_date,
            'referencia_salida': referencia_salida,
            'concepto': concepto_salida,
            'id_entrada_almacen_ref': id_entrada_almacen
        }

        salida_especial_serializer = SalidasEspecialesArticulosSerializer(data=salida_especial_data)
        salida_especial_serializer.is_valid(raise_exception=True)
        salida_especial_obj = salida_especial_serializer.save()

        # Variable para almacenar el serializer_anexo
        serializer_anexo = None


        # Actualizar registros en T062Inventario
        activos_incluidos = data.get('activos_incluidos', "")
        
        if activos_incluidos == "":
            raise ValidationError ("Debe enviar minimo un activo.")
        
        for id_bien in activos_incluidos.split(","):
                
            # Obtener el objeto de inventario por su ID
            inventario_obj = get_object_or_404(Inventario, id_bien=id_bien)
            
            # Realizar las actualizaciones en el objeto de inventario
            inventario_obj.realizo_salida = True
            inventario_obj.ubicacion_en_bodega = False
            inventario_obj.fecha_ultimo_movimiento = current_date
            inventario_obj.tipo_doc_ultimo_movimiento = 'SAL_E'
            inventario_obj.id_registro_doc_ultimo_movimiento = None
            inventario_obj.save()

        if anexos_data and anexos:
            anexos_data = json.loads(data.get('anexos'))

            for index, (data_anexo, anexo) in enumerate(zip(anexos_data, anexos)):
                cont = index + 1
                # Validar formato de archivo
                archivo_nombre = anexo.name 
                nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
                extension_sin_punto = extension[1:] if extension.startswith('.') else extension
                
                formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
                
                if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
                    raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
                
                # Crear archivo en T238
                current_year = current_date.year
                ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

                md5_hash = hashlib.md5()
                for chunk in anexo.chunks():
                    md5_hash.update(chunk)

                md5_value = md5_hash.hexdigest()

                data_archivo = {
                    'es_Doc_elec_archivo': True,
                    'ruta': ruta,
                    'md5_hash': md5_value
                }
                
                archivo_class = ArchivosDgitalesCreate()
                respuesta = archivo_class.crear_archivo(data_archivo, anexo)
                # Crear registros en T087AnexosDocsAlma
                if isinstance(data_anexo, dict):
                    data_anexo['id_baja_activo'] = None
                    data_anexo['id_salida_espec_arti'] = salida_especial_obj.id_salida_espec_arti
                    data_anexo['fecha_creacion_anexo'] = current_date
                    data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
                    
                    serializer_anexo = self.serializer_class(data=data_anexo)
                    serializer_anexo.is_valid(raise_exception=True)
                    serializer_anexo.save()


        # Verifica si se ha creado un serializer_anexo
        if serializer_anexo:
            return Response({'success': True, 'detail': 'Archivo opcional creado exitosamente.', 'data': salida_especial_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'Archivo opcional creado exitosamente.','data': salida_especial_serializer.data}, status=status.HTTP_200_OK)


class ObtenerDatosSalidaEspecialView(generics.RetrieveAPIView):
    def retrieve(self, request, consecutivo, *args, **kwargs):
        # Buscar la salida especial por su consecutivo
        salida_especial = get_object_or_404(SalidasEspecialesArticulos, consecutivo_por_salida=consecutivo)
        
        # Serializar la salida especial
        salida_especial_serializer = SalidasEspecialesArticulosSerializer(salida_especial)
        
        # Buscar los anexos relacionados con la salida especial
        anexos = AnexosDocsAlma.objects.filter(id_salida_espec_arti=salida_especial.id_salida_espec_arti)
        
        # Serializar los anexos
        anexos_serializer = AnexosDocsAlmaSerializer(anexos, many=True)
        
        # Lista para almacenar la data de los archivos digitales
        archivos_digital_data = []

        # Iterar sobre los anexos y obtener los archivos digitales relacionados
        for anexo in anexos:
            archivo_digital = ArchivosDigitales.objects.filter(id_archivo_digital=anexo.id_archivo_digital_id).first()
            if archivo_digital:
                archivo_digital_serializer = ArchivosDigitalesSerializer(archivo_digital)
                archivos_digital_data.append(archivo_digital_serializer.data)

        # Obtener los bienes asociados a la entrada de almacén de referencia
        bienes_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=salida_especial.id_entrada_almacen_ref)
        
        # Serializar los bienes
        bienes_serializer = ItemEntradaAlmacenSerializer(bienes_entrada, many=True)

        # Obtener la primera entrada de almacén asociada a la salida especial
        primera_entrada_almacen = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=salida_especial.id_entrada_almacen_ref).first()
        
        # Lista para almacenar los datos de los proveedores
        proveedores_data = []

        # Obtener el nombre del proveedor asociado a la primera entrada de almacén
        if primera_entrada_almacen:
            proveedor = primera_entrada_almacen.id_entrada_almacen.id_proveedor
            if proveedor:
                proveedor_nombre = f"{proveedor.primer_nombre} {proveedor.segundo_nombre} {proveedor.primer_apellido} {proveedor.segundo_apellido}"
                proveedor_tipo_documento = proveedor.tipo_documento.cod_tipo_documento
                proveedor_numero_documento = proveedor.numero_documento
                proveedores_data.append({
                    'nombre': proveedor_nombre,
                    'tipo_documento': proveedor_tipo_documento,
                    'numero_documento': proveedor_numero_documento
        })

        
        # Devolver la información como respuesta
        return Response({
            'salida_especial': salida_especial_serializer.data,
            'informacion_tercero': proveedores_data, 
            'anexos': anexos_serializer.data, 
            'archivos_digitales': archivos_digital_data,
            'bienes': bienes_serializer.data,  
        }, status=status.HTTP_200_OK)




class ObtenerUltimoConsecutivoView(generics.ListAPIView):
    def get(self, request):
            # Obtener el último consecutivo en la base de datos
            ultimo_consecutivo = SalidasEspecialesArticulos.objects.all().order_by('-consecutivo_por_salida').first()
            if ultimo_consecutivo:
                ultimo_consecutivo = ultimo_consecutivo.consecutivo_por_salida + 1
            else:
                ultimo_consecutivo = 1  # Si no hay ningún registro, empezar desde 1
            
            # Devolver el último consecutivo incrementado en 1
            return Response({"success": True, "detail": "Último consecutivo obtenido correctamente.", "ultimo_consecutivo": ultimo_consecutivo}, status=status.HTTP_200_OK)
    



class InfoAlmcenistaPersonaGet(generics.ListAPIView):
    serializer_class = AlmacenistaLogueadoSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Obtener el ID de la persona logueada
        id_persona_logueada = self.request.user.persona.id_persona  # Suponiendo que la relación entre usuario y persona existe

        # Obtener los datos de la persona logueada
        persona_logueada = Personas.objects.filter(id_persona=id_persona_logueada).first()

        return persona_logueada

    def list(self, request, *args, **kwargs):
        persona_logueada = self.get_queryset()
        serializer = self.serializer_class(persona_logueada)
        return Response({'success': True, 'detail': 'Información de la persona logueada', 'data': serializer.data}, status=status.HTTP_200_OK)
    



class DespachosDeActivosListGet(generics.ListAPIView):
    serializer_class = DespachoActivosSerializer

    def get_queryset(self):
        id_persona = self.kwargs.get('id_persona')

        asignaciones = AsignacionActivos.objects.filter(
            id_funcionario_resp_asignado=id_persona,
            actual=True
        )

        if not asignaciones:
            return []
        
        despachos = [asignacion.id_despacho_asignado for asignacion in asignaciones]

        serializer_despachos = self.serializer_class(despachos, many=True)

 
        return serializer_despachos.data
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response({'success': True, 'detail': 'Despachos de activos encontrados', 'data': queryset}, status=status.HTTP_200_OK)


class ActivosDespachadosDevolucionView(generics.RetrieveAPIView):
    serializer_class = ActivosDespachadosDevolucionSerializer

    def retrieve(self, request, *args, **kwargs):
        # Obtener el ID del despacho de activos desde los parámetros de la URL
        id_despacho_activo = self.kwargs.get('id_despacho_activo')

        try:
            # Consultar los registros de ItemsDespachoActivos asociados al despacho
            items_despacho = ItemsDespachoActivos.objects.filter(id_despacho_activo=id_despacho_activo)
        except ItemsDespachoActivos.DoesNotExist:
            return Response({'success': False, 'detail': 'El despacho de activos especificado no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Serializar los registros encontrados
        serializer = self.serializer_class(items_despacho, many=True)

        # Retornar la respuesta con la data procesada
        return Response({'success': True, 'detail': 'Datos de los activos despachados', 'data': serializer.data})
    
class EstadosArticuloListView(generics.ListAPIView):
    queryset = EstadosArticulo.objects.all()
    serializer_class = EstadosArticuloSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Estados de artículo obtenidos correctamente', 'data': serializer.data})
    
# class DevolucionActivosCreateView(generics.CreateAPIView):
#     serializer_class = DevolucionActivosSerializer

#     def create(self, request, *args, **kwargs):
#         # Serializar los datos de la devolución de activos
#         devolucion_serializer = self.get_serializer(data=request.data)
#         devolucion_serializer.is_valid(raise_exception=True)
#         devolucion_data = devolucion_serializer.validated_data

#         # Obtener ID de unidad organizacional del solicitante
#         id_unidad_org_solicitante = devolucion_data.get('id_persona_devolucion').id_unidad_organizacional_actual.id_unidad_organizacional

#         # Validar la justificación si el estado seleccionado lo requiere
#         estado_seleccionado = devolucion_data.get('cod_estado_activo')
#         justificacion = devolucion_data.get('justificacion_anulacion')
#         if estado_seleccionado and estado_seleccionado != 'O' and not justificacion:
#             return Response({'success': False, 'detail': 'Debe proporcionar una justificación para el estado seleccionado'}, status=status.HTTP_400_BAD_REQUEST)

#         # Crear el registro de devolución de activos
#         devolucion_activos = DevolucionActivos.objects.create(**devolucion_data)

#         # Actualizar los campos en la tabla T092DevolucionActivos
#         devolucion_activos.devolucion_anulada = False
#         devolucion_activos.justificacion_anulacion = None
#         devolucion_activos.fecha_anulacion = None
#         devolucion_activos.id_persona_anulacion = None
#         devolucion_activos.consecutivo_devolucion = DevolucionActivos.objects.latest('id_devolucion_activos').id_devolucion_activos + 1  # Obtener el último consecutivo y asignar el siguiente
#         devolucion_activos.fecha_devolucion = datetime.now()
#         devolucion_activos.id_persona_devolucion = devolucion_data.get('id_persona_devolucion')  # Asignar el id de la persona que devolvió
#         devolucion_activos.id_uni_org_persona_devolucion = id_unidad_org_solicitante  # Asignar el id de la unidad organizacional del solicitante
#         devolucion_activos.save()

#         # Obtener los datos de los activos devueltos
#         activos_devueltos_data = request.data.get('activos_devueltos', [])

#         # Lista para almacenar los activos devueltos creados
#         activos_devueltos_creados = []

#         # Iterar sobre los datos de los activos devueltos
#         for activo_devuelto_data in activos_devueltos_data:
#             # Serializar los datos del activo devuelto
#             activo_devuelto_serializer = ActivosDevolucionadosSerializer(data=activo_devuelto_data)
#             activo_devuelto_serializer.is_valid(raise_exception=True)
#             activo_devuelto_data = activo_devuelto_serializer.validated_data

#             # Crear el registro de activo devuelto
#             activo_devuelto = ActivosDevolucionados.objects.create(devolucion_activo=devolucion_activos, **activo_devuelto_data)

#             # Actualizar el atributo se_Devolvio en el item del despacho de activos
#             item_despacho = activo_devuelto.item_despacho_activo
#             item_despacho.se_devolvio = True
#             item_despacho.save()

#             # Actualizar el estado y la ubicación del activo en el inventario
#             inventario_activo = activo_devuelto.item_despacho_activo.bien_despachado.inventario
#             inventario_activo.cod_estado_del_activo = activo_devuelto.cod_estado_activo_devol
#             inventario_activo.ubicacion_en_bodega = True
#             inventario_activo.fecha_ultimo_mov = devolucion_activos.fecha_devolucion
#             inventario_activo.tipo_doc_ultimo_mov = 'DEV'
#             inventario_activo.save()

#             # Agregar el activo devuelto creado a la lista
#             activos_devueltos_creados.append(activo_devuelto)

#         # Retornar la respuesta con los activos devueltos creados
#         return Response({'success': True, 
#                          'detail': 'Devolución de activos creada correctamente', 
#                          'data': {'id_devolucion_activos': devolucion_activos.id_devolucion_activos, 
#                                   'activos_devueltos': [activo.id for activo in activos_devueltos_creados]}}, status=status.HTTP_201_CREATED)


# class DevolucionActivosCreateView(generics.CreateAPIView):
#     serializer_class = DevolucionActivosSerializer

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         current_date = datetime.now()

#         # Obtener el último registro
#         ultimo_registro = DevolucionActivos.objects.last()

#         # Obtener el último consecutivo y sumarle 1
#         ultimo_consecutivo = ultimo_registro.consecutivo_devolucion if ultimo_registro else 0
#         nuevo_consecutivo = ultimo_consecutivo + 1

#         # Obtener el objeto de AsignacionActivos utilizando el id_asignacion_activos
#         id_despacho_asignado = data['id_despacho_asignado']
#         asignacion_activos = get_object_or_404(AsignacionActivos, pk=id_despacho_asignado)

#         # Obtener ID del responsable y del operario
#         id_persona_que_devuelve = data.get('id_persona_que_devuelve')
#         try:
#             persona_que_devuelve = Personas.objects.get(id_persona=id_persona_que_devuelve)
#             id_uni_org_persona_que_devuelve = persona_que_devuelve.id_unidad_organizacional_actual.id_unidad_organizacional
#         except Personas.DoesNotExist:
#             return Response({"success": False, 'detail': 'El usuario operario especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Crear registro en T092DevolucionActivos
#         devolucion_data = {
#             'id_asignacion_activo': asignacion_activos.id_asignacion_activos,
#             'id_despacho_activo': id_despacho_asignado,
#             'consecutivo_devolucion': nuevo_consecutivo,
#             'fecha_devolucion': current_date,
#             'id_persona_que_devuelve': id_persona_que_devuelve,
#             'id_unidad_organizacional_devolucion': id_uni_org_persona_que_devuelve,
#             'devolucion_anulada': False,
#             'justificacion_anulacion': None,
#             'fecha_anulacion': None,
#             'id_persona_que_anula': None
#         }

#         devolucion_serializer = self.get_serializer(data=devolucion_data)
#         devolucion_serializer.is_valid(raise_exception=True)
#         devolucion_obj = devolucion_serializer.save()

#         # Crear registro en T096ActivosDevolucionados
#         activos_devolucionados_data = data['activos_devolucionados']
#         for activo_devolucionado_data in activos_devolucionados_data:
#             activo_devolucionado_data['id_devolucion_activo'] = devolucion_obj.pk
#             activo_devolucionado_serializer = ActivosDevolucionadosSerializer(data=activo_devolucionado_data)
#             activo_devolucionado_serializer.is_valid(raise_exception=True)
#             activo_devolucionado_obj = activo_devolucionado_serializer.save()

#             # Actualizar registro en T093Items_DespachoActivos
#             id_item_despacho_activo = activo_devolucionado_data['id_item_despacho_activo']
#             item_despacho_activo = ItemsDespachoActivos.objects.get(pk=id_item_despacho_activo)
#             item_despacho_activo.se_devolvio = True
#             item_despacho_activo.save()

#             # Actualizar registro en T062Inventario
#             id_bien_despachado = activo_devolucionado_data['id_bien_despachado']
#             bien_despachado = CatalogoBienes.objects.get(pk=id_bien_despachado)
#             inventario_obj = Inventario.objects.get(id_bien=bien_despachado)
#             inventario_obj.cod_estado_activo = activo_devolucionado_obj.cod_estado_activo_devolucion
#             inventario_obj.ubicacion_en_bodega = True
#             inventario_obj.fecha_ultimo_movimiento = current_date
#             inventario_obj.tipo_doc_ultimo_movimiento = 'DEV'
#             inventario_obj.id_registro_doc_ultimo_movimiento = None
#             inventario_obj.save()

#         return Response({'success': True, 'detail': 'Devolución de activos creada exitosamente.', 'data': devolucion_serializer.data}, status=status.HTTP_201_CREATED)


class DevolucionActivosCreateView(generics.CreateAPIView):
    serializer_class = DevolucionActivosSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        current_date = datetime.now()
        persona_despacha_id = self.request.user.persona.id_persona

        # Obtener el id_devolucion_activo
        id_despacho_activo = data.get('id_despacho_activo')

        # Obtener el último registro de DevolucionActivos
        ultimo_registro = DevolucionActivos.objects.last()

        # Obtener el último consecutivo y sumarle 1
        ultimo_consecutivo = ultimo_registro.consecutivo_devolucion if ultimo_registro else 0
        nuevo_consecutivo = ultimo_consecutivo + 1

        # Obtener id_persona_devolucion
        id_persona_devolucion = data.get('id_persona_devolucion')
        try:
            persona_que_devuelve = Personas.objects.get(id_persona=id_persona_devolucion)
            id_uni_org_persona_que_devuelve = persona_que_devuelve.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario PERSONA DEVOLUCION especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
    
        # Obtener el id_asignacion_activo del último registro de AsignacionActivos
        ultimo_asignacion = AsignacionActivos.objects.last()
        if ultimo_asignacion:
            id_asignacion_activo = ultimo_asignacion.id_asignacion_activos
        else:
            return Response({"success": False, 'detail': 'No hay asignaciones de activos disponibles'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear registro en T092DevolucionActivos
        devolucion_data = {
            'id_asignacion_activo': id_asignacion_activo,
            'id_despacho_activo': id_despacho_activo,
            'consecutivo_devolucion': nuevo_consecutivo,
            'fecha_devolucion': current_date,
            'id_persona_devolucion': id_persona_devolucion,
            'id_uni_org_persona_devolucion': id_uni_org_persona_que_devuelve,
            'devolucion_anulada': False,
            'justificacion_anulacion': None,
            'fecha_anulacion': None,
            'id_persona_anulacion': None
        }

        devolucion_serializer = DevolucionActivosSerializer(data=devolucion_data)
        devolucion_serializer.is_valid(raise_exception=True)
        devolucion_obj = devolucion_serializer.save()


        #T096ActivosDevolucionados
        activos_devolucionados_data = data.get('activos_devolucionados', [])
        for activo_devolucionado_data in activos_devolucionados_data:
            activo_devolucionado_data['id_devolucion_activo'] = devolucion_obj.id_devolucion_activos
            activo_devolucionado_serializer = ActivosDevolucionadosSerializer(data=activo_devolucionado_data)
            activo_devolucionado_serializer.is_valid(raise_exception=True)
            activo_devolucionado_obj = activo_devolucionado_serializer.save()
            

            # Actualizar T093Items_DespachoActivos
            id_item_despacho_activo = activo_devolucionado_data.get('id_item_despacho_activo')
            print(id_item_despacho_activo)
            if id_item_despacho_activo:
                item_despacho_activo = ItemsDespachoActivos.objects.get(id_item_despacho_activo=id_item_despacho_activo)
                item_despacho_activo.se_devolvio = True
                item_despacho_activo.save()

            # Actualizar T062Inventario
            id_bien_despachado = activo_devolucionado_data.get('id_bien_despachado')
            if id_bien_despachado:
                bien_despachado = CatalogoBienes.objects.get(pk=id_bien_despachado)
                inventario_obj = Inventario.objects.get(id_bien=bien_despachado)
                inventario_obj.cod_estado_activo = activo_devolucionado_obj.cod_estado_activo_devolucion
                inventario_obj.ubicacion_en_bodega = True
                inventario_obj.fecha_ultimo_movimiento = current_date
                inventario_obj.tipo_doc_ultimo_movimiento = 'DEV'
                inventario_obj.id_registro_doc_ultimo_movimiento = None
                inventario_obj.save()

        return Response({'success': True, 'detail': 'Despacho de activo creado exitosamente.'}, status=status.HTTP_201_CREATED)
    

class ObtenerUltimoConsecutivoDevolucionView(generics.ListAPIView):
    def get(self, request):
            # Obtener el último consecutivo en la base de datos
            ultimo_consecutivo = DevolucionActivos.objects.all().order_by('-consecutivo_devolucion').first()
            if ultimo_consecutivo:
                ultimo_consecutivo = ultimo_consecutivo.consecutivo_devolucion + 1
            else:
                ultimo_consecutivo = 1  # Si no hay ningún registro, empezar desde 1
            
            # Devolver el último consecutivo incrementado en 1
            return Response({"success": True, "detail": "Último consecutivo obtenido correctamente.", "ultimo_consecutivo": ultimo_consecutivo}, status=status.HTTP_200_OK)
    



class ObtenerDatosDevolucionActivos(generics.RetrieveAPIView):
    def retrieve(self, request, consecutivo, *args, **kwargs):
        # Buscar la devolución de activos por su consecutivo
        devolucion_activos = get_object_or_404(DevolucionActivos, consecutivo_devolucion=consecutivo)
        
        # Serializar la devolución de activos
        devolucion_activos_serializer = DevolucionActivosSerializer(devolucion_activos)

        # Buscar los activos devueltos asociados a esta devolución
        activos_devueltos = ActivosDevolucionados.objects.filter(id_devolucion_activo=devolucion_activos.id_devolucion_activos)
        
        # Serializar los activos devueltos
        activos_devueltos_serializer = ActivosDevolucionadosSerializer(activos_devueltos, many=True)

        # Obtener información del id_item_despacho_activo para cada activo devuelto
        item_despacho_activos_data = []
        for activo_devuelto in activos_devueltos:
            item_despacho_activo = activo_devuelto.id_item_despacho_activo
            if item_despacho_activo:
                item_despacho_activo_serializer = ItemsDespachoActivosSerializer(item_despacho_activo)
                item_despacho_activos_data.append(item_despacho_activo_serializer.data)

        # Obtener la información de id_despacho_activo
        id_despacho_activo = devolucion_activos.id_despacho_activo
        if id_despacho_activo:
            despacho_activos_serializer = DespachoActivosSerializer(id_despacho_activo)
            id_despacho_activo_data = despacho_activos_serializer.data
        else:
            id_despacho_activo_data = None

        # Devolver la información como respuesta
        return Response({
            'success': True,
            'detail': 'Devolución de activos encontrada exitosamente.',
            'devolucion_activos': devolucion_activos_serializer.data,
            'activos_devueltos': activos_devueltos_serializer.data,
            'item_despacho_activos': item_despacho_activos_data,
            'despacho_activo': id_despacho_activo_data
        }, status=status.HTTP_200_OK)

# class ObtenerDatosDevolucionActivos(generics.RetrieveAPIView):
#     def retrieve(self, request, consecutivo, *args, **kwargs):
#         # Buscar la salida especial por su consecutivo
#         salida_especial = get_object_or_404(DevolucionActivos, consecutivo_devolucion=consecutivo)
        
#         # Serializar la salida especial
#         salida_especial_serializer = SalidasEspecialesArticulosSerializer(salida_especial)
        
#         # Buscar los anexos relacionados con la salida especial
#         anexos = AnexosDocsAlma.objects.filter(id_salida_espec_arti=salida_especial.id_salida_espec_arti)
        
#         # Serializar los anexos
#         anexos_serializer = AnexosDocsAlmaSerializer(anexos, many=True)
        
#         # Lista para almacenar la data de los archivos digitales
#         archivos_digital_data = []

#         # Iterar sobre los anexos y obtener los archivos digitales relacionados
#         for anexo in anexos:
#             archivo_digital = ArchivosDigitales.objects.filter(id_archivo_digital=anexo.id_archivo_digital_id).first()
#             if archivo_digital:
#                 archivo_digital_serializer = ArchivosDigitalesSerializer(archivo_digital)
#                 archivos_digital_data.append(archivo_digital_serializer.data)

#         # Obtener los bienes asociados a la entrada de almacén de referencia
#         bienes_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=salida_especial.id_entrada_almacen_ref)
        
#         # Serializar los bienes
#         bienes_serializer = ItemEntradaAlmacenSerializer(bienes_entrada, many=True)

#         print("bienes encontrados:", bienes_serializer)
      
        
#         # Devolver la información como respuesta
#         return Response({
#             'salida_especial': salida_especial_serializer.data,
#             'anexos': anexos_serializer.data,  # Agregar los anexos serializados
#             'archivos_digitales': archivos_digital_data,
#             'bienes': bienes_serializer.data,  # Agregar los bienes serializados
#         }, status=status.HTTP_200_OK)




class DevolucionActivosUpdateView(generics.UpdateAPIView):
    serializer_class = DevolucionActivosSerializer
    queryset = DevolucionActivos.objects.all()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        current_date = datetime.now()
        persona_que_anula_id = self.request.user.persona.id_persona

        # Actualizar registro en T092DevolucionActivos
        instance.devolucion_anulada = True
        instance.justificacion_anulacion = data.get('justificacion_anulacion')
        instance.fecha_anulacion = current_date
        instance.id_persona_que_anula = persona_que_anula_id
        instance.save()

        # Obtener los registros de T096ActivosDevolucionados relacionados
        activos_devueltos = ActivosDevolucionados.objects.filter(id_devolucion_activo=instance.id_activo_devolucionado)

        for activo_devuelto in activos_devueltos:
            # Actualizar registro en T093Items_DespachoActivos
            item_despacho_activo = ItemsDespachoActivos.objects.get(pk=activo_devuelto.id_item_despacho_activo)
            item_despacho_activo.se_devolvio = False
            item_despacho_activo.save()

            # Obtener el registro de T057CatalogoBienes y T062Inventario relacionados
            bien_despachado = CatalogoBienes.objects.get(pk=activo_devuelto.id_bien_despachado_id)
            inventario_obj = Inventario.objects.get(id_bien=bien_despachado)

            # Actualizar campos en el inventario
            inventario_obj.cod_estado_activo = bien_despachado.cod_estado_activo
            inventario_obj.ubicacion_en_bodega = True
            inventario_obj.fecha_ultimo_movimiento = current_date
            inventario_obj.tipo_doc_ultimo_movimiento = 'DEV'
            inventario_obj.id_registro_doc_ultimo_movimiento = None
            inventario_obj.save()

        return Response({'success': True, 'detail': 'Devolución anulada exitosamente.'}, status=status.HTTP_200_OK)



class BusquedaAvanzadaSolicitudesDespacho(generics.ListAPIView):
    serializer_class = BusquedaSolicitudActivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener parámetros de consulta
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        id_persona_solicita = self.request.query_params.get('id_persona_solicita') 
        # Obtener el ID de la persona logueada
        persona_logueada = self.request.user.persona

        # Filtrar las solicitudes por estado y por persona responsable de la unidad
        queryset = SolicitudesActivos.objects.filter(id_funcionario_resp_unidad=persona_logueada)

        # Filtrar las solicitudes por estado_solicitud
        queryset = queryset.filter(estado_solicitud__in=['R', 'SA', 'DA', 'DR'])

        # Filtrar por id_persona_solicita si se proporciona
        if id_persona_solicita:
            queryset = queryset.filter(id_persona_solicita=id_persona_solicita)

        # Filtrar las solicitudes por rango de fechas
        if fecha_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_hasta)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Solicitudes obtenidas correctamente.',
            'data': serializer.data
        }
        return Response(data)


class CancelarSolicitudDespacho(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Obtener el ID de la solicitud de la URL
        solicitud_id = kwargs.get('pk')
        
        
        # Obtener la instancia de la solicitud
        try:
            solicitud = SolicitudesActivos.objects.get(id_solicitud_activo=solicitud_id)
        except SolicitudesActivos.DoesNotExist:
            return Response({'detail': 'La solicitud especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si la solicitud está en estado "Solicitud Autorizada"
        if solicitud.estado_solicitud != 'SA':
            return Response({'detail': 'Solo se puede cancelar una solicitud que esté en estado "Solicitud Autorizada".'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar los datos de la solicitud
        solicitud.estado_solicitud = 'F'
        solicitud.fecha_cierra_solicitud = datetime.now()
        solicitud.gestionada_alma = True
        solicitud.rechazada_almacen = True
        solicitud.fecha_rechazo_almacen = datetime.now()
        solicitud.justificacion_rechazo_almacen = request.data.get('justificacion_rechazo_almacen')
       # Obtener la instancia de la persona actual
        usuario_actual = request.user
        persona_actual = usuario_actual.persona
        
        # Asignar la instancia de persona actual a id_persona_alma_rechaza
        solicitud.id_persona_alma_rechaza = persona_actual
        
        # Guardar los cambios en la base de datos
        solicitud.save()
        
        # Serializar y retornar la solicitud actualizada
        serializer = self.serializer_class(solicitud)
        return Response({'detail': 'La solicitud se ha cancelado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class AnularSolicitudDespacho(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Obtener el ID de la solicitud de la URL
        solicitud_id = kwargs.get('pk')
        
        # Obtener la instancia de la solicitud
        try:
            solicitud = SolicitudesActivos.objects.get(id_solicitud_activo=solicitud_id)
        except SolicitudesActivos.DoesNotExist:
            return Response({'detail': 'La solicitud especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si la solicitud está en estado "Respondida"
        if solicitud.estado_solicitud != 'R':
            return Response({'detail': 'Solo se puede anular una solicitud que esté en estado "Respondida".'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar los datos de la solicitud
        solicitud.estado_solicitud = 'F'
        solicitud.fecha_cierra_solicitud = datetime.now()
        solicitud.save()
        
        # Obtener el despacho asociado a la solicitud
        despacho = solicitud.despachoactivos_set.first()
        
        # Verificar si el despacho existe y aún no ha sido anulado
        if despacho and not despacho.despacho_anulado:
            # Actualizar los datos del despacho
            despacho.despacho_anulado = True
            despacho.justificacion_anulacion = request.data.get('justificacion_anulacion')
            despacho.fecha_anulacion = datetime.now()
            # Obtener la instancia de la persona actual
            usuario_actual = request.user
            persona_actual = usuario_actual.persona
            # Asignar la instancia de la persona actual a Id_PersonaAnula
            despacho.id_persona_anula = persona_actual
            # Guardar los cambios en el despacho
            despacho.save()
        
        # Serializar y retornar la solicitud actualizada
        serializer = self.serializer_class(solicitud)
        return Response({'detail': 'La solicitud y el despacho asociado se han anulado correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ObtenerDatosPersonasSolicitud(generics.RetrieveAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id_solicitud_activo'  # Este es el nombre del campo que se utilizará en la URL

    def retrieve(self, request, *args, **kwargs):
        try:
            instancia = self.get_object()
            serializer = self.get_serializer(instancia)
            return Response({'success': True, 'detail': 'Solicitud obtenida correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'detail': 'No se pudo encontrar la solicitud especificada.'}, status=status.HTTP_404_NOT_FOUND)
        

class BusquedaAvanzadaBodegas(generics.ListAPIView):
    serializer_class = BodegasSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Bodegas.objects.all()
        nombre = self.request.query_params.get('nombre')
        cod_municipio = self.request.query_params.get('cod_municipio')

        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        if cod_municipio:
            queryset = queryset.filter(cod_municipio=cod_municipio)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Bodegas obtenidas correctamente.',
            'data': serializer.data
        }
        return Response(data)
    

class DespachosSinSolicitudGet(generics.ListAPIView):
    serializer_class = DespachoSinSolicitudSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener el usuario logueado actualmente
        usuario_actual = self.request.user

        # Obtener el ID de la persona asociada al usuario
        id_persona_despacha = usuario_actual.persona.id_persona

        # Obtener los parámetros de la consulta
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        persona_responsable = self.request.query_params.get('persona_responsable')
        estado_despacho = self.request.query_params.get('estado_despacho')

        # Construir el queryset inicial filtrando los despachos por persona y despacho sin solicitud
        queryset = DespachoActivos.objects.filter(id_persona_despacha=id_persona_despacha, despacho_sin_solicitud=True)

        # Aplicar filtros adicionales si se proporcionan
        if fecha_desde:
            queryset = queryset.filter(fecha_despacho__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_despacho__lte=fecha_hasta)
        if persona_responsable:
            queryset = queryset.filter(id_persona_despacha=persona_responsable)
        if estado_despacho:
            queryset = queryset.filter(estado_despacho=estado_despacho)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Despachos sin solicitud obtenidos correctamente.',
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    

    
class BusquedaArticulosPrincipalView(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer

    def get(self, request, solicitud_id):
        try:
            # Verificar si la solicitud de activos existe
            solicitud = SolicitudesActivos.objects.get(id_solicitud_activo=solicitud_id)
        except SolicitudesActivos.DoesNotExist:
            return Response({'success': False, 'detail': 'La solicitud de activos especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener los items de la solicitud de activos
        items_solicitud = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=solicitud)

        # Inicializar una lista para almacenar los datos de los items
        items_data = []

        # Iterar sobre los items de la solicitud y obtener la información necesaria
        for item in items_solicitud:
            # Obtener el código del bien solicitado
            codigo_bien = item.id_bien.codigo_bien

            # Obtener el nombre del bien solicitado
            nombre_bien = item.id_bien.nombre

            # Concatenar la cantidad solicitada y la unidad de medida
            cantidad_solicitada = f"{item.cantidad} {item.id_unidad_medida.nombre}" if item.id_unidad_medida else str(item.cantidad)

            # Obtener la fecha de devolución si es una solicitud de préstamo
            fecha_devolucion = item.fecha_devolucion if solicitud.solicitud_prestamo else None

            # Obtener las observaciones
            observaciones = item.observacion

            # Agregar los datos del item a la lista
            items_data.append({
                'id_item_solicitud_activo': item.id_item_solicitud_activo,
                'id_solicitud_activo': item.id_solicitud_activo.id_solicitud_activo,
                "id_bien": item.id_bien.id_bien,
                'codigo_bien': codigo_bien,
                'nombre_bien': nombre_bien,
                'id_unidad_medida': item.id_unidad_medida.id_unidad_medida,
                'nombre_unidad_medida': item.id_unidad_medida.nombre,
                'abreviatura_unidad_medida': item.id_unidad_medida.abreviatura,
                'cantidad_solicitada': cantidad_solicitada,
                'fecha_devolucion': fecha_devolucion,
                'observaciones': observaciones
            })

        # Preparar la respuesta JSON con los datos de los items y el mensaje de éxito
        response_data = {
            'success': True,
            'detail': 'Items de la solicitud de activos obtenidos correctamente.',
            'items': items_data
        }

        # Devolver la respuesta JSON
        return Response(response_data)
    

class BusquedaArticulosSubView(generics.ListAPIView):
    serializer_class = BusquedaArticuloSubSerializer  # Utiliza tu serializer personalizado

    def get_queryset(self):
        id_bien = self.kwargs['id_bien']  # Suponiendo que pasas el ID del bien como parte de la URL

        # Obtener el ID de la solicitud de activos filtrando por el ID del bien
        solicitud_id = ItemsSolicitudActivos.objects.filter(id_bien=id_bien).first().id_solicitud_activo

        # Obtener el ID del bien solicitado de la tabla ItemsSolicitudActivos
        id_bien_solicitado = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=solicitud_id).values_list('id_bien', flat=True)

        # Filtrar los registros de CatalogoBienes que tengan id_bien_padre igual al ID del bien solicitado
        bienes_coincidentes = CatalogoBienes.objects.filter(id_bien_padre__in=id_bien_solicitado)

        # Inicializar una lista para almacenar los datos que serán serializados
        queryset = []

        # Iterar sobre los bienes coincidentes para obtener la información necesaria
        for bien in bienes_coincidentes:
            # Obtener la cantidad de artículos despachados (siempre será 1)
            cantidad_despachada = 1

            # Obtener las observaciones del item
            observaciones = ItemsSolicitudActivos.objects.filter(id_bien=bien.id_bien, id_solicitud_activo=solicitud_id).values_list('observacion', flat=True).first()

            # Obtener el nombre de la bodega desde el modelo Inventario
            nombre_bodega = Inventario.objects.filter(id_bien=bien.id_bien).values_list('id_bodega__nombre', flat=True).first()

            # Crear un diccionario con la información recopilada
            item_data = {
                'id_bien_despachado': bien.id_bien,
                'codigo_bien_espachado': bien.codigo_bien,
                'nombre_bien_espachado': bien.nombre,
                'cantidad_despachada': cantidad_despachada,
                'observaciones': observaciones,
                'nombre_bodega': nombre_bodega
            }

            # Agregar el diccionario a la lista de queryset
            queryset.append(item_data)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            # Si se encontraron elementos, devolver respuesta exitosa
            return Response({'success': True, 'detail': 'Items obtenidos correctamente.', 'items': queryset})
        else:
            # Si no se encontraron elementos, devolver respuesta de no encontrado
            return Response({'success': False, 'detail': 'No se encontraron items para este ID de bien.'}, status=status.HTTP_404_NOT_FOUND)
        
    


class CrearDespachoActivosView(generics.CreateAPIView):
    serializer_class = DespachoActivosSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        fecha_solicitud = datetime.now()
        anexo = request.FILES.get('anexo_opcional')
        current_date = datetime.now()
        persona_despacha_id = self.request.user.persona.id_persona

        # Obtener el ID de la solicitud si existe
        solicitud_id = data.get('id_solicitud_activo')

        # Determinar el valor de T089despachoSinSolicitud
        if solicitud_id:
            despacho_sin_solicitud = False
        else:
            despacho_sin_solicitud = True

        print(despacho_sin_solicitud)

        # Obtener la fecha de solicitud si existe la solicitud
        fecha_solicitud = None
        id_persona_solicita = None
        if solicitud_id:
            try:
                solicitud = SolicitudesActivos.objects.get(id_solicitud_activo=solicitud_id)
                fecha_solicitud = solicitud.fecha_solicitud  # Suponiendo que el campo en el modelo sea "fecha_solicitud2"
                id_persona_solicita = solicitud.id_persona_solicita.id_persona
            except SolicitudesActivos.DoesNotExist:
                pass

        id_archivo_doc_recibido = None

        if anexo:

            # Validar formato de archivo
            archivo_nombre = anexo.name 
            nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            
            formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)

            
            if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
                raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
            
            # Crear archivo en T238
            current_year = current_date.year
            ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

            md5_hash = hashlib.md5()
            for chunk in anexo.chunks():
                md5_hash.update(chunk)

            md5_value = md5_hash.hexdigest()

            data_archivo = {
                'es_Doc_elec_archivo': True,
                'ruta': ruta,
                'md5_hash': md5_value
            }
            
            archivo_class = ArchivosDgitalesCreate()
            respuesta = archivo_class.crear_archivo(data_archivo, anexo)


            id_archivo_doc_recibido = respuesta.data.get('data').get('id_archivo_digital')


        # Crear registro en T089DespachoActivos
        despacho_data = {
            'fecha_solicitud': fecha_solicitud,
            'fecha_despacho': current_date,
            'id_persona_despacha': persona_despacha_id,
            'observacion': data.get('observacion'),
            'estado_despacho': 'Ep',
            'id_bodega': data.get('id_bodega'),
            'id_archivo_doc_recibido': id_archivo_doc_recibido,  # Será actualizado después
            'despacho_sin_solicitud': despacho_sin_solicitud,  
            'id_persona_solicita': id_persona_solicita 
        }

        # Agregar T089Id_SolicitudActivo si corresponde
        if solicitud_id:
            despacho_data['id_solicitud_activo'] = solicitud_id
        else:
            despacho_data['id_solicitud_activo'] = None
            
        despacho_serializer = DespachoActivosCreateSerializer(data=despacho_data)
        despacho_serializer.is_valid(raise_exception=True)
        despacho_obj = despacho_serializer.save()
    
        # Obtener ID del responsable y del operario
        id_funcionario_resp_asignado = data.get('id_funcionario_resp_asignado')
        try:
            funcionario_resp_asignado = Personas.objects.get(id_persona=id_funcionario_resp_asignado)
            id_uni_org_funcionario_resp_asignado = funcionario_resp_asignado.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario operario especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        id_persona_operario_asignado = data.get('id_persona_operario_asignado')
        try:
            persona_operario_asignado = Personas.objects.get(id_persona=id_persona_operario_asignado)
            id_uni_org_operario_asignado = persona_operario_asignado.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario operario especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        
        # Crear registro en T095AsignacionActivos
        asignacion_data = {
            'id_despacho_asignado': despacho_obj.id_despacho_activo,
            'id_funcionario_resp_asignado': id_funcionario_resp_asignado,  # Suponiendo que responsable_id contiene el ID del responsable
            'id_uni_org_funcionario_resp_asignado': id_uni_org_funcionario_resp_asignado,
            'id_persona_operario_asignado': id_persona_operario_asignado,  # Suponiendo que operario_id contiene el ID del operario
            'id_uni_org_operario_asignado': id_uni_org_operario_asignado,
            'actual': True,
            'fecha_asignacion': current_date,
        }

        asignacion_serializer = AsignacionActivosSerializer(data=asignacion_data)
        asignacion_serializer.is_valid(raise_exception=True)
        asignacion_obj = asignacion_serializer.save()

        

        # Obtener la lista de bienes despachados
        bienes_despachados = data.get('bienes_despachados', [])

        if not bienes_despachados:
            raise ValidationError ("Debe enviar minimo 1 bien despachado.")
        
        bienes_despachados = json.loads(data.get('bienes_despachados'))

        
        bienes_no_despachados = [bien for bien in bienes_despachados if not bien['id_bien_despachado'] ]
        if len(bienes_no_despachados) == len(bienes_despachados):
            raise ValidationError("Debe realizar minimo tener un bien de despacho.")

        # Iterar sobre cada bien despachado
        for bien_despachado in bienes_despachados:
            # Obtener el ID del bien despachado
            id_bien_despachado = bien_despachado.get('id_bien_despachado')
            
            print(bien_despachado)
            # Obtener el ID de la entrada del almacén del bien
            entrada_almacen_del_bien_id = None
            if id_bien_despachado:
                try:
                    # Suponiendo que existe un modelo T064Items_EntradaAlmacen para buscar la entrada del almacén del bien
                    entrada_almacen = ItemEntradaAlmacen.objects.get(id_bien=id_bien_despachado)
                    entrada_almacen_del_bien_id = entrada_almacen.id_entrada_almacen.id_entrada_almacen
                except ItemEntradaAlmacen.DoesNotExist:
                    raise ValidationError ("No posee una entrada de almancen")

            # Obtener la cantidad solicitada del modelo ItemsSolicitudActivos
            cantidad_solicitada = None
            id_unidad_medida_solicitada = None
            fecha_devolucion = None
            observacion_item = None

            try:
                # Suponiendo que existe un modelo ItemsSolicitudActivos con un atributo T091cantidad
                items_solicitud_activos = ItemsSolicitudActivos.objects.get(id_solicitud_activo=solicitud_id ,id_bien=bien_despachado.get('id_bien_solicitado'))
                cantidad_solicitada = items_solicitud_activos.cantidad
                id_unidad_medida_solicitada = items_solicitud_activos.id_unidad_medida.id_unidad_medida
                fecha_devolucion = items_solicitud_activos.fecha_devolucion

            except ItemsSolicitudActivos.DoesNotExist:
                raise ValidationError ("Item de solicitud de activos no existe.")
        


            # Crear el registro en T093Items_DespachoActivos
            item_despacho_data = {
                'id_despacho_activo': despacho_obj.id_despacho_activo,
                'id_bien_solicitado': bien_despachado.get('id_bien_solicitado'),
                'id_bien_despachado': id_bien_despachado,
                'id_entrada_alma': entrada_almacen_del_bien_id,
                'id_bodega': bien_despachado.get('id_bodega'),
                'cantidad_solicitada': cantidad_solicitada,
                'id_uni_medida_solicitada': id_unidad_medida_solicitada,
                'cantidad_despachada': 1 if id_bien_despachado else 0,
                'fecha_devolucion': fecha_devolucion,
                'se_devolvio': False,
                'observacion': bien_despachado.get('observacion'),
                'nro_posicion_despacho': bien_despachado.get('nro_posicion_despacho')
            }
            
            print (item_despacho_data['id_bien_despachado'])
            print (item_despacho_data['cantidad_despachada'])
            print (item_despacho_data['id_bodega'])
            print (item_despacho_data['observacion'])
            item_despacho_serializer = ItemsDespachoActivosSerializer(data=item_despacho_data)
            item_despacho_serializer.is_valid(raise_exception=True)
            item_despacho_serializer.save()

        
        # Realizar las actualizaciones en el modelo SolicitudesActivos si existe solicitud_id
        if solicitud_id:
            solicitud = get_object_or_404(SolicitudesActivos, pk=solicitud_id)
            solicitud.estado_solicitud = 'R'  # Actualizar estado a 'Respondido'
            solicitud.gestionada_alma = True  # Actualizar gestionadaAlmacen a True
            solicitud.save()

        # # Obtener el ID de la bodega del despacho
        # id_bodega_despacho = despacho_data['id_bodega']

        # # Realizar las actualizaciones en el modelo Inventario si existe id_bodega_despacho
        # if id_bodega_despacho:
        #     inventarios = Inventario.objects.filter(id_bodega=id_bodega_despacho)
        #     for inventario in inventarios:
        #         # Actualizar los atributos según lo indicado
        #         inventario.ubicacion_en_bodega = False
        #         inventario.fecha_ultimo_movimiento = current_date

        #         # Verificar si la solicitud es de préstamo
        #         if not solicitud_id or (solicitud_id and not solicitud.solicitud_prestamo):
        #             inventario.ubicacion_asignado = True
        #             tipo_doc_ultimo_movimiento = 'ASIG'
        #         else:
        #             inventario.ubicacion_asignado = False
        #             tipo_doc_ultimo_movimiento = 'PRES'

        #         # Guardar el ID de la persona responsable y el tipo de documento último movimiento
        #         inventario.id_persona_responsable = funcionario_resp_asignado
        #         inventario.tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento

        #         # Guardar los cambios en el inventario
        #         inventario.save()
            

        return Response({'success': True, 'detail': 'Despacho de activo creado exitosamente.'}, status=status.HTTP_201_CREATED)
    
    



