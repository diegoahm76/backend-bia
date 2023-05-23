from django.urls import path
from transversal.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-unidad/', views.TipoUnidadChoices.as_view(), name='tipo-unidad'),
    path('agrupacion-documental/', views.AgrupacionDocumentalChoices.as_view(), name='agrupacion-documental'),
]