from django.urls import path
from gestion_documental.views import vinculacion_views as views


urlpatterns = [
    #DESVINCULACION
    path('desvinculacion-persona/<str:id_persona>/', views.Desvinculacion_persona.as_view(),name='desvinculacion-persona'),
    
]