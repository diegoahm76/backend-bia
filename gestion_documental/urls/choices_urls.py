from django.urls import path
from gestion_documental.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-clasificacion/', views.TipoClasificacion.as_view(), name='tipo-clasificacion'),
    path('tipos-medios-doc/', views.TiposMediosDoc.as_view(), name='tipos-medios-doc'),
    path('disposicion-final-series/', views.DisposicionFinalSeries.as_view(), name='disposicion-final-series'),
    
]