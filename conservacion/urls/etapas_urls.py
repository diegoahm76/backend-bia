from django.urls import path
from conservacion.views import etapas_views as views


urlpatterns = [
    path('filtro-material-vegetal/',views.FiltroMaterialVegetal.as_view(),name='filtro-material-vegetal')
]