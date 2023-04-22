from django.urls import path
from recaudo.views import liquidaciones_views as views

urlpatterns = [
    path('opciones-liquidacion-base/', views.OpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-todos'),
    path('opciones-liquidacion-base', views.OpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-todos'),
    path('opciones-liquidacion-base/<int:pk>/', views.DetalleOpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-detalles'),
]
