from django.urls import path
from transversal.views import configuracionEntidades_views as views

urlpatterns = [
    path('configuracionEntidad/<str:pk>/', views.GetConfiguracionEntidadByID.as_view(), name='get-configuracionEntidad'),
    path('configuracionEntidad/actualizar/<int:id_persona_entidad>/',views.UpdateConfiguracionEntidad.as_view(),name='update-configuracionEntidad'),
]