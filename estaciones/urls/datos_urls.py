from django.urls import path
from estaciones.views import datos_views as views

urlpatterns=[
    #Estaciones
    path('consultar-datos/',views.ConsultarDatos.as_view(),name='consultardatos'),
    path('consultar-datos-opt/',views.ConsultarDatosOptimizado.as_view(),name='consultardatosopt'),
    path('consultar-datos-id/<str:pk>/',views.ConsultarDatosId.as_view(),name='consultardatosid'),
    path('consultar-datos-fecha/<str:fecha_inicial>/<str:fecha_final>/', views.ConsultarDatosFecha.as_view(), name='consultar-datos-fecha'),
    path('consultar-datos-reporte/<str:fecha_inicial>/', views.ConsultarDatosReportes.as_view(), name='consultar-datos-reporte'),

    #rutas vistas estaciones
    path('consultar-datos-guamal/', views.ConsultarDatosGuamal.as_view(), name='consultar-datos-guamal'),
    path('consultar-datos-ocoa/', views.ConsultarDatosOcoa.as_view(), name='consultar-datos-ocoa'),
    path('consultar-datos-guayuriba/', views.ConsultarDatosGuayuriba.as_view(), name='consultar-datos-guayuriba'),
    path('consultar-datos-gaitan/', views.ConsultarDatosGaitan.as_view(), name='consultar-datos-gaitan'),

     #rutas vistas estaciones paginadas
    path('consultar-pagina-guamal/', views.ConsultarDatosGuamalPage.as_view(), name='consultar-pagina-guamal'),
    path('consultar-pagina-ocoa/', views.ConsultarDatosOcoaPage.as_view(), name='consultar-pagina-ocoa'),
    path('consultar-pagina-guayuriba/', views.ConsultarDatosGuayuribaPage.as_view(), name='consultar-pagina-guayuriba'),
    path('consultar-pagina-gaitan/', views.ConsultarDatosGaitanPage.as_view(), name='consultar-pagina-gaitan'),
]