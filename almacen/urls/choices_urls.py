from django.urls import path
from almacen.views import choices_views as views

urlpatterns = [
    # Choices
    path('agrupacion-documental/', views.AgrupacionDocumentalChoices.as_view(), name='agrupacion-documental'),
    path('tipo-unidad/', views.TipoUnidadChoices.as_view(), name='tipo-unidad'),
    path('estados-articulo/', views.EstadosArticuloChoices.as_view(), name='estados-articulo'),
    path('magnitudes/', views.MagnitudesChoices.as_view(), name='magnitudes'),
    path('tipo-documento/', views.TipoDocumentoChoices.as_view(), name='tipo-documento'),
    path('tipo-combustible/', views.TipoCombustibleChoices.as_view(), name='tipo-combustible'),
    path('tipo-mantenimiento/', views.TipoMantenimientoChoices.as_view(), name='tipo-mantenimiento'),
    path('tipo-vehiculo/', views.TipoVehiculoChoices.as_view(), name='tipo-vehiculo'),
    path('tipo-bien/', views.TipoBienChoices.as_view(), name='tipo-bien'),
]