from django.urls import path
from recurso_hidrico.views import bibliotecas_views as views


urlpatterns = [

    path('get/secciones/',views.GetSecciones.as_view(),name='get-secciones'),
    path('get/seccion-por-id/<str:pk>/',views.GetSeccionSubseccion.as_view(),name='actualizar-subseccion'),
    path('get/subsecciones/por/seccion/<str:pk>/',views.GetSubseccionesPorSecciones.as_view(),name='get-subseccion'),
    path('subsecciones/actualizar/<str:pk>/',views.ActualizarSubsecciones.as_view(),name='actualizar-subseccion'),
    path('secciones/update/<str:pk>/',views.ActualizarSeccionSubseccion.as_view(),name='actualizar-seccion'),
    path('secciones/actualizar/<str:pk>/',views.ActualizarSecciones.as_view(),name='actualizar2-seccion'),
    path('secciones/create/',views.RegistroSeccion.as_view(),name='create-seccion'),
    path('subsecciones/create/',views.RegistroSubSeccion.as_view(),name='create-subseccion'),
    path('subsecciones/delete/<str:pk>/',views.EliminarSubseccion.as_view(),name='eliminar-subseccion'),
    path('secciones-subsecciones/create/',views.RegistroSeccionSubseccion.as_view(),name='create-seccion-subsecciones'),
    path('secciones/delete/<str:pk>/',views.EliminarSeccion.as_view(),name='eliminar-seccion'),
    #consultar biblioteca
    path('subsecciones/subsecciones-cont-instrumentos/<str:sec>/',views.SubseccionesContInstrumentosGet.as_view() ,name='get-subseccion-cont'),
    path('instrumentos/get-instrumentos-seccion-subseccion/<str:pk>/<str:sub>/',views.InstrumentosSeccionSubseccionGet.as_view() ,name='get-instrumenos'),
    path('instrumentos/get-instrumento-cuencas/<str:sec>/<str:sub>/',views.InstrumentoCuencasGet.as_view() ,name='get-instrumenos-cuencas'),
    path('instrumentos/get-instrumento-id/<str:pk>/',views.InstrumentosGetById.as_view() ,name='get-instrumenos-by-id'),
    path('cuencas/get-cuencas-instrumento/<str:ins>/',views.CuencasInstrumentoGet.as_view() ,name='get-cuenca-by-instrumento'),
    path('archivosInstrumento/get-busqueda-avanzada/',views.ArchivosInstrumentoBusquedaAvanzadaGet.as_view(),name='get-avanzada-archivos-instrumento'),
   
]