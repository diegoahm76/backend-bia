from django.urls import path
from gestion_documental.views import radicados_views as views
urlpatterns = [

    path('imprimir-radicado/', views.GetRadicadosImprimir.as_view(), name='imprimir-radicado')
]