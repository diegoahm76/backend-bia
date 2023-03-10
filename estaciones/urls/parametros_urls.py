from django.urls import path
from estaciones.views import parametros_views as views

urlpatterns=[
    #PersonasEstaciones
    path('consultar-parametro/',views.ConsultarParametroEstacion.as_view(),name='consultar-parametro'),
    path('actualizar-parametro/<str:pk>/',views.ActualizarParametro.as_view(),name='actualizar-parametro'),
    path('consultar-parametro-id/<str:pk>/',views.ConsultarParametroEstacionId.as_view(),name='consultar-parametro-id'),
]