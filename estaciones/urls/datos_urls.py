from django.urls import path
from estaciones.views import datos_views as views

urlpatterns=[
    #Estaciones
    path('consultar-datos/',views.ConsultarDatos.as_view(),name='consultardatos'),
    path('consultar-datos-id/',views.ConsultarDatosId.as_view(),name='consultardatosid'),
]