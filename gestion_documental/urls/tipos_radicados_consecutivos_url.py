from django.urls import path
from gestion_documental.views import   configuracion_tipos_radicados_views as views


urlpatterns = [
    path('config_tipos_radicado_agno/update/<str:pk>/', views.ConfigTiposRadicadoAgnoUpdate.as_view(), name='configurar-tipos-radicados-update'),
    path('config_tipos_radicado_agno/create/', views.ConfigTiposRadicadoAgnoCreate.as_view(), name='configurar-tipos-radicados-update'),
    path('config_tipos_radicado_agno/get/<str:agno>/<str:tipo>/', views.ConfigTiposRadicadoAgnoGet.as_view(), name='configurar-tipos-radicados-update'),
    path('config_tipos_radicado_agno/generar_n/', views.ConfigTiposRadicadoAgnoGenerarN.as_view(), name='configurar-tipos-radicados-generar-radicado'),
    path('crear-radicado/', views.RadicadoCreate.as_view(), name='crear-radicado'),
    

]