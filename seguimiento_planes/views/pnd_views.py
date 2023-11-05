from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from seguimiento_planes.serializers.pnd_serializers import PlanNacionalDesarrolloSerializer, SectorSerializer, ProgramaSerializer, ProductoSerializer, PndIndicadorSerializer
from seguimiento_planes.models.pnd_models import PlanNacionalDesarrollo, Sector, Programa, Producto, PndIndicador

# ---------------------------------------- Planes Nacionales de Desarrollo ----------------------------------------

# Listar Planes Nacionales de Desarrollo

class ConsultarPlanNacionalDesarrollo(generics.ListAPIView):
    serializer_class = PlanNacionalDesarrolloSerializer
    queryset = PlanNacionalDesarrollo.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        planes_nacionales_desarrollo = self.queryset.all()
        serializador = self.serializer_class(planes_nacionales_desarrollo, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes planes nacionales de desarrollo', 'data': serializador.data}, status=status.HTTP_200_OK)


# Craer Plan Nacional de Desarrollo

class CrearPlanNacionalDesarrollo(generics.CreateAPIView):
    serializer_class = PlanNacionalDesarrolloSerializer
    queryset = PlanNacionalDesarrollo.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        print('PASOOOOOOOO')
        planes_nacionales_desarrollo = self.queryset.all().filter(
            nombre_plan=data["nombre_plan"]).first()
        print('PLANESSSS', planes_nacionales_desarrollo)
        if planes_nacionales_desarrollo:
            return Response({'success': False, 'detail': 'El plan nacional de desarrollo ya existe'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el plan nacional de desarrollo de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualziar Plan Nacional de Desarrollo

class ActualizarPlanNacionalDesarrollo(generics.UpdateAPIView):
    serializer_class = PlanNacionalDesarrolloSerializer
    queryset = PlanNacionalDesarrollo.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        plan_nacional_desarrollo = self.queryset.all().filter(id_plan=pk).first()

        if not plan_nacional_desarrollo:
            return Response({'success': False, 'detail': 'El plan nacional de desarrollo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(plan_nacional_desarrollo, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el plan nacional de desarrollo de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Eliminar Plan Nacional de Desarrollo

class EliminarPlanNacionalDesarrollo(generics.DestroyAPIView):
    serializer_class = PlanNacionalDesarrolloSerializer
    queryset = PlanNacionalDesarrollo.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        plan_nacional_desarrollo = self.queryset.all().filter(id_plan=pk).first()

        if not plan_nacional_desarrollo:
            return Response({'success': False, 'detail': 'El plan nacional de desarrollo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        plan_nacional_desarrollo.delete()
        return Response({'success': True, 'detail': 'Se elimino el plan nacional de desarrollo de manera exitosa'}, status=status.HTTP_200_OK)
    
# Listar plan de desarrollo por id

class ConsultarPlanNacionalDesarrolloId(generics.ListAPIView):
    serializer_class = PlanNacionalDesarrolloSerializer
    queryset = PlanNacionalDesarrollo.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        plan_nacional_desarrollo = self.queryset.all().filter(id_plan=pk).first()
        if not plan_nacional_desarrollo:
            return Response({'success': False, 'detail': 'El plan nacional de desarrollo ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(plan_nacional_desarrollo)
        return Response({'success': True, 'detail': 'Se encontro el plan nacional de desarrollo', 'data': serializador.data}, status=status.HTTP_200_OK)
    

# ---------------------------------------- Sectores ----------------------------------------

# Listar Sectores

class ConsultarSector(generics.ListAPIView):
    serializer_class = SectorSerializer
    queryset = Sector.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sectores = self.queryset.all()
        serializador = self.serializer_class(sectores, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes sectores', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer Sector

class CrearSector(generics.CreateAPIView):
    serializer_class = SectorSerializer
    queryset = Sector.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        sectores = self.queryset.all().filter(
            nombre_sector=data["nombre_sector"]).first()
        if sectores:
            return Response({'success': False, 'detail': 'El sector ya existe'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el sector de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualziar Sector

class ActualizarSector(generics.UpdateAPIView):
    serializer_class = SectorSerializer
    queryset = Sector.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        sector = self.queryset.all().filter(id_sector=pk).first()

        if not sector:
            return Response({'success': False, 'detail': 'El sector ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(sector, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el sector de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Eliminar Sector

class EliminarSector(generics.DestroyAPIView):
    serializer_class = SectorSerializer
    queryset = Sector.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        sector = self.queryset.all().filter(id_sector=pk).first()

        if not sector:
            return Response({'success': False, 'detail': 'El sector ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        sector.delete()
        return Response({'success': True, 'detail': 'Se elimino el sector de manera exitosa'}, status=status.HTTP_200_OK)
    
# Listar sector por id

class ConsultarSectorId(generics.ListAPIView):
    serializer_class = SectorSerializer
    queryset = Sector.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        sector = self.queryset.all().filter(id_sector=pk).first()
        if not sector:
            return Response({'success': False, 'detail': 'El sector ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(sector)
        return Response({'success': True, 'detail': 'Se encontro el sector', 'data': serializador.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Programas ----------------------------------------

# Listar Programas

class ConsultarPrograma(generics.ListAPIView):
    serializer_class = ProgramaSerializer
    queryset = Programa.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        programas = self.queryset.all()
        serializador = self.serializer_class(programas, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes programas', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer Programa

class CrearPrograma(generics.CreateAPIView):
    serializer_class = ProgramaSerializer
    queryset = Programa.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        programas = self.queryset.all().filter(
            nombre_programa=data["nombre_programa"]).first()
        if programas:
            return Response({'success': False, 'detail': 'El programa ya existe'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el programa de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualziar Programa

class ActualizarPrograma(generics.UpdateAPIView):
    serializer_class = ProgramaSerializer
    queryset = Programa.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        programa = self.queryset.all().filter(id_programa=pk).first()

        if not programa:
            return Response({'success': False, 'detail': 'El programa ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(programa, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el programa de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Eliminar Programa

class EliminarPrograma(generics.DestroyAPIView):
    serializer_class = ProgramaSerializer
    queryset = Programa.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        programa = self.queryset.all().filter(id_programa=pk).first()

        if not programa:
            return Response({'success': False, 'detail': 'El programa ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        programa.delete()
        return Response({'success': True, 'detail': 'Se elimino el programa de manera exitosa'}, status=status.HTTP_200_OK)

# Listar programa por id

class ConsultarProgramaId(generics.ListAPIView):
    serializer_class = ProgramaSerializer
    queryset = Programa.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        programa = self.queryset.all().filter(id_programa=pk).first()
        if not programa:
            return Response({'success': False, 'detail': 'El programa ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(programa)
        return Response({'success': True, 'detail': 'Se encontro el programa', 'data': serializador.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Productos ----------------------------------------

# Listar Productos

class ConsultarProducto(generics.ListAPIView):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        productos = self.queryset.all()
        serializador = self.serializer_class(productos, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes productos', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Craer Producto

class CrearProducto(generics.CreateAPIView):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        productos = self.queryset.all().filter(
            nombre_producto=data["nombre_producto"]).first()
        if productos:
            return Response({'success': False, 'detail': 'El producto ya existe'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el producto de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
    
# Actualziar Producto

class ActualizarProducto(generics.UpdateAPIView):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        producto = self.queryset.all().filter(id_producto=pk).first()

        if not producto:
            return Response({'success': False, 'detail': 'El producto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(producto, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el producto de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK)

# Eliminar Producto

class EliminarProducto(generics.DestroyAPIView):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        producto = self.queryset.all().filter(id_producto=pk).first()

        if not producto:
            return Response({'success': False, 'detail': 'El producto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        producto.delete()
        return Response({'success': True, 'detail': 'Se elimino el producto de manera exitosa'}, status=status.HTTP_200_OK)

# Listar producto por id

class ConsultarProductoId(generics.ListAPIView):
    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        producto = self.queryset.all().filter(id_producto=pk).first()
        if not producto:
            return Response({'success': False, 'detail': 'El producto ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(producto)
        return Response({'success': True, 'detail': 'Se encontro el producto', 'data': serializador.data}, status=status.HTTP_200_OK)

# ---------------------------------------- Indicadores ----------------------------------------

# Listar Indicadores

class ConsultarIndicador(generics.ListAPIView):
    serializer_class = PndIndicadorSerializer
    queryset = PndIndicador.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        indicadores = self.queryset.all()
        serializador = self.serializer_class(indicadores, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes indicadores', 'data': serializador.data}, status=status.HTTP_200_OK)

# Craer Indicador

class CrearIndicador(generics.CreateAPIView):
    serializer_class = PndIndicadorSerializer
    queryset = PndIndicador.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        indicadores = self.queryset.all().filter(
            nombre_indicador=data["nombre_indicador"]).first()
        if indicadores:
            return Response({'success': False, 'detail': 'El indicador ya existe'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se creo el indicador de manera exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

# Actualziar Indicador

class ActualizarIndicador(generics.UpdateAPIView):
    serializer_class = PndIndicadorSerializer
    queryset = PndIndicador.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        # persona_logeada = request.user.persona.id_persona
        # data['id_persona_modifica'] = persona_logeada

        indicador = self.queryset.all().filter(id_indicador=pk).first()

        if not indicador:
            return Response({'success': False, 'detail': 'El indicador ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(indicador, data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success': True, 'detail': 'Se actualizo el indicador de manera exitosa', 'data': serializador.data}, status=status.HTTP_200_OK)
    
# Eliminar Indicador

class EliminarIndicador(generics.DestroyAPIView):
    serializer_class = PndIndicadorSerializer
    queryset = PndIndicador.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        indicador = self.queryset.all().filter(id_indicador=pk).first()

        if not indicador:
            return Response({'success': False, 'detail': 'El indicador ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        indicador.delete()
        return Response({'success': True, 'detail': 'Se elimino el indicador de manera exitosa'}, status=status.HTTP_200_OK)

# Listar indicador por id

class ConsultarIndicadorId(generics.ListAPIView):
    serializer_class = PndIndicadorSerializer
    queryset = PndIndicador.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        indicador = self.queryset.all().filter(id_indicador=pk).first()
        if not indicador:
            return Response({'success': False, 'detail': 'El indicador ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializador = self.serializer_class(indicador)
        return Response({'success': True, 'detail': 'Se encontro el indicador', 'data': serializador.data}, status=status.HTTP_200_OK)
    