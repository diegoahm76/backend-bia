from django.urls import path
from conservacion.views import ingreso_cuarentena_views as views

urlpatterns = [
    path('get-viveros/', views.GetViveroView.as_view(), name='get-viveros'),
    path('get-lotes-etapa/<str:id_vivero>/<str:id_codigo>/', views.GetLotesEtapaView.as_view(), name='get-etapas-lote'),
    path('get-lotes-etapa/<str:id_vivero>/', views.GetLotesEtapaLupaView.as_view(), name='get-etapas-lote-lupa'),
    path('create/', views.CreateIngresoCuarentenaView.as_view(), name='create-ingreso-cuarentena'),
    path('anular/<str:id_ingreso_cuarentena>/', views.AnularIngresoCuarentenaView.as_view(), name='anular-ingreso-cuarentena'),
    path('update/<str:id_ingreso_cuarentena>/', views.UpdateIngresoCuarentenaView.as_view(), name='update-ingreso-cuarentena'),
]