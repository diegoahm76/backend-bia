from django.urls import path
from gestion_documental.views import conf__tipos_exp_views as views


urlpatterns = [#ConfiguracionTiemposRespuestaUpdate
    
    path('seccion-subseccion/get/', views.ConfiguracionTipoExpedienteAgnoGet.as_view(), name='listar-configuraacion-get'),
    path('serie-subserie-unidad/get/<str:uni>/',views.SerieSubserioUnidadGet.as_view(),name='listar-serie-subserie'),
    path('configuracion-tipo-expediente-agno/create/',views.ConfiguracionTipoExpedienteAgnoCreate.as_view(),name='crear-configuracion-tipo-expediente-agno'),
    path('configuracion-tipo-expediente-agno/update/<str:pk>/',views.ConfiguracionTipoExpedienteAgnoUpdate.as_view(),name='actualizar-configuracion-tipo-expediente-agno'),
    path('configuracion-tipo-expediente-agno/get-serie-unidad/<str:uni>/<str:agno>/',views.ConfiguracionTipoExpedienteAgnoGetbyCatalogoUnidad.as_view(),name='listar-configuracion-tipo-expediente-agno'),
    path('configuracion-tipo-expediente-agno/get-serie-unidad/historico/<str:uni>/<str:agno>/',views.ConfiguracionTipoExpedienteAgnoGetHistorico.as_view(),name='listar-configuracion-tipo-expediente-agno-historico'),
    path('generar_n_radicado/update/<str:pk>/',views.ConfiguracionTipoExpedienteAgnoGetConsect.as_view(),name='generar-radicado-tipo-expediente-agno'),

    #ConfiguracionTipoExpedienteAgnoGetHistorico
]
