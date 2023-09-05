from django.urls import path
from gestion_documental.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-clasificacion/', views.TipoClasificacion.as_view(), name='tipo-clasificacion'),
    path('tipos-medios-doc/', views.TiposMediosDoc.as_view(), name='tipos-medios-doc'),
    path('disposicion-final-series/', views.DisposicionFinalSeries.as_view(), name='disposicion-final-series'),
    path('cod-tipo-consecutivo/', views.GetCodConsecutivo.as_view(), name='tipos-consecutivos'),
    # path('permisos-gd/', views.PermisosGD.as_view(), name='permisos-gd'),
    path('tipo-expediente/', views.TipoExpediente.as_view(), name='tipo-expediente'),
    path('estado-expediente/', views.EstadoExpediente.as_view(), name='estado-expediente'),
    path('etapa-actual-expediente/', views.EtapaActualExpediente.as_view(), name='etapa-expediente'),



    
]