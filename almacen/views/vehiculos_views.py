from django.forms import BooleanField
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
from django.db import transaction
from rest_framework.response import Response
from django.http import JsonResponse
from transversal.models.organigrama_models import UnidadesOrganizacionales, NivelesOrganigrama



from almacen.models.vehiculos_models import (
    InspeccionesVehiculosDia,
    PeriodoArriendoVehiculo,
    SolicitudesViajes,
    VehiculosAgendables_Conductor,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor,
    ViajesAgendados
    )
from almacen.serializers.vehiculos_serializers import (
    ActualizarVehiculoArrendadoSerializer,
    AsignacionVehiculoSerializer,
    BusquedaAvanzadaGRLSerializer,
    BusquedaSolicitudViajeSerializer,
    BusquedaVehiculoSerializer,
    BusquedaVehiculosGRLSerializer,
    ClaseTerceroPersonaSerializer,
    CrearAgendaVehiculoDiaSerializer,
    HojaDeVidaVehiculosSerializer,
    InspeccionVehiculoSerializer,
    InspeccionesVehiculosDiaCreateSerializer,
    PeriodoVehiculoArrendadoSerializer,
    PutSolicitudViajeSerializer,
    RegistrarVehiculoArrendadoSerializer,
    SolicitudViajeSerializer,
    UpdateArrendarVehiculoSerializer,
    VehiculoConductorSerializer,
    VehiculoPersonaLogueadaSerializer,
    VehiculosAgendablesConductorSerializer,
    VehiculosArrendadosSerializer,
    ViajesAgendadosSerializer
    )
from transversal.models.base_models import ClasesTerceroPersona
from seguridad.utils import Util
from seguridad.models import Personas
from django.db.models import Value, CharField



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
    
    def get(self, request):
        filters = {}
        
        for key, value in request.query_params.items():
            if value != '':
                if key == 'nombre' or key == 'placa':
                    filters[key + '__icontains'] = value
                elif key == 'nombre_marca':
                    filters['id_marca__nombre__icontains'] = value
                elif key == 'nombre_contratista':
                    filters['empresa_contratista__icontains'] = value
        
        vehiculos_arrendados = self.queryset.filter(**filters)
        serializer = self.serializer_class(vehiculos_arrendados, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros de vehículos arrendados.', 'data': serializer.data}, status=status.HTTP_200_OK)

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
            if vehiculo.id_vehiculo_arrendado:
                vehiculo_marca_nombre = vehiculo.id_vehiculo_arrendado.id_marca.nombre
                vehiculo_placa = vehiculo.id_vehiculo_arrendado.placa
            else:
                vehiculo_marca_nombre = "Desconocido"
                vehiculo_placa = "Desconocido"

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
        
        # Conjunto para almacenar las asignaciones ya realizadas
        asignaciones_realizadas = set()
        
        # Iterar sobre cada asignación proporcionada en la lista
        for asignacion_data in asignaciones:
            serializer = self.serializer_class(data=asignacion_data)
            if serializer.is_valid():
                # Obtener los datos proporcionados por el usuario
                id_hoja_vida_vehiculo = serializer.validated_data['id_hoja_vida_vehiculo']
                id_persona_conductor = serializer.validated_data['id_persona_conductor']
                
                # Verificar si esta asignación ya ha sido realizada
                if (id_hoja_vida_vehiculo, id_persona_conductor) in asignaciones_realizadas:
                    errors.append({'detalle': ['Esta asignación ya ha sido realizada.']})
                    continue
                
                # Verificar si el conductor ya está asignado a otro vehículo
                if VehiculosAgendables_Conductor.objects.filter(id_persona_conductor=id_persona_conductor).exists():
                    errors.append({'id_persona_conductor': ['Este conductor ya está asignado a otro vehículo.']})
                    continue
                
                # Verificar si el vehículo ya está asignado a otro conductor
                if VehiculosAgendables_Conductor.objects.filter(id_hoja_vida_vehiculo=id_hoja_vida_vehiculo).exists():
                    errors.append({'id_hoja_vida_vehiculo': ['Este vehículo ya está asignado a otro conductor.']})
                    continue
                
                # Guardar la asignación como realizada
                asignaciones_realizadas.add((id_hoja_vida_vehiculo, id_persona_conductor))
                
                # Guardar la nueva asignación en la base de datos
                asignacion = VehiculosAgendables_Conductor.objects.create(
                    id_hoja_vida_vehiculo=id_hoja_vida_vehiculo,
                    id_persona_conductor=id_persona_conductor,
                    fecha_inicio_asignacion=serializer.validated_data['fecha_inicio_asignacion'],
                    fecha_final_asignacion=serializer.validated_data['fecha_final_asignacion'],
                    id_persona_que_asigna=request.user.persona,
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

        tipo_vehiculo = self.request.query_params.get('tipo_vehiculo')
        if tipo_vehiculo:
            queryset = queryset.filter(id_hoja_vida_vehiculo__cod_tipo_vehiculo=tipo_vehiculo)

        placa = self.request.query_params.get('placa')
        if placa:
            queryset = queryset.filter(id_hoja_vida_vehiculo__id_vehiculo_arrendado__placa__icontains=placa)

        conductor = self.request.query_params.get('conductor')
        if conductor:
            queryset = queryset.filter(
                Q(id_persona_conductor__primer_nombre__icontains=conductor) |
                Q(id_persona_conductor__primer_apellido__icontains=conductor) |
                Q(id_persona_conductor__primer_nombre__icontains=conductor.split()[0], id_persona_conductor__primer_apellido__icontains=conductor.split()[1])
            )


        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        serializer_data = serializer.data

        tipo_conductor = request.query_params.get('tipo_conductor')
        if tipo_conductor:
            # Verificamos si tipo_conductor es None antes de intentar iterar
            serializer_data = [vehiculo for vehiculo in serializer_data if vehiculo.get("tipo_conductor") and tipo_conductor.upper() in vehiculo["tipo_conductor"].upper()]

            
        return Response({'success': True, 'detail': 'Asignaciones de vehículos obtenidas exitosamente', 'data': serializer_data})
    

class EliminarAsignacionVehiculo(generics.DestroyAPIView):
    queryset = VehiculosAgendables_Conductor.objects.all()
    serializer_class = AsignacionVehiculoSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Asignación eliminada exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
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

        # Obtener el ID de la persona logueada
        id_persona_logueada = persona_logueada.id_persona

        # Obtener el nombre completo del conductor
        nombre_completo = f"{persona_logueada.primer_nombre} {persona_logueada.segundo_nombre} {persona_logueada.primer_apellido} {persona_logueada.segundo_apellido}"

        return Response({'success': True, 'detail': 'Información del conductor', 'data': {'id_persona_logueada': id_persona_logueada, 'nombre_completo': nombre_completo}})



#BUSQUEDA_AVANZADA_VEHICULOS
class VehiculosAsociadosPersona(generics.ListAPIView):
    serializer_class = VehiculoPersonaLogueadaSerializer

    def get(self, request, *args, **kwargs):
        # Obtener el ID de la persona logueada
        id_persona_logueada = self.request.user.persona.id_persona  # Suponiendo que la relación entre usuario y persona existe

        # Filtrar los vehículos asociados a la persona logueada
        vehiculos_asociados = VehiculosAgendables_Conductor.objects.filter(id_persona_conductor=id_persona_logueada)

        # Serializar los datos de los vehículos asociados
        serializer = self.get_serializer(vehiculos_asociados, many=True)

        # Retornar la respuesta con el mensaje
        return Response({'success': True, 'detail': 'Información de los vehículos asociados a la persona logueada', 'data': serializer.data}, status=status.HTTP_200_OK)
    


#INSPECCIONES_VEHICULOS
class CrearInspeccionVehiculo(generics.CreateAPIView):
    queryset = InspeccionesVehiculosDia.objects.all()
    serializer_class = InspeccionesVehiculosDiaCreateSerializer

    def create(self, request, *args, **kwargs):
        # Validamos los datos recibidos en la solicitud
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Asignar automáticamente la fecha de inspección y fecha de registro
            serializer.validated_data['dia_inspeccion'] = datetime.now().date()
            serializer.validated_data['fecha_registro'] = datetime.now()
            
            # Establecer la persona que realiza la inspección como la persona logueada
            serializer.validated_data['id_persona_inspecciona'] = request.user.persona

            # Verificar si se necesita verificación superior
            if not serializer.validated_data.get('requiere_verificacion'):
                # Si no se requiere verificación superior, establecer en False
                serializer.validated_data['verificacion_superior_realizada'] = False

            # Actualizar el kilometraje y fecha de última actualización si corresponde
            id_hoja_vida_vehiculo = serializer.validated_data.get('id_hoja_vida_vehiculo')
            if id_hoja_vida_vehiculo and not id_hoja_vida_vehiculo.id_vehiculo_arrendado:
                hoja_vida_vehiculo = id_hoja_vida_vehiculo
                hoja_vida_vehiculo.ultimo_kilometraje = serializer.validated_data.get('kilometraje')
                hoja_vida_vehiculo.fecha_ultimo_kilometraje = datetime.now().date()
                hoja_vida_vehiculo.save()
            
            #Actualizar el valor de T066esAgendable si está presente en los datos de la solicitud
            es_agendable = request.data['es_agendable']
            if es_agendable is not None:
                id_hoja_vida_vehiculo = serializer.validated_data.get('id_hoja_vida_vehiculo')
                if id_hoja_vida_vehiculo:
                    hoja_vida_vehiculo = HojaDeVidaVehiculos.objects.get(id_hoja_de_vida=id_hoja_vida_vehiculo.id_hoja_de_vida)
                    hoja_vida_vehiculo.es_agendable = es_agendable
                    hoja_vida_vehiculo.save()

            print(es_agendable)
            # Creamos la inspección de vehículo
            with transaction.atomic():
                instancia_inspeccion = serializer.save()

            data = serializer.data
            data['es_agendable'] = es_agendable

            # Retornamos el registro creado con la variable es_agendable
            return Response({'success': True, 'detail': 'Las inspeccion fue creada correctamente: ', 'data': data}, status=status.HTTP_201_CREATED)
        else:
            # Si los datos no son válidos, retornamos los errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        
class NovedadesVehiculosList(generics.ListAPIView):
    serializer_class = InspeccionVehiculoSerializer

    def get(self, request, format=None):
        vehiculos_sin_novedad = []
        vehiculos_con_novedad = []

        # Obtener todas las inspecciones de vehículos
        inspecciones = InspeccionesVehiculosDia.objects.all()

        for inspeccion in inspecciones:
            placa, marca = self.obtener_placa_y_marca(inspeccion)
            id_inspeccion = inspeccion.id_inspeccion_vehiculo
            id_hoja_de_vida = inspeccion.id_hoja_vida_vehiculo_id

            # Verificar las novedades
            novedades = self.verificar_novedades(inspeccion)

            if not novedades:
                vehiculos_sin_novedad.append({
                    "id_inspeccion_vehiculo": id_inspeccion,
                    "id_hoja_de_vida": id_hoja_de_vida,
                    "placa": placa,
                    "marca": marca
                })
            else:
                placa_marca = f"{placa}-{marca}"
                if len(novedades) == 1:
                    vehiculos_con_novedad.append({
                        "id_inspeccion_vehiculo": id_inspeccion,
                        "id_hoja_de_vida": id_hoja_de_vida,
                        "placa_marca": placa_marca,
                        "novedad": novedades[0]
                    })
                else:
                    vehiculos_con_novedad.append({
                        "id_inspeccion_vehiculo": id_inspeccion,
                        "id_hoja_de_vida": id_hoja_de_vida,
                        "placa_marca": placa_marca,
                        "cantidad_novedades": len(novedades)
                    })

        return Response({
            "success": True,
            "detail": "Inspecciones obtenidas correctamente",
            "data": {
                "vehiculos_sin_novedad": vehiculos_sin_novedad,
                "vehiculos_con_novedad": vehiculos_con_novedad
            }
        }, status=status.HTTP_200_OK)

    def obtener_placa_y_marca(self, inspeccion):
        hoja_vida_vehiculo = inspeccion.id_hoja_vida_vehiculo
        #VEHICULO_ARRENDADO
        if hoja_vida_vehiculo:
            if hoja_vida_vehiculo.id_vehiculo_arrendado:
                vehiculo_arrendado = hoja_vida_vehiculo.id_vehiculo_arrendado
                if vehiculo_arrendado:
                    placa = vehiculo_arrendado.placa if hasattr(vehiculo_arrendado, 'placa') else None
                    marca_nombre = vehiculo_arrendado.id_marca.nombre if hasattr(vehiculo_arrendado, 'id_marca') and hasattr(vehiculo_arrendado.id_marca, 'nombre') else None
                    return placa, marca_nombre
            #VEHICULO_PRIOPIO_ARRENDADO
            elif hoja_vida_vehiculo.id_articulo:
                catalogo_bien = hoja_vida_vehiculo.id_articulo
                if catalogo_bien:
                    placa = catalogo_bien.doc_identificador_nro if hasattr(catalogo_bien, 'doc_identificador_nro') else None
                    marca_nombre = catalogo_bien.id_marca.nombre if hasattr(catalogo_bien, 'id_marca') and hasattr(catalogo_bien.id_marca, 'nombre') else None
                    return placa, marca_nombre

        # Si hoja_vida_vehiculo es None o no tiene id_vehiculo_arrendado ni id_articulo
        return None, None

    def verificar_novedades(self, inspeccion):
        novedades = []
        campos_booleanos = [
            'dir_llantas_delanteras', 'dir_llantas_Traseras', 'limpiabrisas_delantero',
            'limpiabrisas_traseros', 'nivel_aceite', 'estado_frenos', 'nivel_refrigerante',
            'apoyo_cabezas_piloto', 'apoyo_cabezas_copiloto', 'apoyo_cabezas_traseros',
            'frenos_generales', 'freno_emergencia', 'llantas_delanteras', 'llantas_traseras',
            'llanta_repuesto', 'espejos_laterales', 'espejo_retrovisor', 'cinturon_seguridad_delantero',
            'cinturon_seguridad_trasero', 'luces_altas', 'luces_media', 'luces_bajas', 'luces_parada',
            'luces_parqueo', 'luces_reversa', 'kit_herramientas', 'botiquin_completo', 'pito'
        ]
        for campo in campos_booleanos:
            if not getattr(inspeccion, campo):
                novedades.append(campo)
        return novedades
    

class InspeccionVehiculoDetail(generics.RetrieveAPIView, generics.UpdateAPIView):
    queryset = InspeccionesVehiculosDia.objects.all()
    serializer_class = InspeccionVehiculoSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verificar si la inspección ya ha sido verificada anteriormente
        if instance.verificacion_superior_realizada:
            serializer = self.get_serializer(instance)
            return Response({'error': 'La inspección ya ha sido verificada anteriormente.', 'data': serializer.data}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el ID de la persona logueada
        persona_id = request.user.persona.id_persona if request.user.is_authenticated else None
        
        # Actualizar los campos de la inspección
        instance.verificacion_superior_realizada = True
        instance.id_persona_que_verifica_id = persona_id  # Actualizamos el ID de la persona logueada
        instance.save()

        serializer = self.get_serializer(instance)
        return Response({'success': True, 'detail': 'La inspección ha sido verificada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'detail': 'La inspección ha sido consultada correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    


#Busqueda_Avanzada_Solicitud_Viajes
class BusquedaSolicitudesViaje(generics.ListAPIView):
    serializer_class = BusquedaSolicitudViajeSerializer

    def get_queryset(self):
        queryset = SolicitudesViajes.objects.exclude(estado_solicitud='FN')  # Excluir las solicitudes en estado "Finalizada"
        
        # Obtener parámetros de consulta
        fecha_solicitud_desde = self.request.query_params.get('fecha_solicitud_desde')
        fecha_solicitud_hasta = self.request.query_params.get('fecha_solicitud_hasta')
        cod_municipio = self.request.query_params.get('cod_municipio')
        nro_pasajeros = self.request.query_params.get('nro_pasajeros')
        requiere_carga = self.request.query_params.get('requiere_carga')
        fecha_partida = self.request.query_params.get('fecha_partida')
        fecha_retorno = self.request.query_params.get('fecha_retorno')
        estado_solicitud = self.request.query_params.get('estado_solicitud')

        # Filtrar por fecha_solicitud DESDE
        if fecha_solicitud_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_solicitud_desde)

        # Filtrar por fecha_solicitud HASTA
        if fecha_solicitud_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_solicitud_hasta)

        # Filtrar por cod_municipio
        if cod_municipio:
            queryset = queryset.filter(cod_municipio=cod_municipio)

        # Filtrar por nro_pasajeros
        if nro_pasajeros:
            queryset = queryset.filter(nro_pasajeros__icontains=nro_pasajeros)

        # Filtrar por requiere_carga
        if requiere_carga:
            queryset = queryset.filter(requiere_carga=requiere_carga)

        # Filtrar por fecha_partida
        if fecha_partida:
            queryset = queryset.filter(fecha_partida__icontains=fecha_partida)

        # Filtrar por fecha_retorno
        if fecha_retorno:
            queryset = queryset.filter(fecha_retorno__icontains=fecha_retorno)

        # Filtrar por estado_solicitud si es válido
        if estado_solicitud:
            # Verificar si el estado proporcionado es válido
            estados_validos = ['ES', 'RE', 'RC']
            if estado_solicitud in estados_validos:
                queryset = queryset.filter(estado_solicitud=estado_solicitud)
            else:
                # Si el estado proporcionado no es válido, devolver una respuesta de error
                return Response({'error': f'El estado {estado_solicitud} no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return JsonResponse({
                'success': False,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.'
            }, status=status.HTTP_404_NOT_FOUND)

        data = []
        for solicitud in queryset:
            data.append({
                'id_solicitud_viaje': solicitud.id_solicitud_viaje,
                "id_persona_solicita": solicitud.id_persona_solicita.id_persona,
                'primer_nombre_solicitante': solicitud.id_persona_solicita.primer_nombre,
                'primer_apellido_solicitante': solicitud.id_persona_solicita.primer_apellido,
                'cod_municipio': solicitud.cod_municipio.cod_municipio,                
                'nombre_municipio': solicitud.cod_municipio.nombre,
                'fecha_solicitud': solicitud.fecha_solicitud,
                'tiene_expediente_asociado': solicitud.tiene_expediente_asociado,
                'motivo_viaje': solicitud.motivo_viaje,
                'direccion': solicitud.direccion,
                'indicaciones_destino': solicitud.indicaciones_destino,
                'nro_pasajeros': solicitud.nro_pasajeros,
                'requiere_carga': solicitud.requiere_carga,
                'fecha_partida': solicitud.fecha_partida,
                'hora_partida': solicitud.hora_partida,
                'fecha_retorno': solicitud.fecha_retorno,
                'hora_retorno': solicitud.hora_retorno,
                'requiere_compagnia_militar': solicitud.requiere_compagnia_militar,
                'consideraciones_adicionales': solicitud.consideraciones_adicionales,
                'fecha_aprobacion_responsable': solicitud.fecha_aprobacion_responsable,
                'fecha_rechazo': solicitud.fecha_rechazo,
                'justificacion_rechazo': solicitud.justificacion_rechazo,
                'estado_solicitud': solicitud.estado_solicitud
            })

        return JsonResponse({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': data
        }, status=status.HTTP_200_OK)
    


#RECHAZAR_SOLICITUD
class CrearReprobacion(generics.CreateAPIView):
    serializer_class = ViajesAgendadosSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Validar si existe la solicitud de viaje
        id_solicitud_viaje = data.get('id_solicitud_viaje')
        solicitud_viaje = SolicitudesViajes.objects.filter(id_solicitud_viaje=id_solicitud_viaje).first()
        if not solicitud_viaje:
            return JsonResponse({'error': 'La solicitud de viaje especificada no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validar que la solicitud de viaje esté en estado de espera
        if solicitud_viaje.estado_solicitud != 'ES':
            return JsonResponse({'error': 'La solicitud de viaje no está en estado de espera.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que se haya proporcionado la observación de no autorizado
        observacion_no_autorizado = data.get('observacion_no_autorizado')
        if not observacion_no_autorizado:
            return JsonResponse({'error': 'La observación de no autorizado es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el registro en la tabla T077ViajesAgendados
        viaje_agendado_data = {
            'id_solicitud_viaje': id_solicitud_viaje,
            'direccion': solicitud_viaje.direccion,
            'cod_municipio_destino': solicitud_viaje.cod_municipio.cod_municipio,
            'indicaciones_destino': solicitud_viaje.indicaciones_destino,
            'nro_total_pasajeros_req': solicitud_viaje.nro_pasajeros,
            'requiere_capacidad_carga': solicitud_viaje.requiere_carga,
            'fecha_partida_asignada': solicitud_viaje.fecha_partida,
            'hora_partida': solicitud_viaje.hora_partida,
            'fecha_retorno_asignada': solicitud_viaje.fecha_retorno,
            'hora_retorno': solicitud_viaje.hora_retorno,
            'requiere_compagnia_militar': solicitud_viaje.requiere_compagnia_militar,
            'viaje_autorizado': False,
            'observacion_autorizacion': observacion_no_autorizado,
            'fecha_no_autorizado': timezone.now(),
            'estado': 'FI',
            'ya_inicio': False,
            'ya_llego': False  
        }

        viaje_agendado_serializer = self.get_serializer(data=viaje_agendado_data)
        viaje_agendado_serializer.is_valid(raise_exception=True)
        viaje_agendado = viaje_agendado_serializer.save()

        # Obtener la persona logueada y la unidad organizacional actual
        persona_logueada = request.user.persona
        unidad_org_actual = persona_logueada.id_unidad_organizacional_actual

        # Actualizar la solicitud de viaje en la tabla T075SolicitudesViaje
        solicitud_viaje.id_persona_responsable = persona_logueada
        solicitud_viaje.id_unidad_org_responsable = unidad_org_actual
        solicitud_viaje.fecha_rechazo = viaje_agendado.fecha_no_autorizado
        solicitud_viaje.justificacion_rechazo = observacion_no_autorizado
        solicitud_viaje.estado_solicitud = 'RC'
        solicitud_viaje.save()

        return JsonResponse({'success': True, 'detail': 'Reprobación de la petición creada exitosamente.', 'data': viaje_agendado_serializer.data}, status=status.HTTP_201_CREATED)


#BUSQUEDA_VEHICULOS
class ListaVehiculosDisponibles(generics.ListAPIView):
    serializer_class = HojaDeVidaVehiculosSerializer

    def get_queryset(self):
        # Obtener todos los vehículos
        vehiculos = HojaDeVidaVehiculos.objects.all()

        # Obtener la fecha actual para realizar las comparaciones
        fecha_actual = timezone.now().date()

        # Filtrar vehículos que estén disponibles para agenda
        vehiculos_disponibles = []
        for vehiculo in vehiculos:
            # Verificar si el vehículo tiene asignaciones activas
            asignaciones_activas = ViajesAgendados.objects.filter(
                Q(id_vehiculo_conductor__id_hoja_vida_vehiculo=vehiculo.id_hoja_de_vida) &
                Q(estado='AC') &
                (Q(fecha_partida_asignada__lte=fecha_actual) & Q(fecha_retorno_asignada__gte=fecha_actual))
            ).exists()

            if not asignaciones_activas:
                vehiculos_disponibles.append(vehiculo)

        return vehiculos_disponibles

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for vehiculo in queryset:
            vehiculo_arrendado_data = {}
            vehiculo_arrendado = vehiculo.id_vehiculo_arrendado
            
            # Verificar si vehiculo_arrendado es None
            if vehiculo_arrendado:
                vehiculo_arrendado_data = {
                    'id_vehiculo_arrendado': vehiculo_arrendado.id_vehiculo_arrendado,
                    'nombre': vehiculo_arrendado.nombre,
                    'descripcion': vehiculo_arrendado.descripcion,
                    'placa': vehiculo_arrendado.placa,
                    'marca': vehiculo_arrendado.id_marca.nombre,
                    'empresa_contratista': vehiculo_arrendado.empresa_contratista,
                    'tiene_hoja_de_vida': vehiculo_arrendado.tiene_hoja_de_vida
                }
            
            data.append({
                'id_vehiculo_hoja_vida': vehiculo.id_hoja_de_vida,
                'cod_tipo_vehiculo': vehiculo.cod_tipo_vehiculo,
                'tiene_platon': vehiculo.tiene_platon,
                'es_arrendado': vehiculo.es_arrendado,
                'vehiculo_arrendado': vehiculo_arrendado_data
            })

        return JsonResponse({'success': True, 'detail': 'Vehículos disponibles para agenda.', 'data': data}, status=status.HTTP_200_OK)




from datetime import datetime

class BusquedaVehiculosGRL(generics.ListAPIView):
    serializer_class = BusquedaAvanzadaGRLSerializer

    def get_queryset(self):
        queryset = VehiculosAgendables_Conductor.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        # Obtener parámetros de la solicitud
        placa = self.request.query_params.get('placa')
        marca = self.request.query_params.get('marca')
        empresa_contratista = self.request.query_params.get('empresa_contratista')
        nombre = self.request.query_params.get('nombre')
        persona_conductor = self.request.query_params.get('persona_conductor')
        es_arrendado = self.request.query_params.get('es_arrendado')
        tiene_platon = self.request.query_params.get('tiene_platon')

        # Filtrar vehículos por parámetros de búsqueda
        data_filtrada = serializer.data

        if placa:
            data_filtrada = [item for item in data_filtrada if placa in (item['placa'] if item['placa'] else '')]

        if marca:
            data_filtrada = [item for item in data_filtrada if marca in (item['marca'] if item['marca'] else '')]

        if empresa_contratista:
            data_filtrada = [item for item in data_filtrada if empresa_contratista in (item['empresa_contratista'] if item['empresa_contratista'] else '')]

        if nombre:
            data_filtrada = [item for item in data_filtrada if nombre in (item['nombre'] if item['nombre'] else '')]

        if persona_conductor:
            data_filtrada = [item for item in data_filtrada if persona_conductor in (item['persona_conductor'] if item['persona_conductor'] else '')]

        if es_arrendado and es_arrendado != '':
            es_arrendado = True if 'True' in es_arrendado else False
            data_filtrada = [item for item in data_filtrada if es_arrendado == item['es_arrendado']]

        if tiene_platon and tiene_platon != '':
            tiene_platon = True if 'True' in tiene_platon else False
            data_filtrada = [item for item in data_filtrada if tiene_platon == item['tiene_platon']]

        # Realizar validación adicional
        vehiculos_disponibles = []
        for vehiculo in data_filtrada:
            # Validar si el vehículo tiene asignaciones activas
            asignaciones_activas = ViajesAgendados.objects.filter(
                id_vehiculo_conductor_id=vehiculo['id_vehiculo_conductor'],  # Usamos el campo id_vehiculo_conductor para la relación
                estado='AC',  # Filtro por estado ACTIVA
                fecha_partida_asignada__lte=datetime.now(),  # Filtramos por fecha de partida menor o igual a la fecha actual
                fecha_retorno_asignada__gte=datetime.now()  # Filtramos por fecha de retorno mayor o igual a la fecha actual
            ).exists()

            if not asignaciones_activas:
                vehiculos_disponibles.append(vehiculo)

        # Retornar la respuesta con la data procesada
        return Response({'success': True, 'detail': 'Vehículos obtenidos exitosamente', 'data': vehiculos_disponibles}, status=status.HTTP_200_OK)

    