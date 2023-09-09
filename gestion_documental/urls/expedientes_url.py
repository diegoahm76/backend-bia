from django.urls import path

from gestion_documental.views import expedientes_views as views


urlpatterns = [
    #Cierre de expedientes         
     path('expedientes/buscar-expediente/',views.ExpedienteSearch.as_view(), name='buscar-expediente'),
     path('expedientes/listar-trd/',views.TrdDateGet.as_view(), name='listar-trd'),

     
]