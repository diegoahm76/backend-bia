from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max, Subquery, OuterRef, F, Value, IntegerField, Case, When
from django.db.models import Case, When, Value, IntegerField

from django.db.models import Q
from django.db import transaction
from rest_framework import generics
from gestion_documental.models.metadatos_models import ListaValores_MetadatosPers, MetadatosPersonalizados
from gestion_documental.serializers.metadatos_serializers import GetMetadatosPersonalizadosOrdenSerializer, MetadatosPersonalizadosDeleteSerializer, MetadatosPersonalizadosGetSerializer, MetadatosPersonalizadosSearchSerializer, MetadatosPersonalizadosSerializer, MetadatosPersonalizadosUpdateSerializer, MetadatosValoresCreateSerializer, MetadatosValoresGetOrdenSerializer, MetadatosValoresGetSerializer

########################## CRUD DE METADATO ##########################

#CREAR-METADATOS
class MetadatosPersonalizadosCreate(generics.CreateAPIView):
    serializer_class = MetadatosPersonalizadosSerializer  
    permission_classes = [IsAuthenticated]
    queryset = MetadatosPersonalizados.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = MetadatosPersonalizadosSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#ORDEN_METADATOS_SIGUIENTE
class MetadatosPersonalizadosGetOrden(generics.ListAPIView):
     
    serializer_class = GetMetadatosPersonalizadosOrdenSerializer
    queryset = MetadatosPersonalizados.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = MetadatosPersonalizados.objects.aggregate(max_orden=Max('orden_aparicion'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)

    
#ORDEN_METADATOS_ACTUAL
class MetadatosPersonalizadosGetOrdenActual(generics.ListAPIView):
     
    serializer_class = GetMetadatosPersonalizadosOrdenSerializer
    queryset = MetadatosPersonalizados.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = MetadatosPersonalizados.objects.aggregate(max_orden=Max('orden_aparicion'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] 
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
    

#LISTAR_METADATOS
class MetadatosPersonalizadosList(generics.ListAPIView):
    serializer_class = MetadatosPersonalizadosSerializer

    def get_queryset(self):
        # Obtener el valor máximo de orden_aparicion
        max_orden_aparicion = MetadatosPersonalizados.objects.aggregate(max_orden=Max('orden_aparicion'))['max_orden']

        # Consulta para los metadatos con orden_aparicion repetido
        subquery = MetadatosPersonalizados.objects.filter(
            orden_aparicion=OuterRef('orden_aparicion')
        ).values('orden_aparicion').annotate(
            max_order=F('orden_aparicion'),
            null_order=Case(
                When(orden_aparicion__isnull=True, then=Value(max_orden_aparicion + 1)),
                default=F('orden_aparicion'),
                output_field=IntegerField(),
            )
        ).order_by('null_order', 'nombre_a_mostrar').values('max_order')[:1]

        # Consulta principal para los metadatos
        queryset = MetadatosPersonalizados.objects.annotate(
            has_duplicate=Subquery(subquery)
        ).order_by('has_duplicate', 'orden_aparicion', 'nombre_a_mostrar')

        return queryset
    

#ELIMINAR_METADATOS
class MetadatosPersonalizadosDelete(generics.DestroyAPIView):
    serializer_class = MetadatosPersonalizadosDeleteSerializer
    queryset = MetadatosPersonalizados.objects.all()
    lookup_field = 'id_metadato_personalizado'  # Configura el campo de clave primaria

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.item_ya_usado:
            return Response({"detail": "No puedes eliminar este metadato porque este ya fue usado."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Eliminar el metadato
        instance.delete()
        
        # Reordenar los metadatos restantes
        max_orden_aparicion = MetadatosPersonalizados.objects.aggregate(max_orden=Max('orden_aparicion'))['max_orden']
        
        # Resto del código para reordenar los metadatos restantes...
        
        return Response({"detail": "El metadato se eliminó y se reordenaron los demás metadatos."}, status=status.HTTP_204_NO_CONTENT)
    

#EDITAR_METADATOS
class MetadatosPersonalizadosUpdate(generics.UpdateAPIView):
    serializer_class = MetadatosPersonalizadosUpdateSerializer
    queryset = MetadatosPersonalizados.objects.all()
    lookup_field = 'id_metadato_personalizado'  # Configura el campo de clave primaria

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.item_ya_usado:
            # Si item_ya_usado es True, no permitir la modificación de ciertos campos
            restricted_fields = ["nombre_metadato", "nombre_a_mostrar", "cod_tipo_dato_alojar"]
            for field in restricted_fields:
                if field in request.data:
                    return Response(
                        {"detail": f"No puedes modificar el campo '{field}' cuando 'item_ya_usado' es True."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Obtener el objeto actualizado y serializarlo para incluirlo en la respuesta
        updated_instance = self.get_object()
        updated_data = MetadatosPersonalizadosUpdateSerializer(updated_instance).data
        
        return Response({"detail": "El metadato se actualizó correctamente.", "data": updated_data}, status=status.HTTP_200_OK)
    
    
#BUSCAR-METADATOS
class MetadatosPersonalizadosSearch(generics.ListAPIView):
    serializer_class = MetadatosPersonalizadosSearchSerializer

    def get_queryset(self):
        nombre_metadato = self.request.query_params.get('nombre_metadato', '').strip()
        descripcion = self.request.query_params.get('descripcion', '').strip()

        metadatos = MetadatosPersonalizados.objects.all()

        if nombre_metadato:
            metadatos = metadatos.filter(nombre_metadato__icontains=nombre_metadato)
        
        if descripcion:
            metadatos = metadatos.filter(descripcion__icontains=descripcion)

        metadatos = metadatos.order_by('orden_aparicion')  # Ordenar aquí

        return metadatos

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron metadatos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes metadatos.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

########################## CRUD DE VALORES DE METADATOS ##########################

#CREAR_LISTA_VALORES
class MetadatosValoresCreate(generics.CreateAPIView):

    serializer_class = MetadatosValoresCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = ListaValores_MetadatosPers.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            orden_siguiente = MetadatosValoresGetOrdenActual()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')

            print(maximo_orden)
            data_in['orden_dentro_de_lista']=  maximo_orden + 1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            estante =serializer.save()


            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)

#ORDEN_VALORES_SIGUIENTE
class MetadatosValoresGetOrden(generics.ListAPIView):
     
    serializer_class = MetadatosValoresGetOrdenSerializer
    queryset = ListaValores_MetadatosPers.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = ListaValores_MetadatosPers.objects.aggregate(max_orden=Max('orden_dentro_de_lista'))
        
        if maximo_orden['max_orden'] is not None:
            orden_siguiente = maximo_orden['max_orden'] + 1
        else:
            orden_siguiente = 1  # O cualquier otro valor por defecto que prefieras
        
        data = {'orden_siguiente': orden_siguiente}
        return Response(data, status=status.HTTP_200_OK)

    
#ORDEN_VALORES_ACTUAL
class MetadatosValoresGetOrdenActual(generics.ListAPIView):
    serializer_class = MetadatosValoresGetOrdenSerializer
    queryset = ListaValores_MetadatosPers.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = ListaValores_MetadatosPers.objects.aggregate(max_orden=Max('orden_dentro_de_lista'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden']
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
    

#LISTAR_TODOS_LOS_VALORES
class ValoresMetadatosGet(generics.ListAPIView):
    serializer_class = MetadatosValoresGetSerializer
    queryset = ListaValores_MetadatosPers.objects.all().order_by('orden_dentro_de_lista')
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de valores registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes valores de metadatos.',
            'data': serializer.data
        })
    

#ELIMINAR_VALORES_METADATOS
class ValoresMetadatosDelete(generics.DestroyAPIView):
    serializer_class = MetadatosPersonalizadosDeleteSerializer
    queryset = ListaValores_MetadatosPers.objects.all()
    permission_classes = [IsAuthenticated]


    def delete(self, request, pk):
        
        valor = ListaValores_MetadatosPers.objects.filter(id_lista_valor_metadato_pers=pk).first()

        if not valor:
            raise ValidationError("No existe el valor que desea eliminar")

        # Reordenar
        valores = ListaValores_MetadatosPers.objects.filter(orden_dentro_de_lista__gt=valor.orden_dentro_de_lista).order_by('orden_dentro_de_lista') 
        valor.delete()

        for valor in valores:
            valor.orden_dentro_de_lista = valor.orden_dentro_de_lista - 1
            valor.save()

        return Response({'success': True, 'detail': 'Se eliminó el valor metadato seleccionado.'}, status=status.HTTP_200_OK)    
        
