from django.urls import path
from recaudo.views import liquidaciones_views as views

urlpatterns = [
    path('opciones-liquidacion-base/', views.OpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-todos'),
    path('clonar-opcion-liquidacion-base/<int:pk>/', views.ClonarOpcionLiquidacionView.as_view(), name='clonar-opciones-liquidacion-base'),
    path('opciones-liquidacion-base/<int:pk>/', views.DetalleOpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-detalles'),
    path('eliminar-opciones-liquidacion-base/<int:pk>/', views.EliminarOpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-eliminar'),

    path('deudores/', views.DeudoresView.as_view(), name='deudores-todos'),
    path('deudores/<str:identificacion>', views.DeudoresIdentificacionView.as_view(), name='deudores-busqueda-identificacion'),

    path('liquidacion-masivo/', views.LiquidacionesBasePostMasivovista.as_view(), name='liquidacion-base-todoffs'),

    path('liquidacion-base/', views.LiquidacionBaseView.as_view(), name='liquidacion-base-todos'),
    path('liquidacion-base/<int:pk>/', views.ObtenerLiquidacionBaseView.as_view(), name='liquidacion-base-detalle'),
    path('liquidacion-base-por-expediente/<int:pk>/', views.ObtenerLiquidacionPorIdExpedienteBaseView.as_view(), name='liquidacion-base-detalle-por-expediente'),
    path('liquidacion-pdf/<int:pk>/', views.liquidacionPdf, name='descargar-liquidacion-pdf'),

    path('detalles-liquidacion-base/', views.DetallesLiquidacionBaseView.as_view(), name='liquidacion-base-agregar'),
    path('detalles-liquidacion-base/<int:liquidacion>/', views.DetallesLiquidacionBaseView.as_view(), name='liquidacion-base-detalles'),

    path('liquidacion-tramite/', views.LiquidacionTramiteCreateView.as_view(), name='liquidacion-tramite-create'),
    path('liquidacion-tramite/get/<str:id_liquidacion_base>/', views.LiquidacionTramiteGetView.as_view(), name='liquidacion-tramite-create'),
    path('liquidacion-tramite/anular/<str:id_liquidacion_base>/', views.LiquidacionesTramiteAnularView.as_view(), name='liquidacion-tramite-anular'),
    path('historico/liquidacion-tramite/get/', views.HistLiquidacionTramiteGetView.as_view(), name='hist-liquidacion-tramite-get'),

    path('expedientes/', views.ExpedientesView.as_view(), name='expedientes-todos'),
    path('expedientes/<int:pk>/', views.ExpedienteEspecificoView.as_view(), name='obtener-expediente'),
    path('expedientes-deudor/get/<int:id_deudor>/', views.ExpedientesDeudorGetView.as_view(), name='expedientes-deudor'),

    path('calculos/', views.CalculosLiquidacionBaseView.as_view(), name='calculos-liquidacion'),




    path('liquidacion-pdf_miguel/<int:pk>/', views.liquidacionPdfpruebaMigueluno.as_view(), name='descargar-liquidacion-pdjhf'),
    path('liquidacion_update_caudlk/<int:pk>/', views.LiquidacionPdfpruebaMiguelUpdate.as_view(), name='_update_cauda'),


    
]
