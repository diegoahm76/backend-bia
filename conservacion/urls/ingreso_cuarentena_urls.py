from django.urls import path
from conservacion.views import ingreso_cuarentena_views as views

urlpatterns = [
    path('get-viveros/', views.GetViveroView.as_view(), name='get-viveros'),
    path('get-lotes-etapa/', views.GetViveroView.as_view(), name='get-viveros'),
]