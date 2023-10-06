from django.urls import path

from gestion_documental.views import expedientes_views as views
from gestion_documental.views import archivos_digitales_views as views_archivos


urlpatterns = [
    #Cierre de expedientes         
     path('expedientes/buscar-expediente/',views.ExpedienteSearch.as_view(), name='buscar-expediente'),
     path('expedientes/listar-trd/',views.TrdDateGet.as_view(), name='listar-trd'),
     path('expedientes/agregar-archivo-soporte/',views.AgregarArchivoSoporte.as_view(), name='listar-trd'),
     path('expedientes/orden-siguiente/',views.ExpedienteGetOrden.as_view(), name='orden-expediente'),
     path('expedientes/orden-actual/',views.ExpedienteGetOrdenActual.as_view(), name='orden-expediente-actual'),
     path('expedientes/listar-topologias/',views.ListarTipologias.as_view(), name='listar-topologias'),
     path('expedientes/archivos-digitales/adjuntar/',views.UploadPDFView.as_view(), name='adjuntar-archvios'),
     path('expedientes/listar-archivos/',views.ListarArchivosDigitales.as_view(), name='listar-archvios-digitales'),
     path('expedientes/listar-expedientes/',views.ListaExpedientesDocumentales.as_view(), name='listar-expedientes'),
     path('expedientes/archivos-digitales/create/',views_archivos.ArchivosDgitalesCreate.as_view(), name='crear-archvios'),
     path('expedientes/cierre-expediente/',views.CierreExpediente.as_view(), name='cierre-expediente'),
     path('expedientes/eliminar-archivo-soporte/<int:id_documento_de_archivo_exped>/',views.EliminarArchivoSoporte.as_view(), name='eliminar-archivo'),
     path('expedientes/listar-todos-archivos-soporte/',views.ArchivosSoporteGetAll.as_view(), name='listar-todos-archivos-soporte'),
     path('expedientes/editar-archivos-soporte/<int:id_documento_de_archivo_exped>/',views.UpdateArchivoSoporte.as_view(), name='editar-archivos-soporte'),


     
]