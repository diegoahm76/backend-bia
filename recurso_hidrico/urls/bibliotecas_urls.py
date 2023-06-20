from django.urls import path
from recurso_hidrico.views import bibliotecas_views as views

urlpatterns = [

    path('get/secciones/',views.GetSecciones.as_view(),name='get-secciones'),

    path('get/subsecciones/por/seccion/<str:pk>/',views.GetSubseccionesPorSecciones.as_view(),name='get-subseccion'),
    path('subsecciones/actualizar/<str:pk>/',views.ActualizarSubsecciones.as_view(),name='actualizar-subseccion'),
    path('secciones/create/',views.RegistroSeccion.as_view(),name='create-seccion'),
]