from django.urls import path
from recaudo.views import liquidaciones_views as views

urlpatterns = [
    path('opciones-liquidacion-base/', views.OpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-todos'),
    path('opciones-liquidacion-base/<int:pk>/', views.DetalleOpcionesLiquidacionBaseView.as_view(), name='opciones-liquidacion-base-detalles'),

    path('deudores/', views.DeudoresView.as_view(), name='deudores-todos'),
    path('deudores/<str:identificacion>', views.DeudoresIdentificacionView.as_view(), name='deudores-busqueda-identificacion'),

    path('liquidacion-base/', views.LiquidacionBaseView.as_view(), name='liquidacion-base-todos'),
    path('liquidacion-base/<int:pk>/', views.ObtenerLiquidacionBaseView.as_view(), name='liquidacion-base-detalle'),

    path('detalles-liquidacion-base/', views.DetallesLiquidacionBaseView.as_view(), name='liquidacion-base-agregar'),
    path('detalles-liquidacion-base/<int:liquidacion>/', views.DetallesLiquidacionBaseView.as_view(), name='liquidacion-base-detalles'),

    path('expedientes/', views.ExpedientesView.as_view(), name='expedientes-todos'),
]
