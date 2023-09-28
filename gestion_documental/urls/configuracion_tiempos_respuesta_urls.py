from django.urls import path
from gestion_documental.views import configuracion_tiempos_respuesta_views as views


urlpatterns = [#ConfiguracionTiemposRespuestaUpdate
    
    path('configuracion_tiempos_respuesta/get/', views.ConfiguracionTiemposRespuestaGet.as_view(), name='listar-configuraacion-get'),
    path('configuracion_tiempos_respuesta/update/<str:pk>/', views.ConfiguracionTiemposRespuestaUpdate.as_view(), name='actualizar-configuraacion-get'),
]
