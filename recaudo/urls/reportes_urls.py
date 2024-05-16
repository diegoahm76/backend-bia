from django.urls import path
from recaudo.views import reportes_views as views

urlpatterns = [
    path('reporte-general-cartera-grafica/<str:fin>/', views.ReporteCarteraGeneralGraficaView.as_view(), name='informe-general-grafica'),
    path('reporte-general-cartera/<str:fin>/', views.ReporteCarteraGeneralView.as_view(), name='informe-general'),
    path('reporte-general-detallado/', views.ReporteCarteraGeneralDetalleView.as_view(), name='informe-detallado'),
    path('reporte-cartera-edades/', views.ReporteCarteraEdadesView.as_view(), name='informe-edades'),
    path('reporte-facilidades-pagos/', views.ReporteFacilidadesPagoView.as_view(), name='informe-facilidad'),
    path('reporte-facilidades-pagos-detalle/', views.ReporteFacilidadesPagosDetalleView.as_view(), name='informe-facilidad-detalle'),


    #Reportes_Nuevos
    path('reporte-rango-edades/', views.RangosEdadListView.as_view(), name='reporte-rango-edades'),
    path('reporte-concepto-contable/', views.ConceptoContableView.as_view(), name='reporte-concepto-contable'),
    path('reporte-general-cartera-edad/', views.CarteraListView.as_view(), name='reporte-cartera-edades'),
    path('reporte-general-cartera-deuda/', views.ReporteGeneralCarteraDeuda.as_view(), name='reporte-cartera-deuda'),
    path('reporte-general-cartera-deuda-top/', views.ReporteGeneralCarteraDeudaTop.as_view(), name='reporte-cartera-deuda'),
    path('reporte-general-cartera-deuda-y-edad/', views.ReporteGeneralCarteraDeudaYEdad.as_view(), name='reporte-cartera-deuda-edad'),
    path('reporte-general-cartera-deuda-y-edad-top/', views.ReporteGeneralCarteraDeudaYEdadTop.as_view(), name='reporte-cartera-deuda-edad-top'),


]