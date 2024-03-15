from django.urls import path
from almacen.views import activos_views as views




urlpatterns = [
    

    #Baja_Activos
    path('busqueda-avanzada-bienes/get/',views.BuscarBien.as_view(),name='busqueda-avanzada-bien'),
    path('crear-baja-activos/create/',views.RegistrarBajaCreateView.as_view(),name='crear-baja-activo'),
    path('restablecer-consecutivo/get/',views.UltimoConsecutivoView.as_view(),name='consecutivo-baja-activo'),
    path('actualizar-baja-activos/update/<int:pk>/', views.ActualizarBajaActivosView.as_view(), name='actualizar-baja-activo'),
    path('eliminar-baja-activos/<int:pk>/', views.BorrarBajaActivosView.as_view(), name='borrar-baja-activos'),
    path('info-baja-activos/get/<int:consecutivo>/', views.BajaActivosPorConsecutivo.as_view(), name='baja-activos-consecutivo'),
    path('bajas-activos/get/', views.ListarBajasActivosView.as_view(), name='listar_bajas_activos'),

    #Solicitud_Bajas_Activos
    path('crear-solicitud-baja-activos/create/',views.CrearSolicitudActivosView.as_view(),name='crear-solicitud-baja-activo'),
    path('editar-solicitud-activos/<int:pk>/', views.EditarSolicitudActivosView.as_view(), name='editar-solicitud-activos'),
    path('listar-unidades-medida/get/',views.ListarUnidadesMedidaActivas.as_view(),name='listar-unidades-medida'),
    path('detalle-solicitud-activos/<int:id_solicitud_viaje>/', views.DetalleSolicitudActivosView.as_view(), name='detalle-solicitud-activos'),
    path('resumen-solicitud-activos/<int:id_solicitud_viaje>/', views.ResumenSolicitudGeneralActivosView.as_view(), name='resumen-solicitud-activos'),





]
