from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recaudo.serializers.registrosconfiguracion_serializer import RegistrosConfiguracionSerializer,TipoCobroSerializer,TipoRentaSerializer, VariablesSerializer,ValoresVariablesSerializer
from recaudo.models.base_models import RegistrosConfiguracion, TipoCobro,TipoRenta, Variables,ValoresVariables

# Vista get para las 4 tablas de zonas hidricas
class Vista_RegistrosConfiguracion (generics.ListAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = RegistrosConfiguracion.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    



class Crear_RegistrosConfiguracion(generics.CreateAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        
    

class Borrar_RegistrosConfiguracion(generics.DestroyAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        


class Actualizar_RegistrosConfiguracion(generics.UpdateAPIView):
    queryset = RegistrosConfiguracion.objects.all()
    serializer_class = RegistrosConfiguracionSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# nuevas Tablas Tipos de cobro


class Vista_TipoCobro(generics.ListAPIView):
    queryset = TipoCobro.objects.all()
    serializer_class = TipoCobroSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_cobro = TipoCobro.objects.all()
        serializer = self.serializer_class(tipo_cobro, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)


class Crear_TipoCobro(generics.CreateAPIView):
    queryset = TipoCobro.objects.all()
    serializer_class = TipoCobroSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        

class Borrar_TipoCobro(generics.DestroyAPIView):
    queryset = TipoCobro.objects.all()
    serializer_class = TipoCobroSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class Actualizar_TipoCobro(generics.UpdateAPIView):
    queryset = TipoCobro.objects.all()
    serializer_class = TipoCobroSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    






# nuevas Tablas Tipos de renta

class Vista_TipoRenta(generics.ListAPIView):
    queryset = TipoRenta.objects.all()
    serializer_class = TipoRentaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos_renta = TipoRenta.objects.all()
        serializer = self.serializer_class(tipos_renta, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)


class Crear_TipoRenta(generics.CreateAPIView):
    queryset = TipoRenta.objects.all()
    serializer_class = TipoRentaSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        

class Borrar_TipoRenta(generics.DestroyAPIView):
    queryset = TipoRenta.objects.all()
    serializer_class = TipoRentaSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class Actualizar_TipoRenta(generics.UpdateAPIView):
    queryset = TipoRenta.objects.all()
    serializer_class = TipoRentaSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    







# nuevas Tablas Variables



class Vista_Variables(generics.ListAPIView):
    queryset = Variables.objects.all()
    serializer_class = VariablesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos_renta = Variables.objects.all()
        serializer = self.serializer_class(tipos_renta, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)


class Crear_Variables(generics.CreateAPIView):
    queryset = Variables.objects.all()
    serializer_class = VariablesSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        

class Borrar_Variables(generics.DestroyAPIView):
    queryset = Variables.objects.all()
    serializer_class = VariablesSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class Actualizar_Variables(generics.UpdateAPIView):
    queryset = Variables.objects.all()
    serializer_class = VariablesSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    





# nuevas Tablas ValoresVariables



class Vista_ValoresVariables(generics.ListAPIView):
    queryset = ValoresVariables.objects.all()
    serializer_class = ValoresVariablesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        valores_variables = ValoresVariables.objects.all()
        serializer = self.serializer_class(valores_variables, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)


class Crear_ValoresVariables(generics.CreateAPIView):
    queryset = ValoresVariables.objects.all()
    serializer_class = ValoresVariablesSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        

class Borrar_ValoresVariables(generics.DestroyAPIView):
    queryset = ValoresVariables.objects.all()
    serializer_class = ValoresVariablesSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class Actualizar_ValoresVariables(generics.UpdateAPIView):
    queryset = ValoresVariables.objects.all()
    serializer_class = ValoresVariablesSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    