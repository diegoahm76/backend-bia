from django.urls import path
from transversal.views import alertas_views as views
urlpatterns = [
    #RECURSO_HIDRICO
    path("configuracion_clase_alerta/get-by-cod/<str:cod>/", views.ConfiguracionClaseAlertaGetByCod.as_view(), name="get-configuracion-alerta"),
    path("fecha_clase_alert/create/", views.FechaClaseAlertaCreate.as_view(), name="create-fecha-alerta"),
    path("fecha_clase_alert/get-by-configuracion/<str:cod>/", views.FechaClaseAlertaGetByConfiguracion.as_view(), name="get-fecha-by-configuracion"),
    path("fecha_clase_alert/delete/<str:cod>/", views.FechaClaseAlertaDelete.as_view(), name="delete-fecha-alerta"),
    #FIN RECURSO_HIDRICO
]