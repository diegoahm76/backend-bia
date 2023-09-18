from django.urls import path

from gestion_documental.views import plantillas_views as views

urlpatterns = [
    path('plantilla_documento/create/', views.PlantillasDocCreate.as_view(),name='crear-plantilla'),
    path('tipos_tipologia/get/',views.TipologiasDocGetActivo.as_view(),name='listar-tipologias')
]