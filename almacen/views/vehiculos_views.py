from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date, timedelta
from almacen.models.hoja_de_vida_models import HojaDeVidaVehiculos

from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    VehiculosAgendables_Conductor,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor
    )
from almacen.serializers.vehiculos_serializers import (
    ActualizarVehiculoArrendadoSerializer,
    CrearAgendaVehiculoDiaSerializer,
    PeriodoVehiculoArrendadoSerializer,
    RegistrarVehiculoArrendadoSerializer,
    UpdateArrendarVehiculoSerializer,
    VehiculosAgendablesConductorSerializer
    )
from transversal.models.base_models import ClasesTerceroPersona
from seguridad.utils import Util

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
 #TABLA T073 INSPECCION DIARIA DE VEHICULO
 