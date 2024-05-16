from django.urls import path
from gestion_documental.views import notificaciones_views as views

urlpatterns = [
    # Notificaciones
    path('get-notificaciones/', views.ListaNotificacionesCorrespondencia.as_view(),name='get-notificaiones'),
    path('get-notificaciones-tareas/', views.NotificacionesCorrespondenciaYTareasGet.as_view(),name='get-notificaiones-tareas'),
    path('get-asignaciones/', views.GetAsignacionesCorrespondencia.as_view(),name='get-asignaciones'),
    path('create-asignacion/', views.CrearAsignacionNotificacion.as_view(),name='create-asignacion'),
    path('create-asignacion-tarea/', views.CrearAsignacionTarea.as_view(),name='create-asignacion-tarea'),
    path('update-asignacion/<int:pk>/', views.UpdateAsignacionNotificacion.as_view(),name='update-asignacion'),
    path('update-asignacion-tarea/<int:pk>/', views.UpdateAsignacionTarea.as_view(),name='update-asignacion-tarea'),
    path('rechazo-notificacion/<int:pk>/', views.RechazoNotificacionCorrespondencia.as_view(),name='rechazo-notificacion'),
    path('create-notificacion-manual/', views.CrearNotiicacionManual.as_view(),name='create-notificacion-manual'),
    path('get-notificacion/<int:id_notificacion_correspondencia>/', views.GetNotificacionesCorrespondeciaAnexos.as_view(),name='get-notificaion'),
    path('get-tarear-funcionario/', views.ListaTareasFuncionario.as_view(),name='get-tareas-funcionario'),
    path('update-tarea/<int:pk>/', views.RegistrosNotificacionesCorrespondenciaCorrespondenciaUpdate.as_view(),name='update-tarea'),
    path('update-estado-tarea/<int:pk>/', views.RegistrosNotificacionesCorrespondenciaEstadoUpdate.as_view(),name='update-tarea-estado'),

    path('cancelar-asignacion-notificacion/<int:pk>/', views.CancelarAsignacionNotificacion.as_view(),name='cancelar-asignacion-notificacion'),
    path('cancelar-asignacion-tarea/<int:pk>/', views.CancelarAsignacionTarea.as_view(),name='cancelar-asignacion-tarea'),

    # Tipos de Notificaciones
    path('create-tipos-notificaciones/', views.TiposNotificacionesCorrespondenciaCreate.as_view(),name='create-tipos-notificaciones'),
    path('get-tipos-notificaciones/', views.TiposNotificacionesCorrespondenciaGet.as_view(),name='get-tipos-notificaciones'),
    path('update-tipos-notificaciones/<int:pk>/', views.TiposNotificacionesCorrespondenciaUpdate.as_view(),name='update-tipos-notificaciones'),
    path('delete-tipos-notificaciones/<int:pk>/', views.TiposNotificacionesCorrespondenciaDelete.as_view(),name='delete-tipos-notificaciones'),

    # Estados de Notificaciones
    path('create-estado-notificaciones/', views.EstadosNotificacionesCorrespondenciaCreate.as_view(),name='create-estado-notificaciones'),
    path('get-estado-notificaciones/', views.EstadosNotificacionesCorrespondenciaGet.as_view(),name='get-estado-notificaciones'),
    path('update-estado-notificaciones/<int:pk>/', views.EstadosNotificacionesCorrespondenciaUpdate.as_view(),name='update-estado-notificaciones'),
    path('delete-estado-notificaciones/<int:pk>/', views.EstadosNotificacionesCorrespondenciaDelete.as_view(),name='delete-estado-notificaciones'),

     # Causas o Anomalias de Notificaciones
    path('create-Causas-notificaciones/', views.CausaOAnomaliasNotificacionesCorrespondenciaCreate.as_view(),name='create-Causas-notificaciones'),
    path('get-Causas-notificaciones/', views.CausaOAnomaliasNotificacionesCorrespondenciaGet.as_view(),name='get-Causas-notificaciones'),
    path('update-Causas-notificaciones/<int:pk>/', views.CausaOAnomaliasNotificacionesCorrespondenciaUpdate.as_view(),name='update-Causas-notificaciones'),
    path('delete-Causas-notificaciones/<int:pk>/', views.CausaOAnomaliasNotificacionesCorrespondenciaDelete.as_view(),name='delete-Causas-notificaciones'),

    # Tipos de Anexos de Notificaciones
    path('create-tipos-anexos-notificaciones/', views.TiposAnexosNotificacionesCorrespondenciaCreate.as_view(),name='create-tipos-anexos-notificaciones'),
    path('get-tipos-anexos-notificaciones/', views.TiposAnexosNotificacionesCorrespondenciaGet.as_view(),name='get-tipos-anexos-notificaciones'),
    path('update-tipos-anexos-notificaciones/<int:pk>/', views.TiposAnexosNotificacionesCorrespondenciaUpdate.as_view(),name='update-tipos-anexos-notificaciones'),
    path('delete-tipos-anexos-notificaciones/<int:pk>/', views.TiposAnexosNotificacionesCorrespondenciaDelete.as_view(),name='delete-tipos-anexos-notificaciones'),

    # Tipos de Documentos de Notificaciones
    path('create-tipos-documentos-notificaciones/', views.TiposDocumentosNotificacionesCorrespondenciaCreate.as_view(),name='create-tipos-documentos-notificaciones'),
    path('get-tipos-documentos-notificaciones/', views.TiposDocumentosNotificacionesCorrespondenciaGet.as_view(),name='get-tipos-documentos-notificaciones'),
    path('update-tipos-documentos-notificaciones/<int:pk>/', views.TiposDocumentosNotificacionesCorrespondenciaUpdate.as_view(),name='update-tipos-documentos-notificaciones'),
    path('delete-tipos-documentos-notificaciones/<int:pk>/', views.TiposDocumentosNotificacionesCorrespondenciaDelete.as_view(),name='delete-tipos-documentos-notificaciones'),

    # Tramites y Actos Administrativos
    path('get-tramites/', views.GetTramite.as_view(),name='get-tramites'),
    path('get-tipos-actos/', views.TipoActosAdministrativos.as_view(),name='get-tipos-actos'),
    path('get-actos/', views.ActosAdministrativosGet.as_view(),name='get-actos'),

    # Pagina Gaceta
    path('get-datos-notificacion-gaceta/<int:id_registro_notificacion>/', views.DatosNotificacionGacetaGet.as_view(),name='get-datos-notificacion-gaceta'),
    path('get-datos-notificacion-anexos-gaceta/<int:id_notificacion>/', views.AnexosNotificacionGacetaGet.as_view(),name='get-datos-notificacion-anexos-gaceta'),
    path('get-datos-notificacion-anexos-registro/<int:id_registro_notificacion>/', views.AnexosNotificacionRegistroGet.as_view(),name='get-datos-notificacion-anexos-registro'),
    path('get-tipos-anexos-gaceta/<int:id_tipo_notificacion>/', views.TipoAnexosSoporteGacetaGet.as_view(),name='get-tipos-anexos-gaceta'),
    path('get-causas-o-anomalias-gaceta/<int:id_tipo_notificacion>/', views.CausasOAnomaliasGacetaGet.as_view(),name='get-causas-o-anomalias-gaceta'),
    path('create-soportes-anexos-gaceta/', views.AnexosSoporteGacetaCreate.as_view(),name='create-soportes-anexos-gaceta'),
    path('update-registro-notificacion-gaceta/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaGacetaUpdate.as_view(),name='update-registro-notificacion-gaceta'),

    # Pagina Edictos
    path('get-datos-notificacion-edictos/<int:id_registro_notificacion>/', views.DatosNotificacionEdictosGet.as_view(),name='get-datos-notificacion-edictos'),
    path('get-datos-notificacion-anexos-edictos/<int:id_registro_notificacion>/', views.AnexosNotificacionEdictosGet.as_view(),name='get-datos-notificacion-anexos-edictos'),
    path('create-soportes-anexos-edictos/', views.AnexosSoporteEdictosCreate.as_view(),name='create-soportes-anexos-edictos'),
    path('update-registro-notificacion-edictos/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaEdictosUpdate.as_view(),name='update-registro-notificacion-edictos'),

    # Pagina Avisos
    path('get-datos-notificacion-avisos/<int:id_registro_notificacion>/', views.DatosNotificacionAvisosGet.as_view(),name='get-datos-notificacion-avisos'),
    path('get-datos-notificacion-anexos-avisos/<int:id_registro_notificacion>/', views.AnexosNotificacionAvisosGet.as_view(),name='get-datos-notificacion-anexos-avisos'),
    path('create-soportes-anexos-avisos/', views.AnexosSoporteAvisosCreate.as_view(),name='create-soportes-anexos-avisos'),
    path('update-registro-notificacion-avisos/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaAvisosUpdate.as_view(),name='update-registro-notificacion-avisos'),

    # Pagina Personal
    path('get-datos-notificacion-personal/<int:id_registro_notificacion>/', views.DatosNotificacionPersonalGet.as_view(),name='get-datos-notificacion-personal'),
    path('get-datos-notificacion-anexos-personal/<int:id_registro_notificacion>/', views.AnexosNotificacionPersonalGet.as_view(),name='get-datos-notificacion-anexos-personal'),
    path('create-soportes-anexos-personal/', views.AnexosSoportePersonalCreate.as_view(),name='create-soportes-anexos-personal'),
    path('update-registro-notificacion-personal/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaPersonalUpdate.as_view(),name='update-registro-notificacion-personal'),

    # Correo electronico
    path('get-datos-notificacion-correo/<int:id_registro_notificacion>/', views.DatosNotificacionCorreoGet.as_view(),name='get-datos-notificacion-correo'),
    path('get-datos-titular-correo/<int:id_registro_notificacion>/', views.DatosTitularesCorreoGet.as_view(),name='get-datos-titular-correo'),
    path('get-datos-notificacion-anexos-correo/<int:id_registro_notificacion>/', views.AnexosNotificacionCorreoGet.as_view(),name='get-datos-notificacion-anexos-correo'),
    path('create-soportes-anexos-correo/', views.AnexosSoporteCorreoCreate.as_view(),name='create-soportes-anexos-correo'),
    path('update-registro-notificacion-correo/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaCorreoUpdate.as_view(),name='update-registro-notificacion-correo'),

    # Correspondecia fisica
    path('get-datos-notificacion-correspondencia/<int:id_registro_notificacion>/', views.DatosNotificacionCorrespondenciaGet.as_view(),name='get-datos-notificacion-correspondencia'),
    path('get-datos-titular-correspondencia/<int:id_registro_notificacion>/', views.DatosTitularesCorrespondenciaGet.as_view(),name='get-datos-titular-correo'),
    path('get-datos-notificacion-anexos-correspondencia/<int:id_registro_notificacion>/', views.AnexosNotificacionCorrespondenciaGet.as_view(),name='get-datos-notificacion-anexos-correspondencia'),
    path('create-soportes-anexos-correspondencia/', views.AnexosSoporteCorrespondenciaCreate.as_view(),name='create-soportes-anexos-correspondencia'),
    path('update-registro-notificacion-correspondencia/<int:id_registro_notificacion>/', views.RegistrosNotificacionesCorrespondenciaCorrespondenciaUpdate.as_view(),name='update-registro-notificacion-correspondencia'),

    # Generar constancias de notificaciones
    path('get-constancias-notificacion/<int:id_registro_notificacion>/', views.GenerarConstanciaNotificacion.as_view(),name='get-constancias-notificacion'),
    path('get-datos-documentos/<int:id_registro_notificacion>/', views.DatosDocumentosNotificacion.as_view(),name='get-datos-documentos'),
    path('create-documento-generado/', views.DocumentosGeneradosCreate.as_view(),name='create-documento-generado'),
    path('notificaciones-automaticas-create/', views.NotificacionesAutomaticasCreate.as_view(),name='notificaciones-automaticas-create'),
    path('notificaciones-automaticas-bia-create/', views.NotificacionesAutomaticasBiaCreate.as_view(),name='notificaciones-automaticas-bia-create'),
    path('notificaciones-opas-create/', views.NotificacionesOPASCreate.as_view(),name='notificaciones-opas-create'),
    path('notificaciones-otros-create/', views.NotificacionesOtrosCreate.as_view(),name='notificaciones-otros-create'),
    

    

    

    
]



 