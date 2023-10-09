from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
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
    BusquedaCCDSerializer,
    BusquedaCCDHomologacionSerializer,
    SeriesDocUnidadHomologacionesSerializer,
    SeriesDocUnidadCatSerieHomologacionesSerializer,
    UnidadesSeccionPersistenteTemporalSerializer,
    AgrupacionesDocumentalesPersistenteTemporalSerializer,
    UnidadesSeccionResponsableTemporalSerializer,
    UnidadesSeccionResponsableTemporalGetSerializer
)
from transversal.models.organigrama_models import Organigramas
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad,
    UnidadesSeccionPersistenteTemporal,
    AgrupacionesDocumentalesPersistenteTemporal,
    UnidadesSeccionResponsableTemporal
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso
)

import copy

from transversal.serializers.organigrama_serializers import UnidadesGetSerializer

class CreateCuadroClasificacionDocumental(generics.CreateAPIView):
    serializer_class = CCDPostSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        #Validación de seleccionar solo organigramas terminados
        organigrama_instance = Organigramas.objects.filter(id_organigrama=data['id_organigrama']).first()
        if organigrama_instance:
            if organigrama_instance.fecha_terminado == None:
                raise PermissionDenied('No se pueden seleccionar organigramas que no estén terminados')
            
            unidades_organigrama = organigrama_instance.unidadesorganizacionales_set.exclude(cod_agrupacion_documental=None)
            if not unidades_organigrama:
                raise ValidationError('Solo puede elegir organigramas que tengan unidades marcadas como sección o subsección')
            
            serializador = serializer.save()

            #Auditoria Crear Cuadro de Clasificación Documental
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(serializador.nombre), "Versión": str(serializador.version)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 27,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            
            return Response({'success':True, 'detail':'Cuadro de Clasificación Documental creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('Debe elegir un organigrama que exista')

class UpdateCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDPutSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        data = request.data
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        
        # VALIDACIONES CCD
        if not ccd:
            raise ValidationError('El CCD ingresado no existe')
        elif ccd.fecha_terminado:
            raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif ccd.fecha_retiro_produccion or ccd.id_organigrama.fecha_retiro_produccion:
            raise PermissionDenied('No puede realizar esta acción en un CCD retirado de producción o en un CCD cuya construcción está basada en un organigrama que ya fue sacado de circulación')
        elif ccd.actual:
            raise PermissionDenied('No se pueden realizar operaciones en un CCD actual')

        elif not ccd.fecha_terminado:
            previoud_ccd = copy.copy(ccd)
            serializer = self.serializer_class(ccd, data=data)
            serializer.is_valid(raise_exception=True)
            
            # Validar que el nuevo nombre del CCD no esté en uso
            nuevo_nombre = data.get('nombre', ccd.nombre)
            if  CuadrosClasificacionDocumental.objects.filter(nombre=nuevo_nombre).exclude(id_ccd=ccd.id_ccd).exists():
                 raise ValidationError('Ya existe un CCD con el nombre ingresado. Por favor ingrese un nombre diferente')

            # Validar que la nueva versión del CCD no esté en uso
            nueva_version = data.get('version', ccd.version)
            if CuadrosClasificacionDocumental.objects.filter(version=nueva_version).exclude(id_ccd=ccd.id_ccd).exists():
                 raise ValidationError('Ya existe un CCD con la versión ingresada. Por favor ingrese una versión diferente')

            series = ccd.seriesdoc_set.all()
            
            valor_aumento_serie = data.get('valor_aumento_serie')
            valor_aumento_subserie = data.get('valor_aumento_subserie')
            
            # Verificar si se intentó cambiar el organigrama
            nuevo_organigrama = data.get('id_organigrama', ccd.id_organigrama.id_organigrama)
            if int(nuevo_organigrama) != ccd.id_organigrama.id_organigrama:
                raise ValidationError('No puede cambiar el organigrama utilizado para crear el CCD')
    
            # CAMBIAR CODIGO DE LA ÚNICA SERIE
            if valor_aumento_serie and int(valor_aumento_serie) != ccd.valor_aumento_serie:
                if series:
                    primera_serie = series.first()
                    primera_serie.codigo = int(valor_aumento_serie)
                    primera_serie.save()
                
            # CAMBIAR CODIGO DE LAS ÚNICAS SUBSERIES
            if valor_aumento_subserie and int(valor_aumento_subserie) != ccd.valor_aumento_subserie:
                for serie in series:
                    primera_subserie = serie.subseriesdoc_set.all().first()
                    if primera_subserie:
                        primera_subserie.codigo = int(valor_aumento_subserie)
                        primera_subserie.save()
            
            serializer.save()
                
            # AUDITORIA DE UPDATE DE CCD
            user_logeado = request.user.id_usuario
            dirip = Util.get_client_ip(request)
            descripcion = {'nombre':str(previoud_ccd.nombre), 'version':str(previoud_ccd.version)}
            valores_actualizados={'previous':previoud_ccd, 'current':ccd}
            auditoria_data = {
                'id_usuario': user_logeado,
                'id_modulo': 27,
                'cod_permiso': 'AC',
                'subsistema': 'GEST',
                'dirip': dirip,
                
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            
        return Response({'success':True, 'detail':'Cuadro de Clasificación Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class FinalizarCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDActivarSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        ccd = self.queryset.all().filter(id_ccd=pk).first()
        
        # VALIDACIONES CCD
        if not ccd:
            raise ValidationError('El CCD ingresado no existe')
        elif ccd.fecha_terminado:
            raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif ccd.fecha_retiro_produccion:
            raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
        elif not ccd.ruta_soporte:
            raise PermissionDenied('No puede finalizar un CCD sin antes haber adjuntado un archivo de soporte')
        
        series = SeriesDoc.objects.filter(id_ccd=pk)
        series_list = [serie.id_serie_doc for serie in series]
        
        cat_series_subseries = CatalogosSeries.objects.filter(id_serie_doc__id_ccd=pk)
        cat_series_subseries_list = [cat_serie_subserie.id_catalogo_serie for cat_serie_subserie in cat_series_subseries]
        cat_series_list = [cat_serie_subserie.id_serie_doc.id_serie_doc for cat_serie_subserie in cat_series_subseries]

        cat_series_unidad = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__in=cat_series_subseries_list)
        cat_series_unidad_list = [cat_serie_unidad.id_catalogo_serie.id_catalogo_serie for cat_serie_unidad in cat_series_unidad]
        
        organigrama_unidades = UnidadesOrganizacionales.objects.filter(id_organigrama=ccd.id_organigrama, activo=True).exclude(cod_agrupacion_documental=None)
        organigrama_unidades_list = organigrama_unidades.values_list('id_unidad_organizacional', flat=True)
        cat_series_unidades_list = [cat_serie_unidad.id_unidad_organizacional.id_unidad_organizacional for cat_serie_unidad in cat_series_unidad if cat_serie_unidad.id_unidad_organizacional.cod_agrupacion_documental != None]
        
        if not set(list(organigrama_unidades_list)).issubset(cat_series_unidades_list):
            unidades_difference = list(set(list(organigrama_unidades_list)) - set(cat_series_unidades_list))
            unidades_difference_instances = organigrama_unidades.filter(id_unidad_organizacional__in=unidades_difference)
            serializer_unidades_difference = UnidadesGetSerializer(unidades_difference_instances, many=True)
            try:
                raise ValidationError('Debe relacionar todas las unidades que tienen agrupación documental en el catalogo')
            except ValidationError as e:
                return Response({'success':False, 'detail':'Debe relacionar todas las unidades que tienen agrupación documental en el catalogo', 'error_unidades':True, 'data': serializer_unidades_difference.data}, status=status.HTTP_400_BAD_REQUEST)
        
        if not set(series_list).issubset(cat_series_list):
            # Mostrar las series sin asignar
            series_diff_list = [serie for serie in series_list if serie not in cat_series_list]
            series_diff_instance = series.filter(id_serie_doc__in=series_diff_list)
            serializer_series = SeriesDocPostSerializer(series_diff_instance, many=True)
            try:
                raise ValidationError('Debe asociar todas las series o eliminar las series faltantes')
            except ValidationError as e:
                return Response({'success':False, 'detail':'Debe asociar todas las series o eliminar las series faltantes', 'error_series':True, 'error_catalogo':False, 'data': serializer_series.data}, status=status.HTTP_400_BAD_REQUEST)
        
        if not set(cat_series_subseries_list).issubset(cat_series_unidad_list):
            # Mostrar los items de catalogo de series y subseries sin asignar
            cat_series_subseries_diff_list = [cat_serie_subserie for cat_serie_subserie in cat_series_subseries_list if cat_serie_subserie not in cat_series_unidad_list]
            cat_series_subseries_diff_instance = cat_series_subseries.filter(id_catalogo_serie__in=cat_series_subseries_diff_list)
            serializer_cat_series_subseries = CatalogoSerieSubserieSerializer(cat_series_subseries_diff_instance, many=True)
            try:
                ValidationError('Debe asociar todos los items del catalogo de serie y subserie o eliminar los items faltantes')
            except ValidationError as e:
                return Response({'success':False, 'detail':'Debe asociar todos los items del catalogo de serie y subserie o eliminar los items faltantes', 'error_series':False, 'error_catalogo':True, 'data': serializer_cat_series_subseries.data}, status=status.HTTP_400_BAD_REQUEST)
            
        ccd.fecha_terminado = datetime.now()
        ccd.save()
        
        return Response({'success':True, 'detail':'El CCD fue finalizado con éxito'}, status=status.HTTP_200_OK)
        
class GetCuadroClasificacionDocumental(generics.ListAPIView):
    serializer_class = CCDSerializer  
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            ccds = self.queryset.all()
            
            if len(ccds) == 0:
                return Response({'success':True, 'detail':'Aún no hay Cuadros de Clasificación Documental registrados', 'data':[]}, status=status.HTTP_200_OK)
            
            serializer = self.serializer_class(ccds, many=True, context={'request':request})
            
            return Response({'success':True, 'detail':'Se encontraron los siguientes CCDs', 'data':serializer.data}, status=status.HTTP_200_OK) 
        else:
            ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=consulta)
        
            if len(ccd) == 0:
                raise NotFound('No se encontró el Cuadro de Clasificación Documental ingresado')

            serializer = self.serializer_class(ccd, many=True, context={'request':request})
        
            return Response({'success':True, 'detail':'Se encontró el siguiente CCD', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetCCDTerminado(generics.ListAPIView):
    serializer_class = CCDSerializer  
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))
    permission_classes = [IsAuthenticated]

class CreateSeriesDoc(generics.CreateAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=data['id_ccd']).first()
        
        # VALIDACIONES CCD
        if not ccd:
             raise ValidationError('El CCD ingresado no existe')
        elif ccd.actual:
            raise PermissionDenied('No puede agregar series a un CCD actual')
        elif ccd.fecha_terminado:
            raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif ccd.fecha_retiro_produccion:
            raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
        
        ultima_serie = self.queryset.all().annotate(codigo_int=Cast('codigo', output_field=BigIntegerField())).filter(id_ccd=data['id_ccd']).order_by('id_ccd','codigo_int').last()
        
        codigo_correcto = ultima_serie.codigo_int + ccd.valor_aumento_serie if ultima_serie else ccd.valor_aumento_serie
        
        # VALIDAR SI SE VA A CREAR SERIE INTERMEDIA
        serie = self.queryset.all().filter(id_ccd=data['id_ccd'], codigo=int(data['codigo'])).first()
        if serie:
            # ACOMODAR CODIGOS DE SERIES POSTERIORES
            series_posteriores = [serie_instance for serie_instance in self.queryset.all().filter(id_ccd=data['id_ccd']) if int(serie_instance.codigo) >= int(data['codigo'])]
            for serie_posterior in series_posteriores:
                serie_posterior.codigo = int(serie_posterior.codigo) + ccd.valor_aumento_serie
                serie_posterior.save()
                
        else:
            if int(data['codigo']) != codigo_correcto:
                raise ValidationError('El codigo ingresado no es correcto. Valide que siga el orden definido por el valor de aumento elegido para las series')
        
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        
        descripcion = {'Nombre':ccd.nombre, 'Versión': ccd.version}
        valores_creados_detalles = [
            {
                'NombreSerie':data['nombre'],
                'CodigoSerie':data['codigo']
            }
        ]
        
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 27,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)            
                 
        
        
        
        return Response ({'success':True, 'detail':'Se ha creado la serie correctamente','data':serializador.data}, status=status.HTTP_201_CREATED)

class UpdateSeriesDoc(generics.RetrieveUpdateAPIView):
    serializer_class = SeriesDocPutSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    

    def put(self, request, id_serie_doc):
        serie = self.queryset.all().filter(id_serie_doc=id_serie_doc).first()
        previous = copy.copy(serie)
        
        if serie:
            # VALIDACIONES CCD
            if serie.id_ccd.actual:
                raise PermissionDenied('No puede modificar series a un CCD actual')
            elif serie.id_ccd.fecha_terminado:
                raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
            elif serie.id_ccd.fecha_retiro_produccion:
                raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
        
            serializer = self.serializer_class(serie, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
                    
            descripcion = {'Nombre':str(serie.id_ccd.nombre), 'Versión':str(serie.id_ccd.version)}
            valores_actualizados_detalles = [
                {
                    'previous':previous,'current':serie,
                    'descripcion': {
                        'NombreSerie':serie.nombre,
                        'CodigoSerie':serie.codigo
                    }
                }
            ]
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 27,
                "cod_permiso" : "AC",
                "subsistema" : 'GEST',
                "dirip" : direccion,
                "descripcion" : descripcion,
                "valores_actualizados_detalles" : valores_actualizados_detalles,
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            
            return Response({'success':True, 'detail':'Registro actualizado exitosamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la serie elegida')

class DeleteSeriesDoc(generics.DestroyAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_serie_doc):
        serie = self.queryset.all().filter(id_serie_doc=id_serie_doc).first()
        
        if serie:
            codigo_serie = serie.codigo
            id_ccd = serie.id_ccd.id_ccd
            
            # VALIDACIONES CCD
            if serie.id_ccd.actual:
                raise PermissionDenied('No puede eliminar series a un CCD actual')
            elif serie.id_ccd.fecha_terminado:
                raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
            elif serie.id_ccd.fecha_retiro_produccion:
                raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
            
            # VALIDAR QUE NO TENGA NADA ASOCIADO
            subseries = serie.subseriesdoc_set.all()
            if subseries:
                raise PermissionDenied('No puede eliminar la serie elegida porque tiene subseries asociadas. Debe eliminar las subseries primero para proceder')
            
            cat_serie_subserie = serie.catalogosseries_set.all()
            if cat_serie_subserie:
                raise PermissionDenied('No puede eliminar la serie elegida porque está asociada en el catalogo de series y subseries. Debe eliminar la asociación antes de proceder')
            
            cat_und = serie.catalogosseries_set.all().first().catalogosseriesunidad_set.all() if serie.catalogosseries_set.all() else None
            if cat_und:
                raise PermissionDenied('No puede eliminar la serie elegida porque está asociada en el catalogo de series de las unidades de las unidades organizacionales. Debe eliminar la asociación antes de proceder')
            
            # ELIMINAR SERIE
            serie.delete()
            
            # ACOMODAR CODIGOS DE SERIES POSTERIORES
            series_posteriores = self.queryset.all().filter(id_ccd=id_ccd,codigo__gt=codigo_serie).order_by('codigo')
            
            for serie_posterior in series_posteriores:
                serie_posterior.codigo = codigo_serie
                codigo_serie = int(codigo_serie) + serie_posterior.id_ccd.valor_aumento_serie
                serie_posterior.save()
            
            descripcion = {'Nombre': str(serie.id_ccd.nombre), 'Versión':str(serie.id_ccd.version)}
            valores_eliminados_detalles = [
                {
                    'NombreSerie':serie.nombre,
                    'CodigoSerie':serie.codigo
                }
            ]    
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 27,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles,  
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Esta serie ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la serie elegida')

class GetSeriesById(generics.ListAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_serie_doc):
        serie = self.queryset.all().filter(id_serie_doc=id_serie_doc).first()
        if serie:
            serializador = self.serializer_class(serie)
            return Response({'success':True, 'detail':'Se encontró la serie', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontró la serie elegida')

class GetSeriesByFilters(generics.ListAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        filter = {}
        
        for key,value in request.query_params.items():
            if key in ['nombre','codigo']:
                if value != "":
                    filter[key+'__icontains']=  value
                        
        series = self.queryset.all().filter(**filter).filter(id_ccd=id_ccd)
        
        serializer = self.serializer_class(series, many=True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes series que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetSeriesByIdCCD(generics.ListAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        series = self.queryset.all().annotate(codigo_int=Cast('codigo', output_field=BigIntegerField())).filter(id_ccd=id_ccd).order_by('codigo_int')
        serializador = self.serializer_class(series, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes series', 'data':serializador.data}, status=status.HTTP_200_OK)

class GetSeriesIndependent(generics.ListAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = CatalogosSeries.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        if not ccd:
             raise ValidationError('El CCD ingresado no existe')
        
        cat_serie_subserie = self.queryset.all().filter(id_serie_doc__id_ccd=id_ccd, id_subserie_doc=None).values_list('id_serie_doc__id_serie_doc', flat=True)
        series = SeriesDoc.objects.filter(id_ccd=id_ccd).exclude(id_serie_doc__in=cat_serie_subserie).order_by('codigo')
        serializador = self.serializer_class(series, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes series', 'data':serializador.data}, status=status.HTTP_200_OK)

class CreateSubseriesDoc(generics.CreateAPIView):
    serializer_class = SubseriesDocPostSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        
        serie = SeriesDoc.objects.filter(id_serie_doc = data['id_serie_doc']).first()
        
        ultima_subserie = self.queryset.all().annotate(codigo_int=Cast('codigo', output_field=BigIntegerField())).filter(id_serie_doc=data['id_serie_doc']).order_by('codigo_int').last()
        
        codigo_correcto = ultima_subserie.codigo_int + serie.id_ccd.valor_aumento_subserie if ultima_subserie else serie.id_ccd.valor_aumento_subserie
        
        if int(data['codigo']) != codigo_correcto:
             raise ValidationError('El codigo ingresado no es correcto. Valide que siga el orden definido por el valor de aumento elegido para las subseries')
        
        subserie_creada = serializador.save()
        
        # CREAR EN ASOCIACION EN CATALOGO SERIE-SUBSERIE
        CatalogosSeries.objects.create(
            id_serie_doc=serie,
            id_subserie_doc=subserie_creada
        )
       
        descripcion = {'Nombre':serie.id_ccd.nombre,'Versión':serie.id_ccd.version}
        valores_creados_detalles = [
            {
                'NombreSerie':serie.nombre,
                'NombreSubSerie':data['nombre'],
                'CodigoSubSerie':data['codigo']
            }
        ]
        
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 27,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
        }
        Util.save_auditoria_maestro_detalle(auditoria_data) 
        
        
        
        return Response ({'success':True, 'detail':'Se ha creado la subserie correctamente','data':serializador.data}, status=status.HTTP_201_CREATED)

class UpdateSubseriesDoc(generics.RetrieveUpdateAPIView):
    serializer_class = SubseriesDocPutSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_subserie_doc):
        subserie = self.queryset.all().filter(id_subserie_doc=id_subserie_doc).first()
        previous = copy.copy(subserie)
        
        if subserie:
            # VALIDACIONES CCD
            if subserie.id_serie_doc.id_ccd.actual:
                raise PermissionDenied('No puede modificar subseries en un CCD actual')
            elif subserie.id_serie_doc.id_ccd.fecha_terminado:
                raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
            elif subserie.id_serie_doc.id_ccd.fecha_retiro_produccion:
                raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
            
            serializer = self.serializer_class(subserie, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            descripcion = {'Nombre':str(subserie.id_serie_doc.nombre)}
            valores_actualizados_detalles = [
                {
                    'previous' : previous,'current':subserie,
                    'descripcion' : {
                        'NombreSubSerie' : subserie.nombre,
                        'CodigoSubSerie' : subserie.codigo
                    }
                }
            ]            
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 27,
                "cod_permiso" : "AC",
                "subsistema" : 'GEST',
                "dirip" : direccion,
                "descripcion" : descripcion,
                "valores_actualizados_detalles" : valores_actualizados_detalles,
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Registro actualizado exitosamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la subserie elegida')

class DeleteSubseriesDoc(generics.DestroyAPIView):
    serializer_class = SubseriesDocPostSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_subserie_doc):
        subserie = self.queryset.all().filter(id_subserie_doc=id_subserie_doc).first()
        
        if subserie:
            codigo_subserie = subserie.codigo
            id_serie_doc = subserie.id_serie_doc.id_serie_doc
            
            # VALIDAR QUE NO TENGA NADA ASOCIADO
            cat_und = subserie.catalogosseries_set.first().catalogosseriesunidad_set.all()
            if cat_und:
                raise PermissionDenied('No puede eliminar la subserie elegida porque su serie está asociada en el catalogo de series de las unidades de las unidades organizacionales. Debe eliminar la asociación antes de proceder')
            
            # ELIMINAR DEL CATALOGO DE SERIE-SUBSERIE
            subserie.catalogosseries_set.all().delete()
            
            # ELIMINAR SUBSERIE
            subserie.delete()
            
            # ACOMODAR CODIGOS DE SUBSERIES POSTERIORES
            subseries_posteriores = self.queryset.all().filter(id_serie_doc=id_serie_doc,codigo__gt=codigo_subserie).order_by('codigo')
            
            for subserie_posterior in subseries_posteriores:
                subserie_posterior.codigo = codigo_subserie
                codigo_subserie = int(codigo_subserie) + subserie_posterior.id_serie_doc.id_ccd.valor_aumento_subserie
                subserie_posterior.save()
                
            descripcion = {'Nombre':str(subserie.id_serie_doc.nombre)}
            valores_eliminados_detalles = [
                {
                    'NombreSubSerie' : subserie.nombre,
                    'CodigoSubSerie' : subserie.codigo
                }
            ]
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 27,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles,
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Esta subserie ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la subserie elegida')

class GetSubseriesById(generics.ListAPIView):
    serializer_class = SubseriesDocPostSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_subserie_doc):
        subserie = self.queryset.all().filter(id_subserie_doc=id_subserie_doc).first()
        if subserie:
            serializador = self.serializer_class(subserie)
            return Response({'success':True, 'detail':'Se encontró la subserie', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontró la subserie elegida')

class GetSubseriesByIdSerieDoc(generics.ListAPIView):
    serializer_class = SubseriesDocPostSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_serie_doc):
        subseries = self.queryset.all().annotate(codigo_int=Cast('codigo', output_field=BigIntegerField())).filter(id_serie_doc=id_serie_doc).order_by('codigo_int')
        serializador = self.serializer_class(subseries, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes subseries', 'data':serializador.data}, status=status.HTTP_200_OK)

class CreateCatalogoSerieSubserie(generics.CreateAPIView):
    serializer_class = CatalogoSerieSubserieSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        return Response ({'success':True, 'detail':'Se ha añadido correctamente la serie al catalogo','data':serializador.data}, status=status.HTTP_201_CREATED)

class DeleteCatalogoSerieSubserie(generics.DestroyAPIView):
    serializer_class = CatalogoSerieSubserieSerializer
    queryset = CatalogosSeries.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_catalogo_serie):
        cat_serie_subserie = self.queryset.all().filter(id_catalogo_serie=id_catalogo_serie).first()
        
        if not cat_serie_subserie:
            raise NotFound('No existe el catalogo de la serie y subserie elegida')
        elif cat_serie_subserie.id_subserie_doc:
            raise PermissionDenied('Solo puede eliminar series independientes del catalogo')
        
        if cat_serie_subserie.id_serie_doc.id_ccd.actual:
            raise PermissionDenied('No puede eliminar del catalogo de series y subseries a un CCD actual')
        elif cat_serie_subserie.id_serie_doc.id_ccd.fecha_terminado:
            raise PermissionDenied('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif cat_serie_subserie.id_serie_doc.id_ccd.fecha_retiro_produccion:
            raise PermissionDenied('No puede realizar esta acción a un CCD retirado de producción')
        
        # ELIMINAR DEL CATALOGO
        cat_serie_subserie.delete()
        
        descripcion = {'Nombre':cat_serie_subserie.id_serie_doc.nombre, 'Codigo':cat_serie_subserie.id_serie_doc.codigo}
        valores_creados_detalles = [
            {
                'NombreSerie':cat_serie_subserie.id_serie_doc.nombre,
                'CodigoSerie':cat_serie_subserie.id_serie_doc.codigo
            }
        ]
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 27,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response({'success':True, 'detail':'Se ha eliminado del catalogo correctamente'}, status=status.HTTP_200_OK)
        
class GetCatalogoSerieSubserieByIdCCD(generics.ListAPIView):
    serializer_class = CatalogoSerieSubserieSerializer
    queryset = CatalogosSeries.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        cat_series_subseries = self.queryset.all().filter(id_serie_doc__id_ccd=id_ccd).order_by('id_serie_doc__codigo', 'id_subserie_doc__codigo')
        serializador = self.serializer_class(cat_series_subseries, many=True)
        
        return Response({'success':True, 'detail':'Se encontró lo siguiente para el catalogo de series y subseries', 'data':serializador.data}, status=status.HTTP_200_OK)

class ReanudarCuadroClasificacionDocumental(generics.UpdateAPIView):
    serializer_class = CCDActivarSerializer
    queryset = CuadrosClasificacionDocumental
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        if ccd:
            if ccd.fecha_terminado:
                if ccd.actual:
                    raise PermissionDenied('No se puede reanudar un cuadro de clasificación documental actual')
                elif ccd.fecha_retiro_produccion:
                    raise PermissionDenied('No se puede reanudar un cuadro de clasificación documental que ya fue retirado de producción')
                trd = TablaRetencionDocumental.objects.filter(id_ccd=pk).exists()
                if not trd:
                    ccd.fecha_terminado = None
                    ccd.save()
                    return Response({'success':True, 'detail':'Se reanudó el CCD'}, status=status.HTTP_201_CREATED)
                else:
                    raise PermissionDenied('No puede reanudar el CCD porque se encuentra en un TRD')
            else:
                raise NotFound('No puede reanudar un CCD no terminado')
        else:
            raise NotFound('No se encontró ningún CCD con estos parámetros')    

class UpdateCatalogoUnidad(generics.UpdateAPIView):
    serializer_class = CatalogosSeriesUnidadSerializer
    queryset = CatalogosSeriesUnidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_ccd):
        data = request.data
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        
        # VALIDAR EXISTENCIA DE CCD
        if not ccd:
             raise ValidationError('Debe elegir un CCD existente')
        if ccd.fecha_terminado and not ccd.actual:
            raise ValidationError('El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar')
        elif ccd.fecha_retiro_produccion:
            raise ValidationError('No puede realizar esta acción a un CCD retirado de producción')
        
        # VALIDAR EXISTENCIA DE UNIDADES
        unidades_list = [item['id_unidad_organizacional'] for item in data]
        unidades_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list)
        
        if len(set(unidades_list)) != len(unidades_instances):
             raise ValidationError('Debe asociar unidades organizacionales existentes')
          
        # VALIDAR EXISTENCIA DE CATALOGO SERIE Y SUBSERIE
        cat_serie_subserie_list = [item['id_catalogo_serie'] for item in data]
        cat_serie_subserie_instances = CatalogosSeries.objects.filter(id_catalogo_serie__in=cat_serie_subserie_list)
        
        if len(set(cat_serie_subserie_list)) != len(cat_serie_subserie_instances):
             raise ValidationError('Debe asociar items del catalogo de series y subseries existentes')
        
        #VALIDAR QUE LA RELACION DE LOS CATALOGOS Y LA CCD SEAN CORRECTOS
        ccd_list = [cat_serie_subserie_instance.id_serie_doc.id_ccd.id_ccd for cat_serie_subserie_instance in cat_serie_subserie_instances]
        
        if len(set(ccd_list)) > 1 or (len(set(ccd_list)) == 1 and ccd_list[0] != int(id_ccd)):
            print(ccd_list)
            raise ValidationError('Los catalogos de la Serie y Subserie deben ser iguales a la CCD ingresada.')
        
        cat_unidad_actual = self.queryset.all().filter(id_catalogo_serie__id_serie_doc__id_ccd=id_ccd)
        cat_unidad_actual_values = cat_unidad_actual.values('id_unidad_organizacional', 'id_catalogo_serie')
        
        if 'actual' in data and data['actual']:
            raise PermissionDenied('No puede eliminar o actualizar registros en este catalogo en un CCD actual')
       
        # SEPARAR REGISTROS A ELIMINAR
        cat_unidad_eliminar = [cat_unidad for cat_unidad in cat_unidad_actual_values if cat_unidad not in data]
        valores_eliminados_detalles = []
        for cat_unidad in cat_unidad_eliminar:
            cat_unidad_actual_eliminar = cat_unidad_actual.filter(id_unidad_organizacional=cat_unidad['id_unidad_organizacional'], id_catalogo_serie=cat_unidad['id_catalogo_serie']).first() 
            
            descripcion_registros_eliminados = {
                'NombreUnidadOrg':str(cat_unidad_actual_eliminar.id_unidad_organizacional.nombre), 
                'CodigoUnidadOrg':str(cat_unidad_actual_eliminar.id_unidad_organizacional.codigo),
                'NombreOrganigrama':str(ccd.id_organigrama.nombre),
                'VersionOrganigrama':str(ccd.id_organigrama.version),
                'NombreSerie':str(cat_unidad_actual_eliminar.id_catalogo_serie.id_serie_doc.nombre),
                'CodigoSerie':str(cat_unidad_actual_eliminar.id_catalogo_serie.id_serie_doc.codigo)
                }
            
            if cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc:
                descripcion_registros_eliminados["NombreSubSerie"]=str(cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc.nombre)
                descripcion_registros_eliminados["CodigoSubSerie"]=str(cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc.codigo)
            
            valores_eliminados_detalles.append(descripcion_registros_eliminados) #para insertar en una lista
            
            if ccd.actual:
                raise PermissionDenied('No puede eliminar registros en un CCD actual')
            
            cat_unidad_actual_eliminar.delete()
        
        # SEPARAR REGISTROS A CREAR
        
        valores_creados_detalles = []
        
        
        
        cat_unidad_crear = [cat_unidad for cat_unidad in data if cat_unidad not in cat_unidad_actual_values]
        if cat_unidad_crear:
            serializador = self.serializer_class(data=cat_unidad_crear, many=True)
            serializador.is_valid(raise_exception=True)
            cat_unidad_creados = serializador.save()
            
            for cat_unidad in cat_unidad_creados:
                descripcion_registros_creados = {
                'NombreUnidadOrg':str(cat_unidad.id_unidad_organizacional.nombre), 
                'CodigoUnidadOrg':str(cat_unidad.id_unidad_organizacional.codigo),
                'NombreOrganigrama':str(ccd.id_organigrama.nombre),
                'VersionOrganigrama':str(ccd.id_organigrama.version),
                'NombreSerie':str(cat_unidad.id_catalogo_serie.id_serie_doc.nombre),
                'CodigoSerie':str(cat_unidad.id_catalogo_serie.id_serie_doc.codigo),
                }
                if cat_unidad.id_catalogo_serie.id_subserie_doc:
                    descripcion_registros_creados["NombreSubSerie"]=str(cat_unidad.id_catalogo_serie.id_subserie_doc.nombre)
                    descripcion_registros_creados["CodigoSubSerie"]=str(cat_unidad.id_catalogo_serie.id_subserie_doc.codigo)
                
                valores_creados_detalles.append(descripcion_registros_creados) #para insertar en una lista

        descripcion = {'Nombre':ccd.nombre,'Versión':ccd.version}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
        "id_usuario" : request.user.id_usuario,
        "id_modulo" : 27,
        "cod_permiso": "AC",
        "subsistema": 'GEST',
        "dirip": direccion,
        "descripcion": descripcion,
        "valores_creados_detalles": valores_creados_detalles,
        'valores_eliminados_detalles':valores_eliminados_detalles,
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return Response ({'success':True, 'detail':'Se guardaron los cambios correctamente en el catalogo'}, status=status.HTTP_201_CREATED)

class GetCatalogoSeriesUnidadByIdCCD(generics.ListAPIView):
    serializer_class = CatalogosSeriesUnidadSerializer
    queryset = CatalogosSeriesUnidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        cat_series_subseries = self.queryset.all().filter(id_catalogo_serie__id_serie_doc__id_ccd=id_ccd).order_by('id_catalogo_serie__id_serie_doc__codigo', 'id_catalogo_serie__id_subserie_doc__codigo')
        serializador = self.serializer_class(cat_series_subseries, many=True)
        
        return Response({'success':True, 'detail':'Se encontró lo siguiente para el catalogo de series de las unidades organizacionales', 'data':serializador.data}, status=status.HTTP_200_OK)

class BusquedaCCD(generics.ListAPIView):
    serializer_class = BusquedaCCDSerializer 
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
        
        ccd = self.queryset.filter(**filter)
        serializador = self.serializer_class(ccd, many=True, context = {'request':request})
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializador.data}, status=status.HTTP_200_OK)


#Permisos sobre Series de Expedientes de los CCD


# HOMOLOGACIONES DE CCD - ENTREGA 55
class BusquedaCCDView(generics.ListAPIView):
    serializer_class = BusquedaCCDSerializer
    permission_classes = [IsAuthenticated]
    
    def get_ccd(self):
        ccd_filtro = CuadrosClasificacionDocumental.objects.exclude(fecha_terminado=None).filter(fecha_retiro_produccion=None)
        return ccd_filtro.order_by('-fecha_terminado')

    def get(self, request):
        ccd_filtro = self.get_ccd()
        serializer = self.serializer_class(ccd_filtro, many=True)

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

class BusquedaCCDHomologacionView(generics.ListAPIView):
    serializer_class = BusquedaCCDHomologacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_validacion_ccd(self):
        tca_actual = TablasControlAcceso.objects.filter(actual=True).first()
        tca_filtro = TablasControlAcceso.objects.filter(
            fecha_puesta_produccion=None, 
            fecha_terminado__gt=tca_actual.fecha_puesta_produccion)
        # trd_filtro = TablaRetencionDocumental.objects.exclude(fecha_terminado=None).filter(fecha_puesta_produccion=None)
        # ccd_filtro = CuadrosClasificacionDocumental.objects.exclude(fecha_terminado=None).filter(fecha_puesta_produccion=None)
        # trd_filtro = trd_filtro.filter(id_trd__in=tca_filtro.values('id_trd'))  
        # ccd_filtro = ccd_filtro.filter(id_ccd__in=trd_filtro.values('id_ccd'))
        trd_filtro = TablaRetencionDocumental.objects.filter(id_trd__in=tca_filtro.values('id_trd'))
        ccd_filtro = CuadrosClasificacionDocumental.objects.filter(id_ccd__in=trd_filtro.values('id_ccd')) 
        return ccd_filtro.order_by('-fecha_terminado')

    def get(self, request):

        ccd_filtro = self.get_validacion_ccd()
        serializer = self.serializer_class(ccd_filtro, many=True)

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)

@staticmethod
def obtener_unidades_ccd(unidades_actual, unidades_nueva):
    data_out = []
    for unidad_actual in unidades_actual:
        for unidad_nueva in unidades_nueva:
            if unidad_actual['codigo'] == unidad_nueva['codigo']:
                data_json = {
                    'id_unidad_actual': unidad_actual['id_unidad_organizacional'],
                    'cod_unidad_actual': unidad_actual['codigo'],
                    'nom_unidad_actual': unidad_actual['nombre'],
                    'id_organigrama_unidad_actual': unidad_actual['id_organigrama'],
                    'id_unidad_nueva': unidad_nueva['id_unidad_organizacional'],
                    'cod_unidad_nueva': unidad_nueva['codigo'],
                    'nom_unidad_nueva': unidad_nueva['nombre'],
                    'id_organigrama_unidad_nueva': unidad_nueva['id_organigrama']
                }
                data_json['iguales'] = unidad_actual['nombre'] == unidad_nueva['nombre']
                data_out.append(data_json)

    data_out = sorted(data_out, key=lambda x: x['iguales'], reverse=True)
    return data_out

@staticmethod
def obtener_cat_series_unidades_ccd(unidad_cat_serie_actual_data, unidad_cat_serie_nueva_data):
    data_out = []

    for uni_cat_ser_actual in unidad_cat_serie_actual_data:
        for uni_cat_ser_nueva in unidad_cat_serie_nueva_data:
            if uni_cat_ser_nueva['cod_serie'] == uni_cat_ser_actual['cod_serie'] and uni_cat_ser_nueva['cod_subserie'] == uni_cat_ser_actual['cod_subserie']:
                data_json = {
                    'id_unidad_org_actual': uni_cat_ser_actual['id_unidad_organizacional'],
                    'id_catalogo_serie_actual': uni_cat_ser_actual['id_cat_serie_und'],
                    'id_serie_actual': uni_cat_ser_actual['id_serie'],
                    'cod_serie_actual': uni_cat_ser_actual['cod_serie'],
                    'nombre_serie_actual': uni_cat_ser_actual['nombre_serie'],
                    'id_subserie_actual': uni_cat_ser_actual['id_subserie'],
                    'cod_subserie_actual': uni_cat_ser_actual['cod_subserie'],
                    'nombre_subserie_actual': uni_cat_ser_actual['nombre_subserie'],
                    'id_unidad_org_nueva': uni_cat_ser_nueva['id_unidad_organizacional'],
                    'id_catalogo_serie_nueva': uni_cat_ser_nueva['id_cat_serie_und'],
                    'id_serie_nueva': uni_cat_ser_nueva['id_serie'],
                    'cod_serie_nueva': uni_cat_ser_nueva['cod_serie'],
                    'nombre_serie_nueva': uni_cat_ser_nueva['nombre_serie'],
                    'id_subserie_nueva': uni_cat_ser_nueva['id_subserie'],
                    'cod_subserie_nueva': uni_cat_ser_nueva['cod_subserie'],
                    'nombre_subserie_nueva': uni_cat_ser_nueva['nombre_subserie']
                }
                data_json['iguales'] = uni_cat_ser_actual['nombre_serie'] == uni_cat_ser_nueva['nombre_serie'] and uni_cat_ser_actual['nombre_subserie'] == uni_cat_ser_nueva['nombre_subserie']
                data_out.append(data_json)

    data_out = sorted(data_out, key=lambda x: x['cod_serie_actual'], reverse=False)
    data_out = sorted(data_out, key=lambda x: x['iguales'], reverse=True)
    return data_out

class CompararSeriesDocUnidadView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_series_doc_unidades(self, id_ccd):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        mismo_organigrama = False

        try:
            ccd = ccd_filro.get(id_ccd=id_ccd)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        try:
            organigrama = Organigramas.objects.get(id_organigrama=ccd.id_organigrama.id_organigrama)
            organigrama_actual = Organigramas.objects.get(actual=True)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama')
        
        if organigrama.id_organigrama == organigrama_actual.id_organigrama: mismo_organigrama = True

        instance_unidades_persistentes = UnidadesSeccionPersistenteTemporalGetView()
        ids_unidad_actual, ids_unidad_nueva = instance_unidades_persistentes.get_unidades_seccion(ccd.id_ccd)

        unidades_organizacionales_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama,cod_agrupacion_documental__isnull=False
            ).exclude(id_unidad_organizacional__in=ids_unidad_actual).order_by('codigo')
        
        unidades_organizacionales_nuevo = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama.id_organigrama,cod_agrupacion_documental__isnull=False
            ).exclude(id_unidad_organizacional__in=ids_unidad_nueva).order_by('codigo')

        unidades_actual = self.serializer_class(unidades_organizacionales_actual, many=True).data
        unidades_nueva = self.serializer_class(unidades_organizacionales_nuevo, many=True).data
 
        data = {
            'id_ccd_actual':ccd_actual.id_ccd,
            'id_ccd_nuevo':ccd.id_ccd,
            'mismo_organigrama':mismo_organigrama,
            'coincidencias': obtener_unidades_ccd(unidades_actual, unidades_nueva)
        }

        return data

    def get(self, request, id_ccd):
        data = self.get_series_doc_unidades(id_ccd)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)

class CompararSeriesDocUnidadCatSerieView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadCatSerieHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_series_doc_unidad_cat_serie(self, data_in):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()        

        try:
            ccd_actual = CuadrosClasificacionDocumental.objects.get(id_ccd=data_in['id_ccd_actual'], actual=True)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no concuerda con el actual')

        try:
            ccd = ccd_filro.get(id_ccd=data_in['id_ccd_nuevo'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        try:
            organigrama = Organigramas.objects.get(id_organigrama=ccd.id_organigrama.id_organigrama)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama')
        
        try:
            organigrama_actual = Organigramas.objects.get(id_organigrama=ccd_actual.id_organigrama.id_organigrama, actual=True)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama como actual')
        
        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual']).exists(): 
            raise NotFound('No se encontro unidad organizacional actual')
        
        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_unidad_nueva']).exists(): 
            raise NotFound('No se encontro unidad organizacional nueva')
        
        unidad_cat_serie_actual = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual'],
                                                                       id_catalogo_serie__id_serie_doc__id_ccd__id_ccd = ccd_actual.id_ccd)
        unidad_cat_serie_nueva = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=data_in['id_unidad_nueva'],
                                                                      id_catalogo_serie__id_serie_doc__id_ccd__id_ccd = ccd.id_ccd)

        instancia_agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporalGetView()
        ids_agrupacion_doc_actual, ids_agrupacion_doc_nueva = instancia_agrupaciones_persistentes.get_unidades_seccion(data_in)

        if ids_agrupacion_doc_actual and ids_agrupacion_doc_nueva:
            unidad_cat_serie_actual = unidad_cat_serie_actual.exclude(id_cat_serie_und__in=ids_agrupacion_doc_actual)
            unidad_cat_serie_nueva = unidad_cat_serie_nueva.exclude(id_cat_serie_und__in=ids_agrupacion_doc_nueva)

        unidad_cat_serie_actual_data = self.serializer_class(unidad_cat_serie_actual, many=True).data
        unidad_cat_serie_nueva_data = self.serializer_class(unidad_cat_serie_nueva, many=True).data

        data = {
            'id_ccd_actual':ccd_actual.id_ccd,
            'id_ccd_nuevo':ccd.id_ccd,
            'coincidencias':obtener_cat_series_unidades_ccd(unidad_cat_serie_actual_data, unidad_cat_serie_nueva_data)
        }

        return data

    def get(self, request):

        id_unidad_actual = self.request.query_params.get('id_unidad_actual', None)
        id_unidad_nueva = self.request.query_params.get('id_unidad_nueva', None)
        id_ccd_actual = self.request.query_params.get('id_ccd_actual', None)
        id_ccd_nuevo = self.request.query_params.get('id_ccd_nuevo', None)
        
        data_in = {
            "id_ccd_actual": id_ccd_actual,
            "id_ccd_nuevo": id_ccd_nuevo,
            "id_unidad_actual": id_unidad_actual,
            "id_unidad_nueva": id_unidad_nueva
        }
        data = self.get_series_doc_unidad_cat_serie(data_in)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)
 
class UnidadesSeccionPersistenteTemporalCreateView(generics.CreateAPIView):
    serializer_class = UnidadesSeccionPersistenteTemporalSerializer
    permission_classes = [IsAuthenticated]

    def crear_actualizar_unidades_persistentes_tmp(self, data_in):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()

        try:
            ccd = ccd_filro.get(id_ccd=data_in['id_ccd_nuevo'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        if not data_in['unidades_persistentes']:
            unidades_nuevas_set = set((None,None))
            print(unidades_nuevas_set)

        unidades_nuevas_set = set(
            (id_unidad['id_unidad_actual'], id_unidad['id_unidad_nueva'])
            for id_unidad in data_in['unidades_persistentes']
        )
        all_ids = {id_unidad for tupla in unidades_nuevas_set for id_unidad in tupla}

        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=all_ids).count() == len(all_ids):
            raise NotFound('No se encontraron todas las unidades organizacionales')
            
        unidades_persistentes_existentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        unidades_existentes_set = set(
            (unidad.id_unidad_seccion_actual.id_unidad_organizacional, unidad.id_unidad_seccion_nueva.id_unidad_organizacional)
            for unidad in unidades_persistentes_existentes
        )

        unidades_a_eliminar = unidades_existentes_set - unidades_nuevas_set
        unidades_a_crear = unidades_nuevas_set - unidades_existentes_set

        self.delete_unidades_persistentes_tmp(ccd.id_ccd, unidades_a_eliminar)

        for unidad in unidades_a_crear:
            data = {
                'id_ccd_nuevo': ccd.id_ccd,
                'id_unidad_seccion_actual': unidad[0],
                'id_unidad_seccion_nueva': unidad[1]
            }
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            unidades_persistentes_create = serializer.save()

        unidades_persistentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        unidades_persistentes_data = self.serializer_class(unidades_persistentes, many=True).data
        return unidades_persistentes_data
    
    def delete_unidades_persistentes_tmp(self, id_ccd_nuevo, unidades_a_eliminar):
        instancia_agrupaciones = AgrupacionesDocumentalesPersistenteTemporalCreateView()
        unidades = UnidadesSeccionPersistenteTemporal.objects.filter(
            id_ccd_nuevo=id_ccd_nuevo,
            id_unidad_seccion_actual__in=[unidad[0] for unidad in unidades_a_eliminar],
            id_unidad_seccion_nueva__in=[unidad[1] for unidad in unidades_a_eliminar]
        )
        for unidad in unidades:
            instancia_agrupaciones.delete_agrupaciones_persistentes_tmp(unidad.id_unidad_seccion_temporal,None)

        unidades.delete()

    def post(self, request):
        data = request.data
        unidades_persistentes = self.crear_actualizar_unidades_persistentes_tmp(data)

        return Response({'success': True, 'detail': 'Se crean o actualizan unidades persistentes', 'data': unidades_persistentes}, status=status.HTTP_201_CREATED)

class AgrupacionesDocumentalesPersistenteTemporalCreateView(generics.CreateAPIView):
    serializer_class = AgrupacionesDocumentalesPersistenteTemporalSerializer
    permission_classes = [IsAuthenticated]

    def crear_actualizar_agrupaciones_persistentes_tmp(self, data_in):
        try:
            unidades_persistentes = UnidadesSeccionPersistenteTemporal.objects.get(id_unidad_seccion_temporal=data_in['id_unidad_seccion_temporal'])
        except UnidadesSeccionPersistenteTemporal.DoesNotExist:
            raise NotFound('No se encontró la unidad persistentente temporal')

        cat_serie_unidad_set = set((id_cat_serie_unidad['id_catalogo_serie_actual'], id_cat_serie_unidad['id_catalogo_serie_nueva'])
            for id_cat_serie_unidad in data_in['catalagos_persistentes']
        )
        all_ids_cat = {id_cat_serie_unidad for tupla in cat_serie_unidad_set for id_cat_serie_unidad in tupla}

        if not CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=all_ids_cat).count() == len(all_ids_cat):
            raise NotFound('No se encontraron todos los catalogos del CCD')

        agrupaciones_persistentes_existentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal=unidades_persistentes.id_unidad_seccion_temporal)

        agrupaciones_existentes_set = set(
            (agrupaciones.id_cat_serie_unidad_ccd_actual.id_cat_serie_und, agrupaciones.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und)
            for agrupaciones in agrupaciones_persistentes_existentes
        )
        
        agrupaciones_a_eliminar = agrupaciones_existentes_set - cat_serie_unidad_set
        agrupaciones_a_crear = cat_serie_unidad_set - agrupaciones_existentes_set

        self.delete_agrupaciones_persistentes_tmp(unidades_persistentes.id_unidad_seccion_temporal,agrupaciones_a_eliminar)

        data_response = []
        
        for id_cat_serie_unidad in agrupaciones_a_crear:
            data = {
                'id_unidad_seccion_temporal':unidades_persistentes.id_unidad_seccion_temporal,
                'id_cat_serie_unidad_ccd_actual':id_cat_serie_unidad[0],
                'id_cat_serie_unidad_ccd_nueva':id_cat_serie_unidad[1]
            }
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            agrupaciones_persistentes = serializer.save()
            data_response.append(self.serializer_class(agrupaciones_persistentes).data)

        return data_response
    
    def  delete_agrupaciones_persistentes_tmp(self, id_unidad_seccion_temporal, agrupaciones_a_eliminar):

        filtro = {'id_unidad_seccion_temporal': id_unidad_seccion_temporal}

        if agrupaciones_a_eliminar is not None:
            filtro['id_cat_serie_unidad_ccd_actual__in'] = [cat[0] for cat in agrupaciones_a_eliminar]
            filtro['id_cat_serie_unidad_ccd_nueva__in'] = [cat[1] for cat in agrupaciones_a_eliminar]

        AgrupacionesDocumentalesPersistenteTemporal.objects.filter(**filtro).delete()

    def post(self, request):
        data = request.data
        agrupaciones_persistentes = self.crear_actualizar_agrupaciones_persistentes_tmp(data)

        return Response({'success':True, 'detail':'Se guardan catalogos persistentes', 'data':agrupaciones_persistentes}, status=status.HTTP_201_CREATED)

class PersistenciaConfirmadaCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        with transaction.atomic():
            instancia_unidades_persistentes = UnidadesSeccionPersistenteTemporalCreateView()
            unidades_persistentes = instancia_unidades_persistentes.crear_actualizar_unidades_persistentes_tmp(data)
            agrupaciones_persistentes = []

            if 'catalagos_persistentes' in data and data['catalagos_persistentes']:

                for unidad_persistente in unidades_persistentes:
                    data_agrup = []
                    for catalogo in data['catalagos_persistentes']:
                        try:
                            cat_actual = CatalogosSeriesUnidad.objects.get(id_cat_serie_und=catalogo['id_catalogo_serie_actual'])
                            cat_nuevo = CatalogosSeriesUnidad.objects.get(id_cat_serie_und=catalogo['id_catalogo_serie_nueva'])
                        except CatalogosSeriesUnidad.DoesNotExist:
                            raise NotFound('No se ha encontrado uno de los catalogos ingresados')
                    
                        if unidad_persistente['id_unidad_seccion_actual'] == cat_actual.id_unidad_organizacional.id_unidad_organizacional and unidad_persistente['id_unidad_seccion_nueva'] == cat_nuevo.id_unidad_organizacional.id_unidad_organizacional:
                            catalogo_persistente = {
                                'id_catalogo_serie_actual': cat_actual.id_cat_serie_und,
                                'id_catalogo_serie_nueva': cat_nuevo.id_cat_serie_und
                                }
                            data_agrup.append(catalogo_persistente)
                            
                    data_a = {
                        'id_unidad_seccion_temporal':unidad_persistente['id_unidad_seccion_temporal'],
                        'catalagos_persistentes':data_agrup
                    }
                    instancia_agrupacion_persistentes = AgrupacionesDocumentalesPersistenteTemporalCreateView()
                    agrupacion_persistentes = instancia_agrupacion_persistentes.crear_actualizar_agrupaciones_persistentes_tmp(data_a)
                    agrupaciones_persistentes.append(agrupacion_persistentes)

            data_out = {
                'unidades_persistentes': unidades_persistentes,
                'agrupaciones_persistentes':agrupaciones_persistentes
            }
            return Response({'success':True, 'detail':'Se guardan catalogos persistentes', 'data':data_out}, status=status.HTTP_201_CREATED)

class UnidadesSeccionPersistenteTemporalGetView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_unidades_seccion(self, id_ccd_nuevo):

        try:
            ccd = CuadrosClasificacionDocumental.objects.get(id_ccd=id_ccd_nuevo)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado')
        uniadades_persistentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        ids_unidad_actual = [unidad.id_unidad_seccion_actual.id_unidad_organizacional for unidad in uniadades_persistentes]
        ids_unidad_nueva = [unidad.id_unidad_seccion_nueva.id_unidad_organizacional for unidad in uniadades_persistentes]

        return ids_unidad_actual, ids_unidad_nueva
    
    def get(self, request, id_ccd):

        ids_unidad_actual, ids_unidad_nueva = self.get_unidades_seccion(id_ccd)
        unidades_organizacionales_actual = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=ids_unidad_actual).order_by('codigo')
        unidades_organizacionales_nuevo = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=ids_unidad_nueva).order_by('codigo')
        unidades_actual = self.serializer_class(unidades_organizacionales_actual, many=True).data
        unidades_nueva = self.serializer_class(unidades_organizacionales_nuevo, many=True).data
        data = {
            'id_ccd_nuevo':id_ccd,
            'unidades_persistentes': obtener_unidades_ccd(unidades_actual, unidades_nueva)
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)

class AgrupacionesDocumentalesPersistenteTemporalGetView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadCatSerieHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_unidades_seccion(self, data_in):
        
        try:
            ccd = CuadrosClasificacionDocumental.objects.get(id_ccd=data_in['id_ccd_nuevo'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado')
        
        unidades_persistentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd, 
                                                                                id_unidad_seccion_actual=data_in['id_unidad_actual'],
                                                                                id_unidad_seccion_nueva=data_in['id_unidad_nueva']).first()
    
        if unidades_persistentes:    
            agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal=unidades_persistentes.id_unidad_seccion_temporal)
            ids_agrupacion_doc_actual = [agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und for agrupacion in agrupaciones_persistentes]
            ids_agrupacion_doc_nueva = [agrupacion.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und for agrupacion in agrupaciones_persistentes]
        else:
            ids_agrupacion_doc_actual = None
            ids_agrupacion_doc_nueva = None
        
        return ids_agrupacion_doc_actual, ids_agrupacion_doc_nueva
    
    def get(self, request):

        id_ccd_nuevo = self.request.query_params.get('id_ccd_nuevo', None)
        id_unidad_actual = self.request.query_params.get('id_unidad_actual', None)
        id_unidad_nueva = self.request.query_params.get('id_unidad_nueva', None)

        data = {
            "id_ccd_nuevo": id_ccd_nuevo,
            "id_unidad_actual": id_unidad_actual,
            "id_unidad_nueva": id_unidad_nueva  
            }
        
        ids_agrupacion_doc_actual, ids_agrupacion_doc_nueva = self.get_unidades_seccion(data)

        if ids_agrupacion_doc_actual == None and ids_agrupacion_doc_nueva == None:
            raise NotFound('No existe unidades persistentes con los datos ingresados')
        
        unidad_cat_serie_actual = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=ids_agrupacion_doc_actual)
        unidad_cat_serie_nueva = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=ids_agrupacion_doc_nueva)
        unidad_cat_serie_actual_data = self.serializer_class(unidad_cat_serie_actual, many=True).data
        unidad_cat_serie_nueva_data = self.serializer_class(unidad_cat_serie_nueva, many=True).data
        data = {
            'id_ccd_nuevo':data['id_ccd_nuevo'],
            'agrupaciones_persistentes':obtener_cat_series_unidades_ccd(unidad_cat_serie_actual_data, unidad_cat_serie_nueva_data)
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)

# ENTREGA 57
class SeriesDocUnidadCCDActualGetView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_ccd):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()
        
        try:
            ccd = ccd_filro.get(id_ccd=id_ccd)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        try:
            organigrama = Organigramas.objects.get(id_organigrama=ccd.id_organigrama.id_organigrama)
            organigrama_actual = Organigramas.objects.get(actual=True)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama')

        instancia_unidades = CompararSeriesDocUnidadView()
        unidades_validacion = instancia_unidades.get_series_doc_unidades(id_ccd)
        Validacion_iguales = [unidad_val['iguales'] for unidad_val in unidades_validacion['coincidencias']]

        if True in Validacion_iguales:
            raise PermissionDenied('Existe una homologacion persistente ')
    
        instance_unidades_persistentes = UnidadesSeccionPersistenteTemporalGetView()
        ids_unidad_actual, ids_unidad_nueva = instance_unidades_persistentes.get_unidades_seccion(ccd.id_ccd)

        unidades_organizacionales_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama,cod_agrupacion_documental__isnull=False
            ).exclude(id_unidad_organizacional__in=ids_unidad_actual).order_by('codigo')
        
        unidades_actual = self.serializer_class(unidades_organizacionales_actual, many=True).data

        data = {
            'id_ccd_actual':unidades_validacion['id_ccd_actual'],
            'id_ccd_nuevo':ccd.id_ccd,
            'mismo_organigrama':unidades_validacion['mismo_organigrama'],
            'coincidencias':len(Validacion_iguales)>0,
            'unidades':unidades_actual
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)

class SeriesDocUnidadCatSerieCCDActualGetView(generics.ListAPIView):
    serializer_class = SeriesDocUnidadCatSerieHomologacionesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_ccd_actual = self.request.query_params.get('id_ccd_actual', None)
        id_ccd_nuevo = self.request.query_params.get('id_ccd_nuevo', None)
        id_unidad_actual = self.request.query_params.get('id_unidad_actual', None)

        data_in = {
            "id_ccd_actual": id_ccd_actual,
            "id_ccd_nuevo": id_ccd_nuevo,
            "id_unidad_actual": id_unidad_actual
        }

        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()
        data_in['id_unidad_nueva'] = None

        try:
            ccd_actual = CuadrosClasificacionDocumental.objects.get(id_ccd=data_in['id_ccd_actual'], actual=True)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no concuerda con el actual')

        try:
            ccd = ccd_filro.get(id_ccd=data_in['id_ccd_nuevo'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        try:
            organigrama = Organigramas.objects.get(id_organigrama=ccd.id_organigrama.id_organigrama)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama')
        
        try:
            organigrama_actual = Organigramas.objects.get(id_organigrama=ccd_actual.id_organigrama.id_organigrama, actual=True)
        except Organigramas.DoesNotExist:
            raise NotFound('No se ha encontrado organigrama como actual')
        
        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual']).exists(): 
            raise NotFound('No se encontro unidad organizacional actual')
        
        unidad_cat_serie_actual = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual'],
                                                                       id_catalogo_serie__id_serie_doc__id_ccd__id_ccd = ccd_actual.id_ccd)

        instancia_agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporalGetView()
        ids_agrupacion_doc_actual, ids_agrupacion_doc_nueva = instancia_agrupaciones_persistentes.get_unidades_seccion(data_in)

        if ids_agrupacion_doc_actual:
            unidad_cat_serie_actual = unidad_cat_serie_actual.exclude(id_cat_serie_und__in=ids_agrupacion_doc_actual)

        unidad_cat_serie_actual_data = self.serializer_class(unidad_cat_serie_actual, many=True).data

        data = {
            'id_ccd_actual':ccd_actual.id_ccd,
            'id_ccd_nuevo':ccd.id_ccd,
            'coincidencias':unidad_cat_serie_actual_data
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)
    
class UnidadesSeccionResponsableTemporalCreateView(generics.CreateAPIView):
    serializer_class = UnidadesSeccionResponsableTemporalSerializer
    permission_classes = [IsAuthenticated]

    def crear_actualizar_unidades_responsable_tmp(self, data_in):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()

        try:
            ccd = ccd_filro.get(id_ccd=data_in['id_ccd_nuevo'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        unidades_nuevas_set = set(
            (id_unidad['id_unidad_actual'], id_unidad['id_unidad_nueva'])
            for id_unidad in data_in['unidades_responsables']
        )
        all_ids = {id_unidad for tupla in unidades_nuevas_set for id_unidad in tupla}

        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=all_ids).count() == len(all_ids):
            raise NotFound('No se encontraron todas las unidades organizacionales')

        unidades_responsables_existentes = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        unidades_existentes_set = set(
            (unidad.id_unidad_seccion_actual.id_unidad_organizacional, unidad.id_unidad_seccion_nueva.id_unidad_organizacional)
            for unidad in unidades_responsables_existentes
        )
        unidades_a_eliminar = unidades_existentes_set - unidades_nuevas_set
        unidades_a_crear = unidades_nuevas_set - unidades_existentes_set

        UnidadesSeccionResponsableTemporal.objects.filter(
            id_ccd_nuevo=ccd.id_ccd,
            id_unidad_seccion_actual__in=[unidad[0] for unidad in unidades_a_eliminar],
            id_unidad_seccion_nueva__in=[unidad[1] for unidad in unidades_a_eliminar]
        ).delete()

        for unidad in unidades_a_crear:
            data = {
                'id_ccd_nuevo': ccd.id_ccd,
                'id_unidad_seccion_actual': unidad[0],
                'id_unidad_seccion_nueva': unidad[1],
                'es_registro_asig_seccion_responsable': True,
                'id_unidad_seccion_actual_padre':unidad[0]
            }
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            unidades_responsables_create = serializer.save()

        unidades_responsables = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        unidades_responsables_data = self.serializer_class(unidades_responsables, many=True).data
        return unidades_responsables_data

    def post(self, request):
        data = request.data
        unidades_responsables = self.crear_actualizar_unidades_responsable_tmp(data)

        if not unidades_responsables:
            raise ValidationError('No se realizaron cambios en las unidades responsables')

        return Response({'success': True, 'detail': 'Se crean o actualizan unidades responsables', 'data': unidades_responsables}, status=status.HTTP_201_CREATED)

class UnidadesSeccionResponsableTemporalGetView(generics.ListAPIView):
    serializer_class = UnidadesSeccionResponsableTemporalGetSerializer
    permission_classes = [IsAuthenticated]

    def get_unidades_seccion(self, id_ccd_nuevo):

        try:
            ccd = CuadrosClasificacionDocumental.objects.get(id_ccd=id_ccd_nuevo)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado')
        
        unidades_responsables = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=ccd.id_ccd)
        unidades_responsables_data = self.serializer_class(unidades_responsables, many=True).data
        # ids_unidad_actual = [unidad.id_unidad_seccion_actual.id_unidad_organizacional for unidad in uniadades_responsables]
        # ids_unidad_nueva = [unidad.id_unidad_seccion_nueva.id_unidad_organizacional for unidad in uniadades_responsables]

        # return ids_unidad_actual, ids_unidad_nueva
        return unidades_responsables_data

    
    def get(self, request, id_ccd):

        unidades_responsables = self.get_unidades_seccion(id_ccd)
        data = {
            'id_ccd_nuevo':id_ccd,
            'unidades_responsables':unidades_responsables
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)


