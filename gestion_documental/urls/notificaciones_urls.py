from django.urls import path
from gestion_documental.views import notificaciones_views as views

urlpatterns = [
    # Notificaciones
    path('get-notificaciones/', views.ListaNotificacionesCorrespondencia.as_view(),name='get-notificaiones'),
    path('get-asignaciones/', views.GetAsignacionesCorrespondencia.as_view(),name='get-asignaciones'),
    path('create-asignacion/', views.CrearAsignacionNotificacion.as_view(),name='create-asignacion'),
    path('create-notificacion-manual/', views.CrearNotiicacionManual.as_view(),name='create-notificacion-manual'),

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
]