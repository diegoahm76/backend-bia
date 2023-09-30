from django.urls import path
from gestion_documental.views import conf__tipos_exp_views as views


urlpatterns = [#ConfiguracionTiemposRespuestaUpdate
    
    path('seccion-subseccion/get/', views.ConfiguracionTipoExpedienteAgnoGet.as_view(), name='listar-configuraacion-get'),
    path('serie-subserie-unidad/get/<str:uni>/',views.SerieSubserioUnidadGet.as_view(),name='listar-serie-subserie'),

    #
]
