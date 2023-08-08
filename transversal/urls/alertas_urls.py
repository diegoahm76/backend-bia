from django.urls import path
from transversal.views import alertas_views as views
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
]