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
    #Instrumentos
    path('instrumentos/create/',views.InstrumentoCreate.as_view(),name='create-instrumentos'),
    path('instrumentos/update/<str:pk>/',views.InstrumentoUpdate.as_view(),name='update-instrumentos'),
    path('instrumentos/delete/<str:pk>/',views.InstrumentoDelete.as_view(),name='delete-instrumentos'),
    path('instrumentos/get-busqueda-avanzada/',views.InstrumentoBusquedaAvanzadaGet.as_view(),name='get-avanzada-instrumento'),
    #Archivos_Instrumento
    path('archivos_instrumento/create/',views.ArchivosInstrumentoCreate.as_view(),name='create-archivo'),
    path('archivos_instrumento/update/<str:pk>/',views.ArchivosInstrumentoUpdate.as_view(),name='update-archivo'),
    path('archivos_instrumento/get-by-instrumento/<str:pk>/',views.ArchivosInstrumentoGetByInstrumento.as_view(),name='get-archivo-by-instrumento'),
    path('archivos_instrumento/get-by-resultado_laboratorio/<str:lab>/',views.ArchivosInstrumentoGetByResultadosLaboratorio.as_view(),name='get-archivo-by-resultado-laboratorio'),
    path('archivos_instrumento/get-by-prueba_bombeo/<str:pru>/',views.ArchivosInstrumentoGetByPruebasBombeo.as_view(),name='get-archivo-by-pruebas-bombeo'),
    path('archivos_instrumento/get-by-cartera-aforo/<str:ca>/',views.ArchivosInstrumentoGetByCarteraAforos.as_view(),name='get-archivo-by-carteras-aforo'),
    #Cuencas_instrumentos
    path('cuencas_instrumento/get-by-instrumento/<str:pk>/',views.CuencasGetByInstrumento.as_view(),name='get-cuencas-by-instrumento'),
    path('cuencas_instrumento/delete/<str:cu>/<str:ins>/',views.CuencaInstrumentoDelete.as_view(),name='delete-cuencas-instrumento'),
    #Carteras_aforo
    path('carteras_aforo/create/',views.CarteraAforosCreate.as_view(),name='create-carteras_aforo'),
    path('carteras_aforo/update/<str:pk>/',views.CarteraAforosUpdate.as_view(),name='update-carteras-aforo'),
    path('carteras_aforo/get-by-instrumento/<str:pk>/',views.CarteraAforosGetByInstrumento.as_view(),name='get-carteras-aforo-by-instrumento'),
    path('cartera_aforos/delete/<str:pk>/',views.CarteraAforosDelete.as_view(),name='delete-cartera-aforo'),
    ##Datos_Cartera_afoto
    path('datos_cartera_aforos/create/',views.DatosCarteraAforosCreate.as_view(),name='create-dato_carteras_aforo'),
    path('datos_cartera_aforos/update/<str:pk>/',views.DatosCarteraAforosUpdate.as_view(),name='update-dato-carteras-aforo'),
    path('datos_cartera_aforos/delete/<str:pk>/',views.DatosCarteraAforosDelete.as_view(),name='delete-dato-cartera-aforo'),
    path('datos_cartera_aforos/get-by-cartera-aforos/<str:ca>/',views.DatosCarteraAforosGetByCarteraAforos.as_view(),name='get-dato-carteras_aforo-by-carteras_aforo'),
    #Resultados de laboratorio
    path('resultados_laboratorio/create/',views.ResultadosLaboratorioCreate.as_view(),name='create-resultado_laboratorio'),
    path('resultados_laboratorio/get-by-instrumento/<str:pk>/',views.ResultadosLaboratorioGetByInstrumento.as_view(),name='get-resultados-by-instrumento'),
    path('resultados_laboratorio/get-by-id/<str:pk>/',views.ResultadosLaboratorioGetById.as_view(),name='get-resultados-by-id'),
    path('resultados_laboratorio/update/<str:pk>/',views.ResultadosLaboratorioUpdate.as_view(),name='update-resultados-laboratorio'),
    path('resultados_laboratorio/delete/<str:pk>/',views.ResultadosLaboratorioDelete.as_view(),name='delete-resultados-laboratorio'),
    #dato_registro_laboratorio
    path('dato_registro_laboratorio/create/',views.DatosRegistroLaboratorioCreate.as_view(),name='create-dato_registro_laboratorio'),
    path('dato_registro_laboratorio/delete/<str:pk>/',views.DatosRegistroLaboratorioDelete.as_view(),name='delete-dato_registro_laboratorio'),
    path('dato_registro_laboratorio/update/<str:pk>/',views.DatosRegistroLaboratorioUpdate.as_view(),name='update-dato_registro_laboratorio'),
    path('dato_registro_laboratorio/get-by-resultado/<str:lab>/<str:para>/',views.DatosRegistroLaboratorioByResultadosLaboratorioGet.as_view(),name='get_dato_registro_laboratorio_by_resultado'),
    path('dato_registro_laboratorio/get-by-id/<str:pk>/',views.DatosRegistroLaboratorioByIdGet.as_view(),name='get-dato_registro_laboratorio_by_id'),
    #pruebas_bombeo
    path('pruebas_bombeo/create/',views.PruebasBombeoCreate.as_view(),name='create_pruebas_bombeo'),
    path('pruebas_bombeo/delete/<str:pk>/',views.PruebaBombeoDelete.as_view(),name='delete_pruebas_bombeo'),
    path('pruebas_bombeo/update/<str:pk>/',views.PruebaBombeoUpdate.as_view(),name='update_pruebas_bombeo'),
    path('pruebas_bombeo/get-by-instrumento/<str:pk>/',views.PruebasBombeoGetByInstrumento.as_view(),name='get-pruebas-bombeo-by-instrumento'),
    path('pruebas_bombeo/get-by-id/<str:pk>/',views.PruebasBombeoGetById.as_view(),name='get-pruebas-bombeo-by-id'),
    #seccion_prueba_bombeo
    path('sesiones_prueba_bombeo/create/',views.SesionesPruebaBombeoCreate.as_view(),name='create_sesiones_prueba_bombeo'),
    path('sesiones_prueba_bombeo/update/<str:pk>/',views.SesionesPruebaBombeoUpdate.as_view(),name='update_sesiones_prueba_bombeo'),
    path('sesiones_prueba_bombeo/delete/<str:pk>/',views.SesionesPruebaBombeoDelete.as_view(),name='delete_sesiones_prueba_bombeo'),
    path('sesiones_prueba_bombeo/get-by-prueba-bombeo/<str:pru>/',views.SesionesPruebaBombeoGetByPrueba.as_view(),name='get_sesiones_prueba_bombeo_by_prueba'),
    path('sesiones_prueba_bombeo/get-by-id/<str:pk>/',views.SesionesPruebaBombeoGetById.as_view(),name='get_sesiones_prueba_bombeo_by_id'),
    #datos_seccion_prueba_bombeo
    path('datos_sesiones_prueba_bombeo/create/',views.DatosSeccionPruebasBombeoCreate.as_view(),name='create_datos_sesiones_prueba_bombeo'),
    path('datos_sesiones_prueba_bombeo/update/<str:pk>/',views.DatosSeccionPruebasBombeoUpdate.as_view(),name='update_datos_sesiones_prueba_bombeo'),
    path('datos_sesiones_prueba_bombeo/delete/<str:pk>/',views.DatosSesionPruebaBombeoDelete.as_view(),name='delete_datos_sesiones_prueba_bombeo'),
    path('datos_sesiones_prueba_bombeo/get-by-id/<str:pk>/',views.DatosSesionPruebaBombeoGetById.as_view(),name='get-dato-sesion-pruebas-bombeo-by-id'),
    path('datos_sesiones_prueba_bombeo/get-by-sesion/<str:pk>/',views.DatosSesionPruebaBombeoGetBySesion.as_view(),name='get-dato-sesion-pruebas-bombeo-by-sesion'),


    #Acciones Correctivas
    path('acciones_correctivas/get-by-id-tramite/<str:pk>/',views.AccionesCorrectivasListByIdTramite.as_view(),name='list_acciones_correctivas'),
    path('acciones_correctivas/create/',views.AccionesCorrectivasCreate.as_view(),name='create_acciones_correctivas'),
    path('acciones_correctivas/update/<str:pk>/',views.AccionesCorrectivasUpdate.as_view(),name='update_acciones_correctivas'),
    path('busqueda_tramites/',views.BusquedaTramitesByExpediente.as_view(),name='busqueda_tramites'),
    path('tipo_acciones/get/',views.TiposAccionesCorrectivasList.as_view(),name='get-tipo-acciones'),
    path('tipo_acciones/create/',views.TiposAccionesCorrectivasCreate.as_view(),name='create_tipo_acciones'),
    path('tipo_acciones/update/<str:pk>/',views.TiposAccionesCorrectivasUpdate.as_view(),name='update_tipo_acciones'),
    path('acciones_correctivas/delete/<str:pk>/',views.TiposAccionesCorrectivasDelete.as_view(),name='delete_acciones_correctivas'),

]   
