from django.urls import path
from estaciones.views import datos_views as views

urlpatterns=[
    #Estaciones
    path('consultar-datos/',views.ConsultarDatos.as_view(),name='consultardatos'),
    path('consultar-datos-opt/',views.ConsultarDatosOptimizado.as_view(),name='consultardatosopt'),
    path('consultar-datos-id/<str:pk>/',views.ConsultarDatosId.as_view(),name='consultardatosid'),
    path('consultar-datos-fecha/<str:fecha_inicial>/<str:fecha_final>/', views.ConsultarDatosFecha.as_view(), name='consultar-datos-fecha'),
]