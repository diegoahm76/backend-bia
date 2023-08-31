from django.urls import path
from recaudo.views import reportes_views as views

urlpatterns = [
    
    path('reporte-general-cartera/<str:fin>/', views.ReporteCarteraGeneralView.as_view(), name='informe-general'),
    path('reporte-general-detallado/', views.ReporteCarteraGeneralDetalleView.as_view(), name='informe-detallado'),
    path('reporte-cartera-edades/', views.ReporteCarteraEdadesView.as_view(), name='informe-edades'),
    path('reporte-facilidades-pagos/', views.ReporteFacilidadesPagoView.as_view(), name='informe-facilidad'),
    path('reporte-facilidades-pagos-detalle/', views.ReporteFacilidadesPagosDetalleView.as_view(), name='informe-facilidad-detalle'),
]