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
     path('expedientes/archivos-digitales/',views.UploadPDFView.as_view(), name='adjuntar-archvios'),
     path('expedientes/listar-archivos/',views.ListarArchivosDigitales.as_view(), name='listar-archvios-digitales'),
     path('expedientes/listar-expedientes/',views.ListaExpedientesDocumentales.as_view(), name='listar-expedientes'),
    path('expedientes/archivos-digitales/create/',views_archivos.ArchivosDgitalesCreate.as_view(), name='crear-archvios'),

     
]