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
    path('vehiculo-persona-conductor/get/',views.VehiculosAsociadosPersona.as_view(),name='info-vehicukos-arrendados'),
    path('inspeccion-vehiculo/create/',views.CrearInspeccionVehiculo.as_view(),name='crear-inspeccion-vehiculos'),
    path('novedades-vehiculo/get/',views.NovedadesVehiculosList.as_view(),name='novedades-vehiculos'),
    path('revisar-vehiculo/<int:pk>/',views.InspeccionVehiculoDetail.as_view(),name='revisar-vehiculos'),


    #Agendamiento_vehiculos
    path('busqueda-solicitudes-viajes/get/',views.BusquedaSolicitudesViaje.as_view(),name='busqueda-solicitudes-viaje'),
    path('reprobar-solicitud-viaje/create/',views.CrearReprobacion.as_view(),name='repobar-solicitudes-viaje'),
    path('aprobar-solicitud-viaje/create/',views.CrearAprobacion.as_view(),name='aprobar-solicitudes-viaje'),
    path('solicitud-viaje/<int:id_solicitud_viaje>/', views.ObtenerSolicitudViaje.as_view(), name='obtener_solicitud_viaje'),
    path('busqueda-vehiculos-general/',views.BusquedaVehiculosGRL.as_view(),name='busqueda-vehiculos-general'),
    path('detalles-vehiculos-agendados/',views.DetallesViajeGet.as_view(),name='detalles-vehiculos-agendados'),
    path('viajes-agendados/<int:pk>/', views.EditarAprobacion.as_view(), name='editar_aprobacion_viaje'),
    path('eliminar-viaje-agendado/<int:pk>/', views.EliminarViajeAgendado.as_view(), name='eliminar_viaje_agendado'),




    




]
