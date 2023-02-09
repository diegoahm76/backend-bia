from django.urls import path
from conservacion.views import ingreso_cuarentena_views as views

urlpatterns = [
    path('get-viveros/', views.GetViveroView.as_view(), name='get-viveros'),
    path('get-lotes-etapa/<str:id_vivero>/<str:id_codigo>/', views.GetLotesEtapaView.as_view(), name='get-etapas-lote'),
]