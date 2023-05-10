from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from seguridad.utils import Util
from rest_framework.exceptions import PermissionDenied
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
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
from almacen.models.organigrama_models import Organigramas
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)

import copy

class CreateCuadroClasificacionDocumental(generics.CreateAPIView):
    serializer_class = CCDPostSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        #Validación de seleccionar solo organigramas terminados
        organigrama_instance = Organigramas.objects.filter(id_organigrama=data['id_organigrama']).first()
        if organigrama_instance:
            if organigrama_instance.fecha_terminado == None:
                return Response({'success': False, 'detail': 'No se pueden seleccionar organigramas que no estén terminados'}, status=status.HTTP_403_FORBIDDEN)
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
            
            return Response({'success': True, 'detail': 'Cuadro de Clasificación Documental creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'Debe elegir un organigrama que exista'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDPutSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        data = request.data
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        
        # VALIDACIONES CCD
        if not ccd:
            return Response({'success':False, 'detail':'El CCD ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        elif ccd.fecha_terminado:
            return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
        elif ccd.fecha_retiro_produccion or ccd.id_organigrama.fecha_retiro_produccion:
            return Response({'success':False, 'detail':'No puede realizar esta acción en un CCD retirado de producción o en un CCD cuya construcción está basada en un organigrama que ya fue sacado de circulación'}, status=status.HTTP_403_FORBIDDEN)
        elif ccd.actual:
            return Response({'success':False, 'detail':'No se pueden realizar operaciones en un CCD actual'}, status=status.HTTP_403_FORBIDDEN)

        elif not ccd.fecha_terminado:
            previoud_ccd = copy.copy(ccd)
            serializer = self.serializer_class(ccd, data=data)
            serializer.is_valid(raise_exception=True)
            
            # Validar que el nuevo nombre del CCD no esté en uso
            nuevo_nombre = data.get('nombre', ccd.nombre)
            if  CuadrosClasificacionDocumental.objects.filter(nombre=nuevo_nombre).exclude(id_ccd=ccd.id_ccd).exists():
                return Response({'success':False, 'detail':'Ya existe un CCD con el nombre ingresado. Por favor ingrese un nombre diferente'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar que la nueva versión del CCD no esté en uso
            nueva_version = data.get('version', ccd.version)
            if CuadrosClasificacionDocumental.objects.filter(version=nueva_version).exclude(id_ccd=ccd.id_ccd).exists():
                return Response({'success':False, 'detail':'Ya existe un CCD con la versión ingresada. Por favor ingrese una versión diferente'}, status=status.HTTP_400_BAD_REQUEST)

            series = ccd.seriesdoc_set.all()
            
            valor_aumento_serie = data.get('valor_aumento_serie')
            valor_aumento_subserie = data.get('valor_aumento_subserie')
            
            # Verificar si se intentó cambiar el organigrama
            nuevo_organigrama = data.get('id_organigrama', ccd.id_organigrama.id_organigrama)
            if int(nuevo_organigrama) != ccd.id_organigrama.id_organigrama:
                print ("ACTUAL",type(nuevo_organigrama))
                print ("PASADO",type(ccd.id_organigrama.id_organigrama))
                return Response({'success':False, 'detail':'No puede cambiar el organigrama utilizado para crear el CCD'}, status=status.HTTP_400_BAD_REQUEST)
    
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
            
        return Response({'success': True, 'detail': 'Cuadro de Clasificación Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class FinalizarCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDActivarSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        ccd = self.queryset.all().filter(id_ccd=pk).first()
        
        # VALIDACIONES CCD
        if not ccd:
            return Response({'success':False, 'detail':'El CCD ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        elif ccd.fecha_terminado:
            return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
        elif ccd.fecha_retiro_produccion:
            return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
        elif not ccd.ruta_soporte:
            return Response({'success':False, 'detail':'No puede finalizar un CCD sin antes haber adjuntado un archivo de soporte'}, status=status.HTTP_403_FORBIDDEN)
        
        series = SeriesDoc.objects.filter(id_ccd=pk)
        series_list = [serie.id_serie_doc for serie in series]
        
        cat_series_subseries = CatalogosSeries.objects.filter(id_serie_doc__id_ccd=pk)
        cat_series_subseries_list = [cat_serie_subserie.id_catalogo_serie for cat_serie_subserie in cat_series_subseries]
        cat_series_list = [cat_serie_subserie.id_serie_doc.id_serie_doc for cat_serie_subserie in cat_series_subseries]

        cat_series_unidad = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__in=cat_series_subseries_list)
        cat_series_unidad_list = [cat_serie_unidad.id_catalogo_serie.id_catalogo_serie for cat_serie_unidad in cat_series_unidad]

        if not set(series_list).issubset(cat_series_list):
            # Mostrar las series sin asignar
            series_diff_list = [serie for serie in series_list if serie not in cat_series_list]
            series_diff_instance = series.filter(id_serie_doc__in=series_diff_list)
            serializer_series = SeriesDocPostSerializer(series_diff_instance, many=True)
            return Response({'success': False, 'detail': 'Debe asociar todas las series o eliminar las series faltantes', 'error_series':True, 'error_catalogo':False, 'data': serializer_series.data}, status=status.HTTP_400_BAD_REQUEST)
        
        if not set(cat_series_subseries_list).issubset(cat_series_unidad_list):
            # Mostrar los items de catalogo de series y subseries sin asignar
            cat_series_subseries_diff_list = [cat_serie_subserie for cat_serie_subserie in cat_series_subseries_list if cat_serie_subserie not in cat_series_unidad_list]
            cat_series_subseries_diff_instance = cat_series_subseries.filter(id_catalogo_serie__in=cat_series_subseries_diff_list)
            serializer_cat_series_subseries = CatalogoSerieSubserieSerializer(cat_series_subseries_diff_instance, many=True)
            return Response({'success': False, 'detail': 'Debe asociar todos los items del catalogo de serie y subserie o eliminar los items faltantes', 'error_series':False, 'error_catalogo':True, 'data': serializer_cat_series_subseries.data}, status=status.HTTP_400_BAD_REQUEST)
            
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
            
            return Response({'success': True, 'detail':'Se encontraron los siguientes CCDs', 'data':serializer.data}, status=status.HTTP_200_OK) 
        else:
            ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=consulta)
        
            if len(ccd) == 0:
                return Response({'success':False, 'detail':'No se encontró el Cuadro de Clasificación Documental ingresado'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(ccd, many=True, context={'request':request})
        
            return Response({'success': True,'detail':'Se encontró el siguiente CCD', 'data':serializer.data}, status=status.HTTP_200_OK)

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
            return Response({'success':False, 'detail':'El CCD ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        elif ccd.actual:
            return Response({'success':False, 'detail':'No puede agregar series a un CCD actual'}, status=status.HTTP_403_FORBIDDEN)
        elif ccd.fecha_terminado:
            return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
        elif ccd.fecha_retiro_produccion:
            return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
        
        ultima_serie = self.queryset.all().filter(id_ccd=data['id_ccd']).order_by('codigo').last()
        
        codigo_correcto = int(ultima_serie.codigo) + ccd.valor_aumento_serie if ultima_serie else ccd.valor_aumento_serie
        
        # VALIDAR SI SE VA A CREAR SERIE INTERMEDIA
        serie = self.queryset.all().filter(id_ccd=data['id_ccd'], codigo=int(data['codigo'])).first()
        if serie:
            # ACOMODAR CODIGOS DE SERIES POSTERIORES
            series_posteriores = self.queryset.all().filter(id_ccd=data['id_ccd'],codigo__gte=int(data['codigo'])).order_by('-codigo')
            
            for serie_posterior in series_posteriores:
                serie_posterior.codigo = int(serie_posterior.codigo) + ccd.valor_aumento_serie
                serie_posterior.save()
        else:
            if int(data['codigo']) != codigo_correcto:
                return Response({'success':False, 'detail':'El codigo ingresado no es correcto. Valide que siga el orden definido por el valor de aumento elegido para las series'}, status=status.HTTP_400_BAD_REQUEST)
        
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
                 
        
        
        
        return Response ({'success':True,'detail':'Se ha creado la serie correctamente','data':serializador.data}, status=status.HTTP_201_CREATED)

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
                return Response({'success':False, 'detail':'No puede modificar series a un CCD actual'}, status=status.HTTP_403_FORBIDDEN)
            elif serie.id_ccd.fecha_terminado:
                return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
            elif serie.id_ccd.fecha_retiro_produccion:
                return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({'success': False, 'detail': 'No existe la serie elegida'}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({'success':False, 'detail':'No puede eliminar series a un CCD actual'}, status=status.HTTP_403_FORBIDDEN)
            elif serie.id_ccd.fecha_terminado:
                return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
            elif serie.id_ccd.fecha_retiro_produccion:
                return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
            
            # VALIDAR QUE NO TENGA NADA ASOCIADO
            subseries = serie.subseriesdoc_set.all()
            if subseries:
                return Response({'success':False, 'detail':'No puede eliminar la serie elegida porque tiene subseries asociadas. Debe eliminar las subseries primero para proceder'}, status=status.HTTP_403_FORBIDDEN)
            
            cat_serie_subserie = serie.catalogosseries_set.all()
            if cat_serie_subserie:
                return Response({'success':False, 'detail':'No puede eliminar la serie elegida porque está asociada en el catalogo de series y subseries. Debe eliminar la asociación antes de proceder'}, status=status.HTTP_403_FORBIDDEN)
            
            cat_und = serie.catalogosseries_set.all().first().catalogosseriesunidad_set.all() if serie.catalogosseries_set.all() else None
            if cat_und:
                return Response({'success':False, 'detail':'No puede eliminar la serie elegida porque está asociada en el catalogo de series de las unidades de las unidades organizacionales. Debe eliminar la asociación antes de proceder'}, status=status.HTTP_403_FORBIDDEN)
            
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
            
            return Response({'success': True, 'detail': 'Esta serie ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail':'No existe la serie elegida'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response ({'success':False, 'detail':'No se encontró la serie elegida'}, status=status.HTTP_404_NOT_FOUND)

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
        series = self.queryset.all().filter(id_ccd=id_ccd).order_by('codigo')
        serializador = self.serializer_class(series, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron las siguientes series', 'data':serializador.data}, status=status.HTTP_200_OK)

class GetSeriesIndependent(generics.ListAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = CatalogosSeries.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_ccd):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        if not ccd:
            return Response({'success':False, 'detail':'El CCD ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        ultima_subserie = self.queryset.all().filter(id_serie_doc=data['id_serie_doc']).order_by('codigo').last()
        
        codigo_correcto = int(ultima_subserie.codigo) + serie.id_ccd.valor_aumento_subserie if ultima_subserie else serie.id_ccd.valor_aumento_subserie
        
        if int(data['codigo']) != codigo_correcto:
            return Response({'success':False, 'detail':'El codigo ingresado no es correcto. Valide que siga el orden definido por el valor de aumento elegido para las subseries'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        
        
        return Response ({'success':True,'detail':'Se ha creado la subserie correctamente','data':serializador.data}, status=status.HTTP_201_CREATED)

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
                return Response({'success':False, 'detail':'No puede modificar subseries en un CCD actual'}, status=status.HTTP_403_FORBIDDEN)
            elif subserie.id_serie_doc.id_ccd.fecha_terminado:
                return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
            elif subserie.id_serie_doc.id_ccd.fecha_retiro_produccion:
                return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
            
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
            return Response({'success': False, 'detail': 'No existe la subserie elegida'}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({'success':False, 'detail':'No puede eliminar la subserie elegida porque su serie está asociada en el catalogo de series de las unidades de las unidades organizacionales. Debe eliminar la asociación antes de proceder'}, status=status.HTTP_403_FORBIDDEN)
            
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
            
            return Response({'success': True, 'detail': 'Esta subserie ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail':'No existe la subserie elegida'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response ({'success':False, 'detail':'No se encontró la subserie elegida'}, status=status.HTTP_404_NOT_FOUND)

class GetSubseriesByIdSerieDoc(generics.ListAPIView):
    serializer_class = SubseriesDocPostSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_serie_doc):
        subseries = self.queryset.all().filter(id_serie_doc=id_serie_doc).order_by('codigo')
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
        
        return Response ({'success':True,'detail':'Se ha añadido correctamente la serie al catalogo','data':serializador.data}, status=status.HTTP_201_CREATED)

class DeleteCatalogoSerieSubserie(generics.DestroyAPIView):
    serializer_class = CatalogoSerieSubserieSerializer
    queryset = CatalogosSeries.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_catalogo_serie):
        cat_serie_subserie = self.queryset.all().filter(id_catalogo_serie=id_catalogo_serie).first()
        
        if cat_serie_subserie.id_serie_doc.id_ccd.actual:
            return Response({'success':False, 'detail':'No puede eliminar del catalogo de series y subseries a un CCD actual'}, status=status.HTTP_403_FORBIDDEN)
        elif cat_serie_subserie.id_serie_doc.id_ccd.fecha_terminado:
            return Response({'success':False, 'detail':'El CCD elegido se encuentra terminado. Por favor intente reanudarlo antes de continuar'}, status=status.HTTP_403_FORBIDDEN)
        elif cat_serie_subserie.id_serie_doc.id_ccd.fecha_retiro_produccion:
            return Response({'success':False, 'detail':'No puede realizar esta acción a un CCD retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
        
        if not cat_serie_subserie:
            return Response({'success': False, 'detail':'No existe el catalogo de la serie y subserie elegida'}, status=status.HTTP_404_NOT_FOUND)
        elif cat_serie_subserie.id_subserie_doc:
            return Response({'success': False, 'detail':'Solo puede eliminar series independientes del catalogo'}, status=status.HTTP_403_FORBIDDEN)
        
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
                    return Response({'success': False, 'detail': 'No se puede reanudar un cuadro de clasificación documental actual'}, status=status.HTTP_403_FORBIDDEN)
                elif ccd.fecha_retiro_produccion:
                    return Response({'success': False, 'detail': 'No se puede reanudar un cuadro de clasificación documental que ya fue retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
                trd = TablaRetencionDocumental.objects.filter(id_ccd=pk).exists()
                if not trd:
                    ccd.fecha_terminado = None
                    ccd.save()
                    return Response({'success': True, 'detail': 'Se reanudó el CCD'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'detail': 'No puede reanudar el CCD porque se encuentra en un TRD'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success': False, 'detail': 'No puede reanudar un CCD no terminado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún CCD con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)    

class UpdateCatalogoUnidad(generics.UpdateAPIView):
    serializer_class = CatalogosSeriesUnidadSerializer
    queryset = CatalogosSeriesUnidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_ccd):
        data = request.data
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        
        # VALIDAR EXISTENCIA DE CCD
        if not ccd:
            return Response({'success':False, 'detail':'Debe elegir un CCD existente'}, status=status.HTTP_400_BAD_REQUEST)
        
        # VALIDAR EXISTENCIA DE UNIDADES
        unidades_list = [item['id_unidad_organizacional'] for item in data]
        unidades_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list)
        
        if len(set(unidades_list)) != len(unidades_instances):
            return Response({'success':False, 'detail':'Debe asociar unidades organizacionales existentes'}, status=status.HTTP_400_BAD_REQUEST)
          
        # VALIDAR EXISTENCIA DE CATALOGO SERIE Y SUBSERIE
        cat_serie_subserie_list = [item['id_catalogo_serie'] for item in data]
        cat_serie_subserie_instances = CatalogosSeries.objects.filter(id_catalogo_serie__in=cat_serie_subserie_list)
        
        if len(set(cat_serie_subserie_list)) != len(cat_serie_subserie_instances):
            return Response({'success':False, 'detail':'Debe asociar items del catalogo de series y subseries existentes'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            
            ############
            descripcion = {'Nombre':ccd.nombre,'Versión':ccd.version}
            descripcion_registros_eliminados = {
                'NombreUnidadOrg':str(cat_unidad_actual_eliminar.id_unidad_organizacional.nombre), 
                'CodigoUnidadOrg':str(cat_unidad_actual_eliminar.id_unidad_organizacional.codigo),
                'NombreOrganigrama':str(ccd.id_organigrama.nombre),
                'VersionOrganigrama':str(ccd.id_organigrama.version),
                'NombreSerie':str(cat_unidad_actual_eliminar.id_catalogo_serie.id_serie_doc.nombre),
                'CodigoSerie':str(cat_unidad_actual_eliminar.id_catalogo_serie.id_serie_doc.codigo)
                }
            
            if cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc:
                descripcion_registros_creados["NombreSubSerie"]=str(cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc.nombre)
                descripcion_registros_creados["CodigoSubSerie"]=str(cat_unidad_actual_eliminar.id_catalogo_serie.id_subserie_doc.codigo)
            
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
                descripcion = {'Nombre':ccd.nombre,'Versión':ccd.version}
                
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
        
        return Response ({'success':True,'detail':'Se guardaron los cambios correctamente en el catalogo'}, status=status.HTTP_201_CREATED)

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
