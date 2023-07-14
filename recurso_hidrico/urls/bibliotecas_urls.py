from django.urls import path
from recurso_hidrico.views import bibliotecas_views as views


urlpatterns = [

    path('get/secciones/',views.GetSecciones.as_view(),name='get-secciones'),
    path('get/seccion-por-id/<str:pk>/',views.GetSeccionSubseccion.as_view(),name='update-subseccion'),
    path('get/subsecciones/por/seccion/<str:pk>/',views.GetSubseccionesPorSecciones.as_view(),name='get-subseccion'),
    path('subsecciones/actualizar/<str:pk>/',views.ActualizarSubsecciones.as_view(),name='update-subseccion'),
    path('secciones/update/<str:pk>/',views.ActualizarSeccionSubseccion.as_view(),name='update-seccion'),
    path('secciones/actualizar/<str:pk>/',views.ActualizarSecciones.as_view(),name='update-seccion'),
    path('secciones/create/',views.RegistroSeccion.as_view(),name='create-seccion'),
    path('subsecciones/create/',views.RegistroSubSeccion.as_view(),name='create-subseccion'),
    path('subsecciones/delete/<str:pk>/',views.EliminarSubseccion.as_view(),name='delete-subseccion'),
    path('secciones-subsecciones/create/',views.RegistroSeccionSubseccion.as_view(),name='create-seccion-subsecciones'),
    path('secciones/delete/<str:pk>/',views.EliminarSeccion.as_view(),name='delete-seccion'),
    #consultar biblioteca
    path('subsecciones/subsecciones-cont-instrumentos/<str:sec>/',views.SubseccionesContInstrumentosGet.as_view() ,name='get-subseccion-cont'),
    path('instrumentos/get-instrumentos-seccion-subseccion/<str:pk>/<str:sub>/',views.InstrumentosSeccionSubseccionGet.as_view() ,name='get-instrumenos'),
    path('instrumentos/get-instrumento-cuencas/<str:sec>/<str:sub>/',views.InstrumentoCuencasGet.as_view() ,name='get-instrumenos-cuencas'),
    path('instrumentos/get-instrumento-id/<str:pk>/',views.InstrumentosGetById.as_view() ,name='get-instrumenos-by-id'),
    path('cuencas/get-cuencas-instrumento/<str:ins>/',views.CuencasInstrumentoGet.as_view() ,name='get-cuenca-by-instrumento'),
    path('archivosInstrumento/get-busqueda-avanzada/',views.ArchivosInstrumentoBusquedaAvanzadaGet.as_view(),name='get-avanzada-archivos-instrumento'),
    path('ArchivosInstrumento/get-ArchivosInstrumento-instrumento/<str:ins>/',views.ArchivosInstrumentoGet.as_view() ,name='get-archivosInstrumento-by-instrumento'),

    #Configuraciones basicas
    #cuencas
    path('cuencas/create/',views.CuencaCreate.as_view(),name='create-cuencas'),
    path('cuencas/delete/<str:pk>/',views.CuencaDelete.as_view(),name='delete-cuencas'),
    path('cuencas/get/',views.CeuncaGet.as_view(),name='get-cuencas'),
    path('cuencas/get-id/<str:pk>/',views.CuencaGetById.as_view(),name='get-cuencas-id'),
    path('cuencas/update/<str:pk>/',views.CuencaUpdate.as_view(),name='update-cuencas'),
    #pozos
    path('pozos/create/',views.PozoCreate.as_view(),name='create-pozos'),
    path('pozos/delete/<str:pk>/',views.PozoDelete.as_view(),name='delete-cuencas'),
    path('pozos/update/<str:pk>/',views.PozoUpdate.as_view(),name='update-pozos'),
    path('pozos/get/',views.PozoGet.as_view(),name='get-cuencas'),
    path('pozos/get-id/<str:pk>/',views.PozoGetById.as_view(),name='get-pozos-id'),
    #Parametro de laboratorio
    path('parametros_laboratorio/create/',views.ParametrosLaboratorioCreate.as_view(),name='create-parametros-laboratorio'),
    path('parametros_laboratorio/delete/<str:pk>/',views.ParametrosLaboratorioDelete.as_view(),name='delete-cuencas'),
    path('parametros_laboratorio/update/<str:pk>/',views.ParametrosLaboratorioUpdate.as_view(),name='update-parametros-laboratorio'),
    path('parametros_laboratorio/get/',views.ParametrosLaboratorioGet.as_view(),name='get-parametros_laboratorio'),
    path('parametros_laboratorio/get-id/<str:pk>/',views.ParametrosLaboratorioGetById.as_view(),name='get-parametros_laboratorio-id'),
    #Registro de Instrumentos en Biblioteca
    path('subsecciones/get-busqueda-avanzada/',views.SeccionSubseccionBusquedaAvanzadaGet.as_view(),name='get-avanzada-subsecciones'),

    path('instrumentos/create/',views.InstrumentoCreate.as_view(),name='create-instrumentos'),
    path('instrumentos/update/<str:pk>/',views.InstrumentoUpdate.as_view(),name='update-instrumentos'),
    
    path('archivos_instrumento/create/',views.ArchivosInstrumentoCreate.as_view(),name='create-archivo'),
    path('archivos_instrumento/get-by-instrumento/<str:pk>/',views.ArchivosInstrumentoGetByInstrumento.as_view(),name='get-archivo-by-instrumento'),
    path('cuencas_instrumento/get-by-instrumento/<str:pk>/',views.CuencasGetByInstrumento.as_view(),name='get-cuencas-by-instrumento'),
     path('cuencas_instrumento/delete/<str:cu>/<str:ins>/',views.CuencaInstrumentoDelete.as_view(),name='delete-cuencas-instrumento'),
]   