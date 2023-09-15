from django.urls import path

from gestion_documental.views import expedientes_views as views


urlpatterns = [
    #Cierre de expedientes         
     path('expedientes/buscar-expediente/',views.ExpedienteSearch.as_view(), name='buscar-expediente'),
     path('expedientes/listar-trd/',views.TrdDateGet.as_view(), name='listar-trd'),
     path('expedientes/agregar-archivo-soporte/',views.AgregarArchivoSoporte.as_view(), name='listar-trd'),
     path('expedientes/orden-siguiente/',views.ExpedienteGetOrden.as_view(), name='orden-expediente'),
     path('expedientes/orden-actual/',views.EstanteDepositoGetOrdenActual.as_view(), name='orden-expediente-actual'),
     path('expedientes/listar-topologias/',views.ListarTipologias.as_view(), name='listar-topologias'),
   




     
]