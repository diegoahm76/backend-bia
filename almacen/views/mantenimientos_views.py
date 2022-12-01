from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.mantenimientos_serializers import (
    SerializerProgramacionMantenimientos,
    SerializerRegistroMantenimientos,
    AnularMantenimientoProgramadoSerializer,
    UpdateMantenimientoProgramadoSerializer
    )
from almacen.models.mantenimientos_models import (
    ProgramacionMantenimientos,
    RegistroMantenimientos,
)
from almacen.models.bienes_models import (
    CatalogoBienes,
)
from almacen.models.inventario_models import (
    Inventario,
)
from seguridad.models import (
    Personas
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import F, Q
from datetime import datetime
from seguridad.utils import Util
import pytz, copy

class GetMantenimientosProgramadosById(generics.RetrieveAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request, pk):
        mantenimiento_programado = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=pk).first()
        if mantenimiento_programado:
            serializador = self.serializer_class(mantenimiento_programado)
            return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe ningún mantenimiento programado con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

class GetMantenimientosProgramadosFiveList(generics.ListAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request, id_articulo):
        mantenimientos_programados = ProgramacionMantenimientos.objects.filter(id_articulo=id_articulo, ejecutado=False, fecha_anulacion=None).values(id_programacion_mantenimiento=F('id_programacion_mtto'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_programada')).order_by('fecha')[:5]
        if mantenimientos_programados:
            mantenimientos_programados = [dict(item, estado='Vencido' if item['fecha'] < datetime.now().date() else 'Programado') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, responsable='NA') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_programados]
            return Response({'status':True, 'detail':mantenimientos_programados}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe ningún mantenimiento programado para este artículo'}, status=status.HTTP_404_NOT_FOUND)
            
class GetMantenimientosProgramadosList(generics.ListAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request, id_articulo):
        mantenimientos_programados = ProgramacionMantenimientos.objects.filter(id_articulo=id_articulo).values(id_programacion_mantenimiento=F('id_programacion_mtto'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_programada')).order_by('fecha')
        if mantenimientos_programados:
            mantenimientos_programados = [dict(item, estado='Vencido' if item['fecha'] < datetime.now().date() else 'Programado') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, responsable='NA') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_programados]
            return Response({'status':True, 'detail':mantenimientos_programados}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe ningún mantenimiento programado para este artículo'}, status=status.HTTP_404_NOT_FOUND)


class AnularMantenimientoProgramado(generics.RetrieveUpdateAPIView):
    serializer_class = AnularMantenimientoProgramadoSerializer
    queryset = ProgramacionMantenimientos.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id_programacion_mtto'

    def patch(self, request, id_programacion_mtto):
        persona_usuario_logeado = request.user.persona.id_persona
        persona_instance = Personas.objects.filter(id_persona=persona_usuario_logeado).first()
        mantenimiento = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_programacion_mtto).first()
        if mantenimiento:
            mantenimiento_previous = copy.copy(mantenimiento)
            if mantenimiento.ejecutado == True:
                return Response({'success': False, 'detail': 'No puede anular un mantenimiento que ya fue ejecutado'}, status=status.HTTP_403_FORBIDDEN)
            if mantenimiento.fecha_anulacion != None:
                return Response({'success': False, 'detail': 'No puede anular un mantenimiento que ya fue anulado'}, status=status.HTTP_403_FORBIDDEN)
            serializador = self.serializer_class(mantenimiento, data=request.data, many=False)
            serializador.is_valid(raise_exception=True)
            mantenimiento.fecha_anulacion = datetime.now(pytz.timezone('America/Bogota'))
            mantenimiento.id_persona_anula = persona_instance
            serializador.save()
            mantenimiento.save()
            
            # Auditoria
            bien = CatalogoBienes.objects.filter(id_bien=mantenimiento.id_articulo.id_bien).first()
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
            direccion=Util.get_client_ip(request)
            valores_actualizados={'previous':mantenimiento_previous, 'current':mantenimiento}
            id_modulo = 0
            
            if bien.cod_tipo_activo == 'Com':
                id_modulo = 21
            elif bien.cod_tipo_activo == 'Veh':
                id_modulo = 22
            else:
                id_modulo = 23
            
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': id_modulo,
                'cod_permiso': 'AC',
                'subsistema': 'ALMA',
                'dirip': direccion,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success': True, 'detail': 'Anulación exitosa'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe ningún mantenimiento con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        

class UpdateMantenimientoProgramado(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateMantenimientoProgramadoSerializer
    queryset = ProgramacionMantenimientos.objects.all()

    def put(self, request, id_mantenimiento):
        mantenimiento = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_mantenimiento).first()
        if mantenimiento:
            serializer = self.serializer_class(mantenimiento, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success': True, 'detail': 'Actualizado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe ningún mantenimiento con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
class GetMantenimientosProgramadosByFechas(generics.ListAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request):
        rango_inicial_fecha = request.query_params.get('rango-inicial-fecha')
        rango_final_fecha = request.query_params.get('rango-final-fecha')
        
        if rango_inicial_fecha==None or rango_final_fecha==None:
            return Response({'success':False, 'detail':'No se ingresaron parámetros de fecha'})
        
        # formateando las variables de tipo fecha
        start_date=datetime(int(rango_inicial_fecha.split('-')[2]),int(rango_inicial_fecha.split('-')[1]),int(rango_inicial_fecha.split('-')[0]), tzinfo=pytz.timezone('America/Bogota'))
        end_date=datetime(int(rango_final_fecha.split('-')[2]),int(rango_final_fecha.split('-')[1]),int(rango_final_fecha.split('-')[0]),23,59,59,999, tzinfo=pytz.timezone('America/Bogota'))
        
        mantenimientos_programados = ProgramacionMantenimientos.objects.filter(fecha_programada__range=[start_date,end_date], ejecutado=False, fecha_anulacion=None).values(id_programacion_mantenimiento=F('id_programacion_mtto'), articulo=F('id_articulo'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_programada')).order_by('fecha')
        if mantenimientos_programados:
            mantenimientos_programados = [dict(item, estado='Vencido' if item['fecha'] < datetime.now().date() else 'Programado') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, responsable='NA') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_programados]
            return Response({'status':True, 'detail':mantenimientos_programados}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe ningún mantenimiento programado entre el rango de fechas ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
class GetMantenimientosEjecutadosFiveList(generics.ListAPIView):
    serializer_class=SerializerRegistroMantenimientos
    queryset=RegistroMantenimientos.objects.all()
    
    def get(self, request, id_articulo):
        mantenimientos_completado = RegistroMantenimientos.objects.filter(id_articulo=id_articulo).values(id_registro_mantenimiento=F('id_registro_mtto'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_ejecutado'), responsable=F('id_persona_realiza')).order_by('-fecha')[:5]
        if mantenimientos_completado:
            mantenimientos_completado = [dict(item, estado='Completado') for item in mantenimientos_completado]
            mantenimientos_completado = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_completado]
            
            for mantenimiento in mantenimientos_completado:
                persona = Personas.objects.filter(id_persona=mantenimiento['responsable']).first()
                mantenimiento['fecha'] = mantenimiento['fecha'].date()
                mantenimiento['responsable'] = persona.primer_nombre + ' ' + persona.primer_apellido if persona.tipo_persona=='N' else persona.razon_social
        else:
            return Response({'success': False, 'detail': 'No existe ningún mantenimiento registrado para este articulo'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status':True, 'detail':mantenimientos_completado}, status=status.HTTP_200_OK)

class GetMantenimientosEjecutadosList(generics.ListAPIView):
    serializer_class=SerializerRegistroMantenimientos
    queryset=RegistroMantenimientos.objects.all()
    
    def get(self, request, id_articulo):
        mantenimientos_completado = RegistroMantenimientos.objects.filter(id_articulo=id_articulo).values(id_registro_mantenimiento=F('id_registro_mtto'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_ejecutado'), responsable=F('id_persona_realiza')).order_by('-fecha')
        if mantenimientos_completado: 
            mantenimientos_completado = [dict(item, estado='Completado') for item in mantenimientos_completado]
            mantenimientos_completado = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_completado]
            
            for mantenimiento in mantenimientos_completado:
                persona = Personas.objects.filter(id_persona=mantenimiento['responsable']).first()
                mantenimiento['fecha'] = mantenimiento['fecha'].date()
                mantenimiento['responsable'] = persona.primer_nombre + ' ' + persona.primer_apellido if persona.tipo_persona=='N' else persona.razon_social
        else:
            return Response({'success': False, 'detail': 'No existe ningún mantenimiento registrado para este articulo'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status':True, 'detail':mantenimientos_completado}, status=status.HTTP_200_OK)

class GetMantenimientosEjecutadosById(generics.ListAPIView):
    serializer_class=SerializerRegistroMantenimientos
    queryset=RegistroMantenimientos.objects.all()
    
    def get(self, request, pk):
        mantenimiento_completado = RegistroMantenimientos.objects.filter(id_registro_mtto=pk).first()
        if mantenimiento_completado:
            serializador = self.serializer_class(mantenimiento_completado)
            return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe ningún mantenimiento con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

class DeleteRegistroMantenimiento(generics.DestroyAPIView):
    serializer_class = SerializerRegistroMantenimientos
    queryset = RegistroMantenimientos.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        registro_mantenimiento = RegistroMantenimientos.objects.filter(id_registro_mtto=pk).first()
        if registro_mantenimiento:
            inventario_bien = Inventario.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
            if inventario_bien.tipo_doc_ultimo_movimiento == 'MANT' and inventario_bien.id_registro_doc_ultimo_movimiento == int(pk):
                inventario_bien.id_registro_doc_ultimo_movimiento = registro_mantenimiento.id_reg_doc_anterior_mov
                inventario_bien.tipo_doc_ultimo_movimiento = registro_mantenimiento.tipo_doc_anterior_mov
                inventario_bien.fecha_ultimo_movimiento = registro_mantenimiento.fecha_estado_anterior
                inventario_bien.cod_estado_activo = registro_mantenimiento.cod_estado_anterior
                inventario_bien.save()
                registro_mantenimiento.delete()
                
                # Auditoria
                bien = CatalogoBienes.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
                usuario = request.user.id_usuario
                descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
                direccion=Util.get_client_ip(request)
                id_modulo = 0
            
                if bien.cod_tipo_activo == 'Com':
                    id_modulo = 24
                elif bien.cod_tipo_activo == 'Veh':
                    id_modulo = 25
                else:
                    id_modulo = 26
                    
                auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : id_modulo,
                    "cod_permiso": "BO",
                    "subsistema": 'ALMA',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                }
                Util.save_auditoria(auditoria_data)
                
                return Response({'success': True, 'detail': 'Eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success': False, 'detail': 'No puede eliminar el mantenimiento porque no es el último movimiento'})
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún mantenimiento con el parámetro ingresado'}, status.HTTP_404_NOT_FOUND)
