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
    path('crear-anexo-opcional/create/<int:id_baja_activo>/',views.CrearArchivosOpcionales.as_view(),name='crear-archivos-opcionales'),
    path('actualizar-anexo-opcional/update/<int:id_baja_activo>/',views.ActualizarAnexoOpcional.as_view(),name='actualizar-archivos-opcionales'),
    path('eliminar-anexo-opcional/delete/<int:id_baja_activo>/',views.EliminarAnexoOpcional.as_view(),name='actualizar-archivos-opcionales'),
    path('listar-anexo-opcional/get/<int:id_baja_activo>/',views.ListarAnexoOpcional.as_view(),name='actualizar-archivos-opcionales'),


    #Solicitud_Bajas_Activos
    path('crear-solicitud-baja-activos/create/',views.CrearSolicitudActivosView.as_view(),name='crear-solicitud-baja-activo'),
    path('editar-solicitud-activos/<int:pk>/', views.EditarSolicitudActivosView.as_view(), name='editar-solicitud-activos'),
    path('listar-unidades-medida/get/',views.ListarUnidadesMedidaActivas.as_view(),name='listar-unidades-medida'),
    path('detalle-solicitud-activos/<int:id_solicitud_activo>/', views.DetalleSolicitudActivosView.as_view(), name='detalle-solicitud-activos'),
    path('resumen-solicitud-activos/<int:id_solicitud_activo>/', views.ResumenSolicitudGeneralActivosView.as_view(), name='resumen-solicitud-activos'),
    path('cancelar-solicitud-activos/<int:id_solicitud_activo>/', views.CancelarSolicitudActivos.as_view(), name='cancelar-solicitud-activos'),
    path('busqueda-solicitudes-realizadas/get/', views.BusquedaAvanzadaSolicitudesActivos.as_view(), name='busqueda-solicitud-activos'),


    #Autorizacion_Solicitud_Activos
    path('busqueda-solicitudes-proceso/get/', views.BusquedaAvanzadaSolicitudesProcesos.as_view(), name='busqueda-solicitud-procesos'),
    path('rechazar-solicitud-activo/put/<int:pk>/', views.RechazarSolicitud.as_view(), name='rechazar-solicitud-activo'),
    path('aprobar-solicitud-activo/put/<int:pk>/', views.AprobarSolicitud.as_view(), name='aprobar-solicitud-activo'),

    #Salida_Activos_Especiales
    path('busqueda-terceros-activos/get/', views.ClasesTerceroPersonaSearchView.as_view(), name='busqueda-terceros-activos'),
    path('entradas-relacionadas-activos/get/<int:id_persona>/', views.EntradasRelacionadasAlmacenListView.as_view(), name='entradas-relacionadas-activos'),
    path('activos-asociados/get/<int:id_entrada_almacen>/', views.ActivosAsociadosDetailView.as_view(), name='activos_asociados_detalles'),
    path('crear-salida-especial-activo/', views.CrearSalidaEspecialView.as_view(), name='activos_salida_especial_create'),
    path('info-salida-especial-activo/get/<int:consecutivo>/', views.ObtenerDatosSalidaEspecialView.as_view(), name='salida-especial-activo'),
    path('obtener-ultimo-consecutivo-salida-especial/get/', views.ObtenerUltimoConsecutivoView.as_view(), name='ultimo-consecutivo-salida-especial'),


    #Devolucion_Activos
    path('Informacion-almacenista/get/', views.InfoAlmcenistaPersonaGet.as_view(), name='info-alamcenista'),
    path('despachos-activos/get/<int:id_persona>/', views.DespachosDeActivosList.as_view(), name='despachos-activos'),
    path('despachos-activos/detalle/<int:id_despacho>/', views.ActivosDespachadosDevolucionView.as_view(), name='activos-despachados-devolucion'),
    path('info-estados-articulo/get/', views.EstadosArticuloListView.as_view(), name='info-estados-articulo'),
    path('devolucion-activos/create/', views.DevolucionActivosCreateView.as_view(), name='devolucion-activos-creacion'),

    #Despacho_Activos
    path('busqueda-solicitudes-despacho/get/', views.BusquedaAvanzadaSolicitudesDespacho.as_view(), name='busqueda-solicitud-despacho'),
    path('cancelar-solicitud-despacho/<int:pk>/', views.CancelarSolicitudDespacho.as_view(), name='cancelar-solicitud-despacho'),
    path('anular-solicitud-despacho/<int:pk>/', views.AnularSolicitudDespacho.as_view(), name='anular-solicitud-despacho'),
    path('solicitudes-activos/<int:id_solicitud_activo>/', views.ObtenerDatosPersonasSolicitud.as_view(), name='detalle-solicitud-activos'),
    path('bodegas/busqueda-avanzada/', views.BusquedaAvanzadaBodegas.as_view(), name='busqueda_avanzada_bodegas'),
    path('despachos-sin-solicitud/get/', views.DespachosSinSolicitudGet.as_view(), name='despachos-sin-solicitud'),
    path('busqueda-articulos-principal/<int:solicitud_id>/', views.BusquedaArticulosPrincipalView.as_view(), name='busqueda-articulos-princiapal'),
    path('busqueda-articulos-sub/<int:id_bien>/', views.BusquedaArticulosSubView.as_view(), name='busqueda-articulos-sub'),
    path('crear-despacho-activo/create/', views.CrearDespachoActivosView.as_view(), name='crear-despacho-activo'),












]
