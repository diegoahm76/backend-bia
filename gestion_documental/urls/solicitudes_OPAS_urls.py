
from gestion_documental.views import solicitudes_OPAS_views as views

from django.urls import path


urlpatterns = [
    # Tabla de Control de Acceso
    path('opas/persona/get/<str:id>/', views.TramiteListOpasGetView.as_view(), name='tca-list-get'),
    #RequerimientosTramiteGetByTramiteOPA
    path('opas/requerimientos/get/<str:tra>/', views.RequerimientosTramiteGetByTramiteOPA.as_view(), name='requerimientos-get'),

]