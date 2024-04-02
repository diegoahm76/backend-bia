from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recaudo.serializers.registrosconfiguracion_serializer import  AdministraciondePersonalSerializer, ConfigaraicionInteresSerializer, IndicadoresSemestralSerializer, RegistrosConfiguracionSerializer,TipoCobroSerializer,TipoRentaSerializer, VariablesSerializer,ValoresVariablesSerializer
from recaudo.models.base_models import  AdministraciondePersonal, ConfigaraicionInteres, IndicadoresSemestral,FRECUENCIA_CHOICES,MONTH_CHOICES,FORMULARIO_CHOICES, RegistrosConfiguracion, TipoCobro,TipoRenta, Variables,ValoresVariables

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

            campo_adicional = request.data.get('campo_adicional','')

            nivel=request.data.get('nivel', '')

            codigo_profesional=str(campo_adicional)+str(nivel)

            # Calcular el valor del campo 'codigo_profesional'
            data = request.data.copy()  # Hacer una copia de los datos para evitar cambios en la solicitud original
            data['codigo_profesional'] = codigo_profesional


            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
           
            
            # Agregar lógica adicional si es necesario, por ejemplo, asignar valores antes de guardar
            # serializer.validated_data['campo_adicional'] = valor

            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        
class BusquedaAvanzadaPersonalProfesional(generics.ListAPIView):
    serializer_class = AdministraciondePersonalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nivel = self.request.query_params.get('nivel')
        nombre = self.request.query_params.get('nombre')

        queryset = AdministraciondePersonal.objects.all()
        if nivel:
            queryset = queryset.filter(nivel=nivel)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)  # Usar '__icontains' para búsqueda insensible a mayúsculas/minúsculas
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data},
                        status=status.HTTP_200_OK)

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
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Utiliza partial=True
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class Eliminar_AdministraciondePersonal(generics.DestroyAPIView):
    queryset = AdministraciondePersonal.objects.all()
    serializer_class = AdministraciondePersonalSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        instance.delete()  # Elimina la instancia de la base de datos

        return Response({'success': True, 'detail': 'El registro ha sido eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
#____________________________________________________
    


# Vista get para las 4 tablas de zonas hidricas
class Vista_ConfigaraicionInteres(generics.ListAPIView):
    queryset = ConfigaraicionInteres.objects.all()
    serializer_class = ConfigaraicionInteresSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.kwargs.get('year')
        if year:
            queryset = queryset.filter(año=year)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)



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
        # Obtiene la instancia existente
        instance = self.get_object()
        
        # Datos enviados en la solicitud
        request_data = {
            'valor_interes': request.data.get('valor_interes'),
            'estado_editable': request.data.get('estado_editable')
        }
        
        # Actualiza los campos de la instancia
        serializer = self.get_serializer(instance, data=request_data, partial=True)
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
    
class Vista_IndicadoresSemestral(generics.ListAPIView):
    serializer_class = IndicadoresSemestralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = IndicadoresSemestral.objects.all()
        year = self.kwargs.get('year')
        formulario = self.kwargs.get('formulario')
        
        if year:
            queryset = queryset.filter(vigencia_reporta=year)
        if formulario:
            queryset = queryset.filter(formulario=formulario)
        
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'detail': 'Se encontraron los siguientes registros',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Error al obtener los registros: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class CrearIndicadoresSemestral(generics.CreateAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

    def create(self, request, *args, **kwargs):
        try:
            nombre_indicador = request.data.get('nombre_indicador')
            vigencia_reporta = request.data.get('vigencia_reporta')

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            self.perform_create(serializer)

            return Response({
                'success': True, 
                'detail': 'Registro creado correctamente', 
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            if 'vigencia_reporta' in str(e):
                error_message = f'Error al crear el registro: Ya existe un registro con vigencia_reporta {vigencia_reporta}'
            else:
                error_message = f'Error al crear el registro: {str(e)}'
            
            return Response({
                'error': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        



class Borrar_IndicadoresSemestral(generics.DestroyAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()  # Obtener la instancia existente
            instance.delete()  # Eliminar la instancia

            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_204_NO_CONTENT)
        except IndicadoresSemestral.DoesNotExist:
            # Si el registro no existe, devolver un error 404
            return Response({'error': 'El registro no existe'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Manejar cualquier otro error
            return Response({'error': f'Error al eliminar el registro: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

class Actualizar_IndicadoresSemestral(generics.UpdateAPIView):
    queryset = IndicadoresSemestral.objects.all()
    serializer_class = IndicadoresSemestralSerializer

    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()  # Obtiene la instancia existente
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)  # Valida los datos
            serializer.save()  # Guarda la instancia con los datos actualizados

            return Response({'success': True, 'detail': 'Registro actualizado correctamente', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            # Manejar la excepción de manera adecuada
            return Response({'error': f'Error al actualizar el registro: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)
class FrecuenciaMedicionListView(generics.ListAPIView):
    def get(self, request):
        
        formatted_choices = [{'value': choice[0], 'label': choice[1]} for choice in FRECUENCIA_CHOICES]
        return Response({'frecuencia_choices': formatted_choices}, status=status.HTTP_200_OK)
    
class MONTH_CHOICESListVieas(generics.ListAPIView):
    def get(self, request):
        
        formatted_choices = [{'value': choice[0], 'label': choice[1]} for choice in MONTH_CHOICES]
        return Response({'meses_enumerados': formatted_choices}, status=status.HTTP_200_OK)
    

class FORMULARIO_CHOICESListView(generics.ListAPIView):
    def get(self, request):
        
        formatted_choices = [{'value': choice[0], 'label': choice[1]} for choice in FORMULARIO_CHOICES]
        return Response({'tipos_Indicador': formatted_choices}, status=status.HTTP_200_OK)