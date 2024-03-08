from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recaudo.serializers.registrosconfiguracion_serializer import  AdministraciondePersonalSerializer, ConfigaraicionInteresSerializer, IndicadoresSemestralSerializer, RegistrosConfiguracionSerializer,TipoCobroSerializer,TipoRentaSerializer, VariablesSerializer,ValoresVariablesSerializer
from recaudo.models.base_models import  AdministraciondePersonal, ConfigaraicionInteres, IndicadoresSemestral, RegistrosConfiguracion, TipoCobro,TipoRenta, Variables,ValoresVariables

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
    

#_____________________________________________________
    
import calendar

class CalculadoraDiasMeses(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        # Obtener los meses y el año del cuerpo de la solicitud
        meses = request.data.get('meses', [])
        año = request.data.get('año', None)

        try:
            if año is not None:
                # Convertir los meses a enteros
                meses = [int(mes) for mes in meses]

                # Realizar la lógica para sumar los días de los meses seleccionados en el año proporcionado
                suma_dias = sum([calendar.monthrange(int(año), mes)[1] for mes in meses])

                # Devolver la respuesta en formato JSON
                return Response({'suma_dias': suma_dias})
            else:
                return Response({'error': 'Año no proporcionado'}, status=400)
        except ValueError:
            # Manejar el caso en el que los meses proporcionados no sean válidos
            return Response({'error': 'Alguno de los meses proporcionados no es válido'}, status=400)

        

#_______________________________________________________________________________________
class Crear_AdministraciondePersonal(generics.CreateAPIView):
    queryset = AdministraciondePersonal.objects.all()
    serializer_class = AdministraciondePersonalSerializer

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
        
    

class Vista_AdministraciondePersonal(generics.ListAPIView):
    queryset = AdministraciondePersonal.objects.all()
    serializer_class = AdministraciondePersonalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_cobro = AdministraciondePersonal.objects.all()
        serializer = self.serializer_class(tipo_cobro, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)



class Actualizar_AdministraciondePersonal(generics.UpdateAPIView):
    queryset = AdministraciondePersonal.objects.all()
    serializer_class = AdministraciondePersonalSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    
#____________________________________________________
    


# Vista get para las 4 tablas de zonas hidricas
class Vista_ConfigaraicionInteres (generics.ListAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = RegistrosConfiguracion.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    



class Crear_ConfigaraicionInteres(generics.CreateAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer

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
        
    

class Borrar_ConfigaraicionInteres(generics.DestroyAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        


class Actualizar_ConfigaraicionInteres(generics.UpdateAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)

class Crear_ConfigaraicionInteres(generics.CreateAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer

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
        
     
    
#__________________________________________________________________
    

    # Vista get para las 4 tablas de zonas hidricas
class Vista_IndicadoresSemestral(generics.ListAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = RegistrosConfiguracion.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    



class Crear_IndicadoresSemestral(generics.CreateAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

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
        
    

class Borrar_IndicadoresSemestral(generics.DestroyAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        


class Actualizar_IndicadoresSemestral(generics.UpdateAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    