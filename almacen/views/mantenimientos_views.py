from almacen.models.generics_models import Bodegas
from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util
from almacen.serializers.mantenimientos_serializers import (
    ControlMantenimientosProgramadosGetListSerializer,
    SerializerProgramacionMantenimientos,
    SerializerRegistroMantenimientos,
    AnularMantenimientoProgramadoSerializer,
    SerializerRegistroMantenimientosPost,
    SerializerProgramacionMantenimientosPost,
    UpdateMantenimientoProgramadoSerializer,
    SerializerUpdateRegistroMantenimientos
    )
from almacen.models.mantenimientos_models import (
    ProgramacionMantenimientos,
    RegistroMantenimientos,
)
from almacen.models.bienes_models import (
    EstadosArticulo
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from almacen.models.hoja_de_vida_models import (
    HojaDeVidaVehiculos
)
from transversal.models.personas_models import (
    Personas
)
from almacen.models.inventario_models import (
    Inventario
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db.models import F, Q
from datetime import datetime, date, timedelta
import pytz
import copy
from holidays_co import get_colombia_holidays_by_year

class GetMantenimientosProgramadosById(generics.RetrieveAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request, pk):
        mantenimiento_programado = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=pk).first()
        if mantenimiento_programado:
            serializador = self.serializer_class(mantenimiento_programado)
            return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe ningún mantenimiento programado con el parámetro ingresado')

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
            raise NotFound('No existe ningún mantenimiento programado para este artículo')
            
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
            raise NotFound('No existe ningún mantenimiento programado para este artículo')


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
                raise PermissionDenied('No puede anular un mantenimiento que ya fue ejecutado')
            if mantenimiento.fecha_anulacion != None:
                raise PermissionDenied('No puede anular un mantenimiento que ya fue anulado')
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
            
            if bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Com':
                id_modulo = 21
            elif bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Veh':
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

            return Response({'success':True, 'detail':'Anulación exitosa'}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe ningún mantenimiento con el parámetro ingresado')
        

class UpdateMantenimientoProgramado(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateMantenimientoProgramadoSerializer
    queryset = ProgramacionMantenimientos.objects.all()

    def put(self, request, id_mantenimiento):
        mantenimiento = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_mantenimiento).first()
        if mantenimiento:
            id_articulo = mantenimiento.id_articulo_id
            articulo = CatalogoBienes.objects.filter(id_bien=id_articulo).values().first()
            if not articulo:
                raise NotFound('El mantenimiento está relacionado con un artículo inválido')
            if not articulo['tiene_hoja_vida']:
                raise NotFound('El artículo no tiene hoja de vida')
            serializer = self.serializer_class(mantenimiento, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True, 'detail':'Actualizado correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe ningún mantenimiento con el parámetro ingresado')
        
class GetMantenimientosProgramadosByFechas(generics.ListAPIView):
    serializer_class=SerializerProgramacionMantenimientos
    queryset=ProgramacionMantenimientos.objects.all()
    
    def get(self, request):
        cod_tipo_activo = request.query_params.get('cod_tipo_activo')
        rango_inicial_fecha = request.query_params.get('rango-inicial-fecha')
        rango_final_fecha = request.query_params.get('rango-final-fecha')
        
        if rango_inicial_fecha==None or rango_final_fecha==None:
            raise ValidationError('No se ingresaron parámetros de fecha')
        
        # formateando las variables de tipo fecha
        start_date=datetime(int(rango_inicial_fecha.split('-')[2]),int(rango_inicial_fecha.split('-')[1]),int(rango_inicial_fecha.split('-')[0]), tzinfo=pytz.timezone('America/Bogota'))
        end_date=datetime(int(rango_final_fecha.split('-')[2]),int(rango_final_fecha.split('-')[1]),int(rango_final_fecha.split('-')[0]),23,59,59,999, tzinfo=pytz.timezone('America/Bogota'))
        
        mantenimientos_programados = ProgramacionMantenimientos.objects.filter(fecha_programada__range=[start_date,end_date], ejecutado=False, fecha_anulacion=None)
        if cod_tipo_activo:
            mantenimientos_programados = mantenimientos_programados.filter(id_articulo__cod_tipo_activo=cod_tipo_activo)
        
        mantenimientos_programados = mantenimientos_programados.values(id_programacion_mantenimiento=F('id_programacion_mtto'), articulo=F('id_articulo'), tipo=F('cod_tipo_mantenimiento'), fecha=F('fecha_programada')).order_by('fecha')
        if mantenimientos_programados:
            mantenimientos_programados = [dict(item, estado='Vencido' if item['fecha'] < datetime.now().date() else 'Programado') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, responsable='NA') for item in mantenimientos_programados]
            mantenimientos_programados = [dict(item, tipo_descripcion='Correctivo' if item['tipo']=='C' else 'Preventivo') for item in mantenimientos_programados]
            return Response({'status':True, 'detail':mantenimientos_programados}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe ningún mantenimiento programado entre el rango de fechas ingresado')
        
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
            raise NotFound('No existe ningún mantenimiento registrado para este articulo')

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
            raise NotFound('No existe ningún mantenimiento registrado para este articulo')

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
            raise NotFound('No existe ningún mantenimiento con el parámetro ingresado')

class DeleteRegistroMantenimiento(generics.DestroyAPIView):
    serializer_class = SerializerRegistroMantenimientos
    queryset = RegistroMantenimientos.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        registro_mantenimiento = RegistroMantenimientos.objects.filter(id_registro_mtto=pk).first()
        if registro_mantenimiento:
            inventario_bien = Inventario.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
            if inventario_bien.tipo_doc_ultimo_movimiento == 'MANT' and inventario_bien.id_registro_doc_ultimo_movimiento == int(pk):
                inventario_bien.id_registro_doc_ultimo_movimiento = registro_mantenimiento.id_reg_en_doc_anterior_mov
                inventario_bien.tipo_doc_ultimo_movimiento = registro_mantenimiento.tipo_doc_anterior_mov
                inventario_bien.fecha_ultimo_movimiento = registro_mantenimiento.fecha_estado_anterior
                inventario_bien.cod_estado_activo = registro_mantenimiento.cod_estado_anterior
                inventario_bien.save()
                
                if registro_mantenimiento.id_programacion_mtto:
                    registro_mantenimiento.id_programacion_mtto.ejecutado = False
                    registro_mantenimiento.id_programacion_mtto.save()
                
                registro_mantenimiento.delete()
                
                # Auditoria
                bien = CatalogoBienes.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
                usuario = request.user.id_usuario
                descripcion = {"NombreBien": str(bien.nombre), "Serial": str(bien.doc_identificador_nro)}
                direccion=Util.get_client_ip(request)
                id_modulo = 0
            
                if bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Com':
                    id_modulo = 24
                elif bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Veh':
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
                
                return Response({'success':True, 'detail':'Eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puede eliminar el mantenimiento porque no es el último movimiento')
        else:
            raise NotFound('No se encontró ningún mantenimiento con el parámetro ingresado')
class UpdateRegistroMantenimiento(generics.UpdateAPIView):
    serializer_class=SerializerUpdateRegistroMantenimientos
    permission_classes = [IsAuthenticated]
    queryset=RegistroMantenimientos.objects.all()
    
    def put (self,request,pk):
        
        registro_mantenimiento=RegistroMantenimientos.objects.filter(id_registro_mtto=pk).first()
        persona = request.user.persona.id_persona
        request.data['id_persona_diligencia']=persona
        serializador=self.serializer_class(registro_mantenimiento,data=request.data)
        if registro_mantenimiento:
            inventario_bien = Inventario.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
            if inventario_bien.tipo_doc_ultimo_movimiento == 'MANT' and inventario_bien.id_registro_doc_ultimo_movimiento == int(pk):
                registro_previous=copy.copy(registro_mantenimiento)
                serializador.is_valid(raise_exception=True)
                serializador.save()
                
                estado_articulo=EstadosArticulo.objects.filter(cod_estado=request.data['cod_estado_final']).first()
                
                inventario_bien.cod_estado_activo = estado_articulo
                inventario_bien.save()
                
                usuario=request.user.id_usuario
                valores_actualizados={'previous':registro_previous,'current':registro_mantenimiento}
                bien = CatalogoBienes.objects.filter(id_bien=registro_mantenimiento.id_articulo.id_bien).first()
                descripcion = {"nombre": str(bien.nombre), "serial": str(bien.doc_identificador_nro)}
                direccion=Util.get_client_ip(request)
                id_modulo = 0
            
                if bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Com':
                    id_modulo = 24
                elif bien.cod_tipo_activo and bien.cod_tipo_activo.cod_tipo_activo == 'Veh':
                    id_modulo = 25
                else:
                    id_modulo = 26
                
                auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : id_modulo,
                    "cod_permiso": "AC",
                    "subsistema": 'ALMA',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados":valores_actualizados
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success':True, 'detail':'actualizacion exitosa'},status=status.HTTP_200_OK)    
            raise PermissionDenied('No puede actualizar el mantenimiento porque no es el último movimiento')    
        raise NotFound('No existe el mantenimineto')
        
    
class ValidarFechasProgramacion(generics.CreateAPIView):
    serializer_class = SerializerProgramacionMantenimientosPost
    queryset = ProgramacionMantenimientos.objects.all()
    
    def post(self, request, *args, **kwargs):
        datos_ingresados = request.data
        today = date.today()
        # Validacion de datos entrantes
        if datos_ingresados['programacion'] != 'automatica' and datos_ingresados['programacion'] != 'kilometraje':
            raise NotFound('Elija entre automatico o kilometraje')
        
        match datos_ingresados['programacion']:
            case 'automatica':
                if datos_ingresados['incluir_festivos'] != 'true' and datos_ingresados['incluir_festivos'] != 'false':
                    raise NotFound('Elija entre true o false')
                if datos_ingresados['incluir_fds'] != 'true' and datos_ingresados['incluir_fds'] != 'false':
                    raise NotFound('Elija entre true o false')
                try:
                    aux_v_f_p = datos_ingresados['desde'].split("-")
                    aux_v_f_p_2 = datos_ingresados['hasta'].split("-")
                except:
                    raise NotFound('Formato de fecha no válido')
        
                if not (aux_v_f_p[0]).isdigit() or not (aux_v_f_p[1]).isdigit() or not (aux_v_f_p[2]).isdigit() or not (aux_v_f_p_2[0]).isdigit() or not (aux_v_f_p_2[1]).isdigit() or not (aux_v_f_p_2[2]).isdigit():
                    raise NotFound('Formato de fecha no válido')
                if len(aux_v_f_p) != 3 or len(aux_v_f_p_2) != 3:
                    raise NotFound('Formato de fecha no válido')
                a = (len(aux_v_f_p[0]) != 4)
                b = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
                c = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
                d = (len(aux_v_f_p[0]) != 4)
                e = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
                f = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
                
                if a or not b or not c or d or not e or not f:
                    raise NotFound('Formato de fecha no válido')

                if int(aux_v_f_p[1]) <= 0 or int(aux_v_f_p[1]) >= 13 or int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32 or int(aux_v_f_p_2[1]) <= 0 or int(aux_v_f_p_2[1]) >= 13 or int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 32:
                    raise NotFound('Formato de fecha no válido, debe ingresar un mes entre 1 y 12 y un día entre 1 y 31')
                mes = int(aux_v_f_p[1])
                anio = int(aux_v_f_p[0])
                mes_2 = int(aux_v_f_p_2[1])
                anio_2 = int(aux_v_f_p_2[0])
                if mes == 2:
                    if anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0):
                        if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 30:
                            raise NotFound('En año bisiesto Febrero sólo puede tener hasta 29 días')
                    else:
                        if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 29:
                            raise NotFound('Para le año ingresado Febrero solo puede tener hasta 28 días')
                if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
                    if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32:
                            raise NotFound('Enero, Marzo, Mayo, Julio, Agosto, Octubre y Diciebre solo pueden tener entre 1 y 31 días')
                if mes == 4 or mes == 6 or mes == 9 or mes == 11:
                    if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 31:
                            raise NotFound('Abril, Junio, Septiembre y Noviembre ssolo pueden tener entre 1 y 30 días')
                
                if mes_2 == 2:
                    if anio_2 % 4 == 0 and (anio_2 % 100 != 0 or anio_2 % 400 == 0):
                        if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 30:
                            raise NotFound('En año bisiesto Febrero sólo puede tener hasta 29 días')
                    else:
                        if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 29:
                            raise NotFound('Para le año ingresado Febrero solo puede tener hasta 28 días')
                if mes_2 == 1 or mes_2 == 3 or mes_2 == 5 or mes_2 == 7 or mes_2 == 8 or mes_2 == 10 or mes_2 == 12:
                    if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 32:
                            raise NotFound('Enero, Marzo, Mayo, Julio, Agosto, Octubre y Diciebre solo pueden tener entre 1 y 31 días')
                if mes_2 == 4 or mes_2 == 6 or mes_2 == 9 or mes_2 == 11:
                    if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 31:
                            raise NotFound('Abril, Junio, Septiembre y Noviembre ssolo pueden tener entre 1 y 30 días')
                aux_cada = int(datos_ingresados['cada'])
                if aux_cada <= 0 or aux_cada >= 18:
                    raise NotFound('La frecuencia (cada) debe de estar entre 1 y 17')
                future_date_after_1yrs = today + timedelta(days = 365)
                future_date_after_2yrs = today + timedelta(days = 730)
                future_date_after_3yrs = today + timedelta(days = 1095)
                current_year = today.year
                holidays_next_year = get_colombia_holidays_by_year(future_date_after_1yrs.year)
                holidays_future_date_after_2yrs = get_colombia_holidays_by_year(future_date_after_2yrs.year)
                holidays_future_date_after_3yrs = get_colombia_holidays_by_year(future_date_after_3yrs.year)
                holidays_current_year = get_colombia_holidays_by_year(current_year)
                total_holidays = holidays_future_date_after_3yrs + holidays_future_date_after_2yrs + holidays_next_year + holidays_current_year
                date_holidays_2022 = [(i[0]).strftime("%F") for i in total_holidays]
                fecha_desde = (datetime.strptime(datos_ingresados['desde'], '%Y-%m-%d')).date()
                fecha_hasta = (datetime.strptime(datos_ingresados['hasta'], '%Y-%m-%d')).date()
                aux_validacion_tiempo_max = future_date_after_2yrs - fecha_hasta
                aux_validacion_tiempo_min =  fecha_desde - today
                aux_validacion_fechas_orden = fecha_hasta - fecha_desde
                #Validación del rango de fechas
                if int(aux_validacion_fechas_orden.days) <= 0:
                    raise NotFound('La fecha hasta debe ser mayor de la fecha desde')
                if int(aux_validacion_tiempo_min.days) <= 0 or int(aux_validacion_tiempo_min.days) >= 180:
                    raise NotFound('La fecha ingresada debe ser mayor a la actual y menor a 180 días despues de hoy')
                if int(aux_validacion_tiempo_max.days) <= 0:
                    raise NotFound('La fecha hasta debe ser menos a dos años a partir de hoy')
                cada = int(datos_ingresados['cada'])
                
                rango_dias = int(aux_validacion_fechas_orden.days)
                cuenta_fechas = 0
                fechas_return = []
                match datos_ingresados['unidad_cada']:
                    case 'semanas':
                        periodo_semanal = cada * 7
                        max_semanal_posible = int(rango_dias/periodo_semanal)
                        cuenta_fechas = fecha_desde
                                                     
                        for i in range(max_semanal_posible + 1):
                            if datos_ingresados['incluir_festivos'] == 'false' and datos_ingresados['incluir_fds'] == 'false':
                                aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                while (aux_validar_sabados_domingos == '6') or (aux_validar_sabados_domingos == '0') or (cuenta_fechas.strftime("%F") in date_holidays_2022):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                                    aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                    
                            if datos_ingresados['incluir_festivos'] == 'false' and datos_ingresados['incluir_fds'] == 'true':
                                while (cuenta_fechas.strftime("%F") in date_holidays_2022):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                            
                            if datos_ingresados['incluir_festivos'] == 'true' and datos_ingresados['incluir_fds'] == 'false':
                                aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                while (aux_validar_sabados_domingos == '6') or (aux_validar_sabados_domingos == '0'):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                                    aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                    
                            fechas_return.append(cuenta_fechas.strftime('%Y-%m-%d'))
                            cuenta_fechas = cuenta_fechas + timedelta(days = periodo_semanal)
                            
                        aux_last = fecha_hasta - (datetime.strptime(fechas_return[len(fechas_return)-1], '%Y-%m-%d')).date()
                        if aux_last.days < 0:
                            fechas_return.pop
                    case 'meses':
                        periodo_meses = cada * 30
                        max_mensual_posible = int(rango_dias/periodo_meses)
                        cuenta_fechas = fecha_desde
                        aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                        
                        while (aux_validar_sabados_domingos == '6') or (aux_validar_sabados_domingos == '0') or (cuenta_fechas.strftime("%F") in date_holidays_2022):
                            cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                            aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                        
                        for i in range(max_mensual_posible + 1):
                            if datos_ingresados['incluir_festivos'] == 'false' or datos_ingresados['incluir_fds'] == 'false':
                                aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                while (aux_validar_sabados_domingos == '6') or (aux_validar_sabados_domingos == '0') or (cuenta_fechas.strftime("%F") in date_holidays_2022):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                                    aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                    
                            if datos_ingresados['incluir_festivos'] == 'false' or datos_ingresados['incluir_fds'] == 'true':
                                while (cuenta_fechas.strftime("%F") in date_holidays_2022):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                            
                            if datos_ingresados['incluir_festivos'] == 'true' or datos_ingresados['incluir_fds'] == 'false':
                                aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                                while (aux_validar_sabados_domingos == '6') or (aux_validar_sabados_domingos == '0'):
                                    cuenta_fechas = cuenta_fechas + timedelta(days = 1)
                                    aux_validar_sabados_domingos = (cuenta_fechas).strftime("%w")
                            fechas_return.append(cuenta_fechas.strftime('%Y-%m-%d'))
                            cuenta_fechas = cuenta_fechas + timedelta(days = periodo_meses)
                            
                        aux_last = fecha_hasta - (datetime.strptime(fechas_return[len(fechas_return)-1], '%Y-%m-%d')).date()
                        if aux_last.days < 0:
                            fechas_return.pop

                    case other:
                        try:
                            raise NotFound('Ingrese una unidad de cada válida')
                        except NotFound as e:
                            return Response({'success':False, 'detail':'Ingrese una unidad de cada válida', 'Opciones' : 'semanas o menses'}, status=status.HTTP_404_NOT_FOUND)
                    
                return Response({'success':True, 'detail':fechas_return}, status=status.HTTP_200_OK)
            case 'kilometraje':
                print("Entra")
                vehiculo = CatalogoBienes.objects.filter(id_bien=int(datos_ingresados['id_articulo'])).values().first()
                if not vehiculo:
                    raise ValidationError('Debe ingresar el id de un articulo existente')
                if vehiculo['cod_tipo_activo_id'] != 'Veh':
                    raise ValidationError('No se puedeprogramar por kilometraje un tipo de activo diferente a un vehículo')
                # if not datos_ingresados['desde'].isdigit() or not datos_ingresados['hasta'].isdigit() or not datos_ingresados['cada'].isdigit():
                #     raise ValidationError('En desde, cada o hasta debe ingresar un número entero')
                kilometraje_actual = HojaDeVidaVehiculos.objects.filter(id_articulo=vehiculo['id_bien']).values().first()
                if not kilometraje_actual:
                    raise ValidationError('El vehiculo ingresado no tiene hoja de vida registrada')
                if not kilometraje_actual['ultimo_kilometraje']:
                    raise ValidationError('El vehiculo ingresado no tiene kilometraje registrado')
                if int(datos_ingresados['desde']) <= int(kilometraje_actual['ultimo_kilometraje']) or int(datos_ingresados['desde']) >= (int(kilometraje_actual['ultimo_kilometraje']) + 10000) or int(datos_ingresados['hasta']) >= (int(kilometraje_actual['ultimo_kilometraje']) + 100000):
                    raise ValidationError('El kilometraje (desde) debe ser mayor al último kilometraje del equipo')
                if int(datos_ingresados['cada']) > 10001:
                    raise ValidationError('Cada debe ser menor 10000')
                max_mantenimientos = int((int(datos_ingresados['hasta']) - int(datos_ingresados['desde']))/int(datos_ingresados['cada']))
                kilometros_mantenimientos = []
                mantenimiento_suma = int(datos_ingresados['desde'])
                for i in range(max_mantenimientos + 1):
                    kilometros_mantenimientos.append(str(mantenimiento_suma))
                    mantenimiento_suma = mantenimiento_suma + int(datos_ingresados['cada'])
                return Response({'success':True, 'detail':kilometros_mantenimientos}, status=status.HTTP_200_OK)
            case other:
                return Response({'success':True, 'detail':'Para (programacion) elija una opción entre kilometraje o automatica'}, status=status.HTTP_200_OK)
            
class CreateProgramacionMantenimiento(generics.CreateAPIView):
    serializer_class = SerializerProgramacionMantenimientosPost
    queryset = ProgramacionMantenimientos.objects.all()
    
    def post(self, request, *args, **kwargs):
        datos_ingresados = request.data
        
        # Validación de datos ingresados
        for i in datos_ingresados:
            id_articulo = i['id_articulo']
            articulo = CatalogoBienes.objects.filter(id_bien=id_articulo).values().first()
            if not articulo:
                raise NotFound('Ingrese un id de articulo válido')
            if not articulo['tiene_hoja_vida']:
                raise ValidationError('El artículo no tiene hoja de vida por lo que no se puede programar mantenimiento')
            if articulo['cod_tipo_bien'] != 'A':
                raise ValidationError('Para programar un mantenimiento el bien debe ser un activo fijo')
            if articulo['cod_tipo_activo_id'] != 'Com' and articulo['cod_tipo_activo_id'] != 'Veh' and articulo['cod_tipo_activo_id'] != 'OAc':
                raise ValidationError('Para programar un mantenimiento el bien debe ser de tipo computador, vehiculo u otro tipo de activo')
            if articulo['nivel_jerarquico'] != 5:
                raise ValidationError('Para programar un mantenimiento el bien debe ser de nivel 5')
            if i['kilometraje_programado'] != None and i['fecha_programada'] != None:
                raise ValidationError('Debe programar por kilometraje o por fecha, no las dos opciones a la vez')
            if i['tipo_programacion'] == "fecha":
                if i['fecha_programada'] == None:
                    raise ValidationError('Si eligió programación por fecha debe ingresar una fecha en (fecha_programada)')
                if i['kilometraje_programado'] != None:
                    raise ValidationError('Si eligió programación por fecha el campo kilometraje debe estar en null')
            elif i['tipo_programacion'] == "kilometraje":
                if i['kilometraje_programado'] == None:
                    raise ValidationError('Si eligió programación por kilometraje debe ingresar un valor de kilometraje')
                # if not (i['kilometraje_programado'].isdigit()):
                #     raise NotFound('El valor del kilometraje debe ser un string que contenga solo números')
                if i['fecha_programada'] != None:
                    raise ValidationError('Si eligió programación por kilometraje el campo fecha_programada debe estar en null')
            #VALIDACION FORMATE DE FECHAS ENTRANTES
            if i['tipo_programacion'] == 'fecha':
                try:
                    aux_v_f_p = i['fecha_programada'].split("-")
                    aux_v_f_p_2 = i['fecha_solicitud'].split("-")
                except:
                    raise ValidationError('Formato de fecha no válido')
                if not (aux_v_f_p[0]).isdigit() or not (aux_v_f_p[1]).isdigit() or not (aux_v_f_p[2]).isdigit() or not (aux_v_f_p_2[0]).isdigit() or not (aux_v_f_p_2[1]).isdigit() or not (aux_v_f_p_2[2]).isdigit():
                    raise ValidationError('Formato de fecha no válido')
                if len(aux_v_f_p) != 3 or len(aux_v_f_p_2) != 3:
                    raise ValidationError('Formato de fecha no válido')
                a = (len(aux_v_f_p[0]) != 4)
                b = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
                c = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
                d = (len(aux_v_f_p[0]) != 4)
                e = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
                f = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
                
                if a or not b or not c or d or not e or not f:
                    raise ValidationError('Formato de fecha no válido')

                if int(aux_v_f_p[1]) <= 0 or int(aux_v_f_p[1]) >= 13 or int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32 or int(aux_v_f_p_2[1]) <= 0 or int(aux_v_f_p_2[1]) >= 13 or int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 32:
                    raise ValidationError('Formato de fecha no válido, debe ingresar un mes entre 1 y 12 y un día entre 1 y 31')
                mes = int(aux_v_f_p[1])
                anio = int(aux_v_f_p[0])
                mes_2 = int(aux_v_f_p_2[1])
                anio_2 = int(aux_v_f_p_2[0])
                if mes == 2:
                    if anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0):
                        if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 30:
                            raise ValidationError('En año bisiesto Febrero sólo puede tener hasta 29 días')
                    else:
                        if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 29:
                            raise ValidationError('Para le año ingresado Febrero solo puede tener hasta 28 días')
                if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
                    if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32:
                            raise ValidationError('Enero, Marzo, Mayo, Julio, Agosto, Octubre y Diciebre solo pueden tener entre 1 y 31 días')
                if mes == 4 or mes == 6 or mes == 9 or mes == 11:
                    if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 31:
                            raise ValidationError('Abril, Junio, Septiembre y Noviembre ssolo pueden tener entre 1 y 30 días')
                
                if mes_2 == 2:
                    if anio_2 % 4 == 0 and (anio_2 % 100 != 0 or anio_2 % 400 == 0):
                        if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 30:
                            raise ValidationError('En año bisiesto Febrero sólo puede tener hasta 29 días')
                    else:
                        if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 29:
                            raise ValidationError('Para el año ingresado Febrero solo puede tener hasta 28 días')
                if mes_2 == 1 or mes_2 == 3 or mes_2 == 5 or mes_2 == 7 or mes_2 == 8 or mes_2 == 10 or mes_2 == 12:
                    if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 32:
                            raise ValidationError('Enero, Marzo, Mayo, Julio, Agosto, Octubre y Diciembre solo pueden tener entre 1 y 31 días')
                if mes_2 == 4 or mes_2 == 6 or mes_2 == 9 or mes_2 == 11:
                    if int(aux_v_f_p_2[2]) <= 0 or int(aux_v_f_p_2[2]) >= 31:
                            raise ValidationError('Abril, Junio, Septiembre y Noviembre solo pueden tener entre 1 y 30 días')
                i['fecha_programada'] = (datetime.strptime(i['fecha_programada'], '%Y-%m-%d')).date()
                i['fecha_generada'] = datetime.now().date()
                i['fecha_solicitud'] = (datetime.strptime(i['fecha_solicitud'], '%Y-%m-%d')).date()
                a = i['fecha_generada'] - i['fecha_programada']
                if (i['fecha_generada'] > i['fecha_solicitud']) or (i['fecha_generada'] > i['fecha_programada']) or (i['fecha_solicitud'] > i['fecha_programada']):
                    raise ValidationError('La fecha de programación y la fecha de solicitud no pueden ser menores a la fecha de hoy')
                
            i['fecha_generada'] = datetime.now()
            
            serializer = self.get_serializer(data=i)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # AUDITORIA CREACIÓN DE MANTENIMIENTO
            user_logeado = request.user.id_usuario
            dirip = Util.get_client_ip(request)
            descripcion = {'Articulo':str(i['id_articulo']), 'Fecha generada':str(i['fecha_generada']), 'Fecha programada':str(i['fecha_programada']), 'Kilometraje programado':str(i['kilometraje_programado'])}
            valores_actualizados= None
            auditoria_data = {
                'id_usuario': user_logeado,
                'id_modulo': 23,
                'cod_permiso': 'CR',
                'subsistema': 'ALMA',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Mantenimiento programado con éxtio'}, status=status.HTTP_200_OK)
   
   
class CreateRegistroMantenimiento(generics.CreateAPIView):
    serializer_class = SerializerRegistroMantenimientosPost
    queryset = RegistroMantenimientos.objects.all()
    
    def post(self, request, *args, **kwargs):
        datos_ingresados = request.data
        #VALIDACION FORMATE DE FECHAS ENTRANTES
        try:
            aux_v_f_p = datos_ingresados['fecha_ejecutado'].split("-")
        except:
            raise ValidationError('Formato de fecha no válido')
        if not (aux_v_f_p[0]).isdigit() or not (aux_v_f_p[1]).isdigit() or not (aux_v_f_p[2]).isdigit():
            raise ValidationError('Formato de fecha no válido')
        if len(aux_v_f_p) != 3:
            raise ValidationError('Formato de fecha no válido')
        a = (len(aux_v_f_p[0]) != 4)
        b = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
        c = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
        d = (len(aux_v_f_p[0]) != 4)
        e = (len(aux_v_f_p[1]) <= 2 and len(aux_v_f_p[1]) >= 1)
        f = (len(aux_v_f_p[2]) <= 2 and len(aux_v_f_p[2]) >= 1)
        
        if a or not b or not c or d or not e or not f:
            raise ValidationError('Formato de fecha no válido')

        if int(aux_v_f_p[1]) <= 0 or int(aux_v_f_p[1]) >= 13 or int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32:
            raise ValidationError('Formato de fecha no válido, debe ingresar un mes entre 1 y 12 y un día entre 1 y 31')
        mes = int(aux_v_f_p[1])
        anio = int(aux_v_f_p[0])
        if mes == 2:
            if anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0):
                if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 30:
                    raise ValidationError('En año bisiesto Febrero sólo puede tener hasta 29 días')
            else:
                if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 29:
                    raise ValidationError('Para le año ingresado Febrero solo puede tener hasta 28 días')
        if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
            if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 32:
                    raise ValidationError('Enero, Marzo, Mayo, Julio, Agosto, Octubre y Diciembre solo pueden tener entre 1 y 31 días')
        if mes == 4 or mes == 6 or mes == 9 or mes == 11:
            if int(aux_v_f_p[2]) <= 0 or int(aux_v_f_p[2]) >= 31:
                    raise ValidationError('Abril, Junio, Septiembre y Noviembre ssolo pueden tener entre 1 y 30 días')
        
        id_articulo = datos_ingresados['id_articulo']
        articulo = CatalogoBienes.objects.filter(id_bien=id_articulo).exclude(nro_elemento_bien=None).values().first()
        datos_ingresados['fecha_registrado'] = datetime.now()
        fecha_registrado = datos_ingresados['fecha_registrado'].date()
        fecha_ejecutado = (datetime.strptime(datos_ingresados['fecha_ejecutado'], '%Y-%m-%d')).date()
        
        diferencia_dias = fecha_registrado - fecha_ejecutado
        diferencia_dias = diferencia_dias.days if fecha_registrado != fecha_ejecutado else 1
        
        cod_estado_final = EstadosArticulo.objects.filter(cod_estado=datos_ingresados['cod_estado_final'])
        persona_realiza = Personas.objects.filter(id_persona=datos_ingresados['id_persona_realiza']).values().filter()
        datos_ingresados['id_persona_diligencia'] = request.user.persona.id_persona
        if not articulo:
            raise NotFound('Ingrese un articulo válido. Debe ser activo fijo, de nivel jerarquico 5 y un elemento')
        if not articulo['tiene_hoja_vida']:
            raise PermissionDenied('El artículo no tiene hoja de vida por lo que no se puede registrar mantenimiento')
        if articulo['cod_tipo_bien'] != 'A':
            raise NotFound('Para registrar un mantenimiento el bien debe ser un activo fijo')
        if articulo['cod_tipo_activo_id'] != 'Com' and articulo['cod_tipo_activo_id'] != 'Veh' and articulo['cod_tipo_activo_id'] != 'OAc':
            raise NotFound('Para registrar un mantenimiento el bien debe ser de tipo computador, vehiculo u otro tipo de activo')
        if articulo['nivel_jerarquico'] != 5:
            raise NotFound('Para registrar un mantenimiento el bien debe ser de nivel 5')
        if diferencia_dias < 0:
            raise PermissionDenied('La fecha del registro del mantenimiento debe ser mayor o igual a la fecha de la ejecución del mantenimiento')
        if int(datos_ingresados['dias_empleados']) <= 0:
            raise ValidationError('Cantidad de días debe ser un número entero mayor a cero')
        if int(datos_ingresados['dias_empleados']) > diferencia_dias:
            raise ValidationError('La diferencia de fecha registrado y fecha ejecutado no puede ser mayor a la cantidad de días empleados')
        articulo = CatalogoBienes.objects.filter(id_bien=id_articulo).values().first()
        if datos_ingresados['cod_tipo_mantenimiento'] != 'P' and datos_ingresados['cod_tipo_mantenimiento'] != 'C':
            raise ValidationError('El tipo de mantenimiento debe ser P (preventivo) o C (correctivo)')
        if datos_ingresados['id_programacion_mtto'] != None and datos_ingresados['id_programacion_mtto'] != '':
            programacion_mantenimientos = ProgramacionMantenimientos.objects.filter(id_programacion_mtto = datos_ingresados['id_programacion_mtto']).values().first() 
            if not programacion_mantenimientos:
                raise NotFound('El id de programación de mantenimientos no existe')
            if programacion_mantenimientos['id_articulo_id'] != int(id_articulo):
                raise ValidationError('El id de programación de mantenimientos no tiene relación con el artículo enviado')
        else:
            programacion_mantenimientos = None
        if not cod_estado_final:
            raise NotFound('El codigo final no existe')
        if not persona_realiza:
            raise NotFound('El id de la persona que realiza el mantenimiento no existe')
        if programacion_mantenimientos:
            intance_programacion_mantenimientos = ProgramacionMantenimientos.objects.filter(id_programacion_mtto = datos_ingresados['id_programacion_mtto']).first()
            intance_programacion_mantenimientos.ejecutado = True
            intance_programacion_mantenimientos.save()
        inventario = Inventario.objects.filter(id_bien=datos_ingresados['id_articulo']).first()
        if inventario == None:
            raise NotFound('El id del artículo aún no se encuentra en el inventario')
        fecha_ultimo_movimiento = inventario.fecha_ultimo_movimiento.date()
        if inventario.fecha_ultimo_movimiento != None:
            aux_fecha = fecha_registrado - fecha_ultimo_movimiento
        else:
            aux_fecha = None
        if aux_fecha == None:
            raise NotFound('El bien seleeccionado no tiene movimientos registrados')
        if aux_fecha.days < 0:
            raise PermissionDenied('No se puede registrar el mantenimiento debido a que La fecha del registro del mantenimiento debe ser POSTERIOR O IGUAL a la fecha en la cual fue actualizado el estado anterior del activo')
        
        datos_ingresados['cod_estado_anterior'] = inventario.cod_estado_activo.cod_estado
        datos_ingresados['fecha_estado_anterior'] = inventario.fecha_ultimo_movimiento
        datos_ingresados['tipo_doc_anterior_mov'] = inventario.tipo_doc_ultimo_movimiento
        datos_ingresados['id_reg_en_doc_anterior_mov'] = inventario.id_registro_doc_ultimo_movimiento
        
        inventario.fecha_ultimo_movimiento = datos_ingresados['fecha_registrado']
        inventario.cod_estado_activo = cod_estado_final.first()
        
        serializer = self.get_serializer(data=datos_ingresados)
        serializer.is_valid(raise_exception=True)
        registro_mantenimiento = serializer.save()
        
        inventario.id_registro_doc_ultimo_movimiento = registro_mantenimiento.pk
        inventario.tipo_doc_ultimo_movimiento = 'MANT'
        inventario.save()        
        
        return Response({'success':True, 'detail':'Mantenimiento registrado con éxito'}, status=status.HTTP_200_OK)
    
class ControlMantenimientosProgramadosGetListView(generics.ListAPIView):
    serializer_class=ControlMantenimientosProgramadosGetListSerializer
    queryset=ProgramacionMantenimientos.objects.filter(ejecutado=False)
    permission_classes = [IsAuthenticated]

    def get(self,request):
        mantenimientos_programados = self.queryset.all()
        serializer = self.serializer_class(mantenimientos_programados, many=True)

        return Response({'success':True,'detail':'Se encontró la siguiente información','data':serializer.data},status=status.HTTP_200_OK)
