from django.urls import path

from gestion_documental.views import encuentas_views as views

urlpatterns = [
    path('encabezado_encuesta/create/',views.EncabezadoEncuestaCreate.as_view(), name='crear-encabezado'),
    path('encabezado_encuesta/get/',views.EncabezadoEncuestaGet.as_view(), name='get-encabezado'),
    path('encabezado_encuesta/delete/<str:pk>/',views.EncabezadoEncuestaDelete.as_view(), name='delete-encabezado'),
    path('preguntas_encuesta/create/',views.PreguntasEncuestaCreate.as_view(), name='crear-pregunta'),
    path('opciones_rta/create/',views.OpcionesRtaCreate.as_view(), name='crear-opcion-respuesta'),
    

]#EncabezadoEncuestaGet