from django.urls import path

from gestion_documental.views import encuentas_views as views

urlpatterns = [
    path('encabezado_encuesta/create/',views.EncabezadoEncuestaCreate.as_view(), name='crear-encabezado'),
    path('encabezado_encuesta/get/',views.EncabezadoEncuestaGet.as_view(), name='get-encabezado'),
    path('encabezado_encuesta/get/detalle/<str:pk>/',views.EncabezadoEncuestaDetalleGet.as_view(), name='get-encabezado-detalle'),
    path('encabezado_encuesta/update/<str:pk>/', views.EncabezadoEncuestaUpdate.as_view(), name='actualizar_encabezado_encuesta'),
    path('encabezado_encuesta/delete/<str:pk>/',views.EncabezadoEncuestaDelete.as_view(), name='delete-encabezado'),
    path('preguntas_encuesta/create/',views.PreguntasEncuestaCreate.as_view(), name='crear-pregunta'),
    path('preguntas_encuesta/update/<str:pk>/',views.PreguntasEncuestaUpdate.as_view(), name='actualizar-pregunta'),
    path('preguntas_encuesta/delete/<str:pk>/',views.PreguntasEncuestaDelete.as_view(), name='eliminar-pregunta'),
    path('opciones_rta/create/',views.OpcionesRtaCreate.as_view(), name='crear-opcion-respuesta'),
    path('opciones_rta/update/<str:pk>/',views.OpcionesRtaUpdate.as_view(), name='actualizar-opcion-respuesta'),
    path('opciones_rta/delete/<str:pk>/',views.OpcionesRtaDelete.as_view(), name='eliminar-opcion'),
    #EncuentasContestados
    path('datos_encuestas_resueltas/create/',views.DatosEncuestasResueltasCreate.as_view(), name='crear-datos-encuentas'),
    path('usuario_registrado/get/',views.UsuarioRegistradoGet.as_view(), name='traer usuario registrado'),
    #INFORMES
    path('encuesta_realizadas/get/',views.EncuestasRealizadasGet.as_view(), name='get-encabezado'),
    path('conteo_encuesta/get/<str:pk>/',views.ConteoEncuestasGet.as_view(), name='get-respuestas-conteo'),
    path('reporte_region/get/<str:pk>/',views.ConteoEncuestasRegionesGet.as_view(), name='get-reporte_region'),
    path('reporte_tipos_usuario/get/<str:pk>/',views.ConteoEncuestasTiposUsuarioGet.as_view(), name='get-reporte_n_usuarios'),
    path('reporte_tipos_sexo/get/<str:pk>/',views.ConteoEncuestasPorGenero.as_view(), name='get-reporte_genero_usuarios'),
    path('reporte_rango_edad/get/<str:pk>/',views.ConteoEncuestasPorRangoEdad.as_view(), name='get-reporte_edad'),

    path('encuesta_disponibles/get/',views.EncuestasDisponbles.as_view(), name='listar-encuesta-disponibles'),
    path('asignacion_encuesta/get/<str:enc>/',views.EncuestasAsignadasGet.as_view(), name='listado-asignacion-encuesta'),
    path('asignacion_encuesta/create/',views.AsignacionEncuestaCreate.as_view(), name='crear-asignacion-encuesta'),
    path('asignacion_encuesta_usuario/get/<str:pk>/',views.EncuestasAsignadasUsuarioGet.as_view(), name='listado-usuarios-encuesta'),
    path('asignacion_encuesta/delete/<str:pk>/',views.DeleteAsignacion.as_view(), name='eliminar-asignacion-encuesta-usuario'),
]#EncuestasAsignadasUsuarioGet