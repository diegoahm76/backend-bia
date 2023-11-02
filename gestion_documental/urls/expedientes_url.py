from django.urls import path

from gestion_documental.views import expedientes_views as views
from gestion_documental.views import archivos_digitales_views as views_archivos


urlpatterns = [
    #Apertura de expedientes
    path('expedientes/trd-actual/',views.TrdActualGet.as_view(), name='trd-actual'),
    path('expedientes/serie-subserie-unidad-trd/get/',views.SerieSubserieUnidadTRDGetView.as_view(), name='tripleta-trd'),
    path('expedientes/configuracion-expediente/get/<str:id_catserie_unidadorg>/',views.ConfiguracionExpedienteGet.as_view(), name='configuracion-expediente'),
    path('expedientes/apertura-expediente/create/',views.AperturaExpedienteCreate.as_view(), name='apertura-expediente-create'),
    path('expedientes/apertura-expediente/get/<str:id_expediente_documental>/',views.AperturaExpedienteGet.as_view(), name='apertura-expediente-get'),
    path('expedientes/apertura-expediente/update/<str:id_expediente_documental>/',views.AperturaExpedienteUpdate.as_view(), name='apertura-expediente-update'),
    path('expedientes/apertura-expediente/anular/<str:id_expediente_documental>/',views.AnularExpediente.as_view(), name='anular-expediente'),
    path('expedientes/apertura-expediente/borrar/<str:id_expediente_documental>/',views.BorrarExpediente.as_view(), name='borrar-expediente'),
    
    #Indexación de documentos
    path('expedientes/trd-actual-retirados/',views.TrdActualRetiradosGet.as_view(), name='trd-actual-retirados'),
    path('expedientes/list-complejos/get/<str:id_catserie_unidadorg>/',views.ListExpedientesComplejosGet.as_view(), name='list-exp-complejos'),
    path('expedientes/indexar-documentos/create/<str:id_expediente_documental>/',views.IndexarDocumentosCreate.as_view(), name='indexar-documentos-create'),
    path('expedientes/indexar-documentos/get/<str:id_documento_de_archivo_exped>/',views.IndexarDocumentosGet.as_view(), name='indexar-documentos-get'),
    path('expedientes/indexar-documentos/update/<str:id_documento_de_archivo_exped>/',views.IndexarDocumentosUpdate.as_view(), name='indexar-documentos-update'),
    path('expedientes/indexar-documentos/anular/<str:id_documento_de_archivo_exped>/',views.IndexarDocumentosAnular.as_view(), name='indexar-documentos-anular'),
    path('expedientes/indexar-documentos/delete/<str:id_documento_de_archivo_exped>/',views.IndexarDocumentosBorrar.as_view(), name='indexar-documentos-borrar'),
    
    #Cierre de expedientes         
     path('expedientes/buscar-expediente-abierto/',views.ExpedienteSearch.as_view(), name='buscar-expediente'),
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
     path('expedientes/listar-archivos-soporte/<int:id_expediente>/',views.ArchivosSoporteGetId.as_view(), name='listar-todos-archivos-soporte'),
     path('expedientes/editar-archivos-soporte/<int:id_documento_de_archivo_exped>/',views.UpdateArchivoSoporte.as_view(), name='editar-archivos-soporte'),
     path('expedientes/listar-info-archivos/<int:id_documento_de_archivo_exped>/',views.DetalleArchivoSoporte.as_view(), name='listar-info-archivos-soporte'),



     #Reapertura_Expediente
     path('expedientes/buscar-expediente-cerrado/',views.ExpedienteSearchCerrado.as_view(), name='buscar-expediente'),
     path('expedientes/info-expediente-cerrado/<int:id_expediente>/',views.CierresReaperturasExpedienteDetailView.as_view(), name='informacion-expediente-cerrado'),
     path('expedientes/reapertura-expediente/',views.ReaperturaExpediente.as_view(), name='reapertura-expediente'),


     
  


      


     
]