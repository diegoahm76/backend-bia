from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date, timedelta, timezone
from almacen.models.hoja_de_vida_models import HojaDeVidaVehiculos
from transversal.models.base_models import Municipio, ApoderadoPersona, ClasesTerceroPersona, Personas
from django.utils import timezone
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from almacen.models.bienes_models import (CatalogoBienes)



from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    SolicitudesViajes,
    VehiculosAgendables_Conductor,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor
    )
from almacen.serializers.vehiculos_serializers import (
    ActualizarVehiculoArrendadoSerializer,
    AsignacionVehiculoSerializer,
    BusquedaVehiculoSerializer,
    ClaseTerceroPersonaSerializer,
    CrearAgendaVehiculoDiaSerializer,
    HojaDeVidaVehiculosSerializer,
    PeriodoVehiculoArrendadoSerializer,
    PutSolicitudViajeSerializer,
    RegistrarVehiculoArrendadoSerializer,
    SolicitudViajeSerializer,
    UpdateArrendarVehiculoSerializer,
    VehiculoConductorSerializer,
    VehiculosAgendablesConductorSerializer
    )
from transversal.models.base_models import ClasesTerceroPersona
from seguridad.utils import Util
from seguridad.models import Personas


#TABLA T071 CREAR REGISTROS DE ARRENDAMIENTO(MODELADO)
def crear_arriendo_vehiculo(data):
    serializer = RegistrarVehiculoArrendadoSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    creacion_arriendo = serializer.save()

    if data['asignar_hoja_de_vida']:
        agendable = data.get('es_agendable')
        if agendable is None:
            raise ValidationError("Debe indicar si el vehiculo es agendable o no.")
        
        hoja_de_vida = HojaDeVidaVehiculos.objects.create(
            id_vehiculo_arrendado=creacion_arriendo,
            es_arrendado=True,
            es_agendable=agendable
        )
        
        if data['fecha_inicio'] is None or data['fecha_fin'] is None:
            raise ValidationError("Los campos de las fechas son obligatorios para la creación del registro del vehículo arrendado.")
        
        fecha_data_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
        fecha_data_incio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
        
        if fecha_data_incio.date() > fecha_data_fin.date():
            raise ValidationError("No se puede crear un nuevo registro si la fecha de inicio supera la fecha final.")
        
        vehiculo = PeriodoArriendoVehiculo.objects.create(
            id_vehiculo_arrendado=creacion_arriendo,
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin']
        )

    return creacion_arriendo, serializer.data

class RegistrarVehiculoArrendado(generics.CreateAPIView):
    serializer_class = RegistrarVehiculoArrendadoSerializer
    permission_classes = [IsAuthenticated]
    queryset = VehiculosArrendados.objects.all()
    
    def post(self, request):
        data = request.data
        creacion_arriendo, serializer_data = crear_arriendo_vehiculo(data)
        
        return Response({'success': True, 'detail': 'Se creó correctamente el registro', 'data': serializer_data}, status=status.HTTP_201_CREATED)
# class RegistrarVehiculoArrendado(generics.CreateAPIView):
#     serializer_class = RegistrarVehiculoArrendadoSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = VehiculosArrendados.objects.all()
    
#     def post(self,request):
#         data = request.data
              
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
        
#         creacion_arriendo = serializer.save()
        
             
#         if data['asignar_hoja_de_vida']== True:
#             agendable = data.get('es_agendable')
#             if agendable == None:
#                 raise ValidationError("Debe de indicar si el vehiculo es agendable o no.")
#             hoja_de_vida = HojaDeVidaVehiculos.objects.create(
#                 # id_persona = persona_logueada,
#                 id_vehiculo_arrendado = creacion_arriendo,
#                 es_arrendado = True,
#                 es_agendable = agendable
#             )   
#             #REGISTRO DE LAS FECHAS DE ARRENDAMIENTO
      
#             if data['fecha_inicio'] == None or data['fecha_fin'] == None:
#                 raise ValidationError("Los campos de las fechas son obligatorio para la creación del registro del vehiculo arrendado.")
            
#             fecha_data_fin = datetime.strptime(data['fecha_fin'],'%Y-%m-%d')
#             fecha_data_incio = datetime.strptime(data['fecha_inicio'],'%Y-%m-%d')
                        
#             if fecha_data_incio.date() > fecha_data_fin.date():
#                 raise ValidationError("No se puede crear un nuevo registro si la fecha de inicio supera la fecha final.")
            
#             vehiculo = PeriodoArriendoVehiculo.objects.create(
#                 id_vehiculo_arrendado = creacion_arriendo,
#                 fecha_inicio = data['fecha_inicio'],
#                 fecha_fin = data['fecha_fin']
#             )
                  
#         return Response({'success':True, 'detail':'Se creo correctamente el registro', 'data': serializer.data}, status=status.HTTP_201_CREATED)

#********************************************************************************************************#

#TABLA T071 MODIFICAR ARRENDAMIENTO DE VEHICULOS
class ActualizarVehiculoArrendado(generics.UpdateAPIView):
    serializer_class = ActualizarVehiculoArrendadoSerializer
    queryset = VehiculosArrendados.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        data = request.data
        veh_arriendo = VehiculosArrendados.objects.filter(id_vehiculo_arrendado=pk).last()
        
        if not veh_arriendo:
            raise ValidationError("El registro que desea modificar no existe.")
        
        serializer = self.serializer_class(veh_arriendo,data=data)       
        serializer.is_valid(raise_exception=True)

        #//*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/**#
        
        registro = PeriodoArriendoVehiculo.objects.filter(id_vehiculo_arrendado = pk).last()
        
        if not data['periodos']:
            raise ValidationError('El vehiculo no puede quedar sin periodos de arrendamiento.')
        
        ultimo_data_periodo = data['periodos'][-1]        
        
        id_periodo_vehiculo_arriendo = ultimo_data_periodo['id_periodo_vehiculo_arriendo']
        
        fecha_data_inicio = datetime.strptime(ultimo_data_periodo['fecha_inicio'],'%Y-%m-%d')
        fecha_data_fin = datetime.strptime(ultimo_data_periodo['fecha_fin'],'%Y-%m-%d')
        
        hoja_vida_veh_arrendado = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=veh_arriendo.id_vehiculo_arrendado).first()
        
        agendas = VehiculosAgendadosDiaDisponible.objects.filter(id_Hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida)        
        conductores = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida)
        
        ultima_agenda = agendas.last()
        ultimo_conductor = conductores.last()
        
        fecha_sistema = datetime.now()
        
        
        if registro.fecha_fin < fecha_sistema.date():
            raise ValidationError ("Solo se pueden modificar registros que esten vigentes.")
        
        if id_periodo_vehiculo_arriendo: # modificar
            
            if fecha_data_inicio.date() > fecha_data_fin.date():
                raise ValidationError("No se puede agregar un periodo de tiempo, cuando la fecha inicial es mayor a la fecha final.")
            
            if registro.fecha_inicio != fecha_data_inicio.date():
                if conductores:
                    fechas_conductores = conductores.filter(fecha_inicio_asignacion__range = [registro.fecha_inicio, fecha_data_inicio.date()])
                    if fechas_conductores:
                        raise ValidationError("No se pueden actualizar las fechas debido a que se encuentran conductores asignados.")
                
                if agendas:
                    fechas_agendas = agendas.filter(dia_disponibilidad__range = [registro.fecha_fin, fecha_data_inicio.date()])
                    if fechas_agendas:
                        raise ValidationError("No se pueden actualizar las fechas, debido a que se encuentra con agenda disponible.")
                    
                registro.fecha_inicio = fecha_data_inicio.date()
 
            if registro.fecha_fin != fecha_data_fin.date():
                if agendas:
                    if fecha_data_fin.date() < ultima_agenda.dia_disponibilidad:
                        raise ValidationError("No es posible modificar el periodo de arriendo, el vehículo se encuentra agendado en las fechas a remover")
                if conductores:
                    if fecha_data_fin.date() < ultimo_conductor.fecha_final_asignacion:
                        raise ValidationError("No es posible modificar el periodo de arriendo, el vehículo tiene designado conductor en las fechas a remover")
                registro.fecha_fin = fecha_data_fin.date()
                
            registro.save()
        else:#crear
            
            if fecha_data_inicio.date() > fecha_data_fin.date():
                raise ValidationError("No se puede agregar un periodo de tiempo, cuando la fecha inicial es mayor a la fecha final.")
            
            if registro.fecha_fin > fecha_sistema.date():
                raise ValidationError("No se puede agregar un registro, hasta que la fecha el ultimo periodo de arrendamiento haya vencido.")
            if fecha_data_inicio.date() <= registro.fecha_fin:
                raise ValidationError("No se puede crear un nuevo periodo de arrendamiento, si el ultimo registro no ha vencido.")
        
            arriendo = PeriodoArriendoVehiculo.objects.create(
                id_vehiculo_arrendado = veh_arriendo,
                fecha_inicio = ultimo_data_periodo['fecha_inicio'],
                fecha_fin = ultimo_data_periodo['fecha_fin']
            )
            
        #ELIMINAR EL ULTIMO PERIODO DE ARRENDAMIENTO
        lista_id_periodos = [periodo['id_periodo_vehiculo_arriendo'] for periodo in data['periodos']]
        
        if registro.id_periodo_vehiculo_arriendo not in lista_id_periodos:

            if agendas:                                
                if registro.fecha_inicio <= ultima_agenda.dia_disponibilidad:
                    raise ValidationError("No se puede eliminar.")
                    
            if conductores:                    
                if registro.fecha_inicio <= ultimo_conductor.fecha_final_asignacion:
                    raise ValidationError("No se puede eliminar x2")
                    
            registro.delete()

        serializer.save()
        return Response({'success':True,'detail':'Se realiza la actualizacion Correctamente'},status=status.HTTP_200_OK)

#TABLA "T085PeriodoArriendoVehiculo" ELIMINAR REGISTROS(MODELADO)
def eliminar_registro_arrendamiento(pk):
    vehiculo = VehiculosArrendados.objects.filter(id_vehiculo_arrendado=pk).first()

    if not vehiculo:
        raise ValidationError("No existe el registro del vehiculo arrendado que desea eliminar.")

    periodos_veh_arrendado = PeriodoArriendoVehiculo.objects.filter(id_vehiculo_arrendado=pk)
    ultimo_periodo = periodos_veh_arrendado.last()

    hoja_vida_veh_arrendado = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=vehiculo.id_vehiculo_arrendado).last()
    #agenda = VehiculosAgendadosDiaDisponible.objects.filter(id_Hoja_vida_vehiculo=hoja_vida_veh_arrendado.id_hoja_de_vida).last()
    #conductor = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo=hoja_vida_veh_arrendado.id_hoja_de_vida).last()

    fecha_sistema = datetime.now()

    if  ultimo_periodo: #validaciones
        if ultimo_periodo.fecha_fin < fecha_sistema.date():
            raise ValidationError("Los registros con fechas vencidas no se pueden eliminar, solo es permitido eliminar los registros con fechas actuales.")

    # if periodos_veh_arrendado.count() > 1:
    #     raise ValidationError("No se puede eliminar.")
    # else:
    #     if agenda and ultimo_periodo.fecha_inicio <= agenda.dia_disponibilidad:
    #         raise ValidationError("No se puede eliminar.")

    #     if conductor and ultimo_periodo.fecha_inicio <= conductor.fecha_final_asignacion:
    #         raise ValidationError("No se puede eliminar x2")

    vehiculo.delete()#HACE PARTE DEL ELSE
        
    return True

class DeleteRegistroVehiculoArriendo(generics.DestroyAPIView):
    serializer_class = RegistrarVehiculoArrendadoSerializer
    queryset = VehiculosArrendados.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            eliminado = eliminar_registro_arrendamiento(pk)
            if eliminado:
                return Response({'success': True, 'detail': "Se eliminó el registro del arrendamiento del vehiculo exitosamente"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# class DeleteRegistroVehiculoArriendo(generics.DestroyAPIView):
#     serializer_class = RegistrarVehiculoArrendadoSerializer
#     queryset = VehiculosArrendados.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def delete(self,request,pk):
        
#         vehiculo = VehiculosArrendados.objects.filter(id_vehiculo_arrendado=pk).first()
        
#         if not vehiculo:
#             raise ValidationError("No existe el registro del vehiculo arrendado que desea eliminar.")
        
#         periodos_veh_arrendado = PeriodoArriendoVehiculo.objects.filter(id_vehiculo_arrendado=pk)
#         ultimo_periodo = periodos_veh_arrendado.last()
        
        
#         hoja_vida_veh_arrendado = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado = vehiculo.id_vehiculo_arrendado).last()
        
#         agenda = VehiculosAgendadosDiaDisponible.objects.filter(id_Hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida).last()
#         conductor = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida).last()
        
#         fecha_sistema = datetime.now()
        
#         if ultimo_periodo.fecha_fin < fecha_sistema.date():
#             raise ValidationError("Los registros con fechas vencidas no se pueden eliminar, solo es permitido eliminar los registros con fechas actuales.")
        
#         if periodos_veh_arrendado.count() > 1:

#             raise ValidationError("No se puede eliminar.")
                               
#         else:      
#             if agenda:
                            
#                 if ultimo_periodo.fecha_inicio <= agenda.dia_disponibilidad:
#                     raise ValidationError("No se puede eliminar.")
                
#             if conductor:
                
#                 if ultimo_periodo.fecha_inicio <= conductor.fecha_final_asignacion:
#                     raise ValidationError("No se puede eliminar x2")
            
#             vehiculo.delete()
        
#         return Response({'success':True,'detail':"Se elimino el registro del arrendamiento del vehiculo exitosamente"},status=status.HTTP_200_OK)

#SERVICIO DE BUSQUEDA DE VEHICULOS ARRENDADOS 'T071', POR NOMBRE Y VERSION

class BusquedaVehiculoArrendado(generics.ListAPIView):
    serializer_class = RegistrarVehiculoArrendadoSerializer
    queryset = VehiculosArrendados.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter={}
        
        for key, value in request.query_params.items():
            if key in ['nombre','placa']:
                if value != '':
                    filter[key+'__icontains'] = value
                    
        vehiculo_arrendado = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(vehiculo_arrendado,many=True)
        
        return Response({'succes':True,'detail':'Se encontraron los siguientes registros de vehiculos arrendados.','data':serializador.data},status=status.HTTP_200_OK)

class BusquedaFechasArrendamientoVehiculo(generics.ListAPIView):
    serializer_class = PeriodoVehiculoArrendadoSerializer
    queryset = PeriodoArriendoVehiculo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        vehiculo = PeriodoArriendoVehiculo.objects.filter(id_vehiculo_arrendado=pk).order_by('fecha_inicio')
        serializer = self.serializer_class(vehiculo, many=True)
        if not vehiculo:
            raise ValidationError("No existe el vehiculo arrendado que busca.")
        
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros de arrendamiento del vehiculo.','data':serializer.data},status=status.HTTP_200_OK)
        
# #TABLA T072 PARA CREAR REGISTROS
# class VehiculosAgendables(generics.CreateAPIView):
#     serializer_class = VehiculosAgendablesConductorSerializer
#     queryset = VehiculosAgendables_Conductor.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def post(self,request):
        
#         # persona = request.user.persona.id_persona 
               
#         data = request.data
#         persona_logueada = request.user.persona.id_persona        
#         data['id_persona_que_asigna'] = persona_logueada
        
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
        
#         conductor = ClasesTerceroPersona.objects.filter(id_persona=data['id_persona_conductor'],id_clase_tercero=7).first()
#         if not conductor:
#             raise ValidationError('Solo se pueden asignar conductores externos a los vehiculos arrendados.')
        
#         vehiculo_agendable = serializer.save()
              
#         return Response({'success':True,'detail':'Se Crea el Agendamiento del Vehiculo Correctamente'},status=status.HTTP_201_CREATED)

# #TABLA T085PERIODOSVEHICULOSARRENDADOS CREAR REGISTROS
# class PeriodoVehiculoArrendado(generics.CreateAPIView):
#     serializer_class = PeriodoVehiculoArrendadoSerializer
#     queryset = PeriodoArriendoVehiculo.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def post(self,request):
#         data = request.data
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
        
#         registro = PeriodoArriendoVehiculo.objects.filter(id_vehiculo_arrendado = data['id_vehiculo_arrendado']).last()
        
#         fecha_data_fin = datetime.strptime(data['fecha_fin'],'%Y-%m-%d')
#         fecha_data_inicio = datetime.strptime(data['fecha_inicio'],'%Y-%m-%d')
#         fecha_sistema = datetime.now()

#         if fecha_data_inicio.date() > fecha_data_fin.date():
#             raise ValidationError("No se puede crear un nuevo registro si la fecha de inicio supera la fecha final.")
        
#         if registro:
#             if registro.fecha_fin > fecha_sistema.date():
#                 raise ValidationError('ERROR x2')
            
#             if fecha_data_inicio.date() <= registro.fecha_fin:
#                 raise ValidationError("ERROR")
        
#         serializer.save()
        
#         return Response({'success':True, 'detail':'Se Crea el registro de arrendamiento'})
    
# #TABLA "T085PeriodoArriendoVehiculo" ACTUALIZAR FECHAS DE ARRENDAMIENTO  
# class UpdateArrendamientoVehiculos(generics.UpdateAPIView):
#     serializer_class = UpdateArrendarVehiculoSerializer
#     queryset = PeriodoArriendoVehiculo.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def put(self,request,pk):
#         data = request.data
        
#         periodo_veh_arrendado = PeriodoArriendoVehiculo.objects.filter(id_periodo_vehiculo_arriendo=pk).last()
        
#         if not periodo_veh_arrendado:
#             raise ValidationError("El registro que desea actualizar no existe, verificar datos.") 
        
#         hoja_vida_veh_arrendado = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=periodo_veh_arrendado.id_vehiculo_arrendado.id_vehiculo_arrendado).first()
        
               
#         serializer = self.serializer_class(periodo_veh_arrendado,data=data)
#         serializer.is_valid(raise_exception=True)
#         fecha_fin_data = datetime.strptime(data["fecha_fin"],'%Y-%m-%d').date()
        
#         #fecha_inicio_data = datetime.strptime(data["fecha_inicio"],'%Y-%m-%d')
        
#         agenda = VehiculosAgendadosDiaDisponible.objects.filter(id_Hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida).last()
        
#         conductor = VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo = hoja_vida_veh_arrendado.id_hoja_de_vida).last()
        
#         if fecha_fin_data < periodo_veh_arrendado.fecha_fin:
#             if fecha_fin_data < agenda.dia_disponibilidad:
#                 raise ValidationError("No es posible modificar el periodo de arriendo, el vehículo se encuentra agendado en las fechas a remover")

#             if fecha_fin_data < conductor.fecha_final_asignacion:
#                 raise ValidationError("No es posible modificar el periodo de arriendo, el vehículo tiene designado conductor en las fechas a remover")
              
#         serializer.save()
        
#         return Response({'success':True,'detail':'Se actualizo el registro correctamente.'},status=status.HTTP_200_OK)

# #TABLA T074 VEHICULOS AGENDADOS POR DIA - CREAR
# class CrearAgendaVehiculoDia(generics.CreateAPIView):
#     serializer_class = CrearAgendaVehiculoDiaSerializer
#     queryset = VehiculosAgendadosDiaDisponible.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def post(self,request):
#         data = request.data
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
        
#         serializer.save()
        
#         return Response({'succes':True,'detail':'Se crea la agenda solicitada.','data':serializer.data},status=status.HTTP_201_CREATED)
        
    
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#VEHICULOS_FINAL
    
#CREAR_SOLICITUD_VIAJE

class CrearSolicitudViaje(generics.CreateAPIView):
    serializer_class = SolicitudViajeSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Validar que el número de pasajeros sea válido
        nro_pasajeros = data.get('nro_pasajeros', 0)
        if nro_pasajeros <= 0:
            raise ValidationError({'nro_pasajeros': 'El número de pasajeros debe ser mayor que 0'})

        # Validar que se haya proporcionado el código de municipio y departamento
        cod_municipio = data.get('cod_municipio')
        if not cod_municipio:
            raise ValidationError({'cod_municipio': 'El código de municipio es obligatorio'})
        
        cod_departamento = data.get('cod_departamento')
        if not cod_departamento:
            raise ValidationError({'cod_departamento': 'El código de departamento es obligatorio'})

        # Validar que si tiene_expediente_asociado es False, no se permita agregar el campo id_expediente_asociado
        tiene_expediente_asociado = data.get('tiene_expediente_asociado', False)
        if not tiene_expediente_asociado and 'id_expediente_asociado' in data:
            raise ValidationError({'id_expediente_asociado': 'No se puede especificar un expediente asociado si tiene_expediente_asociado es False'})
        
        # Validar que existe el ID de expediente asociado si tiene_expediente_asociado es True
        if tiene_expediente_asociado and not data.get('id_expediente_asociado'):
            raise ValidationError({'id_expediente_asociado': 'Se debe proporcionar un ID de expediente asociado si tiene_expediente_asociado es True'})

        # Validar que los campos de fecha y hora de partida y retorno sean obligatorios
        fecha_partida = data.get('fecha_partida')
        if not fecha_partida:
            raise ValidationError({'fecha_partida': 'La fecha de partida es obligatoria'})

        hora_partida = data.get('hora_partida')
        if not hora_partida:
            raise ValidationError({'hora_partida': 'La hora de partida es obligatoria'})

        fecha_retorno = data.get('fecha_retorno')
        if not fecha_retorno:
            raise ValidationError({'fecha_retorno': 'La fecha de retorno es obligatoria'})

        hora_retorno = data.get('hora_retorno')
        if not hora_retorno:
            raise ValidationError({'hora_retorno': 'La hora de retorno es obligatoria'})

        # Obtener la fecha y hora actual del sistema
        fecha_solicitud = timezone.now()

        # Asignar el estado predeterminado "En Espera"
        data['estado_solicitud'] = 'ES'

        # Obtener la persona logueada
        persona_logueada = request.user.persona

        # Obtener la unidad organizacional actual de la persona logueada
        id_unidad_org_solicita = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional

        # Asignar los valores a los campos de la solicitud de viaje
        solicitud_data = {
            'id_persona_solicita': persona_logueada.id_persona,
            'id_unidad_org_solicita': id_unidad_org_solicita,
            'fecha_solicitud': fecha_solicitud,
            'nro_pasajeros': nro_pasajeros,
            'cod_municipio': cod_municipio,
            'motivo_viaje': data.get('motivo_viaje_solicitado', ''),  # Corregido el nombre del campo
            'indicaciones_destino': data.get('indicaciones_destino', ''),
            'requiere_carga': data.get('requiere_carga', False),
            'fecha_partida': fecha_partida,
            'hora_partida': hora_partida,
            'fecha_retorno': fecha_retorno,
            'hora_retorno': hora_retorno,
            'requiere_compagnia_militar': data['req_compagnia_militar'],  # Corregido el nombre del campo
            'consideraciones_adicionales': data.get('consideraciones_adicionales', ''),
        }

        # Combinar los datos proporcionados con los valores calculados y asignados
        data.update(solicitud_data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()

        return Response({'success': True, 'detail': 'Solicitud creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    

#Listar_Solicitudes_Viaje
class ListaSolicitudesViaje(generics.ListAPIView):
    serializer_class = SolicitudViajeSerializer

    def get_queryset(self):
        queryset = SolicitudesViajes.objects.all()  # Obtiene todas las solicitudes de viaje

        # Obtener parámetros de consulta
        fecha_solicitud_desde = self.request.query_params.get('fecha_solicitud_desde')
        fecha_solicitud_hasta = self.request.query_params.get('fecha_solicitud_hasta')
        estado_solicitud = self.request.query_params.get('estado_solicitud')

        # Filtrar por fecha_solicitud DESDE
        if fecha_solicitud_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_solicitud_desde)

        # Filtrar por fecha_solicitud HASTA
        if fecha_solicitud_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_solicitud_hasta)
    
         # Filtrar por estado_solicitud si es válido
        if estado_solicitud:
            # Verificar si el estado proporcionado es válido
            estados_validos = ['ES', 'RE', 'RC', 'FN']
            if estado_solicitud in estados_validos:
                queryset = queryset.filter(estado_solicitud=estado_solicitud)
            else:
                # Si el estado proporcionado no es válido, devolver una respuesta de error
                return Response({'error': f'El estado {estado_solicitud} no es válido.'}, status=status.HTTP_400_BAD_REQUEST)


        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Solicitudes obtenidas exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    



class EliminarSolicitudViaje(generics.DestroyAPIView):
    queryset = SolicitudesViajes.objects.all()
    serializer_class = SolicitudViajeSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Validar que la solicitud no esté en estado "Finalizada"
            if instance.estado_solicitud == 'FN':
                return Response({'success': False, 'detail': 'No se puede eliminar una solicitud finalizada'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Serializar los datos de la instancia antes de eliminarla
            serializer = self.get_serializer(instance)
            
            self.perform_destroy(instance)
            
            return Response({'success': True, 'detail': 'Solicitud eliminada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({'success': False, 'detail': 'La solicitud de viaje no existe'}, status=status.HTTP_404_NOT_FOUND)
        

class EditarSolicitudViaje(generics.UpdateAPIView):
    queryset = SolicitudesViajes.objects.all()
    serializer_class = PutSolicitudViajeSerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar que la solicitud esté en estado "Rechazada"
            if instance.estado_solicitud != 'RC':
                return Response({'success': False, 'detail': 'Solo se pueden editar solicitudes en estado "Rechazada"'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({'success': True, 'detail': 'Solicitud editada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        except SolicitudesViajes.DoesNotExist:
            return Response({'success': False, 'detail': 'La solicitud de viaje no existe'}, status=status.HTTP_404_NOT_FOUND)




#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ASIGNACION-VEHICULO-CONDUCTOR
    

#Busqueda-Vehiculos
class BusquedaVehiculos(generics.ListAPIView):
    serializer_class = HojaDeVidaVehiculosSerializer

    def get_queryset(self):
        tipo_vehiculo = self.request.query_params.get('tipo_vehiculo')
        marca = self.request.query_params.get('marca')
        placa = self.request.query_params.get('placa')

        queryset = HojaDeVidaVehiculos.objects.filter(es_agendable=True)

        if tipo_vehiculo:
            queryset = queryset.filter(cod_tipo_vehiculo=tipo_vehiculo)

        if marca:
            queryset = queryset.filter(id_vehiculo_arrendado__id_marca__nombre__icontains=marca)

        if placa:
            queryset = queryset.filter(id_vehiculo_arrendado__placa__icontains=placa)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        # Agregar el nombre de la marca y el tipo de vehículo a cada objeto serializado
        for data in serializer.data:
            vehiculo = HojaDeVidaVehiculos.objects.get(pk=data['id_hoja_de_vida'])
            vehiculo_marca_nombre = vehiculo.id_vehiculo_arrendado.id_marca.nombre
            vehiculo_placa = vehiculo.id_vehiculo_arrendado.placa
            if data['cod_tipo_vehiculo'] == "C":
                tipo_vehiculo = "CARRO"
            elif data['cod_tipo_vehiculo'] == "M":
                tipo_vehiculo = "MOTO"
            else:
                tipo_vehiculo = data['cod_tipo_vehiculo']
            data['marca_nombre'] = vehiculo_marca_nombre
            data['vehiculo_placa'] = vehiculo_placa
            data['tipo_vehiculo'] = tipo_vehiculo

        # Retornar la respuesta con la data procesada
        return Response({'success': True, 'detail': 'Vehículos obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    

#Busqueda-Conductores
class BusquedaConductores(generics.ListAPIView):
    serializer_class = ClaseTerceroPersonaSerializer

    def get_queryset(self):
        tipo_conductor = self.request.query_params.get('tipo_conductor')
        conductor_nombre = self.request.query_params.get('conductor_nombre')

        # Filtrar los conductores que tengan la clase "Conductor" o "Conductor Externo" en T007ClasesTerceros
        queryset = ClasesTerceroPersona.objects.filter(
            Q(id_clase_tercero__nombre="Conductor") | Q(id_clase_tercero__nombre="Conductor Externo")
        )

       # Filtrar por tipo de conductor
        if tipo_conductor:
            if tipo_conductor == "IN":
                queryset = queryset.filter(id_clase_tercero__nombre="Conductor")
            elif tipo_conductor == "EX":
                queryset = queryset.filter(id_clase_tercero__nombre="Conductor Externo")
                
        # Filtrar por nombre del conductor
        if conductor_nombre:
            # Obtener los IDs de las personas con el nombre buscado
            personas_ids = Personas.objects.filter(
                Q(primer_nombre__icontains=conductor_nombre) |
                Q(primer_apellido__icontains=conductor_nombre)
            ).values_list('id_persona', flat=True)
            # Filtrar las ClasesTerceroPersona con esos IDs
            queryset = queryset.filter(id_persona__in=personas_ids)

        # Filtrar conductores que no tienen asignaciones de vehículos
        conductores_sin_asignacion = []
        for conductor in queryset:
            if not VehiculosAgendables_Conductor.objects.filter(id_persona_conductor=conductor.id_persona.id_persona).exists():
                conductores_sin_asignacion.append(conductor)

        return conductores_sin_asignacion

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        
        # Agregar el nombre de la clase tercera y los datos de la persona a cada objeto serializado
        for data in serializer.data:
            clase_tercera = ClasesTerceroPersona.objects.get(pk=data['id_clase_tercero_persona'])
            persona = Personas.objects.get(pk=data['id_persona'])
            data['nombre_clase_tercero'] = clase_tercera.id_clase_tercero.nombre
            # data['nombre_persona'] = persona.primer_nombre
            # data['apellidos_persona'] = persona.primer_apellido
            data['nombre_persona'] = f"{persona.primer_nombre} {persona.primer_apellido}"
            data['nro_documento'] = persona.numero_documento

           

        return Response({'success': True, 'detail': 'Conductores obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)

#Asignar_Vehiculo
class AsignarVehiculo(generics.CreateAPIView):
    serializer_class = VehiculosAgendablesConductorSerializer

    def post(self, request, *args, **kwargs):
        asignaciones = request.data  # Obtener la lista de asignaciones desde el cuerpo de la solicitud
        
        # Lista para almacenar los errores de validación
        errors = []
        # Lista para almacenar las asignaciones exitosas
        asignaciones_exitosas = []
        
        # Iterar sobre cada asignación proporcionada en la lista
        for asignacion_data in asignaciones:
            serializer = self.serializer_class(data=asignacion_data)
            if serializer.is_valid():
                # Obtener los datos proporcionados por el usuario
                id_hoja_vida_vehiculo = serializer.validated_data['id_hoja_vida_vehiculo']
                id_persona_conductor = serializer.validated_data['id_persona_conductor']
                fecha_inicio_asignacion = serializer.validated_data['fecha_inicio_asignacion']
                fecha_final_asignacion = serializer.validated_data['fecha_final_asignacion']
                
                # Obtener la persona logueada
                persona_logueada = request.user.persona
                
                # Guardar la nueva asignación en la base de datos
                asignacion = VehiculosAgendables_Conductor.objects.create(
                    id_hoja_vida_vehiculo=id_hoja_vida_vehiculo,
                    id_persona_conductor=id_persona_conductor,
                    fecha_inicio_asignacion=fecha_inicio_asignacion,
                    fecha_final_asignacion=fecha_final_asignacion,
                    id_persona_que_asigna=persona_logueada,
                    fecha_registro=datetime.now()  # Utilizar now() para obtener la fecha actual
                )
                
                # Serializar la asignación creada y añadirla a la lista de asignaciones exitosas
                asignacion_serializer = self.serializer_class(asignacion)
                asignaciones_exitosas.append(asignacion_serializer.data)
            else:
                # Si los datos proporcionados por el usuario no son válidos, añadir los errores a la lista
                errors.append(serializer.errors)
        
        # Devolver una respuesta exitosa con la información de las asignaciones creadas o errores de validación
        if errors:
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': True, 'detail': 'Se asignaron correctamente los vehículos.', 'data': asignaciones_exitosas}, status=status.HTTP_200_OK)
        


class ListarAsignacionesVehiculos(generics.ListAPIView):
    serializer_class = AsignacionVehiculoSerializer

    def get_queryset(self):
        queryset = VehiculosAgendables_Conductor.objects.all()

        # Filtrar por tipo de vehículo (C: Carro, M: Moto)
        tipo_vehiculo = self.request.query_params.get('tipo_vehiculo')
        if tipo_vehiculo:
            queryset = queryset.filter(id_hoja_vida_vehiculo__cod_tipo_vehiculo=tipo_vehiculo)

        # Filtrar por placa del vehículo
        placa = self.request.query_params.get('placa')
        if placa:
            queryset = queryset.filter(id_hoja_vida_vehiculo__id_vehiculo_arrendado__placa__icontains=placa)

        # Filtrar por nombre o número de documento del conductor
        conductor = self.request.query_params.get('conductor')
        if conductor:
            queryset = queryset.filter(
                id_persona_conductor__primer_nombre__icontains=conductor) | queryset.filter(
                    id_persona_conductor__numero_documento__icontains=conductor)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        serializer_data = serializer.data

        #Filtrar por tipo de conductor (IN: Interno, EX: Externo)
        tipo_conductor = request.query_params.get('tipo_conductor')
        if tipo_conductor:
            serializer_data = [vehiculo for vehiculo in serializer_data if tipo_conductor.lower() in vehiculo["tipo_conductor"].lower()]
            
        
        return Response({'success': True, 'detail': 'Asignaciones de vehículos obtenidas exitosamente', 'data': serializer_data})
    

class EliminarAsignacionVehiculo(generics.DestroyAPIView):
    queryset = VehiculosAgendables_Conductor.objects.all()
    serializer_class = AsignacionVehiculoSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Asignación eliminada exitosamente', 'data': serializer.data}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'success': False, 'detail': 'Error al eliminar la asignación'}, status=status.HTTP_400_BAD_REQUEST)



#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#INSPECCION_VEHICULOS
class DatosBasicosConductorGet(generics.ListAPIView):
    def get(self, request, format=None):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Obtener la persona logueada
        persona_logueada = request.user.persona

        # Obtener el nombre completo del conductor
        nombre_completo = f"{persona_logueada.primer_nombre} {persona_logueada.segundo_nombre} {persona_logueada.primer_apellido} {persona_logueada.segundo_apellido}"


        return Response({'success': True, 'detail': 'nombre_conductor', 'data': nombre_completo})



#BUSQUEDA_AVANZADA_VEHICULOS
class BusquedaAvanzadaVehiculosArrendados(generics.ListAPIView):
    serializer_class = BusquedaVehiculoSerializer

    def get_queryset(self):
            # Obtener la persona logueada (conductor)
            persona_logueada = self.request.user.persona

            # Buscar el registro en la tabla VehiculosAgendables_Conductor
            vehiculo_conductor = VehiculosAgendables_Conductor.objects.get(id_persona_conductor=persona_logueada)
            hoja_de_vida_vehiculo = vehiculo_conductor.id_hoja_vida_vehiculo

            if hoja_de_vida_vehiculo.es_arrendado:
                # Si el vehículo es arrendado, obtener la información de la tabla VehiculosArrendados
                vehiculo_arrendado = VehiculosArrendados.objects.get(id_vehiculo_arrendado=hoja_de_vida_vehiculo.id_vehiculo_arrendado)
                placa = vehiculo_arrendado.placa
                nombre_vehiculo = vehiculo_arrendado.nombre
                marca_vehiculo = vehiculo_arrendado.id_marca.nombre  # Obtener el nombre de la marca
                tiene_hoja_vida = vehiculo_arrendado.tiene_hoja_de_vida
            else:
                # Si el vehículo no es arrendado, obtener la información de la tabla CatalogoBienes
                articulo = CatalogoBienes.objects.get(id_bien=hoja_de_vida_vehiculo.id_articulo)
                placa = articulo.doc_identificador_nro
                nombre_vehiculo = articulo.nombre
                marca_vehiculo = None  # No aplicable para vehículos no arrendados
                tiene_hoja_vida = articulo.tiene_hoja_de_vida

            # Agregar la placa, el nombre del vehículo y la marca seleccionada al contexto
            self.request.session['vehiculo_seleccionado_placa'] = placa
            self.request.session['vehiculo_seleccionado_nombre'] = nombre_vehiculo
            self.request.session['vehiculo_seleccionado_marca'] = marca_vehiculo

            queryset = HojaDeVidaVehiculos.objects.all()

            # Filtrar los vehículos por placa, nombre del vehículo, nombre del contratista y marca
            placa_param = self.request.query_params.get('placa', None)
            nombre_vehiculo_param = self.request.query_params.get('nombre_vehiculo', None)
            nombre_contratista_param = self.request.query_params.get('nombre_contratista', None)
            marca_param = self.request.query_params.get('marca', None)

            if placa_param:
                queryset = queryset.filter(placa=placa_param)
            if nombre_vehiculo_param:
                queryset = queryset.filter(nombre=nombre_vehiculo_param)
            if nombre_contratista_param:
                queryset = queryset.filter(nombre_contratista=nombre_contratista_param)
            if marca_param:
                # Filtrar por marca (si el vehículo es arrendado)
                if hoja_de_vida_vehiculo.es_arrendado:
                    queryset = queryset.filter(id_vehiculo_arrendado__id_marca__nombre=marca_param)
                else:
                    # Si el vehículo no es arrendado, buscar en la tabla CatalogoBienes
                    queryset = queryset.filter(id_articulo__id_marca__nombre=marca_param)

            return queryset, tiene_hoja_vida