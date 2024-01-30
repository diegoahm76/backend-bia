from django.urls import path


from gestion_documental.views import consecutivo_unidad_views as views


urlpatterns = [
    
    path('config_tipo_consec_agno/get/<str:agno>/<str:uni>/', views.ConfigTipoConsecAgnoGetView.as_view(), name='listar-consecutivos'),
    path('config_tipo_consec_agno/create/', views.ConfigTipoConsecAgnoCreateView.as_view(), name='crear-consecutivos'),
    path('unidades_organigrama_actual/get/', views.UnidadesOrganigramaActualGet.as_view(), name='unidades-organigrama-actual'),
    path('config_tipo_consec_agno/update/<str:pk>/', views.ConfigTiposConsecutivoAgnoUpdate.as_view(), name='actualizar-consecutivos'),
    path('config_tipo_consec_agno/generar_numeracion/', views.ConfigTiposRadicadoAgnoGenerarN.as_view(), name='generar-numeracion'),
    path('serie_subserio_unidad/get/<str:uni>/', views.SerieSubserioUnidadGet.as_view(), name='serie-subserio-unidad'),
    path('consecutivo/create/', views.ConsecutivoCreateView.as_view(), name='crear-consecutivo'),
    path('consecutivo/get/', views.ConsecutivoGetView.as_view(), name='listar-consecutivo'),
]
