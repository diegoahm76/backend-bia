from django.urls import path
from gestion_documental.views import reporte_indices_archivos_carpetas_views as views

urlpatterns = [
    # Tabla de Control de Acceso
    path('reporte_general/get/', views.ReporteIndicesTodosGet.as_view(), name='tca-list-get'),

]