from django.urls import path

from gestion_documental.views import encuentas_views as views

urlpatterns = [
    path('encabezado_encuesta/create/',views.EncabezadoEncuestaCreate.as_view(), name='crear-encabezado'),

]