from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from gestion_documental.models.trd_models import TablaRetencionDocumental
from seguridad.utils import Util
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import  AgregarArchivoSoporteCreateSerializer, ExpedienteGetOrdenSerializer, ExpedienteSearchSerializer, ListarTRDSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q
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
    
#AGREGAR_ARCHIVO_SOPORTE(PENDINETE)
class AgregarArchivoSoporte(generics.CreateAPIView):
    serializer_class = AgregarArchivoSoporteCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = DocumentosDeArchivoExpediente.objects.all()
    
    def post(self, request, format=None):
        # Asocia el serializador con una instancia de DocumentosDeArchivoExpediente
        serializer = AgregarArchivoSoporteCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Obtén el id_persona del usuario logueado
            id_persona_logueada = self.request.user.persona.id_persona

            # Establece la relación antes de guardar el objeto
            serializer.save(id_persona_que_crea=id_persona_logueada)
            
            # Guarda la instancia del documento de archivo expediente
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#IDENTIFICACION_DOC_EN_EXPEDIENTE
class ListarDocumentosEnExpediente(generics.ListAPIView):
    queryset = DocumentosDeArchivoExpediente.objects.all()
    serializer_class = DocumentosDeArchivoExpediente

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Recorre los documentos y genera la identificación
        for documento in queryset:
            if DocumentosDeArchivoExpediente.id_expediente_documental.cod_tipo_expediente == "S":
                # Formatea el número de orden de documento en expediente con una longitud de 10 dígitos
                orden_en_expediente_formatted = f"{documento.T237ordenEnExpediente:010}"
                
                # Genera la identificación del documento según las reglas
                documento.T237IdentificacionDoc_EnExpediente = (
                    f"{documento.T236codigoExp_Agno}{documento.T236codTipoExpediente}{orden_en_expediente_formatted}"
                )
                documento.save()
        
        return queryset
    
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
class EstanteDepositoGetOrdenActual(generics.ListAPIView):
    serializer_class = ExpedienteGetOrdenSerializer
    queryset = DocumentosDeArchivoExpediente.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = DocumentosDeArchivoExpediente.objects.aggregate(max_orden=Max('orden_en_expediente'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden']
        
        return Response({'success': True, 'orden_actual': orden_siguiente}, status=status.HTTP_200_OK)