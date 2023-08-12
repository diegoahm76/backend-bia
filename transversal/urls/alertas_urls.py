from django.urls import path
from transversal.views import alertas_views as views
from transversal.views  import bandeja_alertas_views  as bandejas_views
urlpatterns = [
    #RECURSO_HIDRICO
    path("configuracion_clase_alerta/get-by-cod/<str:cod>/", views.ConfiguracionClaseAlertaGetByCod.as_view(), name="get-configuracion-alerta-by-id"),
    path("configuracion_clase_alerta/get-by-cod/", views.ConfiguracionClaseAlertaGet.as_view(), name="get-configuracion-alerta"),

    path('configuracion_clase_alerta/update/<str:pk>/', views.ConfiguracionClaseAlertaUpdate.as_view(), name='configuracion_clase_alerta_update'),
    #Fecha alerta
    path("fecha_clase_alert/create/", views.FechaClaseAlertaCreate.as_view(), name="create-fecha-alerta"),
    path("fecha_clase_alert/get-by-configuracion/<str:cod>/", views.FechaClaseAlertaGetByConfiguracion.as_view(), name="get-fecha-by-configuracion"),
    path("fecha_clase_alert/delete/<str:cod>/", views.FechaClaseAlertaDelete.as_view(), name="delete-fecha-alerta"),
    #persona alerta
    path("personas_alertar/create/", views.PersonasAAlertarCreate.as_view(), name="create-persona-alerta"),
    path("personas_alertar/delete/<str:pk>/", views.PersonasAAlertarDelete.as_view(), name="delete-personas-alertar"),
    path("personas_alertar/get-by-configuracion/<str:cod>/", views.PersonasAAlertarGetByConfAlerta.as_view(), name="create-persona-alerta"),
    #ALERTAS PROGRAMADAS
    path("alertas_programadas/create/", views.AlertasProgramadasCreate.as_view(), name="create-alertas-programadas"),
    path("alertas_programadas/update/<str:pk>/", views.AlertasProgramadasUpdate.as_view(), name="update-alertas-programadas"),
    path('proyectosporh/get-proyectos-vigentes-alerta/',views.AlertaProyectosVigentesGet.as_view(),name='get-proyectos-vigentes'),
    #FIN RECURSO_HIDRICO
    #BANDEJA DE ALERTAS
    path('bandeja_alerta_persona/get-bandeja-by-persona/<str:pk>/',bandejas_views.BandejaAlertaPersonaGetByPersona.as_view(),name='get-bandeja-persona'),
    path('alertas_bandeja_Alerta_persona/get-alerta_bandeja-by-bandeja/<str:pk>/',bandejas_views.AlertasBandejaAlertaPersonaGetByBandeja.as_view(),name='get-bandeja-persona'),
    path('ejecutar-tarea/', views.mi_vista, name='ejecutar_tarea'),
    path('alertas_bandeja_Alerta_persona/get-alerta_bandeja-by-bandeja/<str:pk>/',bandejas_views.AlertasBandejaAlertaPersonaGetByBandeja.as_view(),name='get-items_bandeja-persona'),
    path('alertas_bandeja_Alerta_persona/update/<str:pk>/', bandejas_views.AlertasBandejaAlertaPersonaUpdate.as_view(), name='actualizar_item_bandeja_persona'),


]