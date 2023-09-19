from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
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
    CompararSeriesDocUnidadSerializer,
    CompararSeriesDocUnidadCatSerieSerializer
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

# class BusquedaCCDHomologacionView(generics.ListAPIView):
#     serializer_class = BusquedaCCDHomologacionSerializer

#     def get(self, request):

#         tca_actual = TablasControlAcceso.objects.filter(actual=True).first()
#         tca_filtro = TablasControlAcceso.objects.filter(
#             fecha_puesta_produccion=None,
#             fecha_terminado__gt=tca_actual.fecha_puesta_produccion)
#         trd_filtro = TablaRetencionDocumental.objects.exclude(fecha_terminado = None).filter(fecha_puesta_produccion=None)
#         ccd_filtro = CuadrosClasificacionDocumental.objects.exclude(fecha_terminado = None).filter(fecha_puesta_produccion=None)

#         for tca in tca_filtro:
#             trd_filtro = trd_filtro.filter(id_trd=tca.id_trd.id_trd)

#         for trd in trd_filtro:
#             ccd_filtro = ccd_filtro.filter(id_ccd=trd.id_ccd.id_ccd)

#         serializer = self.serializer_class(ccd_filtro, many=True)

#         return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)


class BusquedaCCDHomologacionView(generics.ListAPIView):
    serializer_class = BusquedaCCDHomologacionSerializer

    def get(self, request):

        tca_actual = TablasControlAcceso.objects.filter(actual=True).first()
        tca_filtro = TablasControlAcceso.objects.filter(fecha_puesta_produccion=None, fecha_terminado__gt=tca_actual.fecha_puesta_produccion)
        trd_filtro = TablaRetencionDocumental.objects.exclude(fecha_terminado=None).filter(fecha_puesta_produccion=None)
        ccd_filtro = CuadrosClasificacionDocumental.objects.exclude(fecha_terminado=None).filter(fecha_puesta_produccion=None)
        trd_filtro = trd_filtro.filter(id_trd__in=tca_filtro.values('id_trd'))  # Filtrar TablaRetencionDocumental relacionada a TablasControlAcceso
        ccd_filtro = ccd_filtro.filter(id_ccd__in=trd_filtro.values('id_ccd'))  # Filtrar CuadrosClasificacionDocumental relacionada a TablaRetencionDocumental
        serializer = self.serializer_class(ccd_filtro, many=True)

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)


class CompararSeriesDocUnidadView(generics.ListAPIView):
    serializer_class = CompararSeriesDocUnidadSerializer

    def get(self, request, id_organigrama):

        if not Organigramas.objects.filter(id_organigrama=id_organigrama, actual=False).exists():
            raise PermissionDenied('No se puede homologar debido a que el CCD pertenece al organigrama actual')

        unidades_organizacionales_nuevo = UnidadesOrganizacionales.objects.filter(id_organigrama=id_organigrama)
        unidades_nueva = self.serializer_class(unidades_organizacionales_nuevo, many=True).data

        organigrama_actual = Organigramas.objects.get(actual=True)
        unidades_organizacionales_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
        unidades_actual = self.serializer_class(unidades_organizacionales_actual, many=True).data

        data = []

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
                    data.append(data_json)

        data = sorted(data, key=lambda x: x['iguales'], reverse=True)

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)


class CompararSeriesDocUnidadCatSerieView(generics.ListAPIView):
    serializer_class = CompararSeriesDocUnidadCatSerieSerializer

    def get(self, request):

        # TO DO: un CCD que ya esté terminado, que no esté puesto en producción aún, 
        # y que ya tenga un TRD y un TCA terminados con fecha de terminado posterior 
        # a la fecha de puesta en producción del TCA actual.


        data_in = request.data

        if not Organigramas.objects.filter(id_organigrama=data_in['id_organigrama_unidad_actual'], actual=True).exists():
            raise NotFound('No se puede homologar debido a que el organigrama actual no existe')
        
        if not Organigramas.objects.filter(id_organigrama=data_in['id_organigrama_unidad_nueva'], actual=False).exists():
            raise PermissionDenied('No se puede homologar debido a que el CCD pertenece al organigrama actual')
        
        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual']).exists(): 
            raise NotFound('No se encontro unidad organizacional actual')
        
        if not UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=data_in['id_unidad_nueva']).exists(): 
            raise NotFound('No se encontro unidad organizacional nueva')

        unidad_cat_serie_actual = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=data_in['id_unidad_actual'])
        unidad_cat_serie_nueva = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=data_in['id_unidad_nueva'])

        if not unidad_cat_serie_actual or not unidad_cat_serie_nueva:
            raise ValidationError('No hay unidades realcionadas con un CCD')
        
        unidad_cat_serie_actual_data = self.serializer_class(unidad_cat_serie_actual, many=True).data
        unidad_cat_serie_nueva_data = self.serializer_class(unidad_cat_serie_nueva, many=True).data
        
        data = []

        for uni_cat_ser_actual in unidad_cat_serie_actual_data:
            for uni_cat_ser_nueva in unidad_cat_serie_nueva_data:
                if uni_cat_ser_nueva['cod_serie'] == uni_cat_ser_actual['cod_serie'] and uni_cat_ser_nueva['cod_subserie'] == uni_cat_ser_actual['cod_subserie']:
                    data_json = {
                        'id_unidad_org_actual': uni_cat_ser_actual['id_unidad_organizacional'],
                        'id_catalogo_serie_actual': uni_cat_ser_actual['id_catalogo_serie'],
                        'id_serie_actual': uni_cat_ser_actual['id_serie'],
                        'cod_serie_actual': uni_cat_ser_actual['cod_serie'],
                        'nombre_serie_actual': uni_cat_ser_actual['nombre_serie'],
                        'id_subserie_actual': uni_cat_ser_actual['id_subserie'],
                        'cod_subserie_actual': uni_cat_ser_actual['cod_subserie'],
                        'nombre_subserie_actual': uni_cat_ser_actual['nombre_subserie'],

                        'id_unidad_org_nueva': uni_cat_ser_nueva['id_unidad_organizacional'],
                        'id_catalogo_serie_nueva': uni_cat_ser_nueva['id_catalogo_serie'],
                        'id_serie_nueva': uni_cat_ser_nueva['id_serie'],
                        'cod_serie_nueva': uni_cat_ser_nueva['cod_serie'],
                        'nombre_serie_nueva': uni_cat_ser_nueva['nombre_serie'],
                        'id_subserie_nueva': uni_cat_ser_nueva['id_subserie'],
                        'cod_subserie_nueva': uni_cat_ser_nueva['cod_subserie'],
                        'nombre_subserie_nueva': uni_cat_ser_nueva['nombre_subserie']
                    }
                    data_json['iguales'] = uni_cat_ser_actual['nombre_serie'] == uni_cat_ser_nueva['nombre_serie'] and uni_cat_ser_actual['nombre_subserie'] == uni_cat_ser_nueva['nombre_subserie']
                    data.append(data_json)

        data = sorted(data, key=lambda x: x['iguales'], reverse=True)

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)

