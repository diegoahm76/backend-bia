from django.urls import path
from almacen.views import choices_views as views

urlpatterns = [
    # Choices
    path('estados-articulo/', views.EstadosArticuloChoices.as_view(), name='estados-articulo'),
    path('magnitudes/', views.MagnitudesChoices.as_view(), name='magnitudes'),
    path('tipo-documento/', views.TipoDocumentoChoices.as_view(), name='tipo-documento'),
    path('tipo-combustible/', views.TipoCombustibleChoices.as_view(), name='tipo-combustible'),
    path('tipo-mantenimiento/', views.TipoMantenimientoChoices.as_view(), name='tipo-mantenimiento'),
    path('tipo-vehiculo/', views.TipoVehiculoChoices.as_view(), name='tipo-vehiculo'),
    path('tipo-bien/', views.TipoBienChoices.as_view(), name='tipo-bien'),
    path('tipo-doc-ultimo/', views.TipoDocUltimoChoices.as_view(), name='tipo-doc-ultimo'),
    path('metodo-valoracion-articulo/', views.MetodoValoracionChoices.as_view(), name='metodo-valoracion-articulo'),
    path('tipo-activo/', views.TipoActivoChoices.as_view(), name='tipo-activo'),
    path('tipo-depreciacion-activo/', views.TipoDepreciacionActivos.as_view(), name='tipo-depreciacion-activos'),
    path('estado-aprobacion/', views.EstadoAprobacionChoices.as_view(), name='estado-aprobacion'),
    path('tipo-elemento/', views.CodTipoElementoViveroChoices.as_view(), name='tipo-elemento'),
    path('estado-solicitud/', views.EstadoSolicitudChoices.as_view(), name='estado-solicitud'),
    path('tipo-conductor/', views.TipoConductorChoices.as_view(), name='tipo-conductor'),
    path('estado-aprobacion-activo/', views.EstadoAprobacionActivo.as_view(), name='estado-aprobacion-activo'),
    path('estado-solicitud-activo/', views.EstadoSolicitudActivo.as_view(), name='estado-solicitud-activo'),
    path('estado-despacho-activo/', views.EstadoDespacho.as_view(), name='estado-despacho-activo'),

    
]