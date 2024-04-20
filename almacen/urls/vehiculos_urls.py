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
    path('obtener-informacion-viajes/<int:id_solicitud_viaje>/', views.ObtenerInformacionViajes.as_view(), name='obtener_informacion_viajes'),


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
    path('listar-inspecciones-id/<int:pk>/',views.InspeccionVehiculoID.as_view(),name='listar-inspecciones-vehiculos'),
    path('listar-inspecciones-id/<int:pk>/',views.InspeccionVehiculoID.as_view(),name='listar-inspecciones-vehiculos'),
    path('viajes-asociados-vehiculo/<int:id_vehiculo_conductor>/',views.ViajesAsociadosVehiculo.as_view(), name='viajes-asociados-vehiculo'),


    #Agendamiento_vehiculos
    path('busqueda-solicitudes-viajes/get/',views.BusquedaSolicitudesViaje.as_view(),name='busqueda-solicitudes-viaje'),
    path('reprobar-solicitud-viaje/create/',views.CrearReprobacion.as_view(),name='repobar-solicitudes-viaje'),
    path('aprobar-solicitud-viaje/create/',views.CrearAprobacion.as_view(),name='aprobar-solicitudes-viaje'),
    path('solicitud-viaje/<int:id_solicitud_viaje>/', views.ObtenerSolicitudViaje.as_view(), name='obtener_solicitud_viaje'),
    path('busqueda-vehiculos-general/',views.BusquedaVehiculosGRL.as_view(),name='busqueda-vehiculos-general'),
    path('detalles-vehiculos-agendados/',views.DetallesViajeGet.as_view(),name='detalles-vehiculos-agendados'),
    path('viajes-agendados/<int:pk>/', views.EditarAprobacion.as_view(), name='editar-aprobacion-viaje'),
    path('eliminar-viaje-agendado/<int:pk>/', views.EliminarViajeAgendado.as_view(), name='eliminar-viaje-agendado'),
    path('obtener-agendamiento-viajes/<int:id_solicitud_viaje>/', views.ObtenerInformacionAgendamiento.as_view(), name='obtener-informacion-agendamiento'),



    #Bitacora_Vehiculos
    path('listar-agendamientos/get/', views.ListarAgendamientos.as_view(), name='listar_agendamientos'),
    path('bitacora-salida/create/', views.CrearBitacoraSalida.as_view(), name='crear_bitacora_salida'),
    path('bitacora-salida/get/<int:id_viaje_agendado>/', views.ObtenerBitacoraSalida.as_view(), name='obtener_bitacora_salida'),
    path('bitacora-llegada/update/<int:id_viaje_agendado>/', views.ActualizarBitacoraLlegada.as_view(), name='actualizar_bitacora_llegada'),
    path('bitacora-llegada/get/<int:id_viaje_agendado>/', views.ObtenerBitacoraSalida.as_view(), name='obtener-bitacora-llegada'),

    #Solicitud_Viaje_Intengracion
    path('listar-solicitud-viaje/get/<int:pk>/',views.BusquedaEstadoSolicitudViaje.as_view(),name='listar-solicitud-viaje'),

    #Autorizacion_Solcitud Viaje
    path('listar-solicitud-viajes-autorizar/get/',views.SolicitudesViajePersona.as_view(),name='listar-solicitud-viaje-autorizar'),
    path('aprobar-solicitud-viaje/<int:pk>/', views.AprobarSolicitudViaje.as_view(), name='aprobar_solicitud_viaje'),
    path('rechazar-solicitud-viaje/<int:pk>/', views.AprobarSolicitudViaje.as_view(), name='rechazarr_solicitud_viaje'),




    







    




]
