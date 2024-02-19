from django.urls import path
from almacen.views import vehiculos_views as views

urlpatterns = [
    
    path('registrar/vehiculo/arrendado/create/',views.RegistrarVehiculoArrendado.as_view(),name='registrar-vehiculo-arrendado'),
    # path('vehiculo/agendable/conductor/create/',views.VehiculosAgendables.as_view(),name='vehiculo-agendable-conductor-create'),
    # path('arrendamiento/vehiculos/create/',views.PeriodoVehiculoArrendado.as_view(),name='arrendamiento-vehiculos-create'),
    # path('agenda/vehiculo/dia/create/',views.CrearAgendaVehiculoDia.as_view(),name='agenda-vehiculo-dia-create'),
    path('update/vehiculo/arrendado/<str:pk>/',views.ActualizarVehiculoArrendado.as_view(),name='update-vehiculo-arrendado'),
    # path('update/fecha/arrendamiento/vehiculo/<str:pk>/',views.UpdateArrendamientoVehiculos.as_view(),name='update-fecha-arrendamiento-vehiculo'),
    path('registro/vehiculo/arrendado/delete/<str:pk>/',views.DeleteRegistroVehiculoArriendo.as_view(),name='registro-vehiculo-arrendado-delete'),
    path('busqueda/vehiculo/arrendado/',views.BusquedaVehiculoArrendado.as_view(),name='busqueda-vehiculo-arrendado'),
    path('busqueda/fechas-arrendamiento/vehiculo/<str:pk>/',views.BusquedaFechasArrendamientoVehiculo.as_view(),name='busqueda-fechas-arrendamiento-vehiculo'),



    #Vehiculos_Final

    #Solicitud_de_viaje
    path('solicitar-viaje/create/',views.CrearSolicitudViaje.as_view(),name='solicitar-vehiculo-viaje'),
    path('listar-solicitudes-viajes/get/',views.ListaSolicitudesViaje.as_view(),name='listar-solicitudes-viaje'),
    path('eliminar-solicitudes-viajes/<int:pk>/',views.EliminarSolicitudViaje.as_view(),name='eliminar-solicitudes-viaje'),
    path('editar-solicitudes-viajes/<int:pk>/',views.EditarSolicitudViaje.as_view(),name='editar-solicitudes-viaje'),

    #Asignacion-vehiculo-conductor
    path('busqueda-vehiculos/get/',views.BusquedaVehiculos.as_view(),name='busqueda-vehiculos'),
    path('busqueda-conductores/get/',views.BusquedaConductores.as_view(),name='busqueda-conductores'),
    path('asignacion-conductor/create/',views.AsignarVehiculo.as_view(),name='asignacion-conductor'),
    path('listar-asignaciones/get/',views.ListarAsignacionesVehiculos.as_view(),name='listar-asignaciones'),
    path('eliminar-asignacion/<int:pk>/',views.EliminarAsignacionVehiculo.as_view(),name='eliminar-asignaciones'),

    #Inspeccion-vehiculos-conductor
    path('info-conductor/get/',views.DatosBasicosConductorGet.as_view(),name='info-conductor'),




]
