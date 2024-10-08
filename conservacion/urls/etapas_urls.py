from django.urls import path
from conservacion.views import etapas_views as views


urlpatterns = [
    path('filtro-material-vegetal/<str:id_vivero>/',views.FiltroMaterialVegetal.as_view(),name='filtro-material-vegetal'),
    path('guardar-cambio-etapa/',views.GuardarCambioEtapa.as_view(),name='guardar-cambio-etapa'),
    path('actualizar-cambio-etapa/<str:pk>/',views.ActualizarCambioEtapa.as_view(),name='actualizar-cambio-etapa'),
    path('filtro-cambio-etapa/<str:id_vivero>/',views.FiltroCambioEtapa.as_view(),name='filtro-cambio-etapa'),
    path('anular-cambio-etapa/<str:pk>/',views.AnularCambioEtapa.as_view(),name='anular-cambio-etapa')
]