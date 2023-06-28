from django.urls import path
from recurso_hidrico.views import bibliotecas_views as views

urlpatterns = [

    path('get/secciones/',views.GetSecciones.as_view(),name='get-secciones'),
    path('get/seccion-por-id/<str:pk>/',views.GetSeccionSubseccion.as_view(),name='actualizar-subseccion'),
    path('get/subsecciones/por/seccion/<str:pk>/',views.GetSubseccionesPorSecciones.as_view(),name='get-subseccion'),
    path('subsecciones/actualizar/<str:pk>/',views.ActualizarSubsecciones.as_view(),name='actualizar-subseccion'),
    path('secciones/update/<str:pk>/',views.ActualizarSeccion.as_view(),name='actualizar-seccion'),
    path('secciones/create/',views.RegistroSeccion.as_view(),name='create-seccion'),
    path('subsecciones/create/',views.RegistroSubSeccion.as_view(),name='create-subseccion'),
    path('secciones-subsecciones/create/',views.RegistroSeccionSubseccion.as_view(),name='create-seccion-subsecciones'),
    path('secciones/delete/<str:pk>/',views.EliminarSeccion.as_view(),name='eliminar-seccion'),
    path('get/subsecciones-cont-instrumentos/<str:pk>/',views.GetSubseccionesContInstrumentos.as_view() ,name='get-subseccion-cont'),
    path('get/instrumentos-por-seccion-subseccion/<str:pk>/<str:sub>/',views.GetInstrumentosPorSeccionSubseccion.as_view() ,name='get-instrumenos'),
   
]